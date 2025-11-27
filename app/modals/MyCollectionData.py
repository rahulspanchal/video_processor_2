from mongoengine import Document, ObjectIdField, StringField, IntField, ListField, DateTimeField, ReferenceField
import datetime
from app.modals import PortfolioManager
import random

def default_like_count():
    # random number between 50–150
    return random.randint(50, 150)


def default_view_count():
    # random number between 300–500
    return random.randint(300, 500)
class MyCollectionData(Document):
    collectionId = ObjectIdField(required=True)
    likeCount = IntField(default=default_like_count)
    likeUsers = ListField(StringField())
    viewCount = IntField(default=default_view_count)
    creatorId = ObjectIdField(required=True)
    workStreamId = StringField()
    multicreatorId = StringField()
    blogId = StringField()
    projectId = ReferenceField(PortfolioManager)
    likes = IntField(default=0)
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    lastModified_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        "collection": "mycollectiondatas",
        "indexes": ["collectionId", "creatorId"],
        "strict": False
    }
