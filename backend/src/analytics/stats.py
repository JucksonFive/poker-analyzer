"""Stat definitions and SQL query builders.

Every stat is defined with:
- Name: Poker-standard abbreviation (VPIP, PFR, etc.)
- Query: The SQL that computes it from raw hand/action data
- Verification: Invariants that must hold (e.g., VPIP >= PFR always)
"""

from __future__ import annotations


class StatCalculator:
    """Computes poker statistics from raw data using SQL aggregation.

    All stats are derived, never stored (ADR-003). The calculator builds
    parameterized SQL queries and executes them via the repository layer.
    """

    # Stat definitions with their SQL templates
    STAT_DEFS = {
        "vpip": {
            "name": "VPIP",
            "description": "Voluntarily Put $ In Pot (excluding blinds)",
            "invariant": "vpip >= pfr",  # VPIP must always be >= PFR
        },
        "pfr": {
            "name": "PFR",
            "description": "Pre-Flop Raise percentage",
        },
        "three_bet": {
            "name": "3Bet",
            "description": "Percentage of hands player 3-bets preflop",
        },
        "fold_to_three_bet": {
            "name": "Fold to 3Bet",
            "description": "Percentage of times player folds when facing a 3-bet",
        },
        "cbet": {
            "name": "CBet",
            "description": "Continuation bet percentage (flop)",
        },
        "fold_to_cbet": {
            "name": "Fold to CBet",
            "description": "Percentage of times player folds to a continuation bet",
        },
        "aggression_factor": {
            "name": "AF",
            "description": "Aggression Factor = (Bets + Raises) / Calls",
        },
        "wtsd": {
            "name": "WTSD",
            "description": "Went to Showdown percentage",
        },
        "wsd": {
            "name": "W$SD",
            "description": "Won $ at Showdown percentage",
        },
        "bb_per_100": {
            "name": "bb/100",
            "description": "Big blinds won per 100 hands",
        },
    }

    def compute_all_stats(self, player_name: str) -> dict[str, float]:
        """Compute all defined stats for a player.

        Args:
            player_name: The player to compute stats for.

        Returns:
            Dict mapping stat keys to computed values.
        """
        # TODO: Implement SQL query execution for each stat
        return {key: 0.0 for key in self.STAT_DEFS}

    def verify_invariants(self, stats: dict[str, float]) -> list[str]:
        """Check that computed stats satisfy poker invariants.

        Returns:
            List of invariant violation descriptions (empty = all good).
        """
        violations = []
        if stats.get("vpip", 0) < stats.get("pfr", 0):
            violations.append("VPIP < PFR — this is impossible")
        # Add more invariants as needed
        return violations
