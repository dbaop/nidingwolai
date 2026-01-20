#!/usr/bin/env python3
# 模拟前端请求格式的最终测试

import requests
import json
import time

# 先登录获取token
def login(phone, password):
    login_url = 'http://localhost:5000/api/users/login'
    login_data = {
        'phone': phone,
        'password': password
    }
    response = requests.post(login_url, json=login_data)
    if response.status_code == 200:
        return response.json().get('data', {}).get('access_token')
    else:
        print(f'登录失败: {response.json()}')
        return None

# 测试不同的请求格式
def test_frontend_request_formats():
    # 先启动服务器
    print('=== 启动服务器 ===')
    import subprocess
    import sys
    
    # 启动服务器
    server_process = subprocess.Popen(
        [sys.executable, '-c', 'from app import create_app; app = create_app(); app.run(host="0.0.0.0", port=5000)'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # 等待服务器启动
    time.sleep(3)
    
    try:
        print('\n=== 登录新测试用户 ===')
        token = login('13800138000', '123456')
        if not token:
            return
        
        print('\n=== 测试不同的请求格式 ===')
        
        # 测试用例列表
        test_cases = [
            # 正常请求
            {
                'name': '正常请求',
                'activity_id': 27,
                'message': '正常测试'
            },
            # 驼峰命名参数
            {
                'name': '驼峰命名参数',
                'activityId': 27,
                'message': '驼峰命名测试'
            },
            # 简写参数名
            {
                'name': '简写参数名',
                'id': 27,
                'message': '简写参数测试'
            },
            # 字符串形式的activity_id
            {
                'name': '字符串形式的activity_id',
                'activity_id': '27',
                'message': '字符串ID测试'
            },
            # 不存在的activity_id
            {
                'name': '不存在的activity_id',
                'activity_id': 9999,
                'message': '不存在ID测试'
            },
        ]
        
        for i, test_case in enumerate(test_cases):
            print(f'\n--- 测试用例 {i+1}: {test_case["name"]} ---')
            enroll_url = 'http://localhost:5000/api/enrollments/'
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            print(f'请求URL: {enroll_url}')
            print(f'请求头: {headers}')
            print(f'请求数据: {test_case}')
            
            try:
                response = requests.post(enroll_url, headers=headers, json=test_case)
                print(f'响应状态码: {response.status_code}')
                print(f'响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}')
            except Exception as e:
                print(f'请求失败: {e}')
                
    finally:
        # 关闭服务器
        print('\n=== 关闭服务器 ===')
        server_process.terminate()
        server_process.wait()

if __name__ == '__main__':
    test_frontend_request_formats()