# test_activity_list_encoding.py
# 测试活动列表接口的JSON编码

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

# 测试活动列表接口
def test_activity_list(token):
    print("\n=== 测试活动列表接口 ===")
    url = f'{BASE_URL}/activities/'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    
    # 打印原始响应内容
    print(f"原始响应内容: {response.text}")
    
    # 解析JSON
    result = response.json()
    print(f"\n解析后的响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if result.get('status') == 'success':
        activities = result.get('data', {}).get('activities', [])
        print(f"\n获取到 {len(activities)} 个活动")
        for activity in activities:
            print(f"活动ID: {activity.get('id')}, 标题: {activity.get('title')}")
            print(f"  原始标题: {json.dumps(activity.get('title'))}")

if __name__ == '__main__':
    token = test_login()
    if token:
        test_activity_list(token)
    else:
        print("登录失败，无法继续测试")
