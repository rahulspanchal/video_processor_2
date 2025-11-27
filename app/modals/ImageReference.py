from mongoengine import Document, ReferenceField, StringField, ObjectIdField

class ImageReference(Document):
    folderId = ReferenceField('Folder', required=True)
    imageId = ReferenceField('Image', required=True)
    creatorType = StringField()
    multiCreatorId = StringField()  # If this should be a list, use ListField(StringField())

    meta = {
        "collection": "imagereferences",
        "versioning": False,
        "indexes": ["folderId", "imageId"],
        "strict": False
    }
