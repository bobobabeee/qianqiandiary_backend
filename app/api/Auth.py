from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from app.utils.response import success_response, error_response
from app.models.User import User
from app import db

# 认证蓝图，前缀 /api/auth
auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# 登录接口（无需 Token 校验）
@auth_bp.route("/login", methods=["POST"])
def login():
    """用户登录，生成 JWT Token"""
    # 1. 获取登录参数
    data = request.get_json()
    if not data or not data.get("username") or not data.get("password"):
        return error_response(message="用户名/密码不能为空")
    
   
    # 查询用户
    user = User.query.filter_by(username=data['username']).first()
    if not user or user.password != data['password']:  # 简化密码校验
        return error_response(message="用户和密码不匹配！！")
    
    # 生成Token（identity存储用户ID）
    access_token = create_access_token(identity=str(user.id))
    return success_response(data={
            'user_id': user.id,
            'token': access_token,
            'nickname': user.nickname or '',
            'user': user.to_dict()
        }, message="登陆成功")

@auth_bp.route("/regist", methods=["POST"])
def regist():
    data = request.get_json() or {}
    if not data.get("username") or not data.get("password"):
        return error_response(message="用户名和密码不能为空")
    if User.query.filter_by(username=data["username"]).first():
        return error_response(message="用户名已存在！")

    new_user = User(
        username=data["username"],
        password=data["password"],
        header=data.get("header"),
    )
    
    db.session.add(new_user)
    db.session.commit()

    access_token = create_access_token(identity=str(new_user.id))
    return success_response(message='注册成功', data={
        'user_id': new_user.id,
        'token': access_token,
        'nickname': new_user.nickname or '',
        'user': new_user.to_dict()
    })

@auth_bp.route("/delete", methods=["POST"])
def delete():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if not user:
        return error_response(message="用户不存在！")
    
    db.session.delete(user)
    db.session.commit()
    return success_response(message='删除成功！')