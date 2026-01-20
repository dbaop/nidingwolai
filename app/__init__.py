# app/__init__.py
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_class='app.config.Config'):
    import logging
    
    # 配置详细日志
    logging.basicConfig(level=logging.DEBUG)
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 添加请求日志中间件
    @app.before_request
    def log_request_info():
        app.logger.debug('Request Headers: %s', dict(request.headers))
        app.logger.debug('Request Body: %s', request.get_data(as_text=True))
        app.logger.debug('Request URL: %s', request.url)
        app.logger.debug('Request Method: %s', request.method)
        app.logger.debug('Request Path: %s', request.path)
        app.logger.debug('Request Host: %s', request.host)
        app.logger.debug('Request Remote Addr: %s', request.remote_addr)
    
    # 添加路由匹配日志
    @app.before_request
    def log_route_matching():
        app.logger.debug('Available routes:')
        for rule in app.url_map.iter_rules():
            if request.method in rule.methods and request.path == str(rule):
                app.logger.debug('Route matched: %s -> %s', rule, rule.endpoint)
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    
    # 注册蓝图
    from app.routes.user import user_bp
    from app.routes.activity import activity_bp
    from app.routes.enrollment import enrollment_bp
    from app.routes.upload import upload_bp
    
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(activity_bp, url_prefix='/api/activities')
    app.register_blueprint(enrollment_bp, url_prefix='/api/enrollments')
    app.register_blueprint(upload_bp, url_prefix='/api/upload')
    
    # 配置静态文件服务，用于访问上传的图片
    from flask import send_from_directory
    import os
    
    # 为/uploads/路径提供静态文件服务
    @app.route('/uploads/<path:filename>')
    def serve_uploads(filename):
        upload_folder = app.config['UPLOAD_FOLDER']
        return send_from_directory(upload_folder, filename)
    
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