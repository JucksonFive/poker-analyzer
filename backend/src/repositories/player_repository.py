"""Player repository — data access for players."""

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.src.models.orm import Player


class PlayerRepository:
    """Repository for Player data access."""

    def __init__(self, db: Session):
        self.db = db

    def get_or_create(self, name: str, site: str) -> Player:
        """Get an existing player or create a new one.

        Players are unique on (name, site).
        """
        # TODO: Implement upsert
        return Player(name=name, site=site)

    def get_by_name(self, name: str, site: str) -> Player | None:
        """Find a player by name and site."""
        # TODO: Implement
        return None

    def list_players(
        self,
        *,
        site: str | None = None,
        min_hands: int = 1,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Player], int]:
        """List players with filtering."""
        # TODO: Implement
        return [], 0
