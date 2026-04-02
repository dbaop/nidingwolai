#!/usr/bin/env python3
# 测试API端点，模拟前端调用

import requests
import json

# API基础URL
BASE_URL = 'http://localhost:5002/api'

# 测试获取活动列表
print('=== 测试获取活动列表 ===')
try:
    response = requests.get(f'{BASE_URL}/activities/')
    print(f'状态码: {response.status_code}')
    print(f'响应头: {dict(response.headers)}')
    
    data = response.json()
    print(f'\n响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}')
    
    if 'data' in data and 'activities' in data['data']:
        print(f'\n获取到的活动数量: {len(data["data"]["activities"])}')
        # 打印用户3创建的活动
        print('\n用户3创建的活动:')
        for activity in data["data"]["activities"]:
            if activity["organizer_id"] == 3:
                print(f'- {activity["title"]} (ID: {activity["id"]}, 状态: {activity["status"]}, 发布: {activity["is_published"]})')
    
except Exception as e:
    print(f'请求失败: {e}')

# 测试用户登录
print('\n=== 测试用户登录 ===')
try:
    login_data = {'phone': '13800138000', 'password': '123456'}
    response = requests.post(f'{BASE_URL}/users/login', json=login_data)
    print(f'状态码: {response.status_code}')
    
    login_response = response.json()
    print(f'登录响应: {json.dumps(login_response, indent=2, ensure_ascii=False)}')
    
    # 如果登录成功，测试获取我创建的活动
    if 'access_token' in login_response:
        token = login_response['access_token']
        print('\n=== 测试获取我创建的活动 ===')
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f'{BASE_URL}/activities/my-organized', headers=headers)
        print(f'状态码: {response.status_code}')
        
        my_activities = response.json()
        print(f'我的活动: {json.dumps(my_activities, indent=2, ensure_ascii=False)}')
    
except Exception as e:
    print(f'登录请求失败: {e}')
