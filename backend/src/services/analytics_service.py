"""Analytics service — on-the-fly stat computation from raw hand data.

ADR-003: Statistics are always computed on-the-fly, never pre-computed and stored.
The cache is optional and always discardable.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session


class AnalyticsService:
    """Computes all poker statistics from raw hand data.

    All stats are derived, never stored. This ensures the raw hand
    data remains the single source of truth.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_dashboard_summary(
        self,
        *,
        hero_name: str,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        stake_sb: float | None = None,
        site: str | None = None,
    ) -> dict:
        """Compute aggregated dashboard statistics.

        Returns:
            Dictionary with total_hands, net_won, bb_per_100, vpip, pfr, etc.
        """
        # TODO: Implement SQL aggregation queries
        return {
            "total_hands": 0,
            "total_sessions": 0,
            "net_won": 0.0,
            "bb_per_100": 0.0,
            "vpip": 0.0,
            "pfr": 0.0,
            "three_bet": 0.0,
            "win_rate": 0.0,
            "win_pct": 0.0,
            "period_start": None,
            "period_end": None,
        }

    def get_profit_chart(
        self,
        *,
        hero_name: str,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        interval: str = "day",  # "day", "session"
    ) -> list[dict]:
        """Get cumulative profit/loss data points for charting.

        Returns:
            List of {date, net_won, cumulative, hands} dicts.
        """
        # TODO: Implement
        return []

    def get_position_stats(
        self,
        *,
        hero_name: str,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> dict:
        """Get stats broken down by position (EP, MP, CO, BTN, SB, BB).

        Returns:
            Dict keyed by position with per-position stat objects.
        """
        # TODO: Implement
        return {}

    def compute_vpip(self, player_name: str) -> float:
        """VPIP: Voluntarily Put $ In Pot (excluding blinds).

        Percentage of hands where the player voluntarily put money in the pot
        preflop. Excludes walks (folding in the big blind unraised).
        """
        # TODO: Implement
        return 0.0

    def compute_pfr(self, player_name: str) -> float:
        """PFR: Pre-Flop Raise percentage."""
        # TODO: Implement
        return 0.0

    def compute_three_bet(self, player_name: str) -> float:
        """3Bet: Percentage of times player 3-bets when facing a raise preflop."""
        # TODO: Implement
        return 0.0

    def compute_aggression_factor(
        self, player_name: str
    ) -> float:
        """Aggression Factor: (Bets + Raises) / Calls."""
        # TODO: Implement
        return 0.0
