# app/routes/activity.py
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timezone
import os
from werkzeug.utils import secure_filename
from app import db
from app.models import Activity, Enrollment, ActivityTag, InterestTag
from app.utils.auth import jwt_required, get_current_user, is_organizer

activity_bp = Blueprint('activity', __name__)


# 创建活动
@activity_bp.post('/')
@jwt_required
def create_activity():
    user = get_current_user()
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    # 处理JSON数据和文件上传
    data = request.form.get('data')
    if data:
        import json
        data = json.loads(data)
    else:
        data = request.get_json()
    
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid input'}), 400
    
    # 验证必填字段
    required_fields = ['title', 'description', 'location', 'start_time', 'end_time', 'max_participants']
    for field in required_fields:
        if field not in data:
            return jsonify({'status': 'error', 'message': f'Missing required field: {field}'}), 400
    
    try:
        # 转换时间格式，处理带Z后缀的ISO时间格式
        # 确保时间字段是字符串类型
        start_time_raw = data['start_time']
        end_time_raw = data['end_time']
        
        # 如果是整数，可能是时间戳，需要先转换
        if isinstance(start_time_raw, int):
            start_time = datetime.fromtimestamp(start_time_raw, timezone.utc)
        else:
            # 处理字符串类型，支持带Z后缀的ISO格式
            start_time_str = str(start_time_raw).replace('Z', '+00:00')
            # 如果字符串没有时区信息，添加UTC时区
            if '+' not in start_time_str and 'Z' not in start_time_str:
                start_time_str += '+00:00'
            start_time = datetime.fromisoformat(start_time_str)
        
        if isinstance(end_time_raw, int):
            end_time = datetime.fromtimestamp(end_time_raw, timezone.utc)
        else:
            # 处理字符串类型，支持带Z后缀的ISO格式
            end_time_str = str(end_time_raw).replace('Z', '+00:00')
            # 如果字符串没有时区信息，添加UTC时区
            if '+' not in end_time_str and 'Z' not in end_time_str:
                end_time_str += '+00:00'
            end_time = datetime.fromisoformat(end_time_str)
        
        # 处理文件上传
        cover_image_url = None
        if 'cover_image' in request.files:
            file = request.files['cover_image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                # 确保上传目录存在
                upload_folder = current_app.config['UPLOAD_FOLDER']
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                
                # 保存文件
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                cover_image_url = f"/uploads/{filename}"
        
        # 创建活动
        # 处理时间字段，处理带Z后缀的ISO时间格式
        registration_deadline = None
        if 'registration_deadline' in data and data['registration_deadline']:
            reg_deadline_raw = data['registration_deadline']
            if isinstance(reg_deadline_raw, int):
                registration_deadline = datetime.fromtimestamp(reg_deadline_raw, timezone.utc)
            else:
                reg_deadline_str = str(reg_deadline_raw).replace('Z', '+00:00')
                # 如果字符串没有时区信息，添加UTC时区
                if '+' not in reg_deadline_str and 'Z' not in reg_deadline_str:
                    reg_deadline_str += '+00:00'
                registration_deadline = datetime.fromisoformat(reg_deadline_str)
        
        refund_deadline = None
        if 'refund_deadline' in data and data['refund_deadline']:
            refund_deadline_raw = data['refund_deadline']
            if isinstance(refund_deadline_raw, int):
                refund_deadline = datetime.fromtimestamp(refund_deadline_raw, timezone.utc)
            else:
                refund_deadline_str = str(refund_deadline_raw).replace('Z', '+00:00')
                # 如果字符串没有时区信息，添加UTC时区
                if '+' not in refund_deadline_str and 'Z' not in refund_deadline_str:
                    refund_deadline_str += '+00:00'
                refund_deadline = datetime.fromisoformat(refund_deadline_str)
            
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
            estimated_cost_per_person=data.get('estimated_cost_per_person'),
            total_cost=data.get('total_cost'),
            deposit_amount=data.get('deposit_amount', 0.0),
            requirements=data.get('requirements'),
            cover_image_url=cover_image_url,  # 添加封面图片URL
            status='active' if start_time > datetime.now(timezone.utc) else 'completed'
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
    
    # 构建查询
    query = Activity.query.filter_by(is_published=True)
    
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
            start_time_min_str = start_time_min.replace('Z', '+00:00')
            # 如果字符串没有时区信息，添加UTC时区
            if '+' not in start_time_min_str and 'Z' not in start_time_min_str:
                start_time_min_str += '+00:00'
            query = query.filter(Activity.start_time >= datetime.fromisoformat(start_time_min_str))
        except:
            pass
    
    if start_time_max:
        try:
            start_time_max_str = start_time_max.replace('Z', '+00:00')
            # 如果字符串没有时区信息，添加UTC时区
            if '+' not in start_time_max_str and 'Z' not in start_time_max_str:
                start_time_max_str += '+00:00'
            query = query.filter(Activity.start_time <= datetime.fromisoformat(start_time_max_str))
        except:
            pass
    
    # 排序
    query = query.order_by(Activity.start_time.desc())
    
    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'status': 'success',
        'message': 'Activities retrieved successfully',
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


# 获取活动详情
@activity_bp.get('/<int:activity_id>')
def get_activity_detail(activity_id):
    activity = Activity.query.get(activity_id)
    if not activity or not activity.is_published:
        return jsonify({'status': 'error', 'message': 'Activity not found'}), 404
    
    return jsonify({
        'status': 'success',
        'message': 'Activity detail retrieved',
        'data': activity.to_dict()
    }), 200


# 更新活动
@activity_bp.put('/<int:activity_id>')
@jwt_required
@is_organizer
def update_activity(activity_id):
    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({'status': 'error', 'message': 'Activity not found'}), 404
    
    data = request.get_json()
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
        
        if 'start_time' in data:
            start_time_raw = data['start_time']
            if isinstance(start_time_raw, int):
                activity.start_time = datetime.fromtimestamp(start_time_raw, timezone.utc)
            else:
                start_time_str = str(start_time_raw).replace('Z', '+00:00')
                # 如果字符串没有时区信息，添加UTC时区
                if '+' not in start_time_str and 'Z' not in start_time_str:
                    start_time_str += '+00:00'
                activity.start_time = datetime.fromisoformat(start_time_str)
        
        if 'end_time' in data:
            end_time_raw = data['end_time']
            if isinstance(end_time_raw, int):
                activity.end_time = datetime.fromtimestamp(end_time_raw, timezone.utc)
            else:
                end_time_str = str(end_time_raw).replace('Z', '+00:00')
                # 如果字符串没有时区信息，添加UTC时区
                if '+' not in end_time_str and 'Z' not in end_time_str:
                    end_time_str += '+00:00'
                activity.end_time = datetime.fromisoformat(end_time_str)
        
        if 'registration_deadline' in data:
            if data['registration_deadline']:
                reg_deadline_raw = data['registration_deadline']
                if isinstance(reg_deadline_raw, int):
                    activity.registration_deadline = datetime.fromtimestamp(reg_deadline_raw, timezone.utc)
                else:
                    reg_deadline_str = str(reg_deadline_raw).replace('Z', '+00:00')
                    # 如果字符串没有时区信息，添加UTC时区
                    if '+' not in reg_deadline_str and 'Z' not in reg_deadline_str:
                        reg_deadline_str += '+00:00'
                    activity.registration_deadline = datetime.fromisoformat(reg_deadline_str)
            else:
                activity.registration_deadline = None
        
        if 'refund_deadline' in data:
            if data['refund_deadline']:
                refund_deadline_raw = data['refund_deadline']
                if isinstance(refund_deadline_raw, int):
                    activity.refund_deadline = datetime.fromtimestamp(refund_deadline_raw, timezone.utc)
                else:
                    refund_deadline_str = str(refund_deadline_raw).replace('Z', '+00:00')
                    # 如果字符串没有时区信息，添加UTC时区
                    if '+' not in refund_deadline_str and 'Z' not in refund_deadline_str:
                        refund_deadline_str += '+00:00'
                    activity.refund_deadline = datetime.fromisoformat(refund_deadline_str)
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
        
        return jsonify({
            'status': 'success',
            'message': 'Activity updated successfully',
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
@jwt_required
def get_my_organized_activities():
    user = get_current_user()
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = Activity.query.filter_by(organizer_id=user.id).order_by(Activity.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
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
    
    pagination = Activity.query.filter(Activity.id.in_(activity_ids)).order_by(Activity.start_time.desc()).paginate(
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
