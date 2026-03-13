from flask import Blueprint, Flask, request, jsonify
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError
import os
import uuid
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.utils import secure_filename
from app import db
from app.models.User_file import User_file
from app.utils.response import error_response
from app.models.User import User

# 加载环境变量（避免硬编码密钥）
load_dotenv()

upload_bp = Blueprint("upload", __name__, url_prefix="/api/upload")

# ========== Cloudflare R2 配置 ==========
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY")
R2_SECRET_KEY = os.getenv("R2_SECRET_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
R2_ENDPOINT = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

# ========== 初始化 R2 客户端（兼容 S3 API） ==========
s3_client = boto3.client(
    "s3",
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=R2_ACCESS_KEY,
    aws_secret_access_key=R2_SECRET_KEY,
    region_name="auto"  # R2 无需指定区域，填auto即可
)

# ========== 配置项 ==========
# 允许的图片格式
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


# ========== 工具函数 ==========
def allowed_file(filename):
    """校验文件格式是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(filename):
    """生成唯一文件名（避免重复）"""
    # 获取文件后缀
    ext = filename.rsplit('.', 1)[1].lower()
    # 用uuid生成唯一前缀
    unique_id = uuid.uuid4().hex
    # 拼接：唯一ID + 后缀
    return f"{unique_id}.{ext}"

# ========== 图片上传接口 ==========
@upload_bp.route('/image', methods=['POST'])
@jwt_required()
def upload_image():
    """图片上传接口（FormData格式传文件）"""
    # 1. 校验是否有文件
    if 'file' not in request.files:
        return error_response(message='文件不能为null')
    
    file = request.files['file']
    
    # 2. 校验文件是否为空
    if file.filename == '':
        return error_response(message="文件为空")
    
    # 3. 校验文件格式
    if not allowed_file(file.filename):
        return error_response(message=f'不支持的文件格式，仅允许：{",".join(ALLOWED_EXTENSIONS)}')
    
    try:
        # 4. 生成唯一文件名（避免覆盖）
        filename = generate_unique_filename(secure_filename(file.filename))
        
        # 5. 上传文件到 Cloudflare R2
        s3_client.upload_fileobj(
            Fileobj=file,  # 上传的文件对象
            Bucket=R2_BUCKET_NAME,  # R2桶名
            Key=filename,  # 存储在R2中的文件名
            ExtraArgs={
                'ContentType': file.content_type  # 设置文件MIME类型（如image/png）
            }
        )
        
        # 6. 生成文件访问URL（两种方式，选其一）
        # 方式1：如果桶配置了公共访问（R2 → 桶 → 设置 → 公共访问）
        file_url = f"https://{R2_ACCOUNT_ID}.r2.dev/{R2_BUCKET_NAME}/{filename}"
        # 方式2：生成预签名URL（无公共访问时用，有效期3600秒）
        # file_url = s3_client.generate_presigned_url(
        #     'get_object',
        #     Params={'Bucket': R2_BUCKET_NAME, 'Key': filename},
        #     ExpiresIn=3600
        # )
        # 提交到数据库
        user_id = int(get_jwt_identity())
        userfile = User_file(user_id=user_id,user_image=file_url)
        db.session.add(userfile)
        db.session.commit()
        # 7. 返回成功响应
        return jsonify({
            'code': 200,
            'msg': '图片上传成功',
            'data': {
                'filename': filename,
                'url': file_url,
                'size': request.content_length  # 文件大小（字节）
            }
        }), 200
    
    except ClientError as e:
        # R2上传异常
        return jsonify({
            'code': 500,
            'msg': f'R2上传失败:{e.response["Error"]["Message"]}'
        }), 500
    except Exception as e:
        # 其他异常
        return jsonify({
            'code': 500,
            'msg': f'上传失败：{str(e)}'
        }), 500
