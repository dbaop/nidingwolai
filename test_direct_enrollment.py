# test_direct_enrollment.py
# 直接测试用户报名状态

import requests
import json

BASE_URL = 'http://127.0.0.1:5000/api'

# 使用已有的token测试
TOKEN = 'yJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2OTkzNjg2OCwianRpIjoiYmMxOTEzNTctMjFmNi00OGI4LThkNzgtOWQ1ZDgwNWM1NGM0IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjMiLCJuYmYiOjE3Njk5MzY4NjgsImV4cCI6MTc3MDU0MTY2OH0.4AXn6_ucMm7VHKiLrk5HwFs7fqHP397-MDmSOhcgtlw'

# 测试获取用户的报名记录
def test_user_enrollments():
    print("=== 测试获取用户的报名记录 ===")
    url = f'{BASE_URL}/enrollments/my'
    headers = {
        'Authorization': f'Bearer {TOKEN}'
    }
    response = requests.get(url, headers=headers)
    result = response.json()
    print(f"用户报名记录响应: {json.dumps(result, indent=2, ensure_ascii=False)}")

# 测试获取活动的报名记录
def test_activity_enrollments():
    print("\n=== 测试获取活动的报名记录 ===")
    activity_id = 36
    url = f'{BASE_URL}/enrollments/activity/{activity_id}'
    headers = {
        'Authorization': f'Bearer {TOKEN}'
    }
    response = requests.get(url, headers=headers)
    result = response.json()
    print(f"活动报名记录响应: {json.dumps(result, indent=2, ensure_ascii=False)}")

if __name__ == '__main__':
    test_user_enrollments()
    test_activity_enrollments()
