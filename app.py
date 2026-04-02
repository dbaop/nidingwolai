# app.py
import os
import time
from app import create_app
from app.config import config
from app.models.user import User
from app import db

# 获取配置环境
config_name = os.environ.get('FLASK_CONFIG') or 'default'

# 创建应用实例
app = create_app(config[config_name])


# ====== 临时跳过认证（仅开发用，上线前务必删除） ======
from flask import g, request

@app.before_request
def skip_auth_for_demo():
    if request.path.startswith('/api/activity/'):
        g.current_user = None
        return
# ====== 到此为止 ======


# ====== 出门前必加：最简活动创建接口（今晚效果闭环） ======
import time
from flask import request, jsonify

@app.route('/api/activity/create', methods=['POST'])
def create_activity():
    try:
        data = request.get_json()
        # 模拟保存（不连 DB，只返回 mock ID）
        activity_id = f"act_{int(time.time()) % 100000}"
        return jsonify({
            "status": "success",
            "id": activity_id,
            "message": "活动已创建，定金支付中...",
            "data": {
                "activity_id": activity_id,
                "title": data.get("title", "未命名活动"),
                "time": data.get("time", "2026-03-22 20:00"),
                "location": data.get("location", "北京朝阳 KTV"),
                "mode": data.get("mode", "AA"),  # "AA" or "host"
                "deposit": data.get("deposit", 20)
            }
        }), 200
    except Exception as e:
        return jsonify({"error": "创建失败", "detail": str(e)}), 400

@app.route('/api/activity/list', methods=['GET'])
def list_activities():
    return jsonify({
        "status": "success",
        "data": [
            {
                "id": "act_123456",
                "title": "三里屯 K 歌局",
                "time": "2026-03-22 20:00",
                "location": "三里屯某 KTV",
                "mode": "AA",
                "deposit": 20,
                "participants": 3,
                "max": 6
            }
        ]
    }), 200
# ====== 到此为止 ======


# 初始化默认管理员账户
def init_default_admin():
    with app.app_context():
        # 检查管理员账户是否已存在
        admin_phone = '13621114638'
        admin = User.query.filter_by(phone=admin_phone).first()
        
        if not admin:
            # 创建管理员账户
            admin = User(
                phone=admin_phone,
                nickname='管理员',
                role='admin'
            )
            admin.password = 'admin123456'  # 使用password属性设置器加密密码
            
            try:
                db.session.add(admin)
                db.session.commit()
                print(f'默认管理员账户创建成功！手机号：{admin_phone}，密码：admin123456')
            except Exception as e:
                db.session.rollback()
                print(f'创建管理员账户失败：{str(e)}')
        else:
            print(f'管理员账户已存在！手机号：{admin_phone}')


if __name__ == '__main__':
    # 初始化默认管理员账户
    init_default_admin()
    
    # 运行应用
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)