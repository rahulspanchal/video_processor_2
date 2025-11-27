from flask import jsonify
from app.modals.images import Image
from io import BytesIO
import os
import boto3
import requests
import uuid
from PIL import Image as PILImage

# --- AWS S3 Configuration ---
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
BUCKET_NAME = os.getenv('BUCKET_NAME')
FOLDER = "webp"

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)

# --- Upload to S3 ---
def upload_to_s3(file_obj, file_name, content_type="image/webp"):
    if isinstance(file_obj, bytes):
        file_obj = BytesIO(file_obj)
    elif not hasattr(file_obj, 'read'):
        raise ValueError("file_obj must be bytes or file-like object")

    try:
        s3_client.upload_fileobj(
            file_obj,
            BUCKET_NAME,
            f"{FOLDER}/{file_name}",
            ExtraArgs={"ACL": "public-read", "ContentType": content_type}
        )
        return f"https://{BUCKET_NAME}.s3.amazonaws.com/{FOLDER}/{file_name}"
    except Exception as e:
        print(f"Error uploading {file_name} to S3: {e}")
        return None


def download_image(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"Failed to download image from {url}: {e}")
        return None


def convert_to_webp(img_bytes, quality=50):
    pil_img = PILImage.open(BytesIO(img_bytes)).convert("RGB")
    webp_io = BytesIO()
    pil_img.save(webp_io, format="WEBP", quality=quality)
    webp_io.seek(0)
    return webp_io


def process_field(field_url, index, field_name):
    if not field_url:
        return None

    if field_url.lower().endswith(".webp"):
        return field_url

    img_bytes = download_image(field_url)
    if img_bytes:
        webp_io = convert_to_webp(img_bytes)
        webp_filename = f"{field_name}_idx{index}_{uuid.uuid4().hex}.webp"
        webp_url = upload_to_s3(webp_io, webp_filename)
        return webp_url if webp_url else field_url

    return field_url


def ImageConvert(number):
    try:
        img_objects = Image.objects.filter(
            __raw__={
                "oldImageLink": {"$exists": False}
            }
        ).order_by('+id').limit(100)

        bulk_updates = []
        updated_entries = []

        for index, img in enumerate(img_objects):
            obj_after = img.to_mongo().to_dict()
            obj_after["_id"] = str(obj_after["_id"])

            update_data = {}

            for field_name in ["imageLink", "imageThumbnail", "imageOriginalLink"]:
                original_url = getattr(img, field_name, None)

                if original_url:  # only process if original exists
                    old_field = "old" + field_name[0].upper() + field_name[1:]
                    if not getattr(img, old_field, None):
                        update_data[old_field] = original_url
                        obj_after[old_field] = original_url

                    webp_url = process_field(original_url, index, field_name)
                    update_data[field_name] = webp_url
                    obj_after[field_name] = webp_url

            if update_data:
                bulk_updates.append((img.id, update_data))
                updated_entries.append(obj_after)

        for img_id, update_data in bulk_updates:
            Image.objects(id=img_id).update(**update_data)

        return jsonify({
            "success": True,
            "count": len(updated_entries),
            "updated": updated_entries
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
