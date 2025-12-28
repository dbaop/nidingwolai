# app.py
import os
from app import create_app
from app.config import config
from app.models.user import User
from app import db

# 获取配置环境
config_name = os.environ.get('FLASK_CONFIG') or 'default'

# 创建应用实例
app = create_app(config[config_name])


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
