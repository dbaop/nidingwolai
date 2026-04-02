#!/usr/bin/env python3
# 创建历史活动测试数据
from datetime import datetime, timedelta
from app import create_app, db
from app.models import Activity, User, Enrollment

# 创建应用实例
app = create_app()

# 添加应用上下文
with app.app_context():
    # 连接数据库
    db.create_all()

    # 查找测试用户
    user1 = User.query.filter_by(phone='13621114638').first()
    user2 = User.query.filter_by(phone='13800138000').first()

    if not user1 or not user2:
        print("错误：测试用户不存在，请先创建用户")
        exit(1)

    # 创建一个历史活动
    activity = Activity(
        title="测试历史活动",
        description="这是一个测试用的历史活动，用于测试评价功能",
        activity_type="K歌",
        location="北京市朝阳区KTV",
        start_time=datetime.utcnow() - timedelta(days=7),  # 7天前
        end_time=datetime.utcnow() - timedelta(days=6),  # 6天前
        organizer_id=user2.id,  # user2作为组织者
        current_participants=2,
        max_participants=10,
        cover_image_url="/images/karaoke1.png",
        status="completed",  # 已完成
        is_published=True
    )

    db.session.add(activity)
    db.session.flush()  # 获取活动ID

    # 创建用户1的报名记录
    enrollment1 = Enrollment(
        user_id=user1.id,
        activity_id=activity.id,
        status="approved",
        cost_paid=0.0,
        deposit_paid=0.0
    )

    # 创建用户2的报名记录（组织者自动报名）
    enrollment2 = Enrollment(
        user_id=user2.id,
        activity_id=activity.id,
        status="approved",
        cost_paid=0.0,
        deposit_paid=0.0
    )

    db.session.add(enrollment1)
    db.session.add(enrollment2)
    db.session.commit()

    print(f"成功创建历史活动：{activity.title}")
    print(f"活动ID：{activity.id}")
    print(f"组织者：{user2.nickname} ({user2.phone})")
    print(f"已报名用户：")
    print(f"  1. {user1.nickname} ({user1.phone})")
    print(f"  2. {user2.nickname} ({user2.phone})")
    print("\n现在可以测试评价功能了！")
