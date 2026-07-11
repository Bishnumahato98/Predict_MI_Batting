"""Prediction router — lineup prediction + Playing XI selection."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from ml import predictor
from models.schemas import PredictRequest, Playing11Request
from db.mongo import predictions_col
from routers.auth import get_current_user

router = APIRouter()


@router.post("")
def predict_lineup(body: PredictRequest, user: dict = Depends(get_current_user)):
    """Predict LOW/MEDIUM/HIGH for each player in a lineup."""
    results = [
        predictor.predict_player(
            p.name, p.batting_pos, body.venue, body.opponent, body.season, body.is_home
        )
        for p in body.lineup
    ]

    record = {
        "type":      "lineup",
        "user":      user["email"],
        "venue":     body.venue,
        "opponent":  body.opponent,
        "season":    body.season,
        "is_home":   body.is_home,
        "results":   results,
        "created_at": datetime.now(timezone.utc),
    }
    predictions_col.insert_one(record)

    return {"success": True, "data": results, "message": "Prediction complete"}


@router.post("/playing11")
def playing11(body: Playing11Request, user: dict = Depends(get_current_user)):
    """Rank full squad and recommend best Playing XI."""
    squad = [p.model_dump() for p in body.squad]

    result = predictor.select_playing11(
        squad, body.venue, body.opponent, body.season, body.is_home
    )

    record = {
        "type":      "playing11",
        "user":      user["email"],
        "venue":     body.venue,
        "opponent":  body.opponent,
        "season":    body.season,
        "is_home":   body.is_home,
        "playing11": result["playing11"],
        "created_at": datetime.now(timezone.utc),
    }
    predictions_col.insert_one(record)

    return {"success": True, "data": result, "message": "Playing XI selected"}
