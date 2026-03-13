from app import db  # 从应用实例导入db

class User_file(db.Model):
    """用户表模型"""
    __tablename__ = "user_file"  # 数据库表名
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键ID
    user_id= db.Column(db.Integer, nullable=False)  
    user_image = db.Column(db.String(50), nullable=False)
    user_text = db.Column(db.String)  # 头像
    # create_time = db.Column(db.DateTime, default=datetime.now)  # 创建时间

    # 模型转字典（方便接口返回数据）
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_image": self.user_image,
            "user_text":self.user_text
        }