from app import db  # 从应用实例导入db

class User(db.Model):
    """用户表模型"""
    __tablename__ = "user"  # 数据库表名
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键ID
    username = db.Column(db.String(50), unique=True, nullable=False)  # 用户名（唯一）
    password = db.Column(db.String(50), unique=True, nullable=False)
    header = db.Column(db.String)  # 头像
    # create_time = db.Column(db.DateTime, default=datetime.now)  # 创建时间

    # 模型转字典（方便接口返回数据）
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "header": self.header
        }