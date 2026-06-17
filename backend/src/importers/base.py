"""Abstract parser interface for hand history import.

Defines the canonical ParsedHand intermediate representation that all
site-specific parsers produce. This is the key to the pluggable architecture.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterator


@dataclass
class ParsedPlayer:
    """A player as seen in a hand history."""

    name: str
    seat: int
    position: str  # e.g., 'BTN', 'SB', 'BB', 'EP', 'CO'
    starting_stack: float = 0.0
    hole_card_1: str | None = None  # 2-char card code, or None if unknown
    hole_card_2: str | None = None
    net_won: float = 0.0
    is_hero: bool = False


@dataclass
class ParsedAction:
    """A single action in a hand history."""

    player: str
    action_type: str  # fold, check, call, bet, raise, all-in
    amount: float = 0.0
    street: str = "preflop"  # preflop, flop, turn, river
    is_all_in: bool = False
    order: int = 0  # Action order within the hand


@dataclass
class ParsedHand:
    """Canonical intermediate representation of a parsed hand.

    All site-specific parsers produce this structure. The import service
    uses this to create ORM objects — it never depends on site-specific
    parser output types.
    """

    hand_number: str
    site: str
    table_name: str
    stake_sb: float
    stake_bb: float
    game_type: str = "Holdem"
    max_players: int = 6
    played_at: datetime = field(default_factory=datetime.utcnow)
    board_cards: list[str] = field(default_factory=list)  # 2-char card codes
    players: list[ParsedPlayer] = field(default_factory=list)
    actions: list[ParsedAction] = field(default_factory=list)
    total_pot: float = 0.0
    rake: float = 0.0
    hero_name: str | None = None
    raw_text: str = ""


class AbstractParser(ABC):
    """Base class for all hand history parsers.

    To add a new site format:
    1. Subclass AbstractParser
    2. Implement all abstract methods
    3. Register in registry.py
    """

    @property
    @abstractmethod
    def site_name(self) -> str:
        """The human-readable site name (e.g., 'PokerStars', 'GGPoker')."""
        ...

    @abstractmethod
    def detect_format(self, raw_text: str) -> bool:
        """Check if the given text matches this parser's format.

        Used for auto-detection when the user doesn't specify the site.

        Returns:
            True if the text appears to be this site's format.
        """
        ...

    @abstractmethod
    def parse_hand(self, raw_text: str) -> ParsedHand:
        """Parse a single hand from raw text.

        Args:
            raw_text: The raw text of exactly one hand.

        Returns:
            A ParsedHand intermediate representation.

        Raises:
            ParseError: If the hand cannot be parsed.
        """
        ...

    @abstractmethod
    def parse_file(self, file_path: Path) -> Iterator[ParsedHand]:
        """Parse all hands from a hand history file.

        Args:
            file_path: Path to the hand history file.

        Yields:
            ParsedHand objects, one per hand in the file.
        """
        ...


class ParseError(Exception):
    """Raised when a hand history cannot be parsed."""

    pass
