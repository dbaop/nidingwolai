#!/usr/bin/env python3
# 创建测试用户

from app import create_app, db
from app.models import User

# 创建应用实例
app = create_app()

with app.app_context():
    print('=== 创建测试用户 ===')
    
    # 创建新用户
    new_user = User(
        phone='13800138000',
        nickname='测试用户',
        role='user'
    )
    new_user.password = '123456'
    
    try:
        db.session.add(new_user)
        db.session.commit()
        print(f'测试用户创建成功！')
        print(f'手机号: {new_user.phone}')
        print(f'昵称: {new_user.nickname}')
        print(f'ID: {new_user.id}')
    except Exception as e:
        db.session.rollback()
        print(f'创建用户失败: {e}')
        
        # 检查是否已存在
        existing_user = User.query.filter_by(phone='13800138000').first()
        if existing_user:
            print(f'用户已存在！ID: {existing_user.id}')