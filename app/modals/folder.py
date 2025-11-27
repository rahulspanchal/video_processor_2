from mongoengine import Document, StringField, BooleanField, DateTimeField, ListField, IntField
import datetime

class Folder(Document):
    folderBrand = StringField()
    folderTitle = StringField()
    clients = ListField(StringField())
    folderGenre = ListField(StringField())
    folderCategory = ListField(StringField())
    isGeneralFolder = BooleanField(default=False)
    multiCreatorId = ListField(StringField())
    sortOrder = IntField(default=0)
    dateAdded = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        "collection": "folders",  
        "indexes": ["folderTitle", "folderBrand"],
        "strict": False
    }
