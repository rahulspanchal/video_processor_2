from mongoengine import Document, ReferenceField, StringField, ObjectIdField
class VideoReference(Document):
    folderId = ReferenceField('Folder', required=True)
    videoId = ReferenceField('Video', required=True)
    creatorType = StringField()
    multiCreatorId = StringField()  # If this should be a list, use ListField(StringField())

    meta = {
        "collection": "videoreferences",
        "versioning": False,
        "indexes": ["folderId", "videoId"],
        "strict": False
    }