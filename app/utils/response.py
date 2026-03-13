from flask import jsonify

def success_response(data=None, message="操作成功"):
    """成功响应封装"""
    return jsonify({
        "code": 200,
        "message": message,
        "data": data or {}
    }), 200

def error_response(code=400, message="操作失败", data=None):
    """失败响应封装"""
    return jsonify({
        "code": code,
        "message": message,
        "data": data or {}
    }), code