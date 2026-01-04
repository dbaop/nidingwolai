# app/utils/auth.py
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models import User


# JWT认证装饰器
def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            # 添加详细日志来诊断问题
            print("=== JWT AUTHENTICATION START ===")
            print(f"Request headers: {request.headers}")
            print(f"Authorization header: {request.headers.get('Authorization')}")
            
            verify_jwt_in_request()
            
            # 获取用户ID并验证用户存在
            user_id = get_jwt_identity()
            print(f"JWT verified successfully. User ID: {user_id}")
            
            user = User.query.get(user_id)
            if not user:
                print(f"User not found for ID: {user_id}")
                return jsonify({
                    'status': 'error',
                    'message': 'User not found'
                }), 404
                
            print(f"User found: {user.nickname} (ID: {user.id})")
            print("=== JWT AUTHENTICATION END ===")
            
            return fn(*args, **kwargs)
        except Exception as e:
            print(f"=== JWT AUTHENTICATION FAILED ===")
            print(f"Error: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            print("=== JWT AUTHENTICATION FAILED ===")
            
            return jsonify({
                'status': 'error',
                'message': f'Authentication failed: {str(e)}',
                'error_details': str(e)  # 添加详细错误信息用于调试
            }), 401
    return wrapper


# 获取当前用户
def get_current_user():
    user_id = get_jwt_identity()
    if isinstance(user_id, str) and user_id.isdigit():
        user_id = int(user_id)
    return User.query.get(user_id)


# 权限验证装饰器
def has_permission(required_role=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({
                    'status': 'error',
                    'message': 'User not found'
                }), 404
            
            if required_role and not user.role == required_role:
                return jsonify({
                    'status': 'error',
                    'message': 'Permission denied'
                }), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


# 组织者权限验证
def is_organizer(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        activity_id = kwargs.get('activity_id')
        
        # 如果没有activity_id，尝试从enrollment_id获取activity_id
        if not activity_id and 'enrollment_id' in kwargs:
            from app.models import Enrollment
            enrollment = Enrollment.query.get(kwargs['enrollment_id'])
            if enrollment:
                activity_id = enrollment.activity_id
        
        if not user or not activity_id:
            return jsonify({
                'status': 'error',
                'message': 'Invalid request'
            }), 400
        
        from app.models import Activity
        activity = Activity.query.get(activity_id)
        
        if not activity:
            return jsonify({
                'status': 'error',
                'message': 'Activity not found'
            }), 404
        
        if activity.organizer_id != user.id:
            return jsonify({
                'status': 'error',
                'message': 'Only organizer can perform this action'
            }), 403
        
        return fn(*args, **kwargs)
    return wrapper
