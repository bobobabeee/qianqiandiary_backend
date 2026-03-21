import uuid
from datetime import datetime
from app import db


def _gen_id():
    return str(uuid.uuid4())


class VisionItem(db.Model):
    __tablename__ = "vision_items_v2"

    id = db.Column(db.String(50), primary_key=True, default=_gen_id)
    user_id = db.Column(db.BigInteger, nullable=False)
    category = db.Column(db.String(20), nullable=False, default='GROWTH')
    title = db.Column(db.String(200), nullable=False, default='')
    description = db.Column(db.Text, default='')
    image_url = db.Column(db.String(500), default='')
    target_date = db.Column(db.Date, default=None)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.Index('idx_vi_user_category', 'user_id', 'category'),
    )

    def to_dict(self):
        if self.target_date is None:
            target_val = None
        elif hasattr(self.target_date, "strftime"):
            target_val = self.target_date.strftime("%Y-%m-%d")
        else:
            target_val = str(self.target_date) if self.target_date else None
        return {
            "id": self.id,
            "category": self.category,
            "title": self.title or '',
            "description": self.description or '',
            "image_url": self.image_url or '',
            "target_date": target_val,
        }
