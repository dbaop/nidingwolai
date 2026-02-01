# test_api_fix.py
# 测试报名审核、活动列表和用户统计接口

import requests
import json

BASE_URL = 'http://127.0.0.1:5000/api'

# 用户登录获取token
def login(phone, password):
    url = f'{BASE_URL}/users/login'
    print(f"登录URL: {url}")
    data = {
        'phone': phone,
        'password': password
    }
    print(f"登录数据: {data}")
    response = requests.post(url, json=data)
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    try:
        return response.json()
    except:
        return {'status': 'error', 'message': 'Invalid response', 'content': response.text}

# 测试138用户登录
def test_user_138_login():
    print("=== 测试138用户登录 ===")
    result = login('13800138000', '123456')
    print(f"登录结果: {result}")
    if result.get('status') == 'success':
        return result.get('data', {}).get('access_token')
    return None

# 测试获取活动列表（包含报名状态）
def test_activity_list(token):
    print("\n=== 测试活动列表接口（包含报名状态） ===")
    url = f'{BASE_URL}/activities/'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    result = response.json()
    print(f"活动列表响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if result.get('status') == 'success':
        activities = result.get('data', {}).get('activities', [])
        print(f"\n获取到 {len(activities)} 个活动")
        for activity in activities:
            print(f"活动ID: {activity.get('id')}, 标题: {activity.get('title')}")
            print(f" 是否已报名: {activity.get('is_enrolled')}, 报名状态: {activity.get('enrollment_status')}")

# 测试获取用户创建的活动
def test_my_organized(token):
    print("\n=== 测试获取用户创建的活动 ===")
    url = f'{BASE_URL}/activities/my-organized'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    result = response.json()
    print(f"我的活动响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if result.get('status') == 'success':
        pagination = result.get('data', {}).get('pagination', {})
        print(f"\n已创建活动总数: {pagination.get('total')}")

# 测试获取用户参与的活动
def test_my_participated(token):
    print("\n=== 测试获取用户参与的活动 ===")
    url = f'{BASE_URL}/activities/my-participated'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    result = response.json()
    print(f"我参与的活动响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if result.get('status') == 'success':
        pagination = result.get('data', {}).get('pagination', {})
        print(f"\n已参加活动总数: {pagination.get('total')}")

# 测试报名审核接口
def test_enrollment_approval(token):
    print("\n=== 测试报名审核接口 ===")
    # 先获取活动列表，找到一个活动ID
    url = f'{BASE_URL}/activities/'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    result = response.json()
    
    if result.get('status') == 'success':
        activities = result.get('data', {}).get('activities', [])
        if activities:
            activity_id = activities[0].get('id')
            print(f"使用活动ID: {activity_id} 进行测试")
            
            # 测试报名
            enroll_url = f'{BASE_URL}/enrollments/'
            enroll_data = {
                'activity_id': activity_id,
                'message': '测试报名'
            }
            enroll_response = requests.post(enroll_url, json=enroll_data, headers=headers)
            print(f"报名响应: {enroll_response.json()}")

if __name__ == '__main__':
    # 测试138用户
    token = test_user_138_login()
    if token:
        test_activity_list(token)
        test_my_organized(token)
        test_my_participated(token)
        test_enrollment_approval(token)
    else:
        print("登录失败，无法继续测试")
