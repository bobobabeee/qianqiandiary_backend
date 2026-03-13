from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.models.User import User
from app import db
from app.utils.response import success_response, error_response

# 创建用户蓝图，前缀统一为/api/user
user_bp = Blueprint("user", __name__, url_prefix="/api/user")

# 1. 创建用户接口（POST）
@user_bp.route("", methods=["POST"])
@jwt_required()
def create_user():
    data = request.get_json()
    if not data or not data.get("username"):
        return error_response(message="用户名不能为空")
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=data["username"]).first():
        return error_response(message="用户名已存在")
    
    # 创建新用户
    new_user = User(
        username=data["username"],
        age=data.get("age", 0)
    )
    db.session.add(new_user)
    db.session.commit()
    
    return success_response(data=new_user.to_dict(), message="用户创建成功")

# 2. 查询用户接口（GET，带动态参数）
@user_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return error_response(code=404, message="用户不存在")
    
    return success_response(data=user.to_dict())

# 3. 查询所有用户接口（GET）
@user_bp.route("", methods=["GET"])
def get_all_users():
    users = User.query.all()
    user_list = [user.to_dict() for user in users]
    return success_response(data=user_list)