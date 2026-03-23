from datetime import datetime
from app import db


class VirtuePracticeLog(db.Model):
    __tablename__ = "virtue_practice_logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, nullable=False)
    date = db.Column(db.Date, nullable=False)
    virtue_type = db.Column(db.String(20), nullable=False)
    completed = db.Column('completed', db.Boolean, nullable=False, default=False)
    reflection = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'date', 'virtue_type', name='uk_user_date_type'),
    )

    def to_dict(self):
        if self.date is None:
            date_val = None
        elif hasattr(self.date, "strftime"):
            date_val = self.date.strftime("%Y-%m-%d")
        else:
            date_val = str(self.date) if self.date else None
        return {
            "id": self.id,
            "date": date_val,
            "virtue_type": self.virtue_type,
            "is_completed": self.completed,
            "reflection": self.reflection or '',
        }
