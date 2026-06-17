"""Poker Engine — Pure Python Texas Hold'em library.

Zero external dependencies. Provides cards, hand evaluation, equity calculation,
range combinatorics, and game state modeling.

Exports:
    Card, Rank, Suit, Deck
    HandRank, HandEvaluation, evaluate, compare_hands
    EquityCalculator, MonteCarloSimulator
    Range, Combo, parse_range
    Action, Street, Position, GameState
"""

from poker_engine.cards import Card, Deck, Rank, Suit
from poker_engine.evaluation import HandEvaluation, HandRank, compare_hands, evaluate
from poker_engine.equity import EquityCalculator, MonteCarloSimulator
from poker_engine.game import Action, GameState, Position, Street
from poker_engine.ranges import Combo, Range, parse_range

__all__ = [
    # cards
    "Card",
    "Rank",
    "Suit",
    "Deck",
    # evaluation
    "HandRank",
    "HandEvaluation",
    "evaluate",
    "compare_hands",
    # equity
    "EquityCalculator",
    "MonteCarloSimulator",
    # ranges
    "Range",
    "Combo",
    "parse_range",
    # game
    "Action",
    "Street",
    "Position",
    "GameState",
]
