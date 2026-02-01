#!/usr/bin/env python3
# 简单测试API的脚本

import requests
import time

def main():
    print('=== 简单API测试 ===')
    print(f'测试时间: {time.strftime("%Y-%m-%d %H:%M:%S")}')
    
    # 测试登录API
    print('\n1. 测试登录API:')
    try:
        login_url = 'http://127.0.0.1:5002/api/users/login'
        login_data = {'phone': '13800138000', 'password': '123456'}
        print(f'请求URL: {login_url}')
        print(f'请求数据: {login_data}')
        
        response = requests.post(login_url, json=login_data, timeout=15)
        print(f'响应状态码: {response.status_code}')
        print(f'响应内容: {response.text}')
        
        if response.status_code == 200:
            print('登录成功!')
            # 可以在这里添加报名测试
    except Exception as e:
        print(f'错误: {e}')
    
    print('\n=== 测试完成 ===')

if __name__ == '__main__':
    main()