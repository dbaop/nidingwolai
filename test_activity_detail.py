# test_activity_detail.py
# 测试活动详情接口的报名状态返回

import requests
import json

BASE_URL = 'http://127.0.0.1:5000/api'

# 使用已有的token测试
TOKEN = 'yJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2OTkzNjg2OCwianRpIjoiYmMxOTEzNTctMjFmNi00OGI4LThkNzgtOWQ1ZDgwNWM1NGM0IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjMiLCJuYmYiOjE3Njk5MzY4NjgsImV4cCI6MTc3MDU0MTY2OH0.4AXn6_ucMm7VHKiLrk5HwFs7fqHP397-MDmSOhcgtlw'

# 测试获取活动详情（包含报名状态）
def test_activity_detail():
    print("=== 测试活动详情接口（包含报名状态） ===")
    # 测试已报名的活动
    activity_id = 36
    url = f'{BASE_URL}/activities/{activity_id}'
    headers = {
        'Authorization': f'Bearer {TOKEN}'
    }
    response = requests.get(url, headers=headers)
    result = response.json()
    print(f"活动详情响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if result.get('status') == 'success':
        activity_data = result.get('data', {})
        print(f"\n活动ID: {activity_data.get('id')}, 标题: {activity_data.get('title')}")
        print(f" 是否已报名: {activity_data.get('is_enrolled')}")
        print(f" 报名状态: {activity_data.get('enrollment_status')}")
        print(f" 当前参与人数: {activity_data.get('current_participants')}")
        print(f" 最大参与人数: {activity_data.get('max_participants')}")
        print(f" 活动状态: {activity_data.get('status')}")

# 测试获取活动列表（包含报名状态）
def test_activity_list():
    print("\n=== 测试活动列表接口（包含报名状态） ===")
    url = f'{BASE_URL}/activities/'
    headers = {
        'Authorization': f'Bearer {TOKEN}'
    }
    response = requests.get(url, headers=headers)
    result = response.json()
    
    if result.get('status') == 'success':
        activities = result.get('data', {}).get('activities', [])
        print(f"\n获取到 {len(activities)} 个活动")
        for activity in activities:
            print(f"活动ID: {activity.get('id')}, 标题: {activity.get('title')}")
            print(f" 是否已报名: {activity.get('is_enrolled')}, 报名状态: {activity.get('enrollment_status')}")

if __name__ == '__main__':
    test_activity_detail()
    test_activity_list()
