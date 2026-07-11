"""History router — retrieve past predictions from MongoDB."""

from fastapi import APIRouter, Depends

from db.mongo import predictions_col
from routers.auth import get_current_user

router = APIRouter()


@router.get("")
def get_history(user: dict = Depends(get_current_user), limit: int = 20):
    """Return this user's most recent predictions."""
    cursor = (
        predictions_col.find({"user": user["email"]})
        .sort("created_at", -1)
        .limit(limit)
    )

    records = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        records.append(doc)

    return {"success": True, "data": records, "message": "Prediction history"}
