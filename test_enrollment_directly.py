#!/usr/bin/env python3
# 在应用程序内部直接测试报名功能

from app import create_app, db
from app.models import User, Activity, Enrollment
from datetime import datetime, timedelta

# 创建应用实例
app = create_app()

with app.app_context():
    print('=== 在应用程序内部测试报名功能 ===')
    
    # 1. 获取测试用户
    print('\n1. 获取测试用户:')
    user = User.query.filter_by(phone='13800138000').first()
    if not user:
        print('❌ 未找到测试用户')
        exit(1)
    print(f'✅ 找到用户: {user.nickname} (ID: {user.id}, 手机号: {user.phone})')
    
    # 2. 创建测试活动
    print('\n2. 创建测试活动:')
    
    # 创建一个3小时后开始的活动（测试时间限制）
    start_time = datetime.utcnow() + timedelta(hours=3)
    end_time = start_time + timedelta(hours=2)
    
    # 创建需要押金的活动
    deposit_activity = Activity(
        title='测试活动-需要押金',
        description='测试押金支付功能',
        location='测试地点',
        start_time=start_time,
        end_time=end_time,
        max_participants=5,
        organizer_id=1,  # 假设用户1是组织者
        deposit_amount=100.0,  # 需要100元押金
        status='active'
    )
    
    # 创建不需要押金的活动
    no_deposit_activity = Activity(
        title='测试活动-无需押金',
        description='测试直接申请功能',
        location='测试地点',
        start_time=start_time,
        end_time=end_time,
        max_participants=5,
        organizer_id=1,  # 假设用户1是组织者
        deposit_amount=0.0,  # 无需押金
        status='active'
    )
    
    db.session.add(deposit_activity)
    db.session.add(no_deposit_activity)
    db.session.commit()
    
    print(f'✅ 创建需要押金的活动: {deposit_activity.title} (ID: {deposit_activity.id}, 押金: {deposit_activity.deposit_amount})')
    print(f'✅ 创建无需押金的活动: {no_deposit_activity.title} (ID: {no_deposit_activity.id}, 押金: {no_deposit_activity.deposit_amount})')
    print(f'   活动开始时间: {start_time}')
    print(f'   当前时间: {datetime.utcnow()}')
    
    # 3. 测试报名无需押金的活动
    print('\n3. 测试报名无需押金的活动:')
    try:
        # 检查是否已经报名
        existing_enrollment = Enrollment.query.filter_by(
            user_id=user.id, activity_id=no_deposit_activity.id
        ).first()
        
        if not existing_enrollment:
            # 创建报名记录
            enrollment = Enrollment(
                user_id=user.id,
                activity_id=no_deposit_activity.id,
                status='pending',
                message='测试无需押金报名',
                deposit_paid=False
            )
            
            db.session.add(enrollment)
            db.session.commit()
            
            print('✅ 无需押金活动报名成功！')
            print(f'   报名ID: {enrollment.id}')
            print(f'   报名状态: {enrollment.status}')
            print(f'   需要支付押金: {no_deposit_activity.deposit_amount > 0}')
        else:
            print('⚠️  用户已经报名该活动')
    
    except Exception as e:
        print(f'❌ 报名失败: {e}')
        import traceback
        traceback.print_exc()
        db.session.rollback()
    
    # 4. 测试报名需要押金的活动
    print('\n4. 测试报名需要押金的活动:')
    try:
        # 检查是否已经报名
        existing_enrollment = Enrollment.query.filter_by(
            user_id=user.id, activity_id=deposit_activity.id
        ).first()
        
        if not existing_enrollment:
            # 创建报名记录
            enrollment = Enrollment(
                user_id=user.id,
                activity_id=deposit_activity.id,
                status='pending',
                message='测试需要押金报名',
                deposit_paid=False
            )
            
            db.session.add(enrollment)
            db.session.commit()
            
            print('✅ 需要押金活动报名成功！')
            print(f'   报名ID: {enrollment.id}')
            print(f'   报名状态: {enrollment.status}')
            print(f'   需要支付押金: {deposit_activity.deposit_amount > 0}')
            print(f'   押金金额: {deposit_activity.deposit_amount}')
        else:
            print('⚠️  用户已经报名该活动')
    
    except Exception as e:
        print(f'❌ 报名失败: {e}')
        import traceback
        traceback.print_exc()
        db.session.rollback()
    
    # 5. 测试时间限制
    print('\n5. 测试时间限制:')
    print(f'   活动开始时间: {start_time}')
    print(f'   当前时间: {datetime.utcnow()}')
    print(f'   距离开始时间: {((start_time - datetime.utcnow()).total_seconds() / 3600):.2f} 小时')
    print('   报名限制: 活动开始前1小时内不允许报名')
    print('   取消限制: 活动开始前2小时内不允许取消')
    
    # 6. 清理测试数据
    print('\n6. 清理测试数据:')
    try:
        # 删除测试活动的报名记录
        Enrollment.query.filter_by(activity_id=deposit_activity.id).delete()
        Enrollment.query.filter_by(activity_id=no_deposit_activity.id).delete()
        
        # 删除测试活动
        db.session.delete(deposit_activity)
        db.session.delete(no_deposit_activity)
        db.session.commit()
        
        print('✅ 测试数据清理完成')
    except Exception as e:
        print(f'❌ 清理失败: {e}')
        db.session.rollback()