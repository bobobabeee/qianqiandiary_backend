from datetime import datetime
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.VisionItem import VisionItem
from app.utils.response import success_response, error_response

vision_bp = Blueprint("vision", __name__, url_prefix="/api/vision")

VALID_CATEGORIES = {"WORK", "HEALTH", "RELATIONSHIP", "GROWTH", "DAILY"}


# ── 5.2 获取愿景列表 ────────────────────────────────────────
@vision_bp.route("/items", methods=["GET"])
@jwt_required()
def list_items():
    uid = int(get_jwt_identity())
    q = VisionItem.query.filter_by(user_id=uid)

    category = request.args.get("category")
    if category and category in VALID_CATEGORIES:
        q = q.filter_by(category=category)

    items = q.order_by(VisionItem.created_at.desc()).all()
    return success_response(data=[i.to_dict() for i in items])


# ── 5.3 获取单个愿景 ────────────────────────────────────────
@vision_bp.route("/items/<item_id>", methods=["GET"])
@jwt_required()
def get_item(item_id):
    uid = int(get_jwt_identity())
    item = VisionItem.query.filter_by(id=item_id, user_id=uid).first()
    if not item:
        return error_response(code=404, message="愿景不存在")
    return success_response(data=item.to_dict())


# ── 5.4 创建愿景 ────────────────────────────────────────────
@vision_bp.route("/items", methods=["POST"])
@jwt_required()
def create_item():
    uid = int(get_jwt_identity())
    data = request.get_json() or {}

    category = data.get("category", "GROWTH")
    if category not in VALID_CATEGORIES:
        return error_response(message=f"无效分类，可选值: {', '.join(VALID_CATEGORIES)}")

    target_date = None
    if data.get("target_date"):
        try:
            target_date = datetime.strptime(data["target_date"], "%Y-%m-%d").date()
        except ValueError:
            return error_response(message="目标日期格式错误，应为 yyyy-MM-dd")

    item = VisionItem(
        user_id=uid,
        category=category,
        title=data.get("title", ""),
        description=data.get("description", ""),
        image_url=data.get("image_url", ""),
        target_date=target_date,
    )
    db.session.add(item)
    db.session.commit()

    return success_response(data=item.to_dict(), message="创建成功")


# ── 5.5 更新愿景 ────────────────────────────────────────────
@vision_bp.route("/items/<item_id>", methods=["PUT"])
@jwt_required()
def update_item(item_id):
    uid = int(get_jwt_identity())
    item = VisionItem.query.filter_by(id=item_id, user_id=uid).first()
    if not item:
        return error_response(code=404, message="愿景不存在")

    data = request.get_json() or {}

    if "category" in data:
        if data["category"] not in VALID_CATEGORIES:
            return error_response(message="无效分类")
        item.category = data["category"]

    if "title" in data:
        item.title = data["title"]
    if "description" in data:
        item.description = data["description"]
    if "image_url" in data:
        item.image_url = data["image_url"]

    if "target_date" in data:
        if data["target_date"]:
            try:
                item.target_date = datetime.strptime(data["target_date"], "%Y-%m-%d").date()
            except ValueError:
                return error_response(message="目标日期格式错误")
        else:
            item.target_date = None

    item.updated_at = datetime.utcnow()
    db.session.commit()

    return success_response(data=item.to_dict(), message="更新成功")


# ── 5.6 删除愿景 ────────────────────────────────────────────
@vision_bp.route("/items/<item_id>", methods=["DELETE"])
@jwt_required()
def delete_item(item_id):
    uid = int(get_jwt_identity())
    item = VisionItem.query.filter_by(id=item_id, user_id=uid).first()
    if not item:
        return error_response(code=404, message="愿景不存在")
    db.session.delete(item)
    db.session.commit()
    return success_response(data=None, message="删除成功")
