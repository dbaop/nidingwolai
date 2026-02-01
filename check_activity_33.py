#!/usr/bin/env python3
# 检查活动ID 33的详细信息

from app import create_app, db
from app.models import Activity

# 创建应用实例
app = create_app()

with app.app_context():
    print('=== 检查活动ID 33 ===')
    
    # 获取活动33
    activity = Activity.query.get(33)
    if activity:
        print(f'活动ID: {activity.id}')
        print(f'标题: {activity.title}')
        print(f'发起人ID: {activity.organizer_id}')
        print(f'状态: {activity.status}')
        print(f'是否发布: {activity.is_published}')
        print(f'开始时间: {activity.start_time}')
        print(f'创建时间: {activity.created_at}')
        print(f'更新时间: {activity.updated_at}')
    else:
        print('活动不存在')
    
    # 检查用户3创建的所有活动
    print('\n=== 用户3创建的活动 ===')
    user3_activities = Activity.query.filter_by(organizer_id=3).all()
    for act in user3_activities:
        print(f'ID: {act.id}, 标题: {act.title}, 状态: {act.status}, 发布: {act.is_published}, 发起人ID: {act.organizer_id}')
    
    # 检查所有应该在首页展示的活动
    print('\n=== 首页应该展示的活动 ===')
    homepage_activities = Activity.query.filter_by(is_published=True).filter(Activity.status != 'canceled').all()
    for act in homepage_activities:
        print(f'ID: {act.id}, 标题: {act.title}, 发起人: {act.organizer_id}, 状态: {act.status}, 发布: {act.is_published}')
