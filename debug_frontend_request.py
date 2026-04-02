#!/usr/bin/env python3
# 模拟前端请求格式，调试404问题

import requests
import json
import time

# 1. 登录获取token
def login(phone, password):
    login_url = 'http://localhost:5000/api/users/login'
    login_data = {
        'phone': phone,
        'password': password
    }
    print(f'\n=== 登录请求 ===')
    print(f'URL: {login_url}')
    print(f'数据: {login_data}')
    
    response = requests.post(login_url, json=login_data)
    print(f'状态码: {response.status_code}')
    print(f'响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}')
    
    if response.status_code == 200:
        return response.json().get('data', {}).get('access_token')
    else:
        print(f'登录失败: {response.json()}')
        return None

# 2. 模拟前端请求
def simulate_frontend_request(token):
    print(f'\n=== 模拟前端请求 ===')
    
    # 模拟前端可能使用的请求格式
    enroll_url = 'http://localhost:5000/api/enrollments/'
    
    # 模拟前端可能使用的headers
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # 模拟前端可能发送的请求数据
    enroll_data = {
        'activity_id': 27,
        'message': '模拟前端请求'
    }
    
    print(f'请求URL: {enroll_url}')
    print(f'请求头: {headers}')
    print(f'请求数据: {enroll_data}')
    
    # 发送请求
    response = requests.post(enroll_url, headers=headers, json=enroll_data)
    
    print(f'\n=== 响应信息 ===')
    print(f'状态码: {response.status_code}')
    print(f'响应头: {dict(response.headers)}')
    print(f'响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}')
    
    return response

# 3. 测试不同的URL格式
def test_different_urls(token):
    print(f'\n=== 测试不同的URL格式 ===')
    
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

# 4. 测试不同的请求数据格式
def test_different_data_formats(token):
    print(f'\n=== 测试不同的请求数据格式 ===')
    
    # 测试数据格式列表
    test_data_formats = [
        # JSON格式
        {
            'name': 'JSON格式',
            'content_type': 'application/json',
            'data': json.dumps({'activity_id': 27, 'message': 'JSON测试'})
        },
        # 表单格式
        {
            'name': '表单格式',
            'content_type': 'application/x-www-form-urlencoded',
            'data': {'activity_id': 27, 'message': '表单测试'}
        },
    ]
    
    for i, test_format in enumerate(test_data_formats):
        print(f'\n--- 测试数据格式 {i+1}: {test_format["name"]} ---')
        enroll_url = 'http://localhost:5000/api/enrollments/'
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': test_format['content_type']
        }
        
        print(f'URL: {enroll_url}')
        print(f'Content-Type: {test_format["content_type"]}')
        print(f'数据: {test_format["data"]}')
        
        try:
            if test_format['content_type'] == 'application/json':
                response = requests.post(enroll_url, headers=headers, data=test_format['data'])
            else:
                response = requests.post(enroll_url, headers=headers, data=test_format['data'])
            
            print(f'状态码: {response.status_code}')
            print(f'响应内容: {response.text}')
        except Exception as e:
            print(f'请求失败: {e}')

if __name__ == '__main__':
    # 先登录获取token
    token = login('13800138000', '123456')
    
    if token:
        # 模拟前端请求
        simulate_frontend_request(token)
        
        # 测试不同的URL格式
        test_different_urls(token)
        
        # 测试不同的请求数据格式
        test_different_data_formats(token)