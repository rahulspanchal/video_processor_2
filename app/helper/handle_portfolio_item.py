from app.modals import PortfolioManager, VideoEmbed, ImageEmbed, SoundEmbed, Image, Video, Folder, ImageReference, VideoReference
from app.modals.MyCollection import MyCollection
import json
import datetime
import os
import requests
from io import BytesIO
from PIL import Image as PILImage
import uuid
import boto3

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
BUCKET_NAME = os.getenv('BUCKET_NAME')
FOLDER = os.getenv('FOLDER')

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)

def upload_webp_to_s3(image_data, prefix="media", quality=85):
    """
    Convert image_data (bytes) to WebP, upload to S3, return S3 URL
    """
    try:
        img = PILImage.open(BytesIO(image_data)).convert("RGB")
        img_io = BytesIO()
        img.save(img_io, "WEBP", quality=quality)
        img_io.seek(0)
        filename = f"{prefix}_{uuid.uuid4().hex}.webp"

        s3_client.upload_fileobj(
            img_io,
            BUCKET_NAME,
            f"{FOLDER}/{filename}",
            ExtraArgs={"ACL": "public-read", "ContentType": "image/webp"}
        )

        return f"https://{BUCKET_NAME}.s3.amazonaws.com/{FOLDER}/{filename}"
    except Exception as e:
        print(f"Failed to convert/upload WebP: {e}")
        return None

def ensure_webp_s3(url, prefix="media", quality=85):
    """
    Check if URL is already WebP, if not download, convert to WebP, upload to S3, return new URL
    """
    if not url:
        return url
    if url.lower().endswith(".webp"):
        return url

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        return upload_webp_to_s3(response.content, prefix=prefix, quality=quality)
    except Exception as e:
        print(f"Failed to process URL {url}: {e}")
        return url  # fallback to original

def handle_portfolio_item(item, normalized_role):
    def ensure_string(value):
        """Convert any value to string, or JSON if list/dict."""
        if isinstance(value, (list, dict)):
            return json.dumps(value)
        return str(value) if value is not None else ""

    # --- Process tags ---
    raw_tags = item.get("tags", [])
    
    if isinstance(raw_tags, str):
        tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
    elif isinstance(raw_tags, list):
        tags = raw_tags
    else:
        tags = []

    # --- Process collections (just keep strings, no MyCollection lookup) ---
    collections_str = item.get("collections", "")
    collections_list = [c.strip() for c in collections_str.split(",") if c.strip()]

    # --- Initial embeds ---
    videos = [
        VideoEmbed(
            video_link=v.get("link") or v.get("video_link"),
            video_thumbnail=ensure_webp_s3(v.get("thumbnail") or v.get("video_thumbnail"), prefix="video_thumb"),
            video_id=v.get("id") or v.get("video_id")
        )
        for v in item.get("videos", [])
    ]

    images = [
        ImageEmbed(
            image_link=ensure_webp_s3(i.get("link") or i.get("image_link"), prefix="image_main"),
            image_thumbnail=ensure_webp_s3(i.get("thumbnail") or i.get("image_thumbnail"), prefix="image_thumb"),
            image_id=i.get("id") or i.get("image_id")
        )
        for i in item.get("images", [])
    ]

    sounds = [SoundEmbed(**s) for s in item.get("sounds", [])]

    # --- Decide portfolio type ---
    if videos:
        portfolio_type = "video"
    elif images:
        portfolio_type = "image"
    else:
        portfolio_type = item.get("portfolio_type", "")

    # --- Create PortfolioManager entry ---
    portfolio_entry = PortfolioManager(
        portfolio_type=portfolio_type,
        label=ensure_string(item.get("label")),
        creatorId=ensure_string(item.get("creatorId")),
        title=ensure_string(item.get("title")),

        metaTitle=ensure_string(item.get("metaTitle")),
        metaDescription=ensure_string(item.get("metaDescription")),
        metaKeyword=ensure_string(item.get("metaKeyword")),
        uri= ensure_string(item.get("uri")) or ensure_string(item.get("title")).strip().replace(" ", "-").lower(),
        client=ensure_string(item.get("brands")),
        genre=item.get("Genre") if isinstance(item.get("Genre"), list) else [item.get("Genre")] if item.get("Genre") else [],
        marketcategory=ensure_string(item.get("Market_Category")),
        videos=videos,
        images=images,
        sounds=sounds,
        multiCreatorIds=item.get("multiCreatorIds", []),
        folderIds=[],
        isFeatured=item.get("isFeatured", False),
        createdat=datetime.datetime.utcnow(),
        lastModified_at=datetime.datetime.utcnow(),
        tags=tags,
        collections=collections_str,  # <-- store strings directly
        description=ensure_string(item.get("description")),
        about=ensure_string(item.get("about")),
        brand=ensure_string(item.get("brands")),
        agencies=ensure_string(item.get("agencies")),
        countries=ensure_string(item.get("countries")),
        regions=ensure_string(item.get("regions")),
        medium_types=ensure_string(item.get("medium_types")),
        credits=json.dumps(item.get("credits")) if item.get("credits") else "",
        year=ensure_string(item.get("year")),
        propositionOrMarketStrategy=ensure_string(item.get("Proposition_or_Market_Strategy")),
        creativeTool=ensure_string(item.get("Creative_Tool")),
        script=ensure_string(item.get("Script")),
        competition=ensure_string(item.get("Competition"))
    )

    portfolio_entry.save()

    # ---  Create or update folder first to get folder_id 
    def create_or_update_folder(portfolio):
        folderTitle = portfolio.title

        existing_folder = Folder.objects(
            folderTitle=folderTitle
        ).first()

        if existing_folder:
            # --- update existing ---
            existing_folder.folderBrand = portfolio.brand
            existing_folder.clients = [portfolio.client] if portfolio.client else []
            # existing_folder.folderGenre = portfolio.genre or []
            existing_folder.folderCategory = [portfolio.marketcategory] if portfolio.marketcategory else []

            # --- merge multiCreatorIds without duplicates ---
            if portfolio.multiCreatorIds:
                # Ensure it's a list
                new_ids = portfolio.multiCreatorIds if isinstance(portfolio.multiCreatorIds, list) else [portfolio.multiCreatorIds]
                existing_ids = existing_folder.multiCreatorId or []
                # Merge and remove duplicates
                merged_ids = list(set(existing_ids + new_ids))
                existing_folder.multiCreatorId = merged_ids

            existing_folder.lastModified_at = datetime.datetime.utcnow()
            existing_folder.save()
            return str(existing_folder.id)
        else:
            # --- create new ---
            folder_entry = Folder(
                folderBrand=portfolio.brand,
                folderTitle=folderTitle,
                clients=[portfolio.client] if portfolio.client else [],
                # folderGenre=portfolio.genre or [],
                folderCategory=[portfolio.marketcategory] if portfolio.marketcategory else [],
                isGeneralFolder=False,
                multiCreatorId=portfolio.multiCreatorIds,
                sortOrder=0,
                dateAdded=datetime.datetime.utcnow()
            )
            folder_entry.save()
            return str(folder_entry.id)

    folder_id = create_or_update_folder(portfolio_entry)  #  folder_id ready 
    portfolio_entry.folderIds = [folder_id]
    portfolio_entry.save()
    multiCreatorIdsProfileType = item.get("multiCreatorIdsProfileType", [])
    # --- Create Image entries and ImageReference for each multiCreatorId 
    if portfolio_type == "image" and images:
        updated_images = []
        for i in images:
            image_entry = Image(
                imageTitle=portfolio_entry.title,
                imageThumbnail=i.image_thumbnail,
                oldImageThumbnail=i.image_thumbnail,
                imageLink=i.image_link,
                oldImageLink=i.image_link,
                imageOriginalLink=i.image_link,
                oldImageOriginalLink=i.image_link,
                brand=portfolio_entry.brand,
                clients=[portfolio_entry.client] if portfolio_entry.client else [],
                genres=portfolio_entry.genre or [],
                marketTypes=[portfolio_entry.marketcategory] if portfolio_entry.marketcategory else [],
                sortOrder=0
            )
            image_entry.save()

            #  Create ImageReference per multiCreatorId 
            for creator_id in portfolio_entry.multiCreatorIds:
                profile_type = next(
                    (entry["profile_type"] for entry in multiCreatorIdsProfileType
                    if entry["id_multicreator"] == creator_id),
                    normalized_role  # fallback if not found
                )
                ImageReference(
                    folderId=folder_id,
                    imageId=str(image_entry.id),
                    creatorType=profile_type,
                    multiCreatorId=creator_id
                ).save()

            updated_images.append(ImageEmbed(
                image_link=i.image_link,
                image_thumbnail=i.image_thumbnail,
                image_id=str(image_entry.id)
            ))

        portfolio_entry.images = updated_images

    # --- Create Video entries and VideoReference for each multiCreatorId 
    if portfolio_type == "video" and videos:
        updated_videos = []
        for v in videos:
            video_entry = Video(
                videoTitle=portfolio_entry.title,
                videoLink=v.video_link,
                thumbnail=v.video_thumbnail,
                OldThumbnail=v.video_thumbnail,
                brand=portfolio_entry.brand,
                clients=[portfolio_entry.client] if portfolio_entry.client else [],
                genres=portfolio_entry.genre or [],
                marketTypes=[portfolio_entry.marketcategory] if portfolio_entry.marketcategory else [],
                sortOrder=0
            )
            video_entry.save()

            # Create VideoReference per multiCreatorId 
            for creator_id in portfolio_entry.multiCreatorIds:
                profile_type = next(
                    (entry["profile_type"] for entry in multiCreatorIdsProfileType
                    if entry["id_multicreator"] == creator_id),
                    normalized_role  # fallback if not found
                )
                VideoReference(
                    folderId=folder_id,
                    videoId=str(video_entry.id),
                    creatorType=profile_type,
                    multiCreatorId=creator_id
                ).save()

            updated_videos.append(VideoEmbed(
                video_link=v.video_link,
                video_thumbnail=v.video_thumbnail,
                video_id=str(video_entry.id)
            ))

        portfolio_entry.videos = updated_videos

    return portfolio_entry