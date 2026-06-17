"""Card, Deck, Rank, and Suit types for Texas Hold'em.

Cards are immutable, comparable, and represented as 2-character strings:
rank (2-9, T, J, Q, K, A) + suit (c, d, h, s). Examples: Ah, Td, 2c, Ks.
"""

from __future__ import annotations

from enum import Enum
from typing import NamedTuple


class Rank(Enum):
    """Card rank from deuce to ace."""

    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "T"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"

    def __lt__(self, other: Rank) -> bool:
        return _RANK_ORDER[self] < _RANK_ORDER[other]

    def __le__(self, other: Rank) -> bool:
        return _RANK_ORDER[self] <= _RANK_ORDER[other]

    def __gt__(self, other: Rank) -> bool:
        return _RANK_ORDER[self] > _RANK_ORDER[other]

    def __ge__(self, other: Rank) -> bool:
        return _RANK_ORDER[self] >= _RANK_ORDER[other]


_RANK_ORDER = {
    Rank.TWO: 2,
    Rank.THREE: 3,
    Rank.FOUR: 4,
    Rank.FIVE: 5,
    Rank.SIX: 6,
    Rank.SEVEN: 7,
    Rank.EIGHT: 8,
    Rank.NINE: 9,
    Rank.TEN: 10,
    Rank.JACK: 11,
    Rank.QUEEN: 12,
    Rank.KING: 13,
    Rank.ACE: 14,
}


class Suit(Enum):
    """Card suit."""

    CLUBS = "c"
    DIAMONDS = "d"
    HEARTS = "h"
    SPADES = "s"


class Card(NamedTuple):
    """An immutable playing card.

    Represented as rank + suit. Examples: Ah (Ace of hearts), Td (Ten of diamonds).
    """

    rank: Rank
    suit: Suit

    @classmethod
    def from_str(cls, s: str) -> Card:
        """Parse a 2-character card string. e.g., 'Ah' -> Card(Rank.ACE, Suit.HEARTS)."""
        if len(s) != 2:
            raise ValueError(f"Card string must be exactly 2 characters, got: {s!r}")
        rank_char, suit_char = s[0].upper(), s[1].lower()
        rank = Rank(rank_char)
        suit = Suit(suit_char)
        return cls(rank, suit)

    def __str__(self) -> str:
        return f"{self.rank.value}{self.suit.value}"

    def __repr__(self) -> str:
        return f"Card({self.rank.name}, {self.suit.name})"


class Deck:
    """A standard 52-card deck."""

    _ALL_CARDS: tuple[Card, ...] = tuple(
        Card(rank, suit) for rank in Rank for suit in Suit
    )

    def __init__(self, seed: int | None = None) -> None:
        import random

        self.cards: list[Card] = list(self._ALL_CARDS)
        self._rng = random.Random(seed)
        self._rng.shuffle(self.cards)

    def draw(self) -> Card:
        """Draw one card from the top of the deck."""
        if not self.cards:
            raise IndexError("Cannot draw from an empty deck")
        return self.cards.pop()

    def draw_many(self, n: int) -> list[Card]:
        """Draw n cards from the top of the deck."""
        if n > len(self.cards):
            raise IndexError(
                f"Cannot draw {n} cards from a deck with only {len(self.cards)} cards"
            )
        drawn = self.cards[:n]
        self.cards = self.cards[n:]
        return drawn

    def __len__(self) -> int:
        return len(self.cards)

    def __bool__(self) -> bool:
        return len(self.cards) > 0
