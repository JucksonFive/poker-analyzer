"""Player API endpoints.

GET /api/players/               — list players
GET /api/players/{player_name}  — player profile with stats
GET /api/players/compare        — compare multiple players
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.src.database import get_db
from backend.src.models.schemas import PlayerProfile
from backend.src.services.player_service import PlayerService

router = APIRouter()


@router.get("/")
async def list_players(
    site: str | None = None,
    min_hands: int = Query(1, ge=1),
    sort_by: str = Query("total_hands"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """List players with basic statistics."""
    service = PlayerService(db)
    players, total = service.list_players(
        site=site,
        min_hands=min_hands,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        page_size=page_size,
    )
    return {"players": players, "total": total, "page": page, "page_size": page_size}


@router.get("/{player_name}")
async def get_player_profile(
    player_name: str,
    site: str = Query(..., description="Poker site name"),
    db: Session = Depends(get_db),
):
    """Get a player's full profile with statistics."""
    service = PlayerService(db)
    profile = service.get_player_profile(player_name, site)
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail=f"Player '{player_name}' not found on {site}",
        )
    return profile


@router.get("/compare")
async def compare_players(
    names: list[str] = Query(..., description="Player names to compare"),
    site: str = Query(..., description="Poker site"),
    db: Session = Depends(get_db),
):
    """Compare statistics across multiple players."""
    service = PlayerService(db)
    stats = service.compare_players(names, site)
    return {"players": stats}
