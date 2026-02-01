# check_enrollment.py
# 检查用户的报名记录

from app import create_app
from app.models import User, Activity, Enrollment
from app.config import config

# 创建应用实例
app = create_app(config['default'])

with app.app_context():
    print("=== 检查用户报名记录 ===")
    
    # 检查用户ID为3的用户
    user_id = 3
    user = User.query.get(user_id)
    print(f"用户ID: {user_id}, 手机号: {user.phone}, 昵称: {user.nickname}")
    
    # 检查用户的所有报名记录
    enrollments = Enrollment.query.filter_by(user_id=user_id).all()
    print(f"\n用户 {user_id} 的报名记录 ({len(enrollments)} 条):")
    for enrollment in enrollments:
        activity = Activity.query.get(enrollment.activity_id)
        print(f"  报名ID: {enrollment.id}, 活动ID: {enrollment.activity_id}, 活动标题: {activity.title}")
        print(f"  报名状态: {enrollment.status}, 创建时间: {enrollment.created_at}")
        print(f"  活动状态: {activity.status}, 当前参与人数: {activity.current_participants}/{activity.max_participants}")
        print()
    
    # 检查活动ID为36的报名情况
    print("=== 检查活动ID 36 的报名情况 ===")
    activity_id = 36
    activity = Activity.query.get(activity_id)
    print(f"活动ID: {activity_id}, 标题: {activity.title}")
    print(f"状态: {activity.status}, 当前参与人数: {activity.current_participants}/{activity.max_participants}")
    
    # 检查该活动的所有报名记录
    activity_enrollments = Enrollment.query.filter_by(activity_id=activity_id).all()
    print(f"\n活动 {activity_id} 的报名记录 ({len(activity_enrollments)} 条):")
    for enrollment in activity_enrollments:
        enroll_user = User.query.get(enrollment.user_id)
        print(f"  报名ID: {enrollment.id}, 用户ID: {enrollment.user_id}, 用户手机号: {enroll_user.phone}")
        print(f"  报名状态: {enrollment.status}, 创建时间: {enrollment.created_at}")
        print()
