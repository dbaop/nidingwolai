#!/usr/bin/env python3
# 检查活动的to_dict()方法输出

from app import create_app, db
from app.models import Activity

# 创建应用实例
app = create_app()

with app.app_context():
    print('=== 检查活动的to_dict()方法 ===')
    
    # 检查活动33
    activity33 = Activity.query.get(33)
    if activity33:
        print('\n=== 活动33的to_dict()输出 ===')
        activity33_dict = activity33.to_dict()
        for key, value in activity33_dict.items():
            print(f'{key}: {value}')
    
    # 检查活动31
    activity31 = Activity.query.get(31)
    if activity31:
        print('\n=== 活动31的to_dict()输出 ===')
        activity31_dict = activity31.to_dict()
        for key, value in activity31_dict.items():
            print(f'{key}: {value}')
    
    # 检查活动34（对比）
    activity34 = Activity.query.get(34)
    if activity34:
        print('\n=== 活动34的to_dict()输出 ===')
        activity34_dict = activity34.to_dict()
        for key, value in activity34_dict.items():
            print(f'{key}: {value}')
