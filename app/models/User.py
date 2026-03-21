from app import db  # 从应用实例导入db

class User(db.Model):
    """用户表模型"""
    __tablename__ = "user"  # 数据库表名
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), unique=True, nullable=False)
    nickname = db.Column(db.String(64), default='')
    header = db.Column(db.String)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "nickname": self.nickname or '',
            "header": self.header
        }