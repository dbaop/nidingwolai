# app/routes/enrollment.py
from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from app.models import Enrollment, Activity, User
from app.utils.auth import jwt_required, get_current_user, is_organizer

enrollment_bp = Blueprint('enrollment', __name__)


# 报名参加活动
@enrollment_bp.post('/')
@jwt_required
def enroll_activity():
    user = get_current_user()
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid JSON data'}), 400
        
    # 支持多种参数名
    activity_id = None
    possible_activity_id_fields = ['activity_id', 'id', 'activityId']
    for field_name in possible_activity_id_fields:
        if field_name in data:
            activity_id = data.get(field_name)
            break
    
    if activity_id is None:
        return jsonify({'status': 'error', 'message': 'Missing activity_id parameter'}), 400
    
    # 确保activity_id是整数
    try:
        activity_id = int(activity_id)
        print(f'转换后的activity_id: {activity_id}, 类型: {type(activity_id)}')
    except (ValueError, TypeError) as e:
        print(f'activity_id转换失败: {activity_id}, 错误: {e}')
        return jsonify({'status': 'error', 'message': 'Invalid activity_id format'}), 400
    
    message = data.get('message', '')
    
    print(f'准备查找活动: ID={activity_id}')
    
    # 检查活动是否存在
    activity = Activity.query.get(activity_id)
    print(f'查找结果: {activity}')
    
    # 如果使用get()找不到，尝试使用filter_by()
    if not activity:
        print('使用filter_by()再次尝试查找')
        activity = Activity.query.filter_by(id=activity_id).first()
        print(f'filter_by()查找结果: {activity}')
    
    # 检查数据库连接和表结构
    print('检查数据库连接和表结构:')
    try:
        # 获取所有活动的ID
        all_activity_ids = db.session.query(Activity.id).all()
        print(f'所有活动ID: {all_activity_ids}')
    except Exception as e:
        print(f'检查数据库失败: {e}')
    if not activity:
        return jsonify({'status': 'error', 'message': 'Activity not found'}), 404
    
    # 检查活动状态
    if activity.status != 'active':
        return jsonify({'status': 'error', 'message': 'Activity is not active'}), 400
    
    # 检查是否超过报名截止时间
    if activity.registration_deadline and datetime.utcnow() > activity.registration_deadline:
        return jsonify({'status': 'error', 'message': 'Registration deadline has passed'}), 400
    
    # 检查是否在活动开始前1小时内，不允许报名
    import math
    time_before_start = activity.start_time - datetime.utcnow()
    if time_before_start.total_seconds() < 3600:  # 1小时 = 3600秒
        return jsonify({'status': 'error', 'message': 'Enrollment is not allowed within 1 hour before activity start time'}), 400
    
    # 检查活动是否已满
    if activity.current_participants >= activity.max_participants:
        return jsonify({'status': 'error', 'message': 'Activity is full'}), 400
    
    # 检查用户是否已经报名
    existing_enrollment = Enrollment.query.filter_by(
        user_id=user.id, activity_id=activity_id
    ).first()
    if existing_enrollment:
        return jsonify({'status': 'error', 'message': 'You have already enrolled in this activity'}), 400
    
    # 检查用户是否是发起人（不能自己报名自己的活动）
    if activity.organizer_id == user.id:
        return jsonify({'status': 'error', 'message': 'Organizer cannot enroll in their own activity'}), 400
    
    try:
        # 根据押金金额决定是否需要支付
        needs_payment = activity.deposit_amount > 0
        deposit_paid = False
        
        # 创建报名记录
        enrollment = Enrollment(
            user_id=user.id,
            activity_id=activity_id,
            status='pending',
            message=message,
            deposit_paid=deposit_paid
        )
        
        db.session.add(enrollment)
        
        # 注意：不立即增加活动的当前参与人数，而是在创建者审批通过后再增加
        # 这样可以避免未审批的报名就占用名额
        
        db.session.commit()
        
        # 构建响应
        response_data = {
            'status': 'success',
            'data': enrollment.to_dict()
        }
        
        if needs_payment:
            # 需要押金，返回支付接口调用信息
            response_data['message'] = 'Enrollment created, please complete deposit payment'
            response_data['requires_payment'] = True
            response_data['deposit_amount'] = activity.deposit_amount
        else:
            # 不需要押金，直接等待组织者审批
            response_data['message'] = 'Enrollment created successfully, waiting for organizer approval'
            response_data['requires_payment'] = False
        
        return jsonify(response_data), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Enrollment failed: {str(e)}'
        }), 500


# 审核报名（仅活动发起人）
@enrollment_bp.put('/<int:enrollment_id>/approve')
@jwt_required
@is_organizer
def approve_enrollment(enrollment_id):
    # 获取当前用户（活动发起人）
    organizer = get_current_user()
    if not organizer:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    # 获取报名记录
    enrollment = Enrollment.query.get(enrollment_id)
    if not enrollment:
        return jsonify({'status': 'error', 'message': 'Enrollment not found'}), 404
    
    # 检查报名记录是否属于当前活动
    if enrollment.activity.organizer_id != organizer.id:
        return jsonify({'status': 'error', 'message': 'Permission denied'}), 403
    
    # 检查活动是否已满
    if enrollment.activity.current_participants >= enrollment.activity.max_participants:
        return jsonify({'status': 'error', 'message': 'Activity is full'}), 400
    
    try:
        # 更新报名状态
        enrollment.status = 'approved'
        
        # 标记押金已转入对公账户
        enrollment.deposit_transferred = True
        
        # 增加活动当前参与人数
        enrollment.activity.current_participants += 1
        
        # 如果已满，更新活动状态
        if enrollment.activity.current_participants >= enrollment.activity.max_participants:
            enrollment.activity.status = 'full'
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Enrollment approved, deposit transferred to corporate account',
            'data': enrollment.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Approval failed: {str(e)}'
        }), 500


# 拒绝报名（仅活动发起人）
@enrollment_bp.put('/<int:enrollment_id>/reject')
@jwt_required
@is_organizer
def reject_enrollment(enrollment_id):
    # 获取当前用户（活动发起人）
    organizer = get_current_user()
    if not organizer:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    # 获取报名记录
    enrollment = Enrollment.query.get(enrollment_id)
    if not enrollment:
        return jsonify({'status': 'error', 'message': 'Enrollment not found'}), 404
    
    # 检查报名记录是否属于当前活动
    if enrollment.activity.organizer_id != organizer.id:
        return jsonify({'status': 'error', 'message': 'Permission denied'}), 403
    
    try:
        # 更新报名状态
        enrollment.status = 'rejected'
        
        # 注意：由于在报名时没有增加活动参与人数，所以拒绝时也不需要减少
        # 只有在审批通过后才会增加参与人数，相应的取消操作会在取消接口中处理
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Enrollment rejected',
            'data': enrollment.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Rejection failed: {str(e)}'
        }), 500


# 取消报名
@enrollment_bp.delete('/<int:enrollment_id>')
@jwt_required
def cancel_enrollment(enrollment_id):
    user = get_current_user()
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    # 获取报名记录
    enrollment = Enrollment.query.get(enrollment_id)
    if not enrollment:
        return jsonify({'status': 'error', 'message': 'Enrollment not found'}), 404
    
    # 检查是否是用户自己的报名记录
    if enrollment.user_id != user.id:
        return jsonify({'status': 'error', 'message': 'Permission denied'}), 403
    
    # 检查活动状态
    if enrollment.activity.status == 'completed' or enrollment.activity.status == 'canceled':
        return jsonify({'status': 'error', 'message': 'Cannot cancel enrollment for completed or canceled activity'}), 400
    
    # 检查报名状态
    if enrollment.status == 'approved':
        # 对于已审批的报名，需要检查活动是否已经开始
        if datetime.utcnow() > enrollment.activity.start_time:
            return jsonify({'status': 'error', 'message': 'Cannot cancel approved enrollment after activity start time'}), 400
    
    try:
        # 设置取消时间
        cancel_time = datetime.utcnow()
        enrollment.cancel_time = cancel_time
        enrollment.status = 'canceled'
        
        # 检查是否可以退款
        can_refund = True
        if enrollment.activity.refund_deadline and cancel_time > enrollment.activity.refund_deadline:
            can_refund = False
        
        # 只有已审批的报名才需要减少活动参与人数
        if enrollment.status == 'approved':
            enrollment.activity.current_participants -= 1
            
            # 如果活动状态是full，更新为active
            if enrollment.activity.status == 'full':
                enrollment.activity.status = 'active'
        
        db.session.commit()
        
        # 构建响应消息
        message = 'Enrollment canceled successfully'
        if can_refund:
            message += ' and deposit will be refunded'
        else:
            message += ' but deposit will not be refunded (refund deadline passed)'
        
        return jsonify({
            'status': 'success',
            'message': message,
            'data': {
                'can_refund': can_refund,
                'refund_deadline': enrollment.activity.refund_deadline.isoformat() if enrollment.activity.refund_deadline else None,
                'cancel_time': cancel_time.isoformat()
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Cancelation failed: {str(e)}'
        }), 500


# 获取活动的所有报名记录（仅活动发起人）
@enrollment_bp.get('/activity/<int:activity_id>')
@jwt_required
def get_activity_enrollments(activity_id):
    user = get_current_user()
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    # 检查活动是否存在
    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({'status': 'error', 'message': 'Activity not found'}), 404
    
    # 检查用户是否是发起人
    if activity.organizer_id != user.id:
        return jsonify({'status': 'error', 'message': 'Permission denied'}), 403
    
    # 获取所有报名记录
    enrollments = Enrollment.query.filter_by(activity_id=activity_id).all()
    
    return jsonify({
        'status': 'success',
        'message': 'Enrollments retrieved',
        'data': [enrollment.to_dict() for enrollment in enrollments]
    }), 200


# 获取用户的所有报名记录
@enrollment_bp.get('/my')
@jwt_required
def get_my_enrollments():
    user = get_current_user()
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    
    # 构建查询
    query = Enrollment.query.filter_by(user_id=user.id)
    
    if status:
        query = query.filter_by(status=status)
    
    # 排序并分页
    pagination = query.order_by(Enrollment.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'status': 'success',
        'message': 'My enrollments retrieved',
        'data': {
            'enrollments': [enrollment.to_dict() for enrollment in pagination.items],
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


# 更新报名状态为安全结束
@enrollment_bp.put('/<int:enrollment_id>/safe-complete')
@jwt_required
def mark_safe_complete(enrollment_id):
    user = get_current_user()
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    # 获取报名记录
    enrollment = Enrollment.query.get(enrollment_id)
    if not enrollment:
        return jsonify({'status': 'error', 'message': 'Enrollment not found'}), 404
    
    # 检查是否是用户自己的报名记录
    if enrollment.user_id != user.id:
        return jsonify({'status': 'error', 'message': 'Permission denied'}), 403
    
    try:
        enrollment.status = 'safe_completed'
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Activity marked as safe completed'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Update failed: {str(e)}'
        }), 500
