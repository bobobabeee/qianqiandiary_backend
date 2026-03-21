from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.User import User
from app import db
from app.utils.response import success_response, error_response

profile_bp = Blueprint("profile", __name__, url_prefix="/api/user")


# ── 6.1 获取当前用户信息 ─────────────────────────────────────
@profile_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user:
        return error_response(code=404, message="用户不存在")

    return success_response(data={
        "id": user.id,
        "username": user.username,
        "header": user.header or '',
    })


# ── 6.2 更新用户信息 ─────────────────────────────────────────
@profile_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user:
        return error_response(code=404, message="用户不存在")

    data = request.get_json() or {}

    if "username" in data:
        new_name = (data["username"] or "").strip()
        if not new_name:
            return error_response(message="用户名不能为空")
        existing = User.query.filter(User.username == new_name, User.id != uid).first()
        if existing:
            return error_response(code=409, message="用户名已存在")
        user.username = new_name

    if "header" in data:
        user.header = data["header"]

    db.session.commit()

    return success_response(data={
        "id": user.id,
        "username": user.username,
        "header": user.header or '',
    }, message="更新成功")


# ── 6.3 修改密码 ─────────────────────────────────────────────
@profile_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user:
        return error_response(code=404, message="用户不存在")

    data = request.get_json() or {}
    old_pwd = data.get("old_password", "")
    new_pwd = data.get("new_password", "")

    if not old_pwd or not new_pwd:
        return error_response(message="旧密码和新密码不能为空")

    if user.password != old_pwd:
        return error_response(code=401, message="旧密码不正确")

    if len(new_pwd) < 6:
        return error_response(message="新密码至少6位")

    user.password = new_pwd
    db.session.commit()

    return success_response(data=None, message="密码修改成功")
