from datetime import datetime, date, timedelta
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, desc
from app import db
from app.models.DiaryEntry import DiaryEntry
from app.utils.response import success_response, error_response

diary_bp = Blueprint("diary", __name__, url_prefix="/api/diary")

CATEGORY_META = {
    "WORK":         {"label": "职业成就", "color": "#FFE4CC"},
    "HEALTH":       {"label": "身体健康", "color": "#D4F5D4"},
    "RELATIONSHIP": {"label": "人际关系", "color": "#FFD6E0"},
    "GROWTH":       {"label": "个人成长", "color": "#E0D4FF"},
    "DAILY":        {"label": "日常微光", "color": "#FFF2D1"},
}

VALID_CATEGORIES = set(CATEGORY_META.keys())


def _normalize_entry_id(entry_id):
    """前端可能传 d-UUID 格式，统一转成小写 UUID 再查询"""
    if not entry_id:
        return ""
    s = entry_id.strip()
    if s.startswith("d-"):
        s = s[2:]
    return s.lower()


# ── 3.2 获取日记列表 ────────────────────────────────────────
@diary_bp.route("/entries", methods=["GET"])
@jwt_required()
def list_entries():
    uid = int(get_jwt_identity())
    print(uid)
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)
    page_size = min(page_size, 50)

    q = DiaryEntry.query.filter_by(user_id=uid)

    date_str = request.args.get("date")
    if date_str:
        try:
            q = q.filter(DiaryEntry.date == datetime.strptime(date_str, "%Y-%m-%d").date())
        except ValueError:
            pass

    category = request.args.get("category")
    if category and category in VALID_CATEGORIES:
        q = q.filter_by(category=category)

    total = q.count()
    items = q.order_by(desc(DiaryEntry.date), desc(DiaryEntry.created_at)) \
             .offset((page - 1) * page_size).limit(page_size).all()

    return success_response(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [e.to_dict() for e in items],
    })


# ── 3.3 获取单条日记 ────────────────────────────────────────
@diary_bp.route("/entries/<entry_id>", methods=["GET"])
@jwt_required()
def get_entry(entry_id):
    uid = int(get_jwt_identity())
    eid = _normalize_entry_id(entry_id)
    entry = DiaryEntry.query.filter_by(id=eid, user_id=uid).first()
    if not entry:
        return error_response(code=404, message="日记不存在")
    return success_response(data=entry.to_dict())


# ── 3.4 创建日记 ────────────────────────────────────────────
@diary_bp.route("/entries", methods=["POST"])
@jwt_required()
def create_entry():
    uid = int(get_jwt_identity())
    data = request.get_json() or {}

    content = (data.get("content") or "").strip()
    if not content or len(content) < 5:
        return error_response(message="日记内容至少5个字符")
    if len(content) > 500:
        return error_response(message="日记内容不能超过500个字符")

    date_str = data.get("date")
    try:
        entry_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
    except ValueError:
        return error_response(message="日期格式错误，应为 yyyy-MM-dd")

    category = data.get("category", "DAILY")
    if category not in VALID_CATEGORIES:
        return error_response(message=f"无效分类，可选值: {', '.join(VALID_CATEGORIES)}")

    mood_icon = data.get("mood_icon", "Sun")
    entry = DiaryEntry(
        user_id=uid,
        date=entry_date,
        content=content,
        category=category,
        mood_icon=mood_icon,
    )
    db.session.add(entry)
    db.session.flush()
    resp_data = {
        "id": entry.id,
        "date": entry_date.strftime("%Y-%m-%d"),
        "content": content,
        "category": category,
        "mood_icon": mood_icon,
    }
    db.session.commit()
    return success_response(data=resp_data, message="创建成功")


# ── 3.5 更新日记 ────────────────────────────────────────────
@diary_bp.route("/entries/<entry_id>", methods=["PUT"])
@jwt_required()
def update_entry(entry_id):
    uid = int(get_jwt_identity())
    eid = _normalize_entry_id(entry_id)
    entry = DiaryEntry.query.filter_by(id=eid, user_id=uid).first()
    if not entry:
        return error_response(code=404, message="日记不存在")

    data = request.get_json() or {}

    if "content" in data:
        content = (data["content"] or "").strip()
        if len(content) < 5:
            return error_response(message="日记内容至少5个字符")
        if len(content) > 500:
            return error_response(message="日记内容不能超过500个字符")
        entry.content = content

    if "date" in data:
        try:
            entry.date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        except ValueError:
            return error_response(message="日期格式错误")

    if "category" in data:
        if data["category"] not in VALID_CATEGORIES:
            return error_response(message="无效分类")
        entry.category = data["category"]

    if "mood_icon" in data:
        entry.mood_icon = data["mood_icon"]

    entry.updated_at = datetime.utcnow()
    db.session.commit()

    return success_response(data=entry.to_dict(), message="更新成功")


# ── 3.6 删除日记 ────────────────────────────────────────────
@diary_bp.route("/entries/<entry_id>", methods=["DELETE"])
@jwt_required()
def delete_entry(entry_id):
    uid = int(get_jwt_identity())
    eid = _normalize_entry_id(entry_id)
    entry = DiaryEntry.query.filter_by(id=eid, user_id=uid).first()
    if not entry:
        return error_response(code=404, message="日记不存在")
    db.session.delete(entry)
    db.session.commit()
    return success_response(data=None, message="删除成功")


# ── 3.7 日记统计 ────────────────────────────────────────────
@diary_bp.route("/stats", methods=["GET"])
@jwt_required()
def diary_stats():
    uid = int(get_jwt_identity())
    base_q = DiaryEntry.query.filter_by(user_id=uid)

    total_count = base_q.count()

    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    this_week_count = base_q.filter(DiaryEntry.date >= week_start).count()

    cat_dist_rows = (
        db.session.query(DiaryEntry.category, func.count(DiaryEntry.id))
        .filter_by(user_id=uid)
        .group_by(DiaryEntry.category)
        .all()
    )
    category_distribution = []
    top_category = None
    top_count = 0
    for cat, cnt in cat_dist_rows:
        meta = CATEGORY_META.get(cat, {"label": cat, "color": "#CCCCCC"})
        category_distribution.append({"category": cat, "count": cnt, "label": meta["label"]})
        if cnt > top_count:
            top_count = cnt
            top_category = cat

    def _parse_date(d):
        if d is None:
            return None
        if hasattr(d, "strftime"):
            return d
        try:
            return datetime.strptime(str(d)[:10], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None

    distinct_dates = (
        db.session.query(DiaryEntry.date)
        .filter_by(user_id=uid)
        .distinct()
        .order_by(desc(DiaryEntry.date))
        .all()
    )
    date_set = sorted(
        filter(None, (_parse_date(r[0]) for r in distinct_dates)),
        reverse=True,
    )
    streak_days = 0
    check = today
    for d in date_set:
        if d == check:
            streak_days += 1
            check -= timedelta(days=1)
        elif d < check:
            break

    return success_response(data={
        "total_count": total_count,
        "this_week_count": this_week_count,
        "top_category": top_category,
        "streak_days": streak_days,
        "category_distribution": category_distribution,
    })


# ── 3.8 日历记录日期 ────────────────────────────────────────
@diary_bp.route("/calendar", methods=["GET"])
@jwt_required()
def diary_calendar():
    uid = int(get_jwt_identity())
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    if not year or not month:
        return error_response(message="year 和 month 参数必填")

    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)

    rows = (
        db.session.query(DiaryEntry.date)
        .filter(DiaryEntry.user_id == uid, DiaryEntry.date >= start, DiaryEntry.date < end)
        .distinct()
        .all()
    )
    def _date_str(d):
        return d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d)

    recorded = sorted(set(_date_str(r[0]) for r in rows))

    return success_response(data={
        "year": year,
        "month": month,
        "recorded_dates": recorded,
    })


# ── 3.9 首页高光时刻 ────────────────────────────────────────
@diary_bp.route("/highlights", methods=["GET"])
@jwt_required()
def diary_highlights():
    uid = int(get_jwt_identity())
    limit = request.args.get("limit", 3, type=int)

    entries = (
        DiaryEntry.query
        .filter_by(user_id=uid)
        .order_by(desc(DiaryEntry.date), desc(DiaryEntry.created_at))
        .limit(limit)
        .all()
    )

    today = date.today()
    yesterday = today - timedelta(days=1)

    def _to_date(d):
        if d is None:
            return None
        if hasattr(d, "strftime"):
            return d
        try:
            return datetime.strptime(str(d)[:10], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None

    result = []
    for e in entries:
        d = _to_date(e.date)
        if d == today:
            display_date = "今天"
        elif d == yesterday:
            display_date = "昨天"
        else:
            display_date = d.strftime("%Y-%m-%d") if d else str(e.date)

        meta = CATEGORY_META.get(e.category, {"label": e.category, "color": "#CCCCCC"})
        result.append({
            **e.to_dict(),
            "display_date": display_date,
            "category_label": meta["label"],
            "category_color": meta["color"],
        })

    return success_response(data=result)
