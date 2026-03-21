import uuid
from datetime import datetime
from app import db


def _gen_id():
    return str(uuid.uuid4())


class DiaryEntry(db.Model):
    __tablename__ = "diary_entries"

    id = db.Column(db.String(50), primary_key=True, default=_gen_id)
    user_id = db.Column(db.BigInteger, nullable=False)
    date = db.Column(db.Date, nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(20), nullable=False, default='DAILY')
    mood_icon = db.Column(db.String(50), nullable=False, default='Sun')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.Index('idx_de_user_date', 'user_id', 'date'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.strftime('%Y-%m-%d') if self.date else None,
            "content": self.content,
            "category": self.category,
            "mood_icon": self.mood_icon,
        }
