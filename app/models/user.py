# app/models/user.py
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    openid = db.Column(db.String(100), unique=True, nullable=True)  # 微信登录使用，手机号登录可为空
    nickname = db.Column(db.String(50), nullable=False)
    avatar = db.Column(db.String(200))
    gender = db.Column(db.Integer, default=0)  # 0:未知, 1:男, 2:女
    phone = db.Column(db.String(20), unique=True, nullable=True)  # 手机号，唯一索引
    password_hash = db.Column(db.String(255))  # 密码哈希
    real_name = db.Column(db.String(50))
    id_card = db.Column(db.String(20))
    bio = db.Column(db.Text)
    singing_style = db.Column(db.String(100))
    credit_score = db.Column(db.Integer, default=100)
    is_verified = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), default='user')  # user:普通用户, merchant:商家, admin:管理员
    merchant_application_status = db.Column(db.String(20), default='none')  # none:未申请, pending:审核中, approved:已通过, rejected:已拒绝
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # 关系
    activities = db.relationship('Activity', backref='organizer', lazy=True)
    enrollments = db.relationship('Enrollment', backref='user', lazy=True)
    reviews_given = db.relationship('Review', foreign_keys='Review.from_user_id', backref='reviewer', lazy=True)
    reviews_received = db.relationship('Review', foreign_keys='Review.to_user_id', backref='reviewee', lazy=True)
    user_tags = db.relationship('UserTag', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.nickname}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nickname': self.nickname,
            'avatar': self.avatar,
            'gender': self.gender,
            'phone': self.phone,
            'bio': self.bio,
            'singing_style': self.singing_style,
            'credit_score': self.credit_score,
            'is_verified': self.is_verified,
            'role': self.role,
            'merchant_application_status': self.merchant_application_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
