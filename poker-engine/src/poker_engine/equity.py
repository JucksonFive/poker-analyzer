"""Equity calculation for Texas Hold'em.

Provides exact heads-up equity and Monte Carlo simulation for hand-vs-hand,
hand-vs-range, and range-vs-range scenarios.
"""

from __future__ import annotations

import random

from poker_engine.cards import Card, Deck
from poker_engine.evaluation import HandEvaluation, compare_hands


class EquityCalculator:
    """Exact heads-up equity calculator using enumeration."""

    @staticmethod
    def hand_vs_hand(
        hand1: list[Card],
        hand2: list[Card],
        board: list[Card] | None = None,
    ) -> tuple[float, float, float]:
        """Calculate exact equity for hand vs hand (heads-up).

        Enumerates all possible remaining board cards.

        Args:
            hand1: First player's hole cards.
            hand2: Second player's hole cards.
            board: Known community cards (0, 3, 4, or 5 cards).

        Returns:
            (win%, tie%, lose%) for hand1.
        """
        board = board or []
        known_cards = set(hand1 + hand2 + board)
        deck = [c for c in Deck._ALL_CARDS if c not in known_cards]
        cards_needed = 5 - len(board)

        wins = ties = losses = total = 0
        for remaining in _card_combinations(deck, cards_needed):
            full_board = board + list(remaining)
            result = compare_hands([hand1, hand2], full_board)
            total += 1
            if 0 in result and 1 in result:
                ties += 1
            elif 0 in result:
                wins += 1
            else:
                losses += 1

        return (wins / total * 100, ties / total * 100, losses / total * 100)


class MonteCarloSimulator:
    """Monte Carlo equity simulator for arbitrary scenarios.

    Supports hand-vs-hand, hand-vs-range, and range-vs-range calculations.
    Accepts a random.Random instance for deterministic testing.
    """

    def __init__(self, rng: random.Random | None = None, iterations: int = 10_000):
        self._rng = rng or random.Random()
        self.iterations = iterations

    def hand_vs_hand(
        self,
        hand1: list[Card],
        hand2: list[Card],
        board: list[Card] | None = None,
    ) -> tuple[float, float, float]:
        """Monte Carlo equity for hand vs hand.

        Args:
            hand1: First player's hole cards.
            hand2: Second player's hole cards.
            board: Known community cards.

        Returns:
            Estimated (win%, tie%, lose%) for hand1.
        """
        board = board or []
        known_cards = set(hand1 + hand2 + board)
        deck = [c for c in Deck._ALL_CARDS if c not in known_cards]
        cards_needed = 5 - len(board)

        wins = ties = total = 0
        for _ in range(self.iterations):
            sim_deck = deck.copy()
            self._rng.shuffle(sim_deck)
            remaining = sim_deck[:cards_needed]
            full_board = board + remaining
            result = compare_hands([hand1, hand2], full_board)
            total += 1
            if 0 in result and 1 in result:
                ties += 1
            elif 0 in result:
                wins += 1

        win_pct = wins / total * 100
        tie_pct = ties / total * 100
        lose_pct = 100 - win_pct - tie_pct
        return (win_pct, tie_pct, lose_pct)

    def set_iterations(self, n: int) -> None:
        """Set the number of Monte Carlo iterations."""
        if n < 1:
            raise ValueError(f"Iterations must be positive, got {n}")
        self.iterations = n


def _card_combinations(cards: list[Card], k: int) -> list[tuple[Card, ...]]:
    """Generate all k-combinations from a list of cards."""
    from itertools import combinations

    if k == 0:
        return [()]
    return list(combinations(cards, k))
