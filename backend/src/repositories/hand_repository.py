"""Hand repository — data access for hands, actions, and hand_players."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from backend.src.models.orm import Action, Hand, HandPlayer


class HandRepository:
    """Repository for Hand, Action, and HandPlayer data access."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, hand_id: int) -> Hand | None:
        """Get a hand by its primary key."""
        # TODO: Implement
        return None

    def get_by_hand_number(self, hand_number: str, site: str) -> Hand | None:
        """Find a hand by its (hand_number, site) unique key. Used for dedup."""
        # TODO: Implement
        return None

    def get_hand_actions(self, hand_id: int) -> list[Action]:
        """Get all actions for a hand, ordered by action_order."""
        # TODO: Implement
        return []

    def get_hand_players(self, hand_id: int) -> list[HandPlayer]:
        """Get all players in a hand."""
        # TODO: Implement
        return []

    def get_hands(
        self,
        *,
        hero_name: str | None = None,
        player_name: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        site: str | None = None,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "played_at",
        sort_dir: str = "desc",
    ) -> tuple[list[Hand], int]:
        """Get paginated, filtered hands."""
        # TODO: Implement
        return [], 0

    def insert_hand(
        self,
        hand: Hand,
        hand_players: list[HandPlayer],
        actions: list[Action],
    ) -> Hand:
        """Insert a hand with its players and actions in a single transaction."""
        # TODO: Implement
        return hand

    def get_total_hand_count(self) -> int:
        """Get total number of hands in the database."""
        # TODO: Implement
        return 0
