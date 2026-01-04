# app/models/review.py
from datetime import datetime
from app import db


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5星
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Review {self.from_user_id} -> {self.to_user_id} for Activity {self.activity_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'from_user_id': self.from_user_id,
            'reviewer': self.reviewer.to_dict() if self.reviewer else None,
            'to_user_id': self.to_user_id,
            'reviewee': self.reviewee.to_dict() if self.reviewee else None,
            'activity_id': self.activity_id,
            'activity': self.activity.to_dict() if self.activity else None,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
