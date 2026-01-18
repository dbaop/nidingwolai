# app/models/tag.py
from datetime import datetime
from app import db


class InterestTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(50))  # 如：音乐风格、活动类型、兴趣爱好
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    user_tags = db.relationship('UserTag', backref='tag', lazy=True)
    activity_tags = db.relationship('ActivityTag', backref='tag', lazy=True)
    
    def __repr__(self):
        return f'<InterestTag {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('interest_tag.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserTag User {self.user_id} -> Tag {self.tag_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'tag_id': self.tag_id,
            'tag': self.tag.to_dict() if self.tag else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ActivityTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('interest_tag.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ActivityTag Activity {self.activity_id} -> Tag {self.tag_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'activity_id': self.activity_id,
            'tag_id': self.tag_id,
            'tag': self.tag.to_dict() if self.tag else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
