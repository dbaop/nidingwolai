# test_create_activity_price.py
# 测试创建活动接口的price参数处理

import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://127.0.0.1:5000/api'

# 测试登录获取token
def test_login():
    print("=== 测试登录获取token ===")
    url = f'{BASE_URL}/users/login'
    data = {
        'phone': '13800138000',
        'password': '123456'
    }
    response = requests.post(url, json=data)
    result = response.json()
    print(f"登录响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if result.get('status') == 'success':
        token = result.get('data', {}).get('access_token')
        print(f"获取到token: {token}")
        return token
    return None

# 测试创建活动（带price参数）
def test_create_activity_with_price(token):
    print("\n=== 测试创建活动（带price参数） ===")
    url = f'{BASE_URL}/activities/'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    # 生成未来时间
    start_time = datetime.utcnow() + timedelta(days=1)
    end_time = start_time + timedelta(hours=2)
    
    data = {
        'title': '测试活动（带价格）',
        'description': '测试price参数处理',
        'location': '测试地点',
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'max_participants': 4,
        'price': '40'  # 使用price参数
    }
    
    print(f"创建活动参数: {json.dumps(data, indent=2, ensure_ascii=False)}")
    response = requests.post(url, json=data, headers=headers)
    result = response.json()
    print(f"创建活动响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if result.get('status') == 'success':
        activity_data = result.get('data', {})
        print(f"\n创建成功！")
        print(f"活动ID: {activity_data.get('id')}")
        print(f"活动标题: {activity_data.get('title')}")
        print(f"estimated_cost_per_person: {activity_data.get('estimated_cost_per_person')}")
        print(f"price参数是否正确处理: {activity_data.get('estimated_cost_per_person') == 40}")
        return activity_data.get('id')
    return None

# 测试获取活动详情
def test_activity_detail(token, activity_id):
    print("\n=== 测试获取活动详情 ===")
    url = f'{BASE_URL}/activities/{activity_id}'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    result = response.json()
    print(f"活动详情响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if result.get('status') == 'success':
        activity_data = result.get('data', {})
        print(f"\n活动详情:")
        print(f"活动ID: {activity_data.get('id')}")
        print(f"活动标题: {activity_data.get('title')}")
        print(f"estimated_cost_per_person: {activity_data.get('estimated_cost_per_person')}")

if __name__ == '__main__':
    token = test_login()
    if token:
        activity_id = test_create_activity_with_price(token)
        if activity_id:
            test_activity_detail(token, activity_id)
    else:
        print("登录失败，无法继续测试")
