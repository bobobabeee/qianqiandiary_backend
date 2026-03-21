import os
from dotenv import load_dotenv

# 加载.env环境变量（可选，生产环境建议用系统环境变量）
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key_123")
    JSON_AS_ASCII = False
    # JWT 核心配置
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt_secret_456")  # JWT 加密密钥
    JWT_ACCESS_TOKEN_EXPIRES = 36000  # Token 过期时间（10小时，单位：秒）

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = False
    # 数据库连接（MySQL示例，sqlite可直接用文件路径）
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PWD', '123456')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', 3306)}/{os.getenv('DB_NAME', 'flask_demo')}?charset=utf8mb4"
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 关闭不必要的警告

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PWD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}?charset=utf8mb4"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# 配置映射，方便切换环境
config_map = {
    "dev": DevelopmentConfig,
    # "prod": ProductionConfig
}