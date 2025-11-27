import json
import requests
from io import BytesIO
import re
import boto3
import os
from PIL import Image
import uuid
import pandas as pd

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
BUCKET_NAME = os.getenv('BUCKET_NAME')
FOLDER = os.getenv('FOLDER')

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)

def download_video(url):
    print("local-url", url)
    try:
        if not url or url.startswith("/rails"):
            return None
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            return BytesIO(response.content)
        else:
            return None
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None

def upload_to_s3(file_obj, file_name, content_type="video/mp4"):
    try:
        if isinstance(file_obj, bytes):
            file_obj = BytesIO(file_obj)
        elif not hasattr(file_obj, 'read'):
            raise ValueError("file_obj must be bytes or file-like object with read() method")

        s3_client.upload_fileobj(
            file_obj,
            BUCKET_NAME,
            f"{FOLDER}/{file_name}",
            ExtraArgs={"ACL": "public-read", "ContentType": content_type}
        )
        s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{FOLDER}/{file_name}"
        return s3_url
    except Exception as e:
        print(f"Error uploading {file_name} to S3: {e}")
        return None

def youtube_parser(url):
    if not url:
        return None
    parts = re.split(r'(vi/|v%3D|v=|/v/|youtu\.be/|/embed/)', url)
    if len(parts) >= 3:
        return re.split(r'[^\w\-]', parts[2])[0]
    else:
        return re.split(r'[^\w\-]', parts[0])[0]

def fetch_thumbnails(video_link):
    try:
        if "youtube.com/embed/" in video_link:
            video_id = video_link.split("embed/")[1].split("?")[0].split("&")[0]
            video_link = f"https://www.youtube.com/watch?v={video_id}"

        if video_link.startswith("https://www-ccv.adobe.io"):
            return "adobe-no-thumbnail"

        if "youtube" in video_link and "vimeo" not in video_link:
            video_id = youtube_parser(video_link)
            if not video_id:
                return ""
            qualities = [
                "maxresdefault.jpg",
                "sddefault.jpg",
                "hqdefault.jpg",
                "mqdefault.jpg",
                "default.jpg"
            ]
            for quality in qualities:
                url = f"https://img.youtube.com/vi/{video_id}/{quality}"
                try:
                    res = requests.head(url)
                    if res.ok:
                        return url
                except:
                    continue
            return ""

        if "vimeo.com" in video_link:
            match = re.search(r'vimeo\.com/(?:video/)?(\d+)', video_link)
            if not match:
                return ""
            video_id = match.group(1)
            api_url = f"https://vimeo.com/api/v2/video/{video_id}.json"
            try:
                response = requests.get(api_url)
                if not response.ok:
                    return ""
                res_json = response.json()
                if res_json and "thumbnail_large" in res_json[0]:
                    return res_json[0]["thumbnail_large"]
                else:
                    return ""
            except:
                return ""

        return ""
    except Exception:
        return ""

def get_compression_quality(size_in_mb):
    if size_in_mb <= 3:
        return 30
    elif size_in_mb <= 5:
        return 50
    else:
        return 70

def compress_image(image_data, quality=30):
    with Image.open(BytesIO(image_data)) as img:
        img_io = BytesIO()
        img.convert("RGB").save(img_io, format="JPEG", quality=quality)
        img_io.seek(0)
        return img_io

# def compress_image_thumb(image_data, quality=40, max_size=(800, 800)):
#     with Image.open(BytesIO(image_data)) as img:
#         # Resize image if larger than max_size
#         img.thumbnail(max_size, Image.ANTIALIAS)
        
#         img_io = BytesIO()
#         img.convert("RGB").save(
#             img_io,
#             format="JPEG",
#             quality=quality,
#             optimize=True,
#             progressive=True
#         )
#         img_io.seek(0)
#         return img_io

def compress_image_thumb(image_data, quality=60):
    with Image.open(BytesIO(image_data)) as img:
        # Reduce dimensions by 50%
        new_width = img.width // 2
        new_height = img.height // 2

        # Resize using new Pillow resampling
        img = img.resize((new_width, new_height), resample=Image.Resampling.LANCZOS)

        # Save to BytesIO with JPEG compression
        img_io = BytesIO()
        img.convert("RGB").save(
            img_io,
            format="JPEG",
            quality=quality,
            optimize=True,
            progressive=True
        )
        img_io.seek(0)
        return img_io
def download_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"Failed to download image from {url}: {e}")
        return None

def process_dataframe(df, max_rows=None):
    rows_to_process = df if max_rows is None else df.head(max_rows)

    for index, row in rows_to_process.iterrows():
        try:
            # [Original processing logic unchanged for credits, videos, images]
            pass  # placeholder, your existing process_dataframe logic
        except Exception as e:
            print(f"Row {index} skipped due to: {e}")
            continue
    return df

def process_json_data(data_list):
    """
    Process a list of JSON objects containing videos, images, and credits.
    Returns a list of processed JSON objects.
    """
    if isinstance(data_list, dict):
        data_list = [data_list]  # wrap single object in a list

    processed_list = []

    for index, item in enumerate(data_list):
        try:
            item = dict(item)  # ensure mutable dict

            # --- Process Credits ---
            credit_current = item.get('credits', '')
            structured_credits = []
            if credit_current:
                cleaned_lines = []
                for line in str(credit_current).split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    if ':' in line:
                        role_part, name_part = line.split(':', 1)
                        role_cleaned = re.split(r'[,&/]', role_part.strip())[0]
                        name_cleaned = name_part.strip()
                        if name_cleaned:
                            cleaned_lines.append(f"{role_cleaned}: {name_cleaned}")
                    elif '(' in line and ')' in line:
                        try:
                            name_part, role_part = line.split('(', 1)
                            role_cleaned = re.split(r'[,&/]', role_part.split(',')[0].replace(')', '').strip())[0]
                            name_cleaned = name_part.strip()
                            if name_cleaned and role_cleaned:
                                cleaned_lines.append(f"{role_cleaned}: {name_cleaned}")
                        except:
                            continue
                    elif '—' in line or '–' in line or '-' in line:
                        try:
                            name_part, role_part = re.split(r'[—–-]', line, 1)
                            name_cleaned = name_part.strip()
                            role_cleaned = re.split(r'[,&/]', role_part.split(',')[0].strip())[0]
                            if name_cleaned and role_cleaned:
                                cleaned_lines.append(f"{role_cleaned}: {name_cleaned}")
                        except:
                            continue

                for cline in cleaned_lines:
                    if ':' not in cline:
                        continue
                    role, names_str = cline.split(':', 1)
                    role = role.strip()
                    for name in [n.strip() for n in names_str.split(',') if n.strip()]:
                        parts = name.split()
                        first = parts[0] if parts else ''
                        last = name[len(first):].strip() if first and name.startswith(first) else ''
                        structured_credits.append({
                            "role": role,
                            "creatorName": name,
                            "firstName": first,
                            "lastName": last
                        })
            item['credits'] = structured_credits

            # --- Process Videos ---
            video_list = item.get('videos', [])
            new_videos = []
            for i, video in enumerate(video_list):
                new_video = {}
                link_url = video.get("link")
                if link_url and ("youtube.com" in link_url.lower() or "youtu.be" in link_url.lower() or "vimeo.com" in link_url.lower()):
                    new_video["link"] = link_url
                    thumbnail_url = fetch_thumbnails(link_url)
                    if thumbnail_url:
                        thumb_data = download_image(thumbnail_url)
                        if thumb_data:
                            size_in_mb = len(thumb_data) / (1024 * 1024)
                            quality = get_compression_quality(size_in_mb)
                            compressed_thumb = compress_image(thumb_data, quality=quality)
                            thumb_filename = f"thumb_{index}_{i}_{uuid.uuid4().hex}.jpg"
                            s3_thumb_url = upload_to_s3(compressed_thumb, thumb_filename, content_type="image/jpeg")
                            new_video["thumbnail"] = s3_thumb_url if s3_thumb_url else thumbnail_url
                        else:
                            new_video["thumbnail"] = ""
                    else:
                        new_video["thumbnail"] = ""
                else:
                    if link_url:
                        video_data = download_video(link_url)
                        if video_data:
                            filename = f"video_{index}_{i}_{uuid.uuid4().hex}.mp4"
                            s3_link = upload_to_s3(video_data, filename, content_type="video/mp4")
                            new_video["link"] = s3_link if s3_link else ""
                        else:
                            new_video["link"] = ""

                    thumb_url = video.get("thumbnail", "")
                    if thumb_url:
                        thumb_data = download_image(thumb_url)
                        if thumb_data:
                            size_in_mb = len(thumb_data) / (1024 * 1024)
                            quality = get_compression_quality(size_in_mb)
                            compressed_thumb = compress_image_thumb(thumb_data, quality=40)
                            thumb_filename = f"thumb_{index}_{i}_{uuid.uuid4().hex}.jpg"
                            s3_thumb_url = upload_to_s3(compressed_thumb, thumb_filename, content_type="image/jpeg")
                            new_video["thumbnail"] = s3_thumb_url if s3_thumb_url else thumb_url
                        else:
                            new_video["thumbnail"] = thumb_url
                    else:
                        new_video["thumbnail"] = ""

                for key in video:
                    if key not in ("link", "thumbnail"):
                        new_video[key] = video[key]
                new_videos.append(new_video)
            item['videos'] = new_videos

            # --- Process Images ---
            image_field = item.get('images', [])
            new_images = []

            if isinstance(image_field, str):
                image_urls = [url.strip() for url in image_field.split(',') if url.strip()]
            else:
                image_urls = list(image_field)  # already a list

            for i, img_url in enumerate(image_urls):
                img_data = download_image(img_url)
                if img_data:
                    size_in_mb = len(img_data) / (1024 * 1024)
                    quality = get_compression_quality(size_in_mb)
                    compressed_thumb = compress_image_thumb(img_data, quality=40)
                    compressed_main = compress_image(img_data, quality=quality)
                    thumb_filename = f"thumb_{index}_{i}_{uuid.uuid4().hex}.jpg"
                    main_filename = f"main_{index}_{i}_{uuid.uuid4().hex}.jpg"
                    s3_thumb_url = upload_to_s3(compressed_thumb, thumb_filename, content_type="image/jpeg")
                    s3_main_url = upload_to_s3(compressed_main, main_filename, content_type="image/jpeg")
                    # print("testing--->",s3_thumb_url,s3_main_url)
                    new_images.append({
                        "link": s3_main_url if s3_main_url else img_url,
                        "thumbnail": s3_thumb_url if s3_thumb_url else img_url
                    })
                else:
                    new_images.append({"link": img_url, "thumbnail": img_url})

            item['images'] = new_images
            processed_list.append(item)

        except Exception as e:
            print(f"Item {index} skipped due to: {e}")
            continue

    return processed_list
