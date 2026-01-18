# app/models/activity.py
from datetime import datetime
from app import db


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    activity_type = db.Column(db.String(50), default='k歌')  # k歌、爬山、踢球等
    
    # 地点信息
    location = db.Column(db.String(100), nullable=False)
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    
    # 时间信息
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    registration_deadline = db.Column(db.DateTime)  # 报名截止时间
    refund_deadline = db.Column(db.DateTime)  # 退款截止时间
    
    # 参与者信息
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    current_participants = db.Column(db.Integer, default=1)
    max_participants = db.Column(db.Integer, nullable=False)
    
    # K歌特定信息
    room_type = db.Column(db.String(50))  # 小中大
    music_style = db.Column(db.String(100))  # 流行、摇滚、经典等
    accept_beginners = db.Column(db.Boolean, default=True)
    accept_microphone_king = db.Column(db.Boolean, default=True)
    
    # 费用信息
    cost_type = db.Column(db.String(50), default='aa')  # aa、发起人请客、男A女免等
    estimated_cost_per_person = db.Column(db.Float)
    total_cost = db.Column(db.Float)
    deposit_amount = db.Column(db.Float, default=0.0)  # 押金金额
    
    # 状态信息
    status = db.Column(db.String(50), default='pending')  # pending、active、full、completed、canceled
    is_published = db.Column(db.Boolean, default=True)
    
    # 其他信息
    requirements = db.Column(db.Text)
    cover_image_url = db.Column(db.String(255))  # 封面图片URL
    images = db.Column(db.Text)  # 其他图片URL列表，以JSON格式存储
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    enrollments = db.relationship('Enrollment', backref='activity', lazy=True)
    reviews = db.relationship('Review', backref='activity', lazy=True)
    activity_tags = db.relationship('ActivityTag', backref='activity', lazy=True)
    
    def __repr__(self):
        return f'<Activity {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'activity_type': self.activity_type,
            'location': self.location,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'registration_deadline': self.registration_deadline.isoformat() if self.registration_deadline else None,
            'refund_deadline': self.refund_deadline.isoformat() if self.refund_deadline else None,
            'organizer_id': self.organizer_id,
            'organizer': self.organizer.to_dict() if self.organizer else None,
            'current_participants': self.current_participants,
            'max_participants': self.max_participants,
            'room_type': self.room_type,
            'music_style': self.music_style,
            'accept_beginners': self.accept_beginners,
            'accept_microphone_king': self.accept_microphone_king,
            'cost_type': self.cost_type,
            'estimated_cost_per_person': self.estimated_cost_per_person,
            'total_cost': self.total_cost,
            'deposit_amount': self.deposit_amount,
            'status': self.status,
            'is_published': self.is_published,
            'requirements': self.requirements,
            'cover_image_url': self.cover_image_url,  # 添加封面图片URL
            'images': self.images,  # 添加其他图片URL列表
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
