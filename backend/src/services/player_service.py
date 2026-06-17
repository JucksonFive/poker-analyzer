"""Player service — player statistics, profiling, and comparisons."""

from __future__ import annotations

from sqlalchemy.orm import Session


class PlayerService:
    """Service for player analysis and statistics."""

    def __init__(self, db: Session):
        self.db = db

    def get_player_stats(self, player_name: str, site: str) -> dict | None:
        """Get computed statistics for a specific player.

        Returns:
            Player stats dict, or None if player not found.
        """
        # TODO: Implement stat computation via analytics engine
        return None

    def get_player_profile(self, player_name: str, site: str) -> dict | None:
        """Get a player's full profile including stats, type, and leaks.

        Returns:
            Player profile dict, or None if not found.
        """
        # TODO: Implement
        return None

    def list_players(
        self,
        *,
        site: str | None = None,
        min_hands: int = 1,
        sort_by: str = "total_hands",
        sort_dir: str = "desc",
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list, int]:
        """List players with basic stats.

        Returns:
            Tuple of (player_summaries, total_count).
        """
        # TODO: Implement
        return [], 0

    def compare_players(
        self, player_names: list[str], site: str
    ) -> list:
        """Compare stats across multiple players.

        Args:
            player_names: List of player names to compare.
            site: The poker site these players are from.

        Returns:
            List of player stat objects.
        """
        # TODO: Implement
        return []
