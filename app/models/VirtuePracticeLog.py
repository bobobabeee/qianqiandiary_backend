import uuid
from datetime import datetime
from app import db


def _gen_id():
    return str(uuid.uuid4())


class VirtuePracticeLog(db.Model):
    __tablename__ = "virtue_practice_logs"

    id = db.Column(db.String(50), primary_key=True, default=_gen_id)
    user_id = db.Column(db.BigInteger, nullable=False)
    date = db.Column(db.Date, nullable=False)
    virtue_type = db.Column(db.String(20), nullable=False)
    is_completed = db.Column(db.Boolean, nullable=False, default=False)
    reflection = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'date', 'virtue_type', name='uk_user_date_type'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.strftime('%Y-%m-%d') if self.date else None,
            "virtue_type": self.virtue_type,
            "is_completed": self.is_completed,
            "reflection": self.reflection or '',
        }
