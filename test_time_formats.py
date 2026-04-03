import requests
import json
from datetime import datetime, timezone

# 测试不同类型的时间格式处理
def test_time_formats():
    # 先登录获取token
    login_url = "http://localhost:5000/api/users/login"
    login_data = {
        "phone": "13621114638",
        "password": "admin123456"
    }
    
    login_response = requests.post(login_url, json=login_data)
    if login_response.status_code != 200:
        print("登录失败:", login_response.text)
        return
    
    token = login_response.json()['data']['access_token']
    print(f"登录成功，获取到token: {token}")
    
    # 测试不同的时间格式
    test_cases = [
        {
            "name": "带Z后缀的ISO时间格式",
            "start_time": "2026-01-04T05:45:00.000Z",
            "end_time": "2026-01-05T06:45:00.000Z"
        },
        {
            "name": "普通ISO时间格式",
            "start_time": "2026-01-04T05:45:00",
            "end_time": "2026-01-05T06:45:00"
        },
        {
            "name": "时间戳格式",
            "start_time": int(datetime(2026, 1, 4, 5, 45, tzinfo=timezone.utc).timestamp()),
            "end_time": int(datetime(2026, 1, 5, 6, 45, tzinfo=timezone.utc).timestamp())
        }
    ]
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    for test_case in test_cases:
        print(f"\n=== 测试: {test_case['name']} ===")
        
        activity_url = "http://localhost:5000/api/activities/"
        activity_data = {
            "title": f"测试活动 - {test_case['name']}",
            "description": f"测试{test_case['name']}的处理",
            "location": "测试地点",
            "start_time": test_case['start_time'],
            "end_time": test_case['end_time'],
            "max_participants": 10,
            "activity_type": "k歌"
        }
        
        print(f"发送请求数据: {json.dumps(activity_data, indent=2, default=str)}")
        
        activity_response = requests.post(activity_url, json=activity_data, headers=headers)
        print(f"创建活动响应状态码: {activity_response.status_code}")
        
        if activity_response.status_code == 201:
            print(f"✅ {test_case['name']} 测试成功！")
            response_data = activity_response.json()
            print(f"活动ID: {response_data['data']['id']}")
        else:
            print(f"❌ {test_case['name']} 测试失败！")
            print(f"响应内容: {activity_response.text}")
    
    print("\n=== 所有测试完成 ===")

if __name__ == "__main__":
    test_time_formats()
