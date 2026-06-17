"""Hand history API endpoints.

GET /api/hands        — list/filter hands
GET /api/hands/{id}   — single hand detail with actions
GET /api/hands/search — FTS5 search
"""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.src.database import get_db
from backend.src.models.schemas import HandDetail, HandListResponse
from backend.src.services.hand_service import HandService

router = APIRouter()


@router.get("/", response_model=HandListResponse)
async def list_hands(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    player_name: str | None = None,
    hero_name: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    stake_sb: float | None = None,
    site: str | None = None,
    sort_by: str = Query("played_at"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    """List hands with filtering and pagination."""
    service = HandService(db)
    hands, total = service.get_hands(
        page=page,
        page_size=page_size,
        player_name=player_name,
        date_from=date_from,
        date_to=date_to,
        stake_sb=stake_sb,
        site=site,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    return HandListResponse(hands=hands, total=total, page=page, page_size=page_size)


@router.get("/{hand_id}", response_model=HandDetail)
async def get_hand(hand_id: int, db: Session = Depends(get_db)):
    """Get full detail for a single hand including all actions."""
    service = HandService(db)
    hand = service.get_hand_detail(hand_id)
    if hand is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail=f"Hand {hand_id} not found")
    return hand


@router.get("/search")
async def search_hands(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Full-text search across hand histories."""
    service = HandService(db)
    results = service.search_hands(q, limit=limit)
    return {"results": results, "query": q}
