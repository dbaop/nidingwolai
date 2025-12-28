# manage.py
import os
import sys
import click
from flask.cli import FlaskGroup
from app import create_app, db
from app.models import User, Activity, Enrollment, Review, InterestTag, UserTag, ActivityTag

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 创建FlaskGroup
cli = FlaskGroup(create_app=create_app)


@cli.command('create_db')
def create_db():
    """创建数据库表"""
    app = create_app()
    with app.app_context():
        db.create_all()
        print('Database tables created successfully')


@cli.command('drop_db')
def drop_db():
    """删除数据库表"""
    if input('Are you sure you want to drop all database tables? (y/n): ').lower() == 'y':
        app = create_app()
        with app.app_context():
            db.drop_all()
            print('Database tables dropped successfully')


@cli.command('recreate_db')
def recreate_db():
    """重建数据库表"""
    app = create_app()
    with app.app_context():
        drop_db()
        create_db()


@cli.command('seed_db')
def seed_db():
    """初始化数据"""
    app = create_app()
    with app.app_context():
        # 创建兴趣标签
        tags = [
            # 音乐风格
            {'name': '流行', 'category': '音乐风格'},
            {'name': '摇滚', 'category': '音乐风格'},
            {'name': '经典', 'category': '音乐风格'},
            {'name': '民谣', 'category': '音乐风格'},
            {'name': '爵士', 'category': '音乐风格'},
            {'name': '嘻哈', 'category': '音乐风格'},
            
            # 活动类型
            {'name': 'K歌', 'category': '活动类型'},
            {'name': '爬山', 'category': '活动类型'},
            {'name': '踢球', 'category': '活动类型'},
            {'name': '剧本杀', 'category': '活动类型'},
            {'name': '桌游', 'category': '活动类型'},
            {'name': '看展', 'category': '活动类型'},
            {'name': '饭局', 'category': '活动类型'},
            {'name': '徒步', 'category': '活动类型'},
            {'name': '羽毛球', 'category': '活动类型'},
            
            # 兴趣爱好
            {'name': '音乐', 'category': '兴趣爱好'},
            {'name': '运动', 'category': '兴趣爱好'},
            {'name': '阅读', 'category': '兴趣爱好'},
            {'name': '旅行', 'category': '兴趣爱好'},
            {'name': '美食', 'category': '兴趣爱好'}
        ]
        
        try:
            for tag_data in tags:
                # 检查标签是否已存在
                existing_tag = InterestTag.query.filter_by(name=tag_data['name']).first()
                if not existing_tag:
                    tag = InterestTag(**tag_data)
                    db.session.add(tag)
            
            db.session.commit()
            print('Initial data seeded successfully')
        except Exception as e:
            db.session.rollback()
            print(f'Seeding data failed: {str(e)}')


@cli.command('run')
def run():
    """运行应用"""
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == '__main__':
    cli()
