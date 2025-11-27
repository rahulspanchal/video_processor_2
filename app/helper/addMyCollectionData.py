from app.modals.MyCollectionData import MyCollectionData
from bson import ObjectId
import datetime
import os

def addMyCollectionData(collections_ids, portfolio_entry_id):
    created_entries = []

    for collection_id in collections_ids:
        collection_obj_id = ObjectId(collection_id)  # convert to ObjectId

        existing_entry = MyCollectionData.objects(
            collectionId=collection_obj_id,
            projectId=portfolio_entry_id,
            creatorId=ObjectId(os.getenv("COLLECTION_ID_ADMIN")),
        ).first()

        if not existing_entry:
            myCollectionData_entry = MyCollectionData(
                collectionId=collection_obj_id,  # store as ObjectId
                projectId=portfolio_entry_id,
                likeUsers=[],
                creatorId=ObjectId(os.getenv("COLLECTION_ID_ADMIN")),
                workStreamId="",
                multicreatorId="",
                blogId="",
                likes=0,
                created_at=datetime.datetime.utcnow(),
                lastModified_at=datetime.datetime.utcnow()
            )
            myCollectionData_entry.save()
            created_entries.append(str(myCollectionData_entry.id))

    return {
        "message": "Processed MyCollectionData entries",
        "created_ids": created_entries
    }
