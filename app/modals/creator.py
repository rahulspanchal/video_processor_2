# app/models/creator.py
from mongoengine import Document,ListField, StringField, BooleanField, DateTimeField, ObjectIdField
import datetime

class Creator(Document):
    parentCategory = ObjectIdField()       # ref: parentcategories
    parentSubCategory = ObjectIdField()    # ref: parentsubcategories
    profileTags = StringField() 
    tags =StringField()
    first_name = StringField()
    last_name = StringField()
    contact_phone = StringField(default="")
    contact_email = StringField(default="")

    profile_type = StringField()
    profile_id = StringField()

    status = StringField(default="Incomplete")
    isReviewed = BooleanField(default=False)
    isRejected = BooleanField(default=False)
    isActive = BooleanField(default=False)

    created_at = DateTimeField(default=datetime.datetime.utcnow)
    lastModified_at = DateTimeField(default=datetime.datetime.utcnow)

    screen_name = StringField()
    display_screen_name = BooleanField(default=False)

    meta = {
        "collection": "creators",
        "indexes": ["contact_email", "first_name", "last_name"],
        "strict": False
    }
