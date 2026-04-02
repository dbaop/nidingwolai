# test_login_token.py
# 测试登录获取token并验证接口

import requests
import json

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

# 测试活动详情接口
def test_activity_detail(token):
    print("\n=== 测试活动详情接口 ===")
    activity_id = 36
    url = f'{BASE_URL}/activities/{activity_id}'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    result = response.json()
    print(f"活动详情响应: {json.dumps(result, indent=2, ensure_ascii=False)}")

# 测试报名接口
def test_enrollment(token):
    print("\n=== 测试报名接口 ===")
    activity_id = 36
    url = f'{BASE_URL}/enrollments/'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    data = {
        'activity_id': activity_id,
        'message': '测试报名'
    }
    response = requests.post(url, json=data, headers=headers)
    result = response.json()
    print(f"报名响应: {json.dumps(result, indent=2, ensure_ascii=False)}")

if __name__ == '__main__':
    token = test_login()
    if token:
        test_activity_detail(token)
        test_enrollment(token)
    else:
        print("登录失败，无法继续测试")
