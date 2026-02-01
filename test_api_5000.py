#!/usr/bin/env python3
# 测试端口5000上的API

import requests
import json

def test_login():
    """测试登录API"""
    print('=== 测试登录API ===')
    try:
        login_url = 'http://127.0.0.1:5000/api/users/login'
        login_data = {'phone': '13800138000', 'password': '123456'}
        login_response = requests.post(login_url, json=login_data, timeout=5)
        print(f'登录状态码: {login_response.status_code}')
        
        if login_response.status_code == 200:
            print('登录成功!')
            data = login_response.json()
            token = data['data']['access_token']
            print(f'Token获取成功: {token[:20]}...')
            return token
        else:
            print(f'登录失败: {login_response.text}')
            return None
    except Exception as e:
        print(f'请求失败: {e}')
        return None

def test_enroll(token):
    """测试报名API"""
    if not token:
        print('没有有效的token，无法测试报名API')
        return
    
    print('\n=== 测试报名API ===')
    try:
        enroll_url = 'http://127.0.0.1:5000/api/enrollments/'
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        enroll_data = {'activity_id': 27, 'message': '测试报名'}
        
        enroll_response = requests.post(enroll_url, headers=headers, json=enroll_data, timeout=5)
        print(f'报名状态码: {enroll_response.status_code}')
        
        if enroll_response.status_code == 200:
            print('报名成功!')
            data = enroll_response.json()
            print(f'报名响应: {json.dumps(data, indent=2, ensure_ascii=False)}')
        else:
            print(f'报名失败: {enroll_response.text}')
            
    except Exception as e:
        print(f'请求失败: {e}')

if __name__ == '__main__':
    token = test_login()
    test_enroll(token)