#!/usr/bin/env python3
# 测试活动列表API

from app import create_app
import json

# 创建应用实例
app = create_app()

with app.test_client() as client:
    print('=== 测试活动列表API ===')
    
    # 发送GET请求获取活动列表
    response = client.get('/api/activities/')
    
    print(f'状态码: {response.status_code}')
    print(f'响应头: {dict(response.headers)}')
    
    # 解析响应数据
    try:
        data = json.loads(response.get_data(as_text=True))
        print(f'响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}')
        
        # 检查活动数量
        if 'data' in data and 'activities' in data['data']:
            print(f'\n获取到的活动数量: {len(data["data"]["activities"])}')
            for activity in data["data"]["activities"]:
                print(f'- {activity["title"]} (ID: {activity["id"]}, 发起人: {activity["organizer_id"]}, 状态: {activity["status"]}, 发布: {activity["is_published"]})')
    except Exception as e:
        print(f'解析响应失败: {e}')
        print(f'原始响应: {response.get_data(as_text=True)}')
    
    print('\n=== 测试完成 ===')
