"""Analytics engine — stat computation from raw hand data.

All statistics are computed on-the-fly per ADR-003. This module contains
the SQL query builders and stat definition logic.
"""

from backend.src.analytics.stats import StatCalculator

__all__ = ["StatCalculator"]
