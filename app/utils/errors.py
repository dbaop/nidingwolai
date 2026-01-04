# app/utils/errors.py
from flask import jsonify


# 自定义错误类
class AppError(Exception):
    def __init__(self, message, status_code=400, data=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.data = data


# 错误处理器
def handle_error(error):
    if isinstance(error, AppError):
        return jsonify({
            'status': 'error',
            'message': error.message,
            'data': error.data
        }), error.status_code
    
    # 处理其他异常
    return jsonify({
        'status': 'error',
        'message': str(error)
    }), 500


# 定义常见错误类型
def bad_request(message, data=None):
    return AppError(message, 400, data)


def unauthorized(message, data=None):
    return AppError(message, 401, data)


def forbidden(message, data=None):
    return AppError(message, 403, data)


def not_found(message, data=None):
    return AppError(message, 404, data)


def conflict(message, data=None):
    return AppError(message, 409, data)


def internal_server_error(message, data=None):
    return AppError(message, 500, data)


def service_unavailable(message, data=None):
    return AppError(message, 503, data)
