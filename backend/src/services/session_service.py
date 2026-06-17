"""Session service — playing session management and summarization."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session


class SessionService:
    """Service for browsing, filtering, and summarizing playing sessions."""

    def __init__(self, db: Session):
        self.db = db

    def get_sessions(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        site: str | None = None,
        min_hands: int | None = None,
    ) -> tuple[list, int]:
        """Get paginated list of sessions.

        Returns:
            Tuple of (session_summaries, total_count).
        """
        # TODO: Implement
        return [], 0

    def get_session_detail(self, session_id: int) -> dict | None:
        """Get session detail including all hands played.

        Returns:
            Session detail dict, or None if not found.
        """
        # TODO: Implement
        return None

    def merge_sessions(self, session_ids: list[int]) -> dict:
        """Merge multiple sessions into one (e.g., split sessions from the same table).

        Args:
            session_ids: List of session IDs to merge.

        Returns:
            The newly created merged session.
        """
        # TODO: Implement
        return {}
