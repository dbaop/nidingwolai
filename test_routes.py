#!/usr/bin/env python3
# 直接在应用程序内部测试路由配置

from app import create_app

# 创建应用实例
app = create_app()

# 获取所有路由
print('=== 所有注册的路由 ===')
for rule in app.url_map.iter_rules():
    # 只显示报名相关的路由
    if 'enroll' in str(rule) or 'api/enrollments' in str(rule):
        print(f'路径: {rule}')
        print(f'  方法: {list(rule.methods)}')
        print(f'  端点: {rule.endpoint}')
        print()

# 检查报名接口的路由配置
enrollment_rules = [rule for rule in app.url_map.iter_rules() if 'api/enrollments/' == str(rule)]
if enrollment_rules:
    print('=== 报名接口路由配置 ===')
    for rule in enrollment_rules:
        print(f'路径: {rule}')
        print(f'  方法: {list(rule.methods)}')
        print(f'  端点: {rule.endpoint}')
        print()
else:
    print('未找到报名接口的路由配置')

# 测试URL构建
with app.test_request_context():
    from flask import url_for
    print('\n=== URL构建测试 ===')
    try:
        # 测试报名接口的URL构建
        enroll_url = url_for('enrollment.enroll_activity')
        print(f'报名接口URL: {enroll_url}')
    except Exception as e:
        print(f'URL构建失败: {e}')