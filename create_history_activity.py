# create_history_activity.py
# 创建历史活动的测试脚本

from app import create_app
from app import db
from app.models import Activity, User, Enrollment
from datetime import datetime

app = create_app()

with app.app_context():
    # 查找两个用户
    user1 = User.query.filter_by(phone='13621114638').first()
    user2 = User.query.filter_by(phone='13800138000').first()
    
    if not user1 or not user2:
        print('用户不存在，请先创建用户')
        exit(1)
    
    # 创建一个历史活动（已完成）
    activity = Activity(
        title='K歌历史活动',
        description='这是一个历史活动，用于测试评价功能',
        location='北京朝阳区',
        start_time=datetime(2025, 12, 1, 19, 0, 0),
        end_time=datetime(2025, 12, 1, 22, 0, 0),
        current_participants=2,
        max_participants=4,
        cost_type='aa',
        estimated_cost_per_person=10.0,
        deposit_amount=0.0,
        status='completed',  # 历史活动状态
        is_published=True,
        organizer_id=user1.id
    )
    
    try:
        db.session.add(activity)
        db.session.commit()
        print(f'历史活动创建成功！ID: {activity.id}')
        
        # 让两个用户报名参加
        enrollment1 = Enrollment(
            user_id=user1.id,
            activity_id=activity.id,
            status='attended'
        )
        
        enrollment2 = Enrollment(
            user_id=user2.id,
            activity_id=activity.id,
            status='attended'
        )
        
        db.session.add(enrollment1)
        db.session.add(enrollment2)
        db.session.commit()
        
        print('两个用户报名成功！')
        
        # 验证数据
        print(f'活动状态: {activity.status}')
        print(f'活动报名人数: {len(activity.enrollments)}')
        
    except Exception as e:
        db.session.rollback()
        print(f'创建失败: {str(e)}')