"""Stats router — player and season statistics from historical data."""

from fastapi import APIRouter, HTTPException

from ml import predictor

router = APIRouter()


@router.get("/players")
def all_players():
    """All MI batters with career summary."""
    return {"success": True, "data": predictor.list_all_players(), "message": "All players"}


@router.get("/players/{name}")
def one_player(name: str):
    """Full stats for a single player."""
    stats = predictor.get_player_stats(name)
    if stats is None:
        raise HTTPException(status_code=404, detail=f"No data found for '{name}'")
    return {"success": True, "data": stats, "message": "Player stats"}


@router.get("/seasons")
def seasons():
    """Season-wise MI batting summary."""
    return {"success": True, "data": predictor.season_summary(), "message": "Season summary"}
