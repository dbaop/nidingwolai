import requests
import json

# 测试用户创建活动和获取用户创建活动的功能
def test_user_activities():
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
    user_id = login_response.json()['data']['user']['id']
    print(f"登录成功，获取到token: {token}")
    print(f"当前用户ID: {user_id}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 1. 创建一个测试活动
    activity_url = "http://localhost:5000/api/activities/"
    activity_data = {
        "title": "测试用户活动",
        "description": "测试用户创建活动和获取活动功能",
        "location": "测试地点",
        "start_time": "2026-01-10T05:45:00.000Z",
        "end_time": "2026-01-10T06:45:00.000Z",
        "max_participants": 10,
        "activity_type": "k歌"
    }
    
    print(f"\n=== 创建测试活动 ===")
    print(f"发送请求数据: {json.dumps(activity_data, indent=2)}")
    
    activity_response = requests.post(activity_url, json=activity_data, headers=headers)
    print(f"创建活动响应状态码: {activity_response.status_code}")
    print(f"创建活动响应内容: {activity_response.text}")
    
    if activity_response.status_code != 201:
        print("\n❌ 创建活动失败")
        return
    
    created_activity = activity_response.json()['data']
    print(f"\n✅ 创建活动成功，活动ID: {created_activity['id']}")
    print(f"活动组织者ID: {created_activity['organizer_id']}")
    print(f"活动状态: {created_activity['status']}")
    print(f"活动是否发布: {created_activity['is_published']}")
    
    # 2. 获取用户创建的活动
    user_activities_url = "http://localhost:5000/api/activities/my-organized"
    
    print(f"\n=== 获取用户创建的活动 ===")
    
    # 测试不同的分页参数
    for page in [1, 2]:
        print(f"\n--- 测试第 {page} 页 --- ")
        params = {"page": page, "per_page": 10}
        user_activities_response = requests.get(user_activities_url, headers=headers, params=params)
        
        print(f"请求URL: {user_activities_response.url}")
        print(f"响应状态码: {user_activities_response.status_code}")
        print(f"响应内容: {user_activities_response.text}")
        
        if user_activities_response.status_code == 200:
            response_data = user_activities_response.json()
            activities = response_data['data']['activities']
            pagination = response_data['data']['pagination']
            
            print(f"\n分页信息: {json.dumps(pagination, indent=2)}")
            print(f"获取到 {len(activities)} 个活动")
            
            if len(activities) > 0:
                print("\n活动列表:")
                for idx, activity in enumerate(activities):
                    print(f"  {idx+1}. ID: {activity['id']}, 标题: {activity['title']}, 组织者ID: {activity['organizer_id']}, 发布状态: {activity['is_published']}")
                    # 检查刚才创建的活动是否在列表中
                    if activity['id'] == created_activity['id']:
                        print(f"  ✅ 刚才创建的活动（ID: {created_activity['id']}）在列表中！")
            else:
                print("\n❌ 没有获取到任何活动")
        else:
            print(f"\n❌ 获取用户活动失败")
    
    print("\n=== 所有测试完成 ===")

if __name__ == "__main__":
    test_user_activities()
