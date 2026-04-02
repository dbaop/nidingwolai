#!/usr/bin/env python3
# 简单测试报名API的脚本

import requests
import json

# 登录获取token
def login():
    login_url = 'http://127.0.0.1:5001/api/users/login'
    login_data = {
        'phone': '13800138000',
        'password': '123456'
    }
    
    print('正在登录...')
    response = requests.post(login_url, json=login_data)
    print(f'登录状态码: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        token = data['data']['access_token']
        print(f'获取到token: {token[:20]}...')
        return token
    else:
        print(f'登录失败: {response.text}')
        return None

# 测试报名接口
def test_enroll(token):
    enroll_url = 'http://127.0.0.1:5001/api/enrollments/'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # 测试数据1：活动ID=27（已经报名过）
    enroll_data_1 = {
        'activity_id': 27,
        'message': '测试报名API'
    }
    
    print('\n=== 测试报名接口（活动ID=27） ===')
    response = requests.post(enroll_url, headers=headers, json=enroll_data_1)
    print(f'状态码: {response.status_code}')
    print(f'响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}')
    
    # 测试数据2：活动ID=6（未报名过）
    enroll_data_2 = {
        'activity_id': 6,
        'message': '测试报名另一个活动'
    }
    
    print('\n=== 测试报名接口（活动ID=6） ===')
    response = requests.post(enroll_url, headers=headers, json=enroll_data_2)
    print(f'状态码: {response.status_code}')
    print(f'响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}')

if __name__ == '__main__':
    token = login()
    if token:
        test_enroll(token)