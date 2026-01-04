# app/utils/helpers.py
import json
import os
import re
import uuid
from datetime import datetime
from flask import jsonify


# 格式化响应
def format_response(status, message, data=None, code=200):
    response = {
        'status': status,
        'message': message
    }
    
    if data is not None:
        response['data'] = data
    
    return jsonify(response), code


# 验证手机号
def validate_phone(phone):
    if not phone:
        return False
    
    # 中国大陆手机号验证
    pattern = r'^1[3-9]\d{9}$'
    return re.match(pattern, phone) is not None


# 验证身份证号
def validate_id_card(id_card):
    if not id_card:
        return False
    
    # 简单的身份证号格式验证（18位）
    pattern = r'^\d{17}[\dXx]$'
    return re.match(pattern, id_card) is not None


# 生成唯一文件名
def generate_unique_filename(filename):
    if not filename:
        return None
    
    ext = os.path.splitext(filename)[1]
    unique_id = uuid.uuid4().hex
    return f'{unique_id}{ext}'


# 计算两点之间的距离（经纬度）
def calculate_distance(lat1, lon1, lat2, lon2):
    """
    使用Haversine公式计算两点之间的距离
    返回距离（单位：公里）
    """
    import math
    
    if not all([lat1, lon1, lat2, lon2]):
        return None
    
    # 地球半径（单位：公里）
    R = 6371.0
    
    # 将经纬度转换为弧度
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    
    # 差值
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    
    # Haversine公式
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return round(distance, 2)


# 格式化日期时间
def format_datetime(dt, format='%Y-%m-%d %H:%M:%S'):
    if not dt:
        return None
    
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except:
            return None
    
    return dt.strftime(format)


# 解析JSON字符串
def parse_json(json_str):
    if not json_str:
        return None
    
    try:
        return json.loads(json_str)
    except:
        return None


# 分页辅助函数
def paginate(query, page=1, per_page=10):
    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return {
        'items': pagination.items,
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }


# 获取当前时间
def get_current_time():
    return datetime.utcnow()


# 计算年龄
def calculate_age(birthdate):
    if not birthdate:
        return None
    
    if isinstance(birthdate, str):
        try:
            birthdate = datetime.fromisoformat(birthdate)
        except:
            return None
    
    today = datetime.utcnow()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    
    return age
