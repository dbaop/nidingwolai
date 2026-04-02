#!/usr/bin/env python3
# 测试用户创建活动功能

from app import create_app, db
from app.models import User, Activity
from datetime import datetime, timedelta

# 创建应用实例
app = create_app()

with app.app_context():
    print('=== 测试用户创建活动功能 ===')
    
    # 获取测试用户（13800138000）
    user = User.query.filter_by(phone='13800138000').first()
    if not user:
        print('❌ 未找到测试用户')
        exit(1)
    print(f'✅ 找到用户: {user.nickname} (ID: {user.id}, 手机号: {user.phone})')
    print(f'   当前创建的活动数量: {Activity.query.filter_by(organizer_id=user.id).count()}')
    
    # 创建测试活动
    print('\n2. 为用户创建测试活动:')
    
    # 创建一个2天后开始的活动
    start_time = datetime.utcnow() + timedelta(days=2)
    end_time = start_time + timedelta(hours=2)
    
    # 创建活动
    new_activity = Activity(
        title='用户测试活动',
        description='这是用户13800138000创建的测试活动',
        location='测试地点',
        start_time=start_time,
        end_time=end_time,
        max_participants=5,
        organizer_id=user.id,
        deposit_amount=0.0,  # 无需押金
        status='active'
    )
    
    db.session.add(new_activity)
    db.session.commit()
    
    print(f'✅ 创建活动成功: {new_activity.title} (ID: {new_activity.id})')
    print(f'   活动状态: {new_activity.status}')
    print(f'   开始时间: {new_activity.start_time}')
    print(f'   发起人ID: {new_activity.organizer_id}')
    
    # 验证活动是否创建成功
    print('\n3. 验证活动创建:')
    user_activities = Activity.query.filter_by(organizer_id=user.id).all()
    print(f'   用户现在创建的活动数量: {len(user_activities)}')
    for activity in user_activities:
        print(f'   - {activity.title} (ID: {activity.id}, 状态: {activity.status})')
    
    # 验证活动是否在首页展示
    print('\n4. 验证首页展示:')
    homepage_activities = Activity.query.filter_by(is_published=True).filter(Activity.status != 'canceled').all()
    user_activity_in_homepage = any(activity.organizer_id == user.id for activity in homepage_activities)
    print(f'   用户的活动是否在首页展示: {user_activity_in_homepage}')
    
    # 清理测试数据（可选）
    # db.session.delete(new_activity)
    # db.session.commit()
    # print('\n5. 清理测试数据完成')
    
    print('\n=== 测试完成 ===')
