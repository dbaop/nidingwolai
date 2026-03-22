# app/routes/review.py
from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from app.models import Review, User, Activity, Enrollment
from app.utils.auth import jwt_required, get_current_user

review_bp = Blueprint('review', __name__)


# 创建评价
@review_bp.post('/')
@jwt_required
def create_review():
    user = get_current_user()
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid JSON data'}), 400
    
    # 获取必要参数
    to_user_id = data.get('to_user_id')
    activity_id = data.get('activity_id')
    rating = data.get('rating')
    comment = data.get('comment', '')
    
    if not all([to_user_id, activity_id, rating]):
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
    
    # 验证评分范围
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({'status': 'error', 'message': 'Rating must be between 1 and 5'}), 400
    
    # 检查用户是否参与了该活动
    enrollment = Enrollment.query.filter_by(
        user_id=user.id,
        activity_id=activity_id
    ).first()
    
    if not enrollment:
        return jsonify({'status': 'error', 'message': 'You must participate in this activity to review it'}), 403
    
    # 检查是否已经评价过该活动
    existing_review = Review.query.filter_by(
        from_user_id=user.id,
        activity_id=activity_id
    ).first()
    
    if existing_review:
        return jsonify({'status': 'error', 'message': 'You have already reviewed this activity'}), 400
    
    try:
        # 创建评价
        review = Review(
            from_user_id=user.id,
            to_user_id=to_user_id,
            activity_id=activity_id,
            rating=rating,
            comment=comment
        )
        
        db.session.add(review)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Review created successfully',
            'data': review.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to create review: {str(e)}'
        }), 500


# 获取用户的所有评价（作为被评价者）
@review_bp.get('/user/<int:user_id>')
def get_user_reviews(user_id):
    # 获取用户信息
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    # 获取该用户的评价
    reviews = Review.query.filter_by(to_user_id=user_id).all()
    
    return jsonify({
        'status': 'success',
        'message': 'Reviews retrieved',
        'data': [review.to_dict() for review in reviews]
    }), 200


# 获取活动的所有评价
@review_bp.get('/activity/<int:activity_id>')
def get_activity_reviews(activity_id):
    # 检查活动是否存在
    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({'status': 'error', 'message': 'Activity not found'}), 404
    
    # 获取该活动的评价
    reviews = Review.query.filter_by(activity_id=activity_id).all()
    
    return jsonify({
        'status': 'success',
        'message': 'Reviews retrieved',
        'data': [review.to_dict() for review in reviews]
    }), 200


# 获取当前用户的评价记录
@review_bp.get('/my')
@jwt_required
def get_my_reviews():
    user = get_current_user()
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    # 获取用户作为评价者的评价
    reviews_given = Review.query.filter_by(from_user_id=user.id).all()
    
    return jsonify({
        'status': 'success',
        'message': 'My reviews retrieved',
        'data': [review.to_dict() for review in reviews_given]
    }), 200