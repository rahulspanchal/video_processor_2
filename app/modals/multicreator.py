# app/models/multicreator.py
from mongoengine import (
    Document, StringField, IntField, BooleanField, ListField, DateTimeField,
    EmbeddedDocument, EmbeddedDocumentField, FloatField, ReferenceField, ObjectIdField
)
from bson import ObjectId

import datetime

# ----- Embedded Schemas -----
class Attribute(EmbeddedDocument):
    name = StringField()
    value = StringField()

class Skill(EmbeddedDocument):
    _id = ObjectIdField(default=ObjectId)  # <-- add this
    name = StringField()
    rating = IntField(default=0)

class Score(EmbeddedDocument):
    _id = ObjectIdField(default=ObjectId)  # <-- add this
    name = StringField()
    score = IntField(default=0)

class RateCard(EmbeddedDocument):
    workStreamId = ObjectIdField()   # ref: Workstreams
    label = StringField()
    value = StringField()
    description = StringField()
    rate = IntField()
    rate2 = IntField()
    rate3 = IntField()
    rate4 = IntField()
    qty = IntField()
    perValue = StringField()
    rateCardDescription = StringField()
    _id = ObjectIdField(default=ObjectId)


class WorkExperience(EmbeddedDocument):
    name = StringField()
    company = StringField()
    description = StringField()
    startDate = StringField()
    endDate = StringField()
    currentlyWorkHere = BooleanField()
    _id = ObjectIdField(default=ObjectId)

class Education(EmbeddedDocument):
    name = StringField()
    description = StringField()
    company = StringField()
    startDate = StringField()
    endDate = StringField()
    currentlyWorkHere = BooleanField()
    _id = ObjectIdField(default=ObjectId)


class Achievement(EmbeddedDocument):
    name = StringField()
    description = StringField()
    _id = ObjectIdField(default=ObjectId)
    
    
# ----- Main Schema -----
class Multicreator(Document):
    userId = StringField()
    profile_type = StringField()
    label = StringField()
    creatorId = StringField()

    parentCategory = ObjectIdField()      # ref: parentcategories
    parentSubCategory = ObjectIdField()   # ref: parentsubcategories

    completion_percent = IntField(default=0)
    first_name = StringField(default="", trim=True)
    last_name = StringField(default="", trim=True)
    screen_name = StringField()
    display_screen_name = BooleanField(default=False)

    contact_phone = StringField(default="")
    contact_email = StringField(default="")
    title = StringField(default="")
    rank = IntField(default=0)
    projects_done_count = IntField(default=0)
    project_view_count = IntField(default=0)

    awards = StringField(default="")
    awards_count = IntField(default=0)
    description = StringField(default="")

    isEditorPicked = BooleanField(default=False)
    isScrappingAvailable = BooleanField(default=False)
    isFeatured = BooleanField(default=False)
    featureOrder = IntField(default=0)

    primaryImage = StringField(default="")
    profileImage = StringField(default="")

    projects = ListField(StringField())  # ids of projects done
    isReviewed = BooleanField(default=False)
    status = StringField(default="Incomplete")
    isPortfolioAvailable = BooleanField(default=False)
    isActive = BooleanField(default=False)

    attributes = ListField(EmbeddedDocumentField(Attribute))
    skills = ListField(EmbeddedDocumentField(Skill))
    scores = ListField(EmbeddedDocumentField(Score))

    totalscore = IntField(default=0)
    rating = IntField(default=0)
    costing = IntField(default=0)

    rateCards = ListField(EmbeddedDocumentField(RateCard))

    languages = ListField(StringField())
    genre = ListField(StringField())
    clients = ListField(StringField())
    tools = ListField(StringField())
    race = ListField(StringField())
    marketTypes = ListField(StringField())
    castSkills = ListField(StringField())

    gender = StringField(default="")
    bodyType = StringField(default="")

    workExperiences = ListField(EmbeddedDocumentField(WorkExperience))
    education = ListField(EmbeddedDocumentField(Education))
    achievement = ListField(EmbeddedDocumentField(Achievement))

    age = StringField(default="20")
    experience = StringField()
    height = StringField()
    weight = StringField()

    location = StringField(default="")
    country = StringField(default="")

    created_at = DateTimeField(default=datetime.datetime.utcnow)
    lastModified_at = DateTimeField(default=datetime.datetime.utcnow)

    tags = ListField(StringField())
    profileTags = StringField()
    searchBrands = ListField(StringField())

    # ----- Enforce uniqueness in genre, marketTypes & normalize tags -----
    def clean(self):
        """Ensure unique entries and normalize tags before saving."""
        # Genre uniqueness
        if self.genre:
            seen = set()
            self.genre = [g for g in self.genre if not (g in seen or seen.add(g))]

        # MarketTypes uniqueness
        if self.marketTypes:
            seen = set()
            self.marketTypes = [m for m in self.marketTypes if not (m in seen or seen.add(m))]

        # Normalize tags: string → list
        if self.tags:
            if isinstance(self.tags, str):
                self.tags = [self.tags]
            seen = set()
            self.tags = [t for t in self.tags if not (t in seen or seen.add(t))]

        # Optional: Normalize profileTags if you want similar behavior
        if self.profileTags and isinstance(self.profileTags, str):
            self.profileTags = self.profileTags.strip()  # remove extra spaces

    meta = {
        "collection": "multicreators",
        "indexes": ["creatorId", "label", "isFeatured"],
        "strict": False
    }
