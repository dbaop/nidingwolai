# app/routes/user.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity
from app import db
from app.models import User, UserTag, InterestTag
from app.utils.auth import jwt_required, get_current_user

user_bp = Blueprint('user', __name__)


# 用户注册（微信登录）
@user_bp.post('/register')
def register():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid input'}), 400
    
    openid = data.get('openid')
    nickname = data.get('nickname')
    avatar = data.get('avatar')
    gender = data.get('gender', 0)
    
    if not openid or not nickname:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
    
    # 检查用户是否已存在
    existing_user = User.query.filter_by(openid=openid).first()
    if existing_user:
        # 用户已存在，直接返回token
        access_token = create_access_token(identity=existing_user.id)
        return jsonify({
            'status': 'success',
            'message': 'User already exists',
            'data': {
                'user': existing_user.to_dict(),
                'access_token': access_token
            }
        }), 200
    
    # 创建新用户
    new_user = User(
        openid=openid,
        nickname=nickname,
        avatar=avatar,
        gender=gender
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        
        # 创建token
        access_token = create_access_token(identity=new_user.id)
        
        return jsonify({
            'status': 'success',
            'message': 'User registered successfully',
            'data': {
                'user': new_user.to_dict(),
                'access_token': access_token
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Registration failed: {str(e)}'
        }), 500


# 用户注册（手机号+密码）
@user_bp.post('/register-phone')
def register_phone():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid input'}), 400
    
    phone = data.get('phone')
    password = data.get('password')
    nickname = data.get('nickname')
    
    if not phone or not password or not nickname:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
    
    # 检查手机号是否已被注册
    existing_user = User.query.filter_by(phone=phone).first()
    if existing_user:
        return jsonify({'status': 'error', 'message': 'Phone number already registered'}), 400
    
    # 创建新用户
    new_user = User(
        phone=phone,
        nickname=nickname
    )
    new_user.password = password  # 使用password属性设置器加密密码
    
    try:
        db.session.add(new_user)
        db.session.commit()
        
        # 创建token
        access_token = create_access_token(identity=new_user.id)
        
        return jsonify({
            'status': 'success',
            'message': 'User registered successfully with phone',
            'data': {
                'user': new_user.to_dict(),
                'access_token': access_token
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Registration failed: {str(e)}'
        }), 500


# 用户登录（支持微信登录和手机号+密码登录）
@user_bp.post('/login')
def login():
    print("=== LOGIN ATTEMPT START ===")
    data = request.get_json()
    print(f"Login data received: {data}")
    
    if not data:
        print("Invalid input data")
        return jsonify({'status': 'error', 'message': 'Invalid input'}), 400
    
    # 检查是否是微信登录
    openid = data.get('openid')
    if openid:
        print(f"WeChat login attempt with openid: {openid}")
        # 微信登录流程
        user = User.query.filter_by(openid=openid).first()
        if not user:
            print("User not found for WeChat openid")
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        print(f"WeChat user found: {user.nickname} (ID: {user.id})")
    else:
        # 手机号+密码登录流程
        phone = data.get('phone')
        password = data.get('password')
        print(f"Phone login attempt with phone: {phone}")
        
        if not phone or not password:
            print("Missing phone or password")
            return jsonify({'status': 'error', 'message': 'Missing phone or password'}), 400
        
        # 查找用户
        user = User.query.filter_by(phone=phone).first()
        if not user:
            print("User not found for phone number")
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        
        # 验证密码
        if not user.verify_password(password):
            print("Invalid password provided")
            return jsonify({'status': 'error', 'message': 'Invalid password'}), 401
        print(f"Phone user found and authenticated: {user.nickname} (ID: {user.id})")
    
    # 创建token
    print("Creating access token...")
    access_token = create_access_token(identity=str(user.id))  # 确保identity是字符串
    print(f"Access token created: {access_token}")
    
    response_data = {
        'status': 'success',
        'message': 'Login successful',
        'data': {
            'user': user.to_dict(),
            'access_token': access_token
        }
    }
    print(f"Login response: {response_data}")
    print("=== LOGIN ATTEMPT END ===")
    
    return jsonify(response_data), 200


# 获取当前用户信息
@user_bp.get('/me')
@jwt_required
def get_my_info():
    user = get_current_user()
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    return jsonify({
        'status': 'success',
        'message': 'User info retrieved',
        'data': user.to_dict()
    }), 200


# 更新用户信息
@user_bp.put('/me')
@jwt_required
def update_my_info():
    user = get_current_user()
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid input'}), 400
    
    # 更新用户信息
    user.nickname = data.get('nickname', user.nickname)
    user.avatar = data.get('avatar', user.avatar)
    user.gender = data.get('gender', user.gender)
    user.phone = data.get('phone', user.phone)
    user.bio = data.get('bio', user.bio)
    user.singing_style = data.get('singing_style', user.singing_style)
    
    try:
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'User info updated',
            'data': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Update failed: {str(e)}'
        }), 500


# 获取用户信息
@user_bp.get('/<int:user_id>')
def get_user_info(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    return jsonify({
        'status': 'success',
        'message': 'User info retrieved',
        'data': user.to_dict()
    }), 200


# 为用户添加标签
@user_bp.post('/me/tags')
@jwt_required
def add_user_tags():
    user = get_current_user()
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    data = request.get_json()
    if not data or 'tag_ids' not in data:
        return jsonify({'status': 'error', 'message': 'Invalid input'}), 400
    
    tag_ids = data.get('tag_ids')
    if not isinstance(tag_ids, list):
        return jsonify({'status': 'error', 'message': 'tag_ids must be a list'}), 400
    
    try:
        # 先删除用户现有的标签
        UserTag.query.filter_by(user_id=user.id).delete()
        
        # 添加新标签
        for tag_id in tag_ids:
            tag = InterestTag.query.get(tag_id)
            if tag:
                user_tag = UserTag(user_id=user.id, tag_id=tag_id)
                db.session.add(user_tag)
        
        db.session.commit()
        
        # 获取更新后的标签
        updated_tags = UserTag.query.filter_by(user_id=user.id).all()
        
        return jsonify({
            'status': 'success',
            'message': 'Tags added successfully',
            'data': [tag.to_dict() for tag in updated_tags]
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to add tags: {str(e)}'
        }), 500


# 获取用户标签
@user_bp.get('/me/tags')
@jwt_required
def get_user_tags():
    user = get_current_user()
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    user_tags = UserTag.query.filter_by(user_id=user.id).all()
    
    return jsonify({
        'status': 'success',
        'message': 'User tags retrieved',
        'data': [tag.to_dict() for tag in user_tags]
    }), 200


# 用户申请成为商家
@user_bp.post('/apply-merchant')
@jwt_required
def apply_merchant():
    user = get_current_user()
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    # 检查用户是否已经是商家或申请中
    if user.role == 'merchant':
        return jsonify({'status': 'error', 'message': 'You are already a merchant'}), 400
    
    if user.merchant_application_status == 'pending':
        return jsonify({'status': 'error', 'message': 'Your application is already pending'}), 400
    
    # 更新用户申请状态
    user.merchant_application_status = 'pending'
    
    try:
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Merchant application submitted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Application submission failed: {str(e)}'
        }), 500


# 管理员获取商家申请列表
@user_bp.get('/merchant-applications')
@jwt_required
def get_merchant_applications():
    current_user = get_current_user()
    if not current_user or current_user.role != 'admin':
        return jsonify({
            'status': 'error', 
            'message': 'Permission denied'
        }), 403
    
    # 获取所有待审核的商家申请
    applications = User.query.filter_by(
        merchant_application_status='pending'
    ).all()
    
    return jsonify({
        'status': 'success',
        'message': 'Merchant applications retrieved',
        'data': {
            'applications': [user.to_dict() for user in applications],
            'count': len(applications)
        }
    }), 200


# 管理员审核商家申请
@user_bp.put('/merchant-applications/<int:user_id>')
@jwt_required
def review_merchant_application(user_id):
    current_user = get_current_user()
    if not current_user or current_user.role != 'admin':
        return jsonify({
            'status': 'error', 
            'message': 'Permission denied'
        }), 403
    
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({
            'status': 'error', 
            'message': 'Missing required fields'
        }), 400
    
    status = data['status']
    if status not in ['approved', 'rejected']:
        return jsonify({
            'status': 'error', 
            'message': 'Invalid status'
        }), 400
    
    # 获取申请用户
    user = User.query.get(user_id)
    if not user or user.merchant_application_status != 'pending':
        return jsonify({
            'status': 'error', 
            'message': 'Application not found or not pending'
        }), 404
    
    try:
        if status == 'approved':
            user.role = 'merchant'
            user.merchant_application_status = 'approved'
        else:
            user.merchant_application_status = 'rejected'
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Merchant application {status} successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Review failed: {str(e)}'
        }), 500
