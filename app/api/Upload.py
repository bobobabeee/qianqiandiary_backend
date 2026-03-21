import os
import uuid
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from app.utils.response import success_response, error_response

load_dotenv()

upload_bp = Blueprint("upload", __name__, url_prefix="/api/upload")

R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY")
R2_SECRET_KEY = os.getenv("R2_SECRET_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def _allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route("/image", methods=["POST"])
@jwt_required()
def upload_image():
    """图片上传，支持 vision / avatar 用途"""
    if "file" not in request.files:
        return error_response(message="未选择文件")

    file = request.files["file"]
    if not file or file.filename == "":
        return error_response(message="文件为空")

    if not _allowed_file(file.filename):
        return error_response(message=f"仅支持: {', '.join(ALLOWED_EXTENSIONS)}")

    if not all([R2_ACCOUNT_ID, R2_ACCESS_KEY, R2_SECRET_KEY, R2_BUCKET_NAME]):
        return error_response(code=500, message="存储服务未配置")

    try:
        import boto3
        from botocore.exceptions import ClientError

        ext = file.filename.rsplit(".", 1)[1].lower()
        key = f"uploads/{uuid.uuid4().hex}.{ext}"

        s3 = boto3.client(
            "s3",
            endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
            aws_access_key_id=R2_ACCESS_KEY,
            aws_secret_access_key=R2_SECRET_KEY,
            region_name="auto",
        )

        s3.upload_fileobj(
            file,
            R2_BUCKET_NAME,
            key,
            ExtraArgs={"ContentType": file.content_type or "image/jpeg"},
        )

        url = f"https://{R2_ACCOUNT_ID}.r2.dev/{R2_BUCKET_NAME}/{key}"
        return success_response(data={"url": url}, message="上传成功")
    except ClientError as e:
        return error_response(code=500, message=f"上传失败: {e.response['Error']['Message']}")
    except Exception as e:
        return error_response(code=500, message=f"上传失败: {str(e)}")
