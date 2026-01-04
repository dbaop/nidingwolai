# app/models/enrollment.py
from datetime import datetime
from app import db


class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending、approved、rejected、attended、canceled
    message = db.Column(db.Text)  # 报名留言
    cost_paid = db.Column(db.Float, default=0.0)
    deposit_paid = db.Column(db.Float, default=0.0)  # 支付的押金金额
    deposit_transferred = db.Column(db.Boolean, default=False)  # 押金是否已转入对公账户
    cancel_time = db.Column(db.DateTime)  # 取消报名时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Enrollment User {self.user_id} -> Activity {self.activity_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user': self.user.to_dict() if self.user else None,
            'activity_id': self.activity_id,
            'activity': self.activity.to_dict() if self.activity else None,
            'status': self.status,
            'message': self.message,
            'cost_paid': self.cost_paid,
            'deposit_paid': self.deposit_paid,
            'deposit_transferred': self.deposit_transferred,
            'cancel_time': self.cancel_time.isoformat() if self.cancel_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
