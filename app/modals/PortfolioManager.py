# app/models/portfolio.py
from mongoengine import (
    Document, StringField, ListField, BooleanField, DateTimeField, EmbeddedDocument,
    EmbeddedDocumentField
)
import datetime

# ----- Embedded Schemas -----
class VideoEmbed(EmbeddedDocument):
    video_link = StringField()
    video_thumbnail = StringField()
    video_id = StringField()

class ImageEmbed(EmbeddedDocument):
    image_link = StringField()
    image_id = StringField()
    image_thumbnail = StringField()

class SoundEmbed(EmbeddedDocument):
    sound_link = StringField()
    sound_id = StringField()

# ----- Main Portfolio Schema -----
class PortfolioManager(Document):
    portfolio_type = StringField(default="")
    label = StringField()
    creatorId = StringField()
    title = StringField(default="")
    
    metaTitle = StringField(default="")
    metaDescription = StringField(default="")
    metaKeyword = StringField(default="")
    uri = StringField(default="")

    client = StringField(default="")
    genre = ListField(StringField())
    marketcategory = StringField(default="")

    videos = ListField(EmbeddedDocumentField(VideoEmbed))
    images = ListField(EmbeddedDocumentField(ImageEmbed))
    sounds = ListField(EmbeddedDocumentField(SoundEmbed))

    multiCreatorIds = ListField(StringField())
    folderIds = ListField(StringField())

    isFeatured = BooleanField(default=False)

    createdat = DateTimeField(default=datetime.datetime.utcnow)
    lastModified_at = DateTimeField(default=datetime.datetime.utcnow)

    tags = ListField(StringField())
    description = StringField()
    about = StringField()
    brand = StringField()
    agencies = StringField()
    countries = StringField()
    regions = StringField()
    medium_types = StringField()
    collections = StringField()
    credits = StringField()
    year = StringField()
    propositionOrMarketStrategy = StringField()
    creativeTool = StringField()
    script = StringField()
    competition = StringField()

    meta = {
        "collection": "portfoliomanagers",
        "indexes": ["creatorId", "title", "isFeatured"],
        "strict": False
    }
