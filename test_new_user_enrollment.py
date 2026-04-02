#!/usr/bin/env python3
# 使用新测试用户测试报名功能

from app import create_app, db
from app.models import User, Activity, Enrollment

# 创建应用实例
app = create_app()

with app.app_context():
    print('=== 使用新测试用户测试报名功能 ===')
    
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
    
    # 4. 测试报名逻辑
    print('\n=== 测试报名逻辑 ===')
    try:
        # 检查活动是否存在
        if not activity:
            print('活动不存在')
        
        # 检查活动状态
        if activity.status != 'active':
            print('活动不是活跃状态')
        
        # 检查活动是否已满
        if activity.current_participants >= activity.max_participants:
            print('活动已满')
        
        # 检查用户是否已经报名
        if existing_enrollment:
            print('用户已经报名')
        
        # 检查用户是否是发起人
        if activity.organizer_id == user.id:
            print('用户是活动发起人')
        
        # 如果所有条件都满足，创建报名记录
        if activity and activity.status == 'active' and activity.current_participants < activity.max_participants and not existing_enrollment and activity.organizer_id != user.id:
            print('所有条件满足，可以报名')
            
            # 创建报名记录
            enrollment = Enrollment(
                user_id=user.id,
                activity_id=activity.id,
                status='pending',
                message='测试报名',
                deposit_paid=activity.deposit_amount
            )
            
            db.session.add(enrollment)
            db.session.commit()
            print(f'报名成功！报名ID: {enrollment.id}, 状态: {enrollment.status}')
        else:
            print('无法报名，条件不满足')
            
    except Exception as e:
        print(f'报名失败: {e}')
        db.session.rollback()