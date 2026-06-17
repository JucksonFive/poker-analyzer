"""Session API endpoints.

GET /api/sessions/          — list sessions
GET /api/sessions/{id}      — session detail with hands
POST /api/sessions/merge   — merge multiple sessions
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.src.database import get_db
from backend.src.services.session_service import SessionService

router = APIRouter()


@router.get("/")
async def list_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    site: str | None = None,
    min_hands: int | None = None,
    db: Session = Depends(get_db),
):
    """List playing sessions with filtering."""
    service = SessionService(db)
    sessions, total = service.get_sessions(
        page=page,
        page_size=page_size,
        date_from=date_from,
        date_to=date_to,
        site=site,
        min_hands=min_hands,
    )
    return {"sessions": sessions, "total": total, "page": page, "page_size": page_size}


@router.get("/{session_id}")
async def get_session(session_id: int, db: Session = Depends(get_db)):
    """Get session detail including all hands played."""
    service = SessionService(db)
    session = service.get_session_detail(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return session


@router.post("/merge")
async def merge_sessions(
    session_ids: list[int],
    db: Session = Depends(get_db),
):
    """Merge multiple sessions into one."""
    if len(session_ids) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 session IDs required to merge",
        )
    service = SessionService(db)
    return service.merge_sessions(session_ids)
