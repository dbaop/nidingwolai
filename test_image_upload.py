import requests
import json

# 登录获取token
login_data = {
    "phone": "13621114638",
    "password": "admin123456"
}

response = requests.post('http://localhost:5000/api/users/login', json=login_data)
print("Login response:", response.status_code)

if response.status_code == 200:
    token_data = response.json()
    token = token_data['data']['access_token']
    print("Token:", token)
    
    # 准备活动数据
    activity_json = {
        "title": "带图片的测试活动",
        "description": "这是一个带图片的测试活动",
        "location": "测试地点",
        "start_time": "2025-12-25T10:00:00",
        "end_time": "2025-12-25T12:00:00",
        "max_participants": 10
    }
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # 使用multipart/form-data发送数据和图片
    data = {
        'data': json.dumps(activity_json)
    }
    
    with open('test_image.jpg', 'rb') as img_file:
        files = {
            'cover_image': ('test_image.jpg', img_file, 'image/jpeg')
        }
        
        response = requests.post('http://localhost:5000/api/activities/', data=data, files=files, headers=headers)
    
    print("Create activity response:", response.status_code)
    print("Create activity response body:", response.text)
    
    # 解析响应
    if response.status_code == 201:
        response_data = response.json()
        print("\n活动创建成功!")
        print("活动ID:", response_data['data']['id'])
        print("活动标题:", response_data['data']['title'])
        if response_data['data']['cover_image_url']:
            print("图片URL:", response_data['data']['cover_image_url'])
        else:
            print("图片URL: 未上传图片")
    else:
        print("活动创建失败!")
else:
    print("Login failed")