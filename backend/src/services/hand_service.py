"""Hand service — hand history browsing, filtering, and replay."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session


class HandService:
    """Service for retrieving and filtering hand histories."""

    def __init__(self, db: Session):
        self.db = db

    def get_hands(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        player_name: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        stake_sb: float | None = None,
        site: str | None = None,
        sort_by: str = "played_at",
        sort_dir: str = "desc",
    ) -> tuple[list, int]:
        """Get paginated list of hands with optional filters.

        Returns:
            Tuple of (hand_summaries, total_count).
        """
        # TODO: Implement repository-based query with filters
        return [], 0

    def get_hand_detail(self, hand_id: int) -> dict | None:
        """Get full detail for a single hand, including all actions.

        Returns:
            Hand detail dict, or None if not found.
        """
        # TODO: Implement
        return None

    def search_hands(self, query: str, limit: int = 50) -> list:
        """Full-text search on hand histories.

        Uses FTS5 for fast text search across hand data.

        Args:
            query: Search query string.
            limit: Maximum number of results.

        Returns:
            List of matching hand summaries.
        """
        # TODO: Implement FTS5 search
        return []
