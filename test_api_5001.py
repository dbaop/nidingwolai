#!/usr/bin/env python3
# 测试API接口，使用端口5001

import requests
import json

# 1. 登录获取token
def login():
    print("=== 登录获取token ===")
    login_url = 'http://localhost:5001/api/users/login'
    login_data = {
        'phone': '13621114638',
        'password': 'admin123456'
    }
    response = requests.post(login_url, json=login_data)
    print(f'登录状态码: {response.status_code}')
    if response.status_code == 200:
        token = response.json().get('data', {}).get('access_token')
        print(f'获取到token: {token[:20]}...')
        return token
    else:
        print(f'登录失败: {response.json()}')
        return None

# 2. 测试报名接口
def test_enroll(token):
    print("\n=== 测试报名接口 ===")
    enroll_url = 'http://localhost:5001/api/enrollments/'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    enroll_data = {
        'activity_id': 27,
        'message': '测试报名'
    }
    
    print(f'请求URL: {enroll_url}')
    print(f'请求头: {headers}')
    print(f'请求数据: {enroll_data}')
    
    response = requests.post(enroll_url, headers=headers, json=enroll_data)
    print(f'\n响应状态码: {response.status_code}')
    print(f'响应头: {dict(response.headers)}')
    print(f'响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}')

if __name__ == '__main__':
    token = login()
    if token:
        test_enroll(token)