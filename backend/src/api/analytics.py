"""Analytics API endpoints.

GET /api/analytics/summary         — dashboard stats
GET /api/analytics/profit-chart    — cumulative profit data
GET /api/analytics/position-stats  — position-based breakdown
"""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.src.database import get_db
from backend.src.models.schemas import DashboardSummary, ProfitChartPoint
from backend.src.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    hero_name: str = Query(..., description="Hero player name"),
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    stake_sb: float | None = None,
    site: str | None = None,
    db: Session = Depends(get_db),
):
    """Get aggregated dashboard statistics."""
    service = AnalyticsService(db)
    stats = service.get_dashboard_summary(
        hero_name=hero_name,
        date_from=date_from,
        date_to=date_to,
        stake_sb=stake_sb,
        site=site,
    )
    return DashboardSummary(**stats)


@router.get("/profit-chart")
async def get_profit_chart(
    hero_name: str = Query(...),
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    interval: str = Query("day", pattern="^(day|session)$"),
    db: Session = Depends(get_db),
):
    """Get cumulative profit/loss data points for charting."""
    service = AnalyticsService(db)
    data = service.get_profit_chart(
        hero_name=hero_name,
        date_from=date_from,
        date_to=date_to,
        interval=interval,
    )
    return {"data": data, "interval": interval}


@router.get("/position-stats")
async def get_position_stats(
    hero_name: str = Query(...),
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    db: Session = Depends(get_db),
):
    """Get stats broken down by table position."""
    service = AnalyticsService(db)
    stats = service.get_position_stats(
        hero_name=hero_name,
        date_from=date_from,
        date_to=date_to,
    )
    return {"positions": stats}
