#!/usr/bin/env python3
# 模拟前端请求格式

import requests
import json

# 登录获取token
def login():
    login_url = 'http://localhost:5000/api/users/login'
    login_data = {
        'phone': '13621114638',
        'password': 'admin123456'
    }
    response = requests.post(login_url, json=login_data)
    if response.status_code == 200:
        return response.json().get('data', {}).get('access_token')
    else:
        print('登录失败:', response.json())
        return None

# 测试不同的URL格式
def test_different_url_formats():
    token = login()
    if not token:
        return
    
    print('=== 测试不同的URL格式 ===')
    
    # 测试URL列表
    test_urls = [
        'http://localhost:5000/api/enrollments/',    # 带斜杠
        'http://localhost:5000/api/enrollments',     # 不带斜杠
        'http://127.0.0.1:5000/api/enrollments/',    # 使用127.0.0.1
        'http://127.0.0.1:5000/api/enrollments'      # 使用127.0.0.1不带斜杠
    ]
    
    for i, url in enumerate(test_urls):
        print(f'\n--- 测试URL {i+1}: {url} ---')
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        enroll_data = {
            'activity_id': 27,
            'message': f'测试URL: {url}'
        }
        
        try:
            response = requests.post(url, headers=headers, json=enroll_data)
            print(f'状态码: {response.status_code}')
            print(f'响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}')
        except Exception as e:
            print(f'请求失败: {e}')

# 测试前端可能的请求格式
def test_frontend_request_format():
    token = login()
    if not token:
        return
    
    print('\n=== 测试前端可能的请求格式 ===')
    
    # 模拟前端可能使用的请求头
    frontend_headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # 模拟前端可能使用的数据格式
    frontend_data = {
        'activityId': 27,  # 驼峰命名
        'message': '前端格式测试'
    }
    
    enroll_url = 'http://localhost:5000/api/enrollments/'
    response = requests.post(enroll_url, headers=frontend_headers, json=frontend_data)
    print(f'状态码: {response.status_code}')
    print(f'响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}')

if __name__ == '__main__':
    test_different_url_formats()
    test_frontend_request_format()