# app/routes/activity.py
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from app import db
from app.models import Activity, Enrollment, ActivityTag, InterestTag
from app.utils.auth import jwt_required, get_current_user, is_organizer
from app.utils.helpers import parse_datetime

activity_bp = Blueprint('activity', __name__)


# 创建活动
@activity_bp.post('/')
@jwt_required
def create_activity():
    user = get_current_user()
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    # 添加调试日志
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    # 记录请求信息
    logger.debug(f"请求方法: {request.method}")
    logger.debug(f"请求头: {dict(request.headers)}")
    logger.debug(f"请求表单: {dict(request.form)}")
    logger.debug(f"请求文件: {list(request.files.keys())}")
    
    # 处理JSON数据和文件上传
    data = request.form.get('data')
    if data:
        import json
        logger.debug(f"表单中的data字段: {data}")
        data = json.loads(data)
    else:
        data = request.get_json()
        logger.debug(f"JSON数据: {data}")
    
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid input'}), 400
    
    # 验证必填字段
    required_fields = ['title', 'description', 'location', 'start_time', 'end_time', 'max_participants']
    for field in required_fields:
        if field not in data:
            return jsonify({'status': 'error', 'message': f'Missing required field: {field}'}), 400
    
    try:
        # 转换时间格式
        start_time = parse_datetime(data['start_time'])
        end_time = parse_datetime(data['end_time'])
        if not start_time or not end_time:
            return jsonify({'status': 'error', 'message': 'Invalid date format for start_time or end_time'}), 400
        
        # 处理文件上传或URL设置
        cover_image_url = None
        logger.debug(f"初始cover_image_url: {cover_image_url}")
        
        # 1. 首先检查是否有文件上传，支持多种字段名称
        file_fields = ['cover_image', 'file', 'image', 'avatar']
        file = None
        
        for field_name in file_fields:
            if field_name in request.files:
                file = request.files[field_name]
                logger.debug(f"找到文件字段: {field_name}, 文件名: {file.filename}")
                break
        
        if file and file.filename:
            filename = secure_filename(file.filename)
            logger.debug(f"安全文件名: {filename}")
            # 确保上传目录存在
            upload_folder = current_app.config['UPLOAD_FOLDER']
            logger.debug(f"上传目录: {upload_folder}")
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            # 保存文件
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            cover_image_url = f"/uploads/{filename}"
            logger.debug(f"文件上传后cover_image_url: {cover_image_url}")
        
        # 2. 如果没有文件上传，检查是否有直接提供的图片URL（JSON数据中）
        if not cover_image_url:
            # 支持多种可能的图片字段名称
            image_fields = ['cover_image_url', 'image', 'img', 'picture', 'pic']
            
            for field_name in image_fields:
                if field_name in data and data[field_name]:
                    logger.debug(f"从data中获取图片URL，字段名: {field_name}, URL: {data[field_name]}")
                    cover_image_url = data[field_name]
                    break
        
        # 3. 额外检查表单中是否有cover_image_url字段（处理form-data中的URL参数）
        if not cover_image_url and 'cover_image_url' in request.form and request.form['cover_image_url']:
            logger.debug(f"从表单中获取cover_image_url: {request.form['cover_image_url']}")
            cover_image_url = request.form['cover_image_url']
        
        logger.debug(f"最终cover_image_url: {cover_image_url}")
        
        # 创建活动
        # 处理时间字段
        registration_deadline = None
        if 'registration_deadline' in data and data['registration_deadline']:
            registration_deadline = parse_datetime(data['registration_deadline'])
        
        refund_deadline = None
        if 'refund_deadline' in data and data['refund_deadline']:
            refund_deadline = parse_datetime(data['refund_deadline'])
            
        new_activity = Activity(
            title=data['title'],
            description=data['description'],
            activity_type=data.get('activity_type', 'k歌'),
            location=data['location'],
            longitude=data.get('longitude'),
            latitude=data.get('latitude'),
            start_time=start_time,
            end_time=end_time,
            registration_deadline=registration_deadline,
            refund_deadline=refund_deadline,
            organizer_id=user.id,
            current_participants=1,  # 发起人自己算一个
            max_participants=data['max_participants'],
            room_type=data.get('room_type'),
            music_style=data.get('music_style'),
            accept_beginners=data.get('accept_beginners', True),
            accept_microphone_king=data.get('accept_microphone_king', True),
            cost_type=data.get('cost_type', 'aa'),
            estimated_cost_per_person=data.get('estimated_cost_per_person') or data.get('price'),
            total_cost=data.get('total_cost'),
            deposit_amount=data.get('deposit_amount', 0.0),
            requirements=data.get('requirements'),
            cover_image_url=cover_image_url,  # 添加封面图片URL
            status='active' if start_time > datetime.utcnow() else 'completed'
        )
        
        db.session.add(new_activity)
        db.session.flush()  # 获取活动ID
        
        # 添加活动标签
        if 'tag_ids' in data and isinstance(data['tag_ids'], list):
            for tag_id in data['tag_ids']:
                tag = InterestTag.query.get(tag_id)
                if tag:
                    activity_tag = ActivityTag(activity_id=new_activity.id, tag_id=tag_id)
                    db.session.add(activity_tag)
        
        # 为发起人自动创建报名记录
        from app.models import Enrollment
        organizer_enrollment = Enrollment(
            user_id=user.id,
            activity_id=new_activity.id,
            status='approved',  # 发起人自动通过审核
            cost_paid=0.0,  # 初始费用为0
            deposit_paid=0.0  # 初始押金为0
        )
        db.session.add(organizer_enrollment)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Activity created successfully',
            'data': new_activity.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to create activity: {str(e)}'
        }), 500


# 获取活动列表
@activity_bp.get('/')
def get_activity_list():
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    activity_type = request.args.get('activity_type')
    status = request.args.get('status')
    location = request.args.get('location')
    min_participants = request.args.get('min_participants', type=int)
    max_participants = request.args.get('max_participants', type=int)
    start_time_min = request.args.get('start_time_min')
    start_time_max = request.args.get('start_time_max')
    
    # 构建查询，排除已取消的活动
    query = Activity.query.filter_by(is_published=True).filter(Activity.status != 'canceled')
    
    # 应用筛选条件
    if activity_type:
        query = query.filter_by(activity_type=activity_type)
    
    if status:
        query = query.filter_by(status=status)
    
    if location:
        query = query.filter(Activity.location.like(f'%{location}%'))
    
    if min_participants:
        query = query.filter(Activity.max_participants >= min_participants)
    
    if max_participants:
        query = query.filter(Activity.max_participants <= max_participants)
    
    if start_time_min:
        try:
            query = query.filter(Activity.start_time >= parse_datetime(start_time_min))
        except:
            pass
    
    if start_time_max:
        try:
            query = query.filter(Activity.start_time <= parse_datetime(start_time_max))
        except:
            pass
    
    # 排序
    query = query.order_by(Activity.start_time.desc())
    
    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # 获取当前用户（如果已登录）
    current_user = None
    try:
        from app.utils.auth import get_current_user
        current_user = get_current_user()
    except:
        pass
    
    # 构建活动数据，添加用户报名状态
    activities_data = []
    for activity in pagination.items:
        activity_dict = activity.to_dict()
        # 检查用户是否已报名
        if current_user:
            from app.models import Enrollment
            existing_enrollment = Enrollment.query.filter_by(
                user_id=current_user.id, activity_id=activity.id
            ).first()
            activity_dict['is_enrolled'] = existing_enrollment is not None
            if existing_enrollment:
                activity_dict['enrollment_status'] = existing_enrollment.status
            else:
                activity_dict['enrollment_status'] = None
        else:
            activity_dict['is_enrolled'] = False
            activity_dict['enrollment_status'] = None
        activities_data.append(activity_dict)
    
    return jsonify({
        'status': 'success',
        'message': 'Activities retrieved successfully',
        'data': {
            'activities': activities_data,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }
    }), 200


# 获取活动详情
@activity_bp.get('/<int:activity_id>')
def get_activity_detail(activity_id):
    activity = Activity.query.get(activity_id)
    if not activity or not activity.is_published:
        return jsonify({'status': 'error', 'message': 'Activity not found'}), 404
    
    # 获取当前用户（如果已登录）
    current_user = None
    try:
        from flask import request
        from flask_jwt_extended import decode_token
        from app.models import User
        
        # 从请求头中获取token
        auth_header = request.headers.get('Authorization', '')
        print(f"=== 请求头: {auth_header} ===")
        
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            print(f"=== Token: {token} ===")
            
            # 解析token
            decoded = decode_token(token)
            user_id = decoded.get('sub')
            print(f"=== 解析用户ID: {user_id} ===")
            
            if user_id:
                if isinstance(user_id, str) and user_id.isdigit():
                    user_id = int(user_id)
                current_user = User.query.get(user_id)
                if current_user:
                    print(f"=== 找到用户: {current_user.nickname} (ID: {current_user.id}) ===")
                else:
                    print(f"=== 未找到用户: {user_id} ===")
            else:
                print("=== 未获取到用户ID ===")
        else:
            print("=== 未提供有效的Authorization头 ===")
    except Exception as e:
        print(f"=== 获取用户信息失败: {str(e)} ===")
    
    # 构建活动数据，添加用户报名状态
    activity_dict = activity.to_dict()
    # 检查用户是否已报名
    if current_user:
        from app.models import Enrollment
        existing_enrollment = Enrollment.query.filter_by(
            user_id=current_user.id, activity_id=activity.id
        ).first()
        print(f"=== 检查报名状态: 用户ID={current_user.id}, 活动ID={activity.id} ===")
        print(f"=== 报名记录: {existing_enrollment} ===")
        activity_dict['is_enrolled'] = existing_enrollment is not None
        if existing_enrollment:
            activity_dict['enrollment_status'] = existing_enrollment.status
            print(f"=== 报名状态: {existing_enrollment.status} ===")
        else:
            activity_dict['enrollment_status'] = None
            print("=== 未报名 ===")
    else:
        activity_dict['is_enrolled'] = False
        activity_dict['enrollment_status'] = None
        print("=== 未登录用户 ===")
    
    return jsonify({
        'status': 'success',
        'message': 'Activity detail retrieved',
        'data': activity_dict
    }), 200


# 更新活动
@activity_bp.put('/<int:activity_id>')
@jwt_required
@is_organizer
def update_activity(activity_id):
    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({'status': 'error', 'message': 'Activity not found'}), 404
    
    # 从请求中获取数据，支持JSON和表单数据
    data = request.get_json(silent=True) or {}
    
    # 从表单数据中补充字段
    for key in request.form:
        if key not in data:
            data[key] = request.form[key]
    
    # 如果既没有JSON数据也没有表单数据，返回错误
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid input'}), 400
    
    try:
        # 更新基本信息
        if 'title' in data:
            activity.title = data['title']
        
        if 'description' in data:
            activity.description = data['description']
        
        if 'activity_type' in data:
            activity.activity_type = data['activity_type']
        
        if 'location' in data:
            activity.location = data['location']
        
        if 'longitude' in data:
            activity.longitude = data['longitude']
        
        if 'latitude' in data:
            activity.latitude = data['latitude']
        
        # 更新封面图片（支持URL或文件上传）
        # 1. 首先检查是否有文件上传，支持多种字段名称（优先处理文件上传）
        file_fields = ['cover_image', 'file', 'image', 'avatar']
        file = None
        
        for field_name in file_fields:
            if field_name in request.files:
                file = request.files[field_name]
                break
        
        if file and file.filename:
            filename = secure_filename(file.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            activity.cover_image_url = f"/uploads/{filename}"
        
        # 2. 如果没有文件上传，检查是否有直接提供的图片URL
        elif 'cover_image_url' in data:
            activity.cover_image_url = data['cover_image_url']
        
        if 'start_time' in data:
            parsed_start_time = parse_datetime(data['start_time'])
            if parsed_start_time:
                activity.start_time = parsed_start_time
            else:
                return jsonify({'status': 'error', 'message': 'Invalid date format for start_time'}), 400
        
        if 'end_time' in data:
            parsed_end_time = parse_datetime(data['end_time'])
            if parsed_end_time:
                activity.end_time = parsed_end_time
            else:
                return jsonify({'status': 'error', 'message': 'Invalid date format for end_time'}), 400
        
        if 'registration_deadline' in data:
            if data['registration_deadline']:
                parsed_reg_deadline = parse_datetime(data['registration_deadline'])
                if parsed_reg_deadline:
                    activity.registration_deadline = parsed_reg_deadline
                else:
                    return jsonify({'status': 'error', 'message': 'Invalid date format for registration_deadline'}), 400
            else:
                activity.registration_deadline = None
        
        if 'refund_deadline' in data:
            if data['refund_deadline']:
                parsed_refund_deadline = parse_datetime(data['refund_deadline'])
                if parsed_refund_deadline:
                    activity.refund_deadline = parsed_refund_deadline
                else:
                    return jsonify({'status': 'error', 'message': 'Invalid date format for refund_deadline'}), 400
            else:
                activity.refund_deadline = None
        
        if 'max_participants' in data:
            activity.max_participants = data['max_participants']
        
        if 'deposit_amount' in data:
            activity.deposit_amount = data['deposit_amount']
        
        # 更新K歌特定信息
        if 'room_type' in data:
            activity.room_type = data['room_type']
        
        if 'music_style' in data:
            activity.music_style = data['music_style']
        
        if 'accept_beginners' in data:
            activity.accept_beginners = data['accept_beginners']
        
        if 'accept_microphone_king' in data:
            activity.accept_microphone_king = data['accept_microphone_king']
        
        # 更新费用信息
        if 'cost_type' in data:
            activity.cost_type = data['cost_type']
        
        if 'estimated_cost_per_person' in data:
            activity.estimated_cost_per_person = data['estimated_cost_per_person']
        
        if 'total_cost' in data:
            activity.total_cost = data['total_cost']
        
        # 更新状态
        if 'status' in data:
            activity.status = data['status']
        
        if 'requirements' in data:
            activity.requirements = data['requirements']
        
        # 更新活动标签
        if 'tag_ids' in data and isinstance(data['tag_ids'], list):
            # 删除现有标签
            ActivityTag.query.filter_by(activity_id=activity_id).delete()
            
            # 添加新标签
            for tag_id in data['tag_ids']:
                tag = InterestTag.query.get(tag_id)
                if tag:
                    activity_tag = ActivityTag(activity_id=activity_id, tag_id=tag_id)
                    db.session.add(activity_tag)
        
        db.session.commit()
        
        return jsonify({        'status': 'success',        'message': 'Activity updated successfully',        'data': activity.to_dict()    }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to update activity: {str(e)}'
        }), 500


# 取消活动
@activity_bp.put('/<int:activity_id>/cancel')
@jwt_required
@is_organizer
def cancel_activity(activity_id):
    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({'status': 'error', 'message': 'Activity not found'}), 404
    
    # 检查是否在活动开始前2小时内，不允许取消
    time_before_start = activity.start_time - datetime.utcnow()
    if time_before_start.total_seconds() < 7200:  # 2小时 = 7200秒
        return jsonify({'status': 'error', 'message': 'Activity cannot be canceled within 2 hours before start time'}), 400
    
    try:
        # 更新活动状态为已取消
        activity.status = 'canceled'
        activity.is_published = False
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Activity canceled successfully',
            'data': activity.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to update activity: {str(e)}'
        }), 500


# 删除活动
@activity_bp.delete('/<int:activity_id>')
@jwt_required
@is_organizer
def delete_activity(activity_id):
    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({'status': 'error', 'message': 'Activity not found'}), 404
    
    try:
        # 删除相关的报名记录
        Enrollment.query.filter_by(activity_id=activity_id).delete()
        
        # 删除活动标签
        ActivityTag.query.filter_by(activity_id=activity_id).delete()
        
        # 删除活动
        db.session.delete(activity)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Activity deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to delete activity: {str(e)}'
        }), 500


# 获取用户创建的活动
@activity_bp.get('/my-organized')
@activity_bp.get('/created')  # 支持前端可能使用的端点名
@activity_bp.get('/history')  # 支持前端可能使用的端点名
@jwt_required
def get_my_organized_activities():
    user = get_current_user()
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    print(f"=== GET MY ORGANIZED ACTIVITIES START ===")
    print(f"Current user: {user.id} - {user.nickname}")
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 获取所有未取消的活动，不管是否发布
    activities = Activity.query.filter_by(organizer_id=user.id).filter(Activity.status != 'canceled').order_by(Activity.created_at.desc()).all()
    print(f"Total activities found: {len(activities)}")
    for activity in activities:
        print(f"Activity: {activity.id} - {activity.title} (published: {activity.is_published}, organizer_id: {activity.organizer_id}, status: {activity.status})")
    
    pagination = Activity.query.filter_by(organizer_id=user.id).filter(Activity.status != 'canceled').order_by(Activity.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    print(f"Paginated activities: {len(pagination.items)} (page: {page}, per_page: {per_page})")
    print(f"=== GET MY ORGANIZED ACTIVITIES END ===")
    
    return jsonify({
        'status': 'success',
        'message': 'My organized activities retrieved',
        'data': {
            'activities': [activity.to_dict() for activity in pagination.items],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }
    }), 200


# 获取用户参与的活动
@activity_bp.get('/my-participated')
@activity_bp.get('/joined')  # 支持前端旧的端点名
@jwt_required
def get_my_participated_activities():
    user = get_current_user()
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 获取用户参与的活动ID
    enrollments = Enrollment.query.filter_by(user_id=user.id).all()
    activity_ids = [enrollment.activity_id for enrollment in enrollments]
    
    pagination = Activity.query.filter(Activity.id.in_(activity_ids)).filter(Activity.status != 'canceled').order_by(Activity.start_time.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'status': 'success',
        'message': 'My participated activities retrieved',
        'data': {
            'activities': [activity.to_dict() for activity in pagination.items],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }
    }), 200
