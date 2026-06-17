"""Session repository — data access for sessions."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from backend.src.models.orm import Session as SessionModel


class SessionRepository:
    """Repository for Session data access."""

    def __init__(self, db: Session):
        self.db = db

    def get_or_create(
        self,
        site: str,
        table_name: str,
        started_at: datetime,
    ) -> SessionModel:
        """Get an existing session or create a new one.

        Sessions are unique on (site, table_name, started_at).
        """
        # TODO: Implement upsert
        return SessionModel(
            site=site, table_name=table_name, started_at=started_at
        )

    def get_sessions(
        self,
        *,
        hero_name: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        site: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[SessionModel], int]:
        """Get paginated, filtered sessions."""
        # TODO: Implement
        return [], 0
