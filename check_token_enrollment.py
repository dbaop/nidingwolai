# check_token_enrollment.py
# 直接在服务器端检查token解析和报名状态

from app import create_app
from app.config import config
from flask_jwt_extended import decode_token

# 创建应用实例
app = create_app(config['default'])

with app.app_context():
    print("=== 检查token解析 ===")
    
    # 使用前端提供的token
    token = 'yJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2OTkzNjg2OCwianRpIjoiYmMxOTEzNTctMjFmNi00OGI4LThkNzgtOWQ1ZDgwNWM1NGM0IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjMiLCJuYmYiOjE3Njk5MzY4NjgsImV4cCI6MTc3MDU0MTY2OH0.4AXn6_ucMm7VHKiLrk5HwFs7fqHP397-MDmSOhcgtlw'
    
    try:
        # 解析token
        decoded = decode_token(token)
        print(f"Token解析成功:")
        print(f"  用户ID: {decoded.get('sub')}")
        print(f"  过期时间: {decoded.get('exp')}")
        print(f"  签发时间: {decoded.get('iat')}")
        
        # 检查用户报名状态
        user_id = decoded.get('sub')
        from app.models import User, Activity, Enrollment
        
        user = User.query.get(user_id)
        if user:
            print(f"\n用户信息:")
            print(f"  ID: {user.id}")
            print(f"  手机号: {user.phone}")
            print(f"  昵称: {user.nickname}")
            
            # 检查活动36的报名状态
            activity_id = 36
            activity = Activity.query.get(activity_id)
            if activity:
                print(f"\n活动信息:")
                print(f"  ID: {activity.id}")
                print(f"  标题: {activity.title}")
                print(f"  当前参与人数: {activity.current_participants}/{activity.max_participants}")
                
                # 检查报名记录
                enrollment = Enrollment.query.filter_by(
                    user_id=user.id, activity_id=activity_id
                ).first()
                if enrollment:
                    print(f"\n报名记录:")
                    print(f"  报名ID: {enrollment.id}")
                    print(f"  状态: {enrollment.status}")
                    print(f"  创建时间: {enrollment.created_at}")
                else:
                    print(f"\n用户 {user.id} 未报名活动 {activity_id}")
            else:
                print(f"活动 {activity_id} 不存在")
        else:
            print(f"用户 {user_id} 不存在")
            
    except Exception as e:
        print(f"Token解析失败: {str(e)}")
