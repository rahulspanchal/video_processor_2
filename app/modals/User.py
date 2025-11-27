from mongoengine import Document, StringField, BooleanField, DateTimeField
import datetime

class User(Document):
    local_email = StringField()
    local_password = StringField()
    local_name = StringField()
    local_firstName = StringField()
    local_lastName = StringField()
    local_reset_password_token = StringField()
    local_reset_password_expiry = DateTimeField()
    local_phone = StringField()
    local_profileType = StringField()
    parentCategory = StringField()
    
    isAdmin = BooleanField(default=False)
    adminType = StringField()
    adminId = StringField()
    isMarketer = BooleanField(default=False)
    marketerId = StringField()
    isCreator = BooleanField(default=False)
    creatorId = StringField()
    
    profileImage = StringField(default="")

    created_at = DateTimeField(default=datetime.datetime.utcnow)
    lastModified_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        "collection": "users",   # <-- MongoDB collection name
        "indexes": ["local_email"],
        "strict": False
    }
