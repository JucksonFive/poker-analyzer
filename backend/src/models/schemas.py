"""Pydantic models (schemas) for API request/response validation.

These are the data transfer objects that cross the API boundary.
Domain logic uses the poker-engine types; database uses SQLAlchemy ORM models.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


# ── Enums ───────────────────────────────────────────────────────────────────


class PositionEnum(str, Enum):
    EP = "EP"
    MP = "MP"
    CO = "CO"
    BTN = "BTN"
    SB = "SB"
    BB = "BB"


class ActionTypeEnum(str, Enum):
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    ALL_IN = "all_in"


class StreetEnum(str, Enum):
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"


# ── Hand Schemas ─────────────────────────────────────────────────────────────


class CardSchema(BaseModel):
    """A single card as a 2-character string (e.g., 'Ah', 'Td')."""

    card: str = Field(..., pattern=r"^[2-9TJQKA][cdhs]$")


class ActionSchema(BaseModel):
    player: str
    action_type: ActionTypeEnum
    amount: float
    street: StreetEnum
    is_all_in: bool = False


class HandPlayerSchema(BaseModel):
    player_name: str
    position: PositionEnum
    hole_cards: list[str] = Field(default_factory=list, max_length=2)
    net_won: float = 0.0


class HandSummary(BaseModel):
    """Summary row for hand lists and tables."""

    id: int
    hand_number: str
    site: str
    table_name: str
    stake_sb: float
    stake_bb: float
    played_at: datetime
    hero_position: PositionEnum | None = None
    hero_cards: list[str] = Field(default_factory=list)
    hero_net_won: float = 0.0
    total_pot: float = 0.0
    num_players: int = 0

    model_config = {"from_attributes": True}


class HandDetail(BaseModel):
    """Full hand detail for the hand replay view."""

    id: int
    hand_number: str
    site: str
    table_name: str
    stake_sb: float
    stake_bb: float
    max_players: int
    played_at: datetime
    board: list[str] = Field(default_factory=list)
    players: list[HandPlayerSchema] = Field(default_factory=list)
    actions: list[ActionSchema] = Field(default_factory=list)
    total_pot: float = 0.0
    rake: float = 0.0
    hero_cards: list[str] = Field(default_factory=list)
    hero_net_won: float = 0.0

    model_config = {"from_attributes": True}


class HandListResponse(BaseModel):
    """Paginated list of hands."""

    hands: list[HandSummary]
    total: int
    page: int
    page_size: int


# ── Player Schemas ───────────────────────────────────────────────────────────


class PlayerStats(BaseModel):
    """Per-player computed statistics."""

    player_name: str
    site: str
    total_hands: int = 0
    vpip: float = 0.0
    pfr: float = 0.0
    three_bet: float = 0.0
    fold_to_three_bet: float = 0.0
    cbet: float = 0.0
    fold_to_cbet: float = 0.0
    aggression_factor: float = 0.0
    wtsd: float = 0.0
    wsd: float = 0.0
    bb_per_100: float = 0.0
    net_won: float = 0.0


class PlayerProfile(BaseModel):
    """A player's profile summary."""

    player_name: str
    site: str
    total_hands: int
    stats: PlayerStats
    player_type: str | None = None  # e.g., TAG, LAG, Nit, etc.
    leaks: list[str] = Field(default_factory=list)


# ── Session Schemas ──────────────────────────────────────────────────────────


class SessionSummary(BaseModel):
    """Summary of a playing session."""

    id: int
    site: str
    table_name: str
    stake_sb: float
    stake_bb: float
    started_at: datetime
    ended_at: datetime | None = None
    hands_count: int = 0
    net_result: float = 0.0
    bb_per_100: float = 0.0


# ── Analytics Schemas ────────────────────────────────────────────────────────


class DashboardSummary(BaseModel):
    """Aggregated dashboard statistics."""

    total_hands: int = 0
    total_sessions: int = 0
    net_won: float = 0.0
    bb_per_100: float = 0.0
    vpip: float = 0.0
    pfr: float = 0.0
    three_bet: float = 0.0
    win_rate: float = 0.0  # bb/100
    win_pct: float = 0.0  # % of sessions won
    period_start: datetime | None = None
    period_end: datetime | None = None


class ProfitChartPoint(BaseModel):
    """A single data point for profit/loss charts."""

    date: str
    net_won: float
    cumulative: float
    hands: int = 0


# ── Import Schemas ───────────────────────────────────────────────────────────


class ImportProgress(BaseModel):
    """SSE event data for import progress."""

    status: str  # "processing", "completed", "error"
    hands_processed: int = 0
    hands_total: int = 0
    errors: list[str] = Field(default_factory=list)
    message: str | None = None


class ImportResult(BaseModel):
    """Final result of a hand history import."""

    hands_imported: int
    hands_skipped: int
    errors: list[str]
    duration_seconds: float


# ── AI Schemas ───────────────────────────────────────────────────────────────


class AIQuery(BaseModel):
    """A natural language query for the AI assistant."""

    question: str = Field(..., min_length=1, max_length=500)


class AIResponse(BaseModel):
    """Response from the AI assistant."""

    question: str
    answer: str
    sql_used: str | None = None
    data: list[dict] | None = None
