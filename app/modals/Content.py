from mongoengine import (
    Document, StringField, ListField, EmbeddedDocument, EmbeddedDocumentField, ObjectIdField,
)
from bson import ObjectId

# ----- Embedded Schema -----
class Param(EmbeddedDocument):
    _id = ObjectIdField(default=ObjectId)
    parentCategory = ObjectIdField()      # ref: parentcategories
    parentSubCategory = ObjectIdField()   # ref: parentsubcategories
    label = StringField()
    value = StringField()
    description = StringField()

# ----- Main Schema -----
class Content(Document):
    name = StringField(required=True)
    code = StringField()
    tag = StringField()
    params = ListField(EmbeddedDocumentField(Param))

    meta = {
        "collection": "contents",      # same as mongoose model name
        "indexes": ["name", "code"],   # optional but good for search
        "strict": False                # ignore unknown fields
    }
