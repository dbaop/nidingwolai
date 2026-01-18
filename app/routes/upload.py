# app/routes/upload.py
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from app.utils.auth import jwt_required

upload_bp = Blueprint('upload', __name__)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 图片上传接口
@upload_bp.post('/image')
@jwt_required
def upload_image():
    # 检查是否有文件上传，支持多种可能的字段名称
    file = None
    file_fields = ['file', 'image', 'cover_image', 'avatar']
    
    for field_name in file_fields:
        if field_name in request.files:
            file = request.files[field_name]
            break
    
    if not file:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400
    
    # 检查文件是否为空
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400
    
    # 检查文件类型
    if file and allowed_file(file.filename):
        # 生成安全的文件名
        filename = secure_filename(file.filename)
        
        # 确保上传目录存在
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        # 保存文件
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # 返回图片URL
        image_url = f"/uploads/{filename}"
        return jsonify({
            'status': 'success',
            'message': 'Image uploaded successfully',
            'data': {
                'url': image_url,
                'filename': filename
            }
        }), 201
    else:
        return jsonify({'status': 'error', 'message': 'File type not allowed'}), 400


# 批量图片上传接口
@upload_bp.post('/images')
@jwt_required
def upload_images():
    # 检查是否有文件上传，支持多种可能的字段名称
    files = []
    file_fields = ['files', 'images', 'cover_images', 'avatars']
    
    for field_name in file_fields:
        if field_name in request.files:
            files = request.files.getlist(field_name)
            break
    
    if not files:
        return jsonify({'status': 'error', 'message': 'No files part'}), 400
    uploaded_files = []
    
    for file in files:
        if file and file.filename and allowed_file(file.filename):
            # 生成安全的文件名
            filename = secure_filename(file.filename)
            
            # 确保上传目录存在
            upload_folder = current_app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            # 保存文件
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            
            # 添加到上传列表
            uploaded_files.append({
                'url': f"/uploads/{filename}",
                'filename': filename
            })
    
    if not uploaded_files:
        return jsonify({'status': 'error', 'message': 'No valid files uploaded'}), 400
    
    return jsonify({
        'status': 'success',
        'message': 'Images uploaded successfully',
        'data': {
            'files': uploaded_files
        }
    }), 201