#!/usr/bin/env python3
# 检查数据库中的活动和用户数据

from app import create_app, db
from app.models import Activity, User

app = create_app()

with app.app_context():
    print('=== 活动数据 ===')
    activities = Activity.query.all()
    for activity in activities:
        user = User.query.get(activity.organizer_id)
        print(f'活动ID: {activity.id}, 标题: {activity.title}')
        print(f'  发起人ID: {activity.organizer_id}, 发起人手机号: {user.phone if user else "未知"}')
        print(f'  状态: {activity.status}, 是否发布: {activity.is_published}')
        print(f'  开始时间: {activity.start_time}')
        print()
    
    print('=== 用户数据 ===')
    users = User.query.all()
    for user in users:
        print(f'用户ID: {user.id}, 手机号: {user.phone}, 昵称: {user.nickname}')
        # 统计用户创建的活动数量
        user_activities = Activity.query.filter_by(organizer_id=user.id).count()
        print(f'  创建的活动数量: {user_activities}')
        print()