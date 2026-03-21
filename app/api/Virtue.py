from datetime import datetime, date
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, desc
from app import db
from app.models.VirtuePracticeLog import VirtuePracticeLog
from app.utils.response import success_response, error_response

virtue_bp = Blueprint("virtue", __name__, url_prefix="/api/virtue")

# ── 美德定义（静态数据） ─────────────────────────────────────
VIRTUE_DEFINITIONS = [
    {
        "id": "virtue-friendly",
        "type": "FRIENDLY",
        "name": "友好亲和",
        "quote": "最美好的事情莫过于温和待人。",
        "guidelines": [
            "祝愿他人生活幸福",
            "不伤害他人，不介入纷争",
            "谦虚尊重他人，我不必永远正确",
        ],
        "icon_name": "Smile",
    },
    {
        "id": "virtue-responsible",
        "type": "RESPONSIBLE",
        "name": "勇于承担",
        "quote": "世界上只有一种英雄主义，那就是认清生活后依然热爱它。",
        "guidelines": [
            "主动承担责任，不推卸",
            "言出必行，信守承诺",
            "面对困难不退缩",
        ],
        "icon_name": "ShieldCheck",
    },
    {
        "id": "virtue-kind",
        "type": "KIND",
        "name": "善待他人",
        "quote": "善良是一种语言，聋子能听见，盲人能看见。",
        "guidelines": [
            "对他人保持善意和同理心",
            "用温柔的方式表达不同意见",
            "宽容他人的不足",
        ],
        "icon_name": "HeartHandshake",
    },
    {
        "id": "virtue-helpful",
        "type": "HELPFUL",
        "name": "帮助给予",
        "quote": "赠人玫瑰，手有余香。",
        "guidelines": [
            "主动帮助需要帮助的人",
            "分享知识和经验",
            "慷慨付出，不求回报",
        ],
        "icon_name": "HandHelping",
    },
    {
        "id": "virtue-grateful",
        "type": "GRATEFUL",
        "name": "感恩之心",
        "quote": "感恩是灵魂的记忆。",
        "guidelines": [
            "每天记录三件感恩的事",
            "向帮助过自己的人表达感谢",
            "珍惜当下拥有的一切",
        ],
        "icon_name": "Grape",
    },
    {
        "id": "virtue-learning",
        "type": "LEARNING",
        "name": "勤学不辍",
        "quote": "学如逆水行舟，不进则退。",
        "guidelines": [
            "每天坚持学习新知识",
            "保持好奇心和求知欲",
            "从错误中汲取经验教训",
        ],
        "icon_name": "BookOpen",
    },
    {
        "id": "virtue-reliable",
        "type": "RELIABLE",
        "name": "值得信赖",
        "quote": "诚实是最好的策略。",
        "guidelines": [
            "做到言行一致",
            "守时守信，不轻易食言",
            "在小事上也保持诚实",
        ],
        "icon_name": "Award",
    },
]

VIRTUE_TYPE_MAP = {v["type"]: v for v in VIRTUE_DEFINITIONS}
VALID_VIRTUE_TYPES = set(VIRTUE_TYPE_MAP.keys())


# ── 4.3 获取所有美德定义 ─────────────────────────────────────
@virtue_bp.route("/definitions", methods=["GET"])
@jwt_required()
def get_definitions():
    return success_response(data=VIRTUE_DEFINITIONS)


# ── 4.4 获取今日美德 ─────────────────────────────────────────
@virtue_bp.route("/today", methods=["GET"])
@jwt_required()
def get_today_virtue():
    uid = int(get_jwt_identity())
    date_str = request.args.get("date")
    try:
        target = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
    except ValueError:
        target = date.today()

    # 按日期轮换：day_of_year % 7 决定今日美德
    idx = target.timetuple().tm_yday % len(VIRTUE_DEFINITIONS)
    definition = VIRTUE_DEFINITIONS[idx]

    log = VirtuePracticeLog.query.filter_by(
        user_id=uid, date=target, virtue_type=definition["type"]
    ).first()

    practice_log = log.to_dict() if log else {
        "id": None,
        "date": target.strftime('%Y-%m-%d'),
        "virtue_type": definition["type"],
        "is_completed": False,
        "reflection": "",
    }

    return success_response(data={
        "definition": definition,
        "practice_log": practice_log,
    })


# ── 4.5 获取践行记录列表 ─────────────────────────────────────
@virtue_bp.route("/logs", methods=["GET"])
@jwt_required()
def list_logs():
    uid = int(get_jwt_identity())
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)
    page_size = min(page_size, 50)

    q = VirtuePracticeLog.query.filter_by(user_id=uid)

    date_str = request.args.get("date")
    if date_str:
        try:
            q = q.filter(VirtuePracticeLog.date == datetime.strptime(date_str, "%Y-%m-%d").date())
        except ValueError:
            pass

    vtype = request.args.get("virtue_type")
    if vtype and vtype in VALID_VIRTUE_TYPES:
        q = q.filter_by(virtue_type=vtype)

    total = q.count()
    items = q.order_by(desc(VirtuePracticeLog.date), desc(VirtuePracticeLog.created_at)) \
             .offset((page - 1) * page_size).limit(page_size).all()

    return success_response(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [l.to_dict() for l in items],
    })


# ── 4.6 提交/更新践行记录（upsert） ─────────────────────────
@virtue_bp.route("/logs", methods=["POST"])
@jwt_required()
def upsert_log():
    uid = int(get_jwt_identity())
    data = request.get_json() or {}

    date_str = data.get("date")
    try:
        log_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
    except ValueError:
        return error_response(message="日期格式错误，应为 yyyy-MM-dd")

    virtue_type = data.get("virtue_type")
    if not virtue_type or virtue_type not in VALID_VIRTUE_TYPES:
        return error_response(message=f"无效美德类型，可选值: {', '.join(VALID_VIRTUE_TYPES)}")

    log = VirtuePracticeLog.query.filter_by(
        user_id=uid, date=log_date, virtue_type=virtue_type
    ).first()

    if log:
        if "is_completed" in data:
            log.is_completed = bool(data["is_completed"])
        if "reflection" in data:
            log.reflection = data["reflection"]
        log.updated_at = datetime.utcnow()
    else:
        log = VirtuePracticeLog(
            user_id=uid,
            date=log_date,
            virtue_type=virtue_type,
            is_completed=bool(data.get("is_completed", False)),
            reflection=data.get("reflection", ""),
        )
        db.session.add(log)

    db.session.commit()
    return success_response(data=log.to_dict(), message="保存成功")


# ── 4.7 美德成长统计 ─────────────────────────────────────────
@virtue_bp.route("/stats", methods=["GET"])
@jwt_required()
def virtue_stats():
    uid = int(get_jwt_identity())

    total_practices = VirtuePracticeLog.query.filter_by(user_id=uid, is_completed=True).count()

    type_rows = (
        db.session.query(VirtuePracticeLog.virtue_type, func.count(VirtuePracticeLog.id))
        .filter_by(user_id=uid, is_completed=True)
        .group_by(VirtuePracticeLog.virtue_type)
        .all()
    )
    virtues_covered = len(type_rows)

    type_distribution = []
    for vt, cnt in type_rows:
        meta = VIRTUE_TYPE_MAP.get(vt, {})
        type_distribution.append({
            "virtue_type": vt,
            "count": cnt,
            "name": meta.get("name", vt),
        })

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
        db.session.query(VirtuePracticeLog.date)
        .filter_by(user_id=uid, is_completed=True)
        .distinct()
        .order_by(desc(VirtuePracticeLog.date))
        .all()
    )
    from datetime import timedelta
    date_set = sorted(
        filter(None, (_parse_date(r[0]) for r in distinct_dates)),
        reverse=True,
    )
    streak_days = 0
    check = date.today()
    for d in date_set:
        if d == check:
            streak_days += 1
            check -= timedelta(days=1)
        elif d < check:
            break

    return success_response(data={
        "total_practices": total_practices,
        "virtues_covered": virtues_covered,
        "streak_days": streak_days,
        "type_distribution": type_distribution,
    })
