from mongoengine import (
    Document, StringField, ListField, IntField
)

class Image(Document):
    imageTitle = StringField()
    imageLink = StringField()
    oldImageLink = StringField()
    imageThumbnail = StringField()
    oldImageThumbnail = StringField()
    imageOriginalLink = StringField()
    oldImageOriginalLink = StringField()
    brand = StringField()
    clients = ListField(StringField())
    genres = ListField(StringField())
    marketTypes = ListField(StringField())
    sortOrder = IntField(default=0)

    meta = {
        "collection": "images",
        "indexes": ["brand"],
        "strict": False
    }