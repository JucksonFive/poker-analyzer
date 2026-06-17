"""Range representation and combinatorics for Texas Hold'em.

Uses a 13×13 matrix (169 combos) representation. Supports parsing standard
range notation (e.g., "AKs, QQ+") and combo counting.
"""

from __future__ import annotations

from enum import Enum

from poker_engine.cards import Card, Rank


class ComboType(Enum):
    """Type of a hand combo: suited, offsuit, or pocket pair."""

    SUITED = "s"
    OFFSUIT = "o"
    PAIR = "p"


class Combo:
    """A single hand combo (e.g., AKs, T9o, QQ)."""

    def __init__(self, high_rank: Rank, low_rank: Rank, combo_type: ComboType):
        self.high_rank = high_rank
        self.low_rank = low_rank
        self.combo_type = combo_type

    @property
    def num_combos(self) -> int:
        """Number of actual card combinations for this combo type."""
        if self.combo_type == ComboType.PAIR:
            return 6  # C(4,2)
        elif self.combo_type == ComboType.SUITED:
            return 4  # 4 suits
        else:
            return 12  # 4×3 offsuit

    def __str__(self) -> str:
        high = self.high_rank.value
        low = self.low_rank.value
        if self.combo_type == ComboType.PAIR:
            return f"{high}{high}"
        return f"{high}{low}{self.combo_type.value}"

    def __repr__(self) -> str:
        return f"Combo({self})"


class Range:
    """A collection of hand combos representing a player's range."""

    def __init__(self, combos: list[Combo] | None = None):
        self.combos: set[Combo] = set(combos) if combos else set()

    @property
    def total_combos(self) -> int:
        """Total number of actual card combinations in this range."""
        return sum(c.num_combos for c in self.combos)

    def add_combo(self, combo: Combo) -> None:
        """Add a combo to the range."""
        self.combos.add(combo)

    def remove_combo(self, combo: Combo) -> None:
        """Remove a combo from the range."""
        self.combos.discard(combo)

    def __contains__(self, hole_cards: list[Card]) -> bool:
        """Check if specific hole cards fall within this range."""
        if len(hole_cards) != 2:
            return False
        c1, c2 = hole_cards
        high = max(c1.rank, c2.rank)
        low = min(c1.rank, c2.rank)
        if c1.rank == c2.rank:
            return Combo(high, low, ComboType.PAIR) in self.combos
        elif c1.suit == c2.suit:
            return Combo(high, low, ComboType.SUITED) in self.combos
        else:
            return Combo(high, low, ComboType.OFFSUIT) in self.combos

    def __len__(self) -> int:
        return len(self.combos)

    def __str__(self) -> str:
        return f"Range({self.total_combos} combos)"


def parse_range(range_str: str) -> Range:
    """Parse standard range notation into a Range object.

    Examples: "AKs", "QQ+", "AKs, AKo, QQ+".

    Args:
        range_str: Comma-separated range notation.

    Returns:
        Range object containing the parsed combos.
    """
    rng = Range()
    # TODO: Implement full range parsing (pairs+, suited+, etc.)
    # For now, this is a placeholder that handles simple cases
    parts = [p.strip() for p in range_str.split(",")]
    for part in parts:
        combo = _parse_single_combo(part)
        if combo:
            rng.add_combo(combo)
    return rng


def _parse_single_combo(combo_str: str) -> Combo | None:
    """Parse a single combo notation. Returns None if unparseable."""
    if len(combo_str) < 2:
        return None

    try:
        r1 = Rank(combo_str[0].upper())
        r2 = Rank(combo_str[1].upper())
    except ValueError:
        return None

    # Pocket pair: QQ
    if r1 == r2:
        return Combo(r1, r2, ComboType.PAIR)

    # Suited/offsuit: AKs, T9o
    if len(combo_str) == 3:
        suffix = combo_str[2].lower()
        if suffix == "s":
            high, low = (r1, r2) if r1 > r2 else (r2, r1)
            return Combo(high, low, ComboType.SUITED)
        elif suffix == "o":
            high, low = (r1, r2) if r1 > r2 else (r2, r1)
            return Combo(high, low, ComboType.OFFSUIT)

    return None
