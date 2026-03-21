from flask import jsonify


def success_response(data=None, message="success"):
    return jsonify({
        "code": 200,
        "message": message,
        "data": data,
    }), 200


def error_response(code=400, message="操作失败", data=None):
    return jsonify({
        "code": code,
        "message": message,
        "data": data,
    }), code
