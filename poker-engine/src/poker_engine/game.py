"""Game state, actions, positions, and rules for Texas Hold'em.

Models the structure of a hand: positions (6-max/9-max), streets, actions,
and the overall game state machine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import NamedTuple

from poker_engine.cards import Card


class Street(Enum):
    """Texas Hold'em betting streets. Integer value represents the street index."""

    PREFLOP = 0
    FLOP = 1
    TURN = 2
    RIVER = 3
    SHOWDOWN = 4


class Position(Enum):
    """Position at a 6-max Texas Hold'em table.

    Also supports 9-max via the additional positions (UTG, UTG+1, LJ, HJ).
    """

    # 6-max positions
    EP = "EP"  # Early Position (UTG in 6-max)
    MP = "MP"  # Middle Position (HJ in 6-max)
    CO = "CO"  # Cutoff
    BTN = "BTN"  # Button
    SB = "SB"  # Small Blind
    BB = "BB"  # Big Blind

    # 9-max additional positions
    UTG = "UTG"  # Under the Gun (9-max)
    UTG1 = "UTG+1"
    LJ = "LJ"  # Lowjack
    HJ = "HJ"  # Hijack

    @classmethod
    def for_seat(cls, seat: int, max_players: int) -> Position:
        """Map a seat number to position for the given table size.

        For 6-max, seat 0 = SB, seat 1 = BB, seat 2 = EP, seat 3 = MP,
        seat 4 = CO, seat 5 = BTN.

        Args:
            seat: 0-indexed seat number.
            max_players: Number of players at the table (6 or 9).

        Returns:
            The Position for that seat.
        """
        if max_players == 6:
            mapping = [
                cls.SB,   # seat 0
                cls.BB,   # seat 1
                cls.EP,   # seat 2
                cls.MP,   # seat 3
                cls.CO,   # seat 4
                cls.BTN,  # seat 5
            ]
        else:
            # 9-max
            mapping = [
                cls.SB,
                cls.BB,
                cls.UTG,
                cls.UTG1,
                cls.LJ,
                cls.HJ,
                cls.CO,
                cls.BTN,
                cls.MP,  # seat 8 (not typically used, placeholder)
            ]
        return mapping[seat] if seat < len(mapping) else cls.MP


class ActionType(Enum):
    """Type of poker action."""

    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    ALL_IN = "all_in"


class Action(NamedTuple):
    """An immutable poker action.

    Attributes:
        player: Player name who made the action.
        action_type: The type of action (fold, check, call, bet, raise).
        amount: The amount of chips — 0 for fold/check, the call amount, bet size, etc.
        street: The street this action occurred on.
        is_all_in: Whether this action put the player all-in.
    """

    player: str
    action_type: ActionType
    amount: float
    street: Street
    is_all_in: bool = False


@dataclass
class GameState:
    """The complete state of a Texas Hold'em hand.

    Tracks the hand from deal through showdown, including all actions,
    board cards, pot size, and player states.
    """

    hand_number: str
    max_players: int = 6
    sb_amount: float = 0.0
    bb_amount: float = 0.0

    # Board cards by street
    flop: list[Card] = field(default_factory=list)
    turn: list[Card] = field(default_factory=list)
    river: list[Card] = field(default_factory=list)

    # Player states
    player_stacks: dict[str, float] = field(default_factory=dict)
    hole_cards: dict[str, list[Card]] = field(default_factory=dict)

    # Action history
    actions: list[Action] = field(default_factory=list)
    current_street: Street = Street.PREFLOP

    # Pot
    pot: float = 0.0
    current_bet: float = 0.0
    last_aggressor: str | None = None

    @property
    def board_cards(self) -> list[Card]:
        """All community cards dealt so far."""
        cards: list[Card] = []
        cards.extend(self.flop)
        cards.extend(self.turn)
        cards.extend(self.river)
        return cards

    @property
    def active_players(self) -> list[str]:
        """Players who haven't folded."""
        folded = {
            a.player
            for a in self.actions
            if a.action_type == ActionType.FOLD
        }
        return [p for p in self.player_stacks if p not in folded]

    @property
    def current_street_actions(self) -> list[Action]:
        """Actions on the current street only."""
        return [a for a in self.actions if a.street == self.current_street]
