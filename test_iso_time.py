import requests
import json

# 测试带Z后缀的ISO时间格式处理
def test_iso_time():
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
    
    # 测试创建活动，使用带Z后缀的ISO时间格式
    activity_url = "http://localhost:5000/api/activities/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    activity_data = {
        "title": "测试活动",
        "description": "测试带Z后缀的ISO时间格式",
        "location": "测试地点",
        "start_time": "2026-01-04T05:45:00.000Z",
        "end_time": "2026-01-05T06:45:00.000Z",
        "max_participants": 10,
        "activity_type": "k歌"
    }
    
    print(f"\n发送请求数据: {json.dumps(activity_data, indent=2)}")
    
    activity_response = requests.post(activity_url, json=activity_data, headers=headers)
    print(f"\n创建活动响应状态码: {activity_response.status_code}")
    print(f"创建活动响应内容: {activity_response.text}")
    
    if activity_response.status_code == 201:
        print("\n✅ 测试成功！带Z后缀的ISO时间格式被正确处理")
    else:
        print("\n❌ 测试失败！带Z后缀的ISO时间格式处理出错")

if __name__ == "__main__":
    test_iso_time()
