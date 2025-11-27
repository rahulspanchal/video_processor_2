from app.modals import Multicreator, Creator, User, Content
import datetime
import os
from bson import ObjectId, errors

def add_or_update_multicreator(item):
    """
    Add or update a creator in Multicreator and Creator, and link User if exists.
    - Existing entries: leave multicreator_existing and creator_existing untouched.
    - New Multicreator: set parentCategory, parentSubCategory, profile_type, profileTags
      based on matching Content.params label. If no match, profile_type='general' and profileTags=original profile_type.
    """
    email = item.get("email")
    firstname = item.get("firstname", "")
    lastname = item.get("lastname", "")
    profile_type = item.get("profile_type", "")
    profile_type_original = item.get("profile_type", "")
    item_genre = item.get("Genre", [])
    item_market_types = item.get("Market_Category", [])
    now = datetime.datetime.utcnow()
    action = {}

    if not email:
        return None, None, None, {
            "multicreator": "skipped",
            "creator": "skipped",
            "user": "skipped"
        }

    # --- fetch Content for profile-types ---
    exising_bucekts = Content.objects(code='profile-types').first()
    params = exising_bucekts.params if exising_bucekts else []

    # --- Match profile_type with label in params ---
    matched_param = None
    for p in params:
        if p.value and str(p.value).lower() == str(profile_type).lower():
            matched_param = p
            break
    if matched_param:
        parent_category = matched_param.parentCategory
        parent_subcategory = matched_param.parentSubCategory
        profile_type =matched_param.value
    else:
        parent_category = os.getenv("PARENT_CATEGORY", "")
        parent_subcategory = os.getenv("PARENT_CATEGORY_SUBCATEGORY", "")
        profile_type = "general"

    # --- Ensure lists ---
    if not isinstance(item_genre, list):
        item_genre = [item_genre] if item_genre else []
    if not isinstance(item_market_types, list):
        item_market_types = [item_market_types] if item_market_types else []

    # --- Check existing entries ---
    multicreator_existing = Multicreator.objects(contact_email=email).first()
    creator_existing = Creator.objects(contact_email=email).first()
    user_existing = User.objects(local_email=email).first()

    # --- Update existing Creator ---
    if creator_existing:
        creator_existing.first_name = firstname or creator_existing.first_name
        creator_existing.last_name = lastname or creator_existing.last_name
        creator_existing.profile_type = profile_type or creator_existing.profile_type
        creator_existing.lastModified_at = now
        creator_existing.profileTags = profile_type_original
        # Always link to correct Multicreator if exists
        if multicreator_existing:
            creator_existing.profile_id = str(multicreator_existing.id)
        creator_existing.save()
        action["creator"] = "updated"

    # --- Update existing Multicreator ---
    if multicreator_existing:
        multicreator_existing.lastModified_at = now
        multicreator_existing.profile_type = profile_type or multicreator_existing.profile_type
        # if item_genre:
        #     multicreator_existing.genre = list(set(multicreator_existing.genre + item_genre))
        if item_market_types:
            multicreator_existing.marketTypes = list(set(multicreator_existing.marketTypes + item_market_types))
        multicreator_existing.save()
        action["multicreator"] = "updated"

        multicreator_entry, creator_entry = multicreator_existing, creator_existing

    # --- Create new Multicreator (only if it does not exist) ---
    else:
        multicreator_entry = Multicreator(
            contact_email=email,
            first_name=firstname,
            last_name=lastname,
            profile_type=profile_type,
            created_at=now,
            isReviewed=False,
            parentCategory=parent_category,
            parentSubCategory=parent_subcategory,
            status="Approved",
            lastModified_at=now,
            marketTypes=list(set(item_market_types)),
            # genre=item_genre,
            profileTags=profile_type_original,
        )
        multicreator_entry.save()
        action["multicreator"] = "created"

        # --- Create linked Creator only if it does not exist ---
        if not creator_existing:
            creator_entry = Creator(
                contact_email=email,
                first_name=firstname,
                last_name=lastname,
                profile_type=profile_type,
                created_at=now,
                profile_id=str(multicreator_entry.id) if multicreator_entry.id else "",
                lastModified_at=now,
                isReviewed=False,
                profileTags=profile_type_original,
                status="Approved",
            )
            creator_entry.save()
            # Link Creator back to Multicreator
            multicreator_entry.creatorId = str(creator_entry.id) if creator_entry.id else ""
            multicreator_entry.save()
            action["creator"] = "created"
        else:
            creator_entry = creator_existing
            # Ensure profile_id is linked to newly created multicreator
            creator_entry.profile_id = str(multicreator_entry.id)
            creator_entry.save()

    # --- Link User if exists ---
    if user_existing:
        multicreator_entry.userId = str(user_existing.id) if user_existing.id else ""
        multicreator_entry.save()
        action["user"] = "linked"
    else:
        action["user"] = "skipped"

    return multicreator_entry, creator_entry, user_existing, action
