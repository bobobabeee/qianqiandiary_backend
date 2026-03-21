from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
import jwt
from app.Config import config_map
from app.utils.response import error_response
# from app.utils.response import error_response
# from flask_jwt_extended import JWTManager

# 初始化数据库实例
db = SQLAlchemy()
jwt = JWTManager()  # 初始化 JWT

def create_app(config_name="dev"):
    """创建Flask应用实例（工厂模式）"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config_map[config_name])
    
    # 初始化数据库
    db.init_app(app)

    

    # 初始化 JWT（绑定到 Flask 应用）
    jwt.init_app(app)
    # 在 create_app 函数内，jwt.init_app(app) 之后添加：
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Token 过期处理"""
        return error_response(code=401, message="Token 已过期，请重新登录")
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """无效 Token 处理"""
        return error_response(code=401, message="无效的 Token，请检查")
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """缺少 Token 处理"""
        return error_response(code=401, message="请先登录获取 Token")
    
    
    # 注册蓝图
    from app.api.User import user_bp
    from app.api.Auth import auth_bp
    from app.api.Upload import upload_bp
    from app.api.Profile import profile_bp
    from app.api.Diary import diary_bp
    from app.api.Virtue import virtue_bp
    from app.api.Vision import vision_bp
    app.register_blueprint(user_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(diary_bp)
    app.register_blueprint(virtue_bp)
    app.register_blueprint(vision_bp)
    
    # # 最大文件大小（5MB）
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    # 导入模型，确保 db.create_all() 能发现所有表
    from app.models import User, DiaryEntry, VirtuePracticeLog, VisionItem  # noqa: F401
    with app.app_context():
        db.create_all()
    
    return app
