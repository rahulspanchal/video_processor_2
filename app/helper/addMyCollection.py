from app.modals.MyCollection import MyCollection
import datetime
import os

def addMyCollection(item):
    """
    Process collections from input item:
    - Split comma-separated string into list
    - Check if each collection exists; if not, create
    - Return list of all collection IDs
    """
    # Get collections string; default empty string
    collections_str = item.get("collections", "")
    
    # Split by comma and strip whitespace, ignore empty
    collections_list = [c.strip() for c in collections_str.split(",") if c.strip()]

    collections_ids = []

    for col_label in collections_list:
        # Check if collection already exists
        existing = MyCollection.objects(label=col_label,collectionType="project").first()
        
        if existing and existing.id:
            collections_ids.append(str(existing.id))
        else:
            # Create new collection entry
            new_collection = MyCollection(
                collectionType="project",
                creatorId=os.getenv("COLLECTION_ID_ADMIN", ""),  # fallback empty string
                profile_type="superadmin",
                label=col_label,
                frontTitle=col_label,
                frontNumber=[],
                profileCardType="",
                isActive=False,
                created_at=datetime.datetime.utcnow(),
                lastModified_at=datetime.datetime.utcnow()
            )
            new_collection.save()

            # Only append if ID is valid
            if new_collection.id:
                collections_ids.append(str(new_collection.id))

    return {
        "message": "Processed collections",
        "collections_ids": collections_ids,  # includes both existing and new
        "input": collections_list
    }
