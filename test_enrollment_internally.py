#!/usr/bin/env python3
# 在应用程序内部模拟请求，直接测试报名功能

from app import create_app, db
from app.models import User, Activity, Enrollment
from datetime import datetime

# 创建应用实例
app = create_app()

with app.app_context():
    print('=== 在应用程序内部测试报名功能 ===')
    
    # 1. 获取测试用户
    user = User.query.filter_by(phone='13800138000').first()
    if not user:
        print('未找到测试用户')
        exit(1)
    print(f'测试用户: {user.nickname} (ID: {user.id})')
    
    # 2. 获取测试活动
    activity = Activity.query.get(27)
    if not activity:
        print('未找到测试活动')
        exit(1)
    print(f'测试活动: {activity.title} (ID: {activity.id})')
    print(f'活动状态: {activity.status}')
    print(f'当前参与人数: {activity.current_participants}/{activity.max_participants}')
    print(f'活动发起人: {activity.organizer_id}')
    
    # 3. 检查是否已经报名
    existing_enrollment = Enrollment.query.filter_by(
        user_id=user.id, activity_id=activity.id
    ).first()
    if existing_enrollment:
        print(f'用户已经报名，状态: {existing_enrollment.status}')
    else:
        print('用户尚未报名')
    
    # 4. 模拟报名请求
    print('\n=== 模拟报名请求 ===')
    
    # 模拟请求数据
    data = {
        'activity_id': 27,
        'message': '内部测试报名'
    }
    
    print(f'请求数据: {data}')
    
    # 模拟业务逻辑
    try:
        # 检查活动是否存在
        if not activity:
            print('错误: 活动不存在')
            exit(1)
        
        # 检查活动状态
        if activity.status != 'active':
            print('错误: 活动不是活跃状态')
            exit(1)
        
        # 检查活动是否已满
        if activity.current_participants >= activity.max_participants:
            print('错误: 活动已满')
            exit(1)
        
        # 检查用户是否已经报名
        if existing_enrollment:
            print('错误: 用户已经报名')
            exit(1)
        
        # 检查用户是否是发起人
        if activity.organizer_id == user.id:
            print('错误: 发起人不能报名自己的活动')
            exit(1)
        
        # 创建报名记录
        enrollment = Enrollment(
            user_id=user.id,
            activity_id=activity.id,
            status='pending',
            message=data.get('message', ''),
            deposit_paid=activity.deposit_amount
        )
        
        db.session.add(enrollment)
        db.session.commit()
        
        print('报名成功！')
        print(f'报名ID: {enrollment.id}')
        print(f'报名状态: {enrollment.status}')
        print(f'支付押金: {enrollment.deposit_paid}')
        
        # 检查活动参与人数
        print(f'\n活动当前参与人数: {activity.current_participants}/{activity.max_participants}')
        
    except Exception as e:
        print(f'报名失败: {e}')
        import traceback
        traceback.print_exc()
        db.session.rollback()