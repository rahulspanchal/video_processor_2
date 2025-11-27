from mongoengine import Document, StringField, BooleanField, DateTimeField, ListField, IntField
import datetime

class MyCollection(Document):
    collectionType = StringField()
    creatorId = StringField()
    profile_type = StringField()
    label = StringField()
    frontTitle = StringField()
    frontDescription = StringField()
    frontNumber = ListField(IntField())
    profileCardType = StringField()
    isActive = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    lastModified_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        "collection": "mycollections",
        "indexes": ["label", "frontTitle"],
        "strict": False
    }
