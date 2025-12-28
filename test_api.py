import requests
import json

# 登录获取token (活动创建者)
creator_login_data = {
    "phone": "13621114638",
    "password": "admin123456"
}

print("=== 登录活动创建者 ===")
response = requests.post('http://localhost:5000/api/users/login', json=creator_login_data)
print("Login response:", response.status_code)
print("Login response body:", response.text)

if response.status_code == 200:
    creator_token_data = response.json()
    creator_token = creator_token_data['data']['access_token']
    print("Creator Token:", creator_token)
    
    # 创建活动测试
    activity_data = {
        "title": "测试活动",
        "description": "这是一个测试活动",
        "location": "测试地点",
        "start_time": "2025-12-25T10:00:00",
        "end_time": "2025-12-25T12:00:00",
        "max_participants": 10,
        "deposit_amount": 50.0  # 设置押金金额
    }
    
    creator_headers = {
        "Authorization": f"Bearer {creator_token}"
    }
    
    print("\n=== 创建活动 ===")
    response = requests.post('http://localhost:5000/api/activities/', json=activity_data, headers=creator_headers)
    print("Create activity response:", response.status_code)
    print("Create activity response body:", response.text)
    
    if response.status_code == 201:
        activity_id = response.json()['data']['id']
        print(f"Created activity ID: {activity_id}")
        
        # 登录另一个用户来报名参加活动
        participant_login_data = {
            "phone": "13621114639",
            "password": "user123456"
        }
        
        print("\n=== 登录参与者 ===")
        response = requests.post('http://localhost:5000/api/users/login', json=participant_login_data)
        print("Participant login response:", response.status_code)
        print("Participant login response body:", response.text)
        
        if response.status_code == 200:
            participant_token_data = response.json()
            participant_token = participant_token_data['data']['access_token']
            print("Participant Token:", participant_token)
            
            participant_headers = {
                "Authorization": f"Bearer {participant_token}"
            }
            
            # 报名参加活动
            enrollment_data = {
                "activity_id": activity_id,
                "message": "我想参加这个活动"
            }
            
            print("\n=== 报名参加活动 ===")
            response = requests.post('http://localhost:5000/api/enrollments/', json=enrollment_data, headers=participant_headers)
            print("Enroll activity response:", response.status_code)
            print("Enroll activity response body:", response.text)
            
            if response.status_code == 201:
                enrollment_id = response.json()['data']['id']
                print(f"Enrollment ID: {enrollment_id}")
                
                # 活动创建者审批报名
                print("\n=== 活动创建者审批报名 ===")
                response = requests.put(f'http://localhost:5000/api/enrollments/{enrollment_id}/approve', headers=creator_headers)
                print("Approve enrollment response:", response.status_code)
                print("Approve enrollment response body:", response.text)
                
                if response.status_code == 200:
                    print("Enrollment approved successfully!")
                    
                    # 验证活动参与人数是否更新
                    print("\n=== 验证活动详情 ===")
                    response = requests.get(f'http://localhost:5000/api/activities/{activity_id}', headers=creator_headers)
                    print("Get activity response:", response.status_code)
                    print("Get activity response body:", response.text)
                else:
                    print("Failed to approve enrollment")
            else:
                print("Failed to enroll in activity")
        else:
            print("Participant login failed")
    else:
        print("Failed to create activity")
else:
    print("Creator login failed")