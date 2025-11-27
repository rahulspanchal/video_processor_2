from mongoengine import (
    Document, StringField, ListField, IntField
)
class Video(Document):
    videoTitle = StringField()
    thumbnail = StringField()
    OldThumbnail = StringField()
    videoLink = StringField()
    brand = StringField()
    clients = ListField(StringField())
    genres = ListField(StringField())
    marketTypes = ListField(StringField())
    sortOrder = IntField(default=0)

    meta = {
        "collection": "videos",
        "indexes": ["brand"],
        "strict": False
    }