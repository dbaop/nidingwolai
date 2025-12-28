# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_class='app.config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    
    # 注册蓝图
    from app.routes.user import user_bp
    from app.routes.activity import activity_bp
    from app.routes.enrollment import enrollment_bp
    
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(activity_bp, url_prefix='/api/activities')
    app.register_blueprint(enrollment_bp, url_prefix='/api/enrollments')
    
    # 初始化默认管理员账户
    with app.app_context():
        from app.models.user import User
        try:
            # 检查是否已创建表
            db.create_all()
            
            admin_phone = '13621114638'
            admin = User.query.filter_by(phone=admin_phone).first()
            
            if not admin:
                try:
                    admin = User(
                        phone=admin_phone,
                        nickname='管理员',
                        role='admin'
                    )
                    admin.password = 'admin123456'
                    db.session.add(admin)
                    db.session.commit()
                    print(f'默认管理员账户创建成功！手机号：{admin_phone}，密码：admin123456')
                except Exception as e:
                    db.session.rollback()
                    print(f'创建管理员账户失败：{str(e)}')
            else:
                print(f'管理员账户已存在！手机号：{admin_phone}')
        except Exception as e:
            print(f'数据库初始化失败：{str(e)}')
    
    return app