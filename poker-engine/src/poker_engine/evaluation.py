"""Hand evaluation for Texas Hold'em.

Evaluates the best 5-card hand from any combination of hole cards and community cards.
Supports comparison of multiple hands to determine the winner(s).
"""

from __future__ import annotations

from enum import IntEnum
from typing import NamedTuple

from poker_engine.cards import Card, Rank


class HandRank(IntEnum):
    """Poker hand rank from lowest to highest value."""

    HIGH_CARD = 0
    ONE_PAIR = 1
    TWO_PAIR = 2
    THREE_OF_A_KIND = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    FOUR_OF_A_KIND = 7
    STRAIGHT_FLUSH = 8
    ROYAL_FLUSH = 9


class HandEvaluation(NamedTuple):
    """Result of evaluating a hand.

    Attributes:
        rank: The HandRank (e.g., FLUSH).
        kickers: Tie-breaking card ranks, ordered from most to least significant.
        cards_used: The 5 cards that form the best hand.
        description: Human-readable description (e.g., "Flush, Ace high").
    """

    rank: HandRank
    kickers: tuple[int, ...]
    cards_used: tuple[Card, ...]
    description: str


def evaluate(hole_cards: list[Card], community_cards: list[Card]) -> HandEvaluation:
    """Evaluate the best 5-card hand from hole + community cards.

    For Texas Hold'em: 2 hole cards + 3-5 community cards = 5-7 total cards.
    Returns the best possible HandEvaluation.

    Args:
        hole_cards: 2 private cards.
        community_cards: 3-5 community cards (flop, turn, river).

    Returns:
        HandEvaluation describing the best 5-card hand.
    """
    all_cards = list(hole_cards) + list(community_cards)
    if len(all_cards) < 5:
        raise ValueError(f"Need at least 5 cards to evaluate, got {len(all_cards)}")
    if len(all_cards) > 7:
        raise ValueError(f"At most 7 cards, got {len(all_cards)}")

    # Select all combinations of 5 cards and find the best
    best: HandEvaluation | None = None
    for combo in _combinations(all_cards, 5):
        evaluation = _evaluate_5_cards(combo)
        if best is None or evaluation.rank > best.rank or (
            evaluation.rank == best.rank and evaluation.kickers > best.kickers
        ):
            best = evaluation

    assert best is not None
    return best


def compare_hands(hands: list[list[Card]], community_cards: list[Card]) -> list[int]:
    """Compare multiple hands against the same board. Returns winner indices.

    Args:
        hands: List of hole card pairs.
        community_cards: The community cards (board).

    Returns:
        List of indices of the winning hand(s). Multiple indices indicate a split pot.
    """
    evaluations = [evaluate(h, community_cards) for h in hands]
    best_idx = 0
    winners = [0]
    for i in range(1, len(evaluations)):
        ev = evaluations[i]
        best_ev = evaluations[best_idx]
        if ev.rank > best_ev.rank or (
            ev.rank == best_ev.rank and ev.kickers > best_ev.kickers
        ):
            best_idx = i
            winners = [i]
        elif ev.rank == best_ev.rank and ev.kickers == best_ev.kickers:
            winners.append(i)
    return winners


def _evaluate_5_cards(cards: tuple[Card, ...]) -> HandEvaluation:
    """Evaluate exactly 5 cards and return their HandEvaluation."""
    ranks = [c.rank for c in cards]
    suits = [c.suit for c in cards]
    rank_values = sorted([_RANK_VALUES[r] for r in ranks], reverse=True)
    is_flush = len(set(suits)) == 1

    # Check for straight
    unique_sorted = sorted(set(rank_values), reverse=True)
    is_straight = False
    straight_high = 0
    if len(unique_sorted) == 5:
        if unique_sorted[0] - unique_sorted[4] == 4:
            is_straight = True
            straight_high = unique_sorted[0]
        # Wheel: A-2-3-4-5
        elif unique_sorted == [14, 5, 4, 3, 2]:
            is_straight = True
            straight_high = 5  # 5-high straight

    # Count rank frequencies
    rank_counts: dict[int, int] = {}
    for rv in rank_values:
        rank_counts[rv] = rank_counts.get(rv, 0) + 1
    counts = sorted(rank_counts.items(), key=lambda x: (x[1], x[0]), reverse=True)

    # Determine hand rank and kickers
    if is_flush and is_straight:
        if straight_high == 14:
            return HandEvaluation(
                HandRank.ROYAL_FLUSH,
                (14,),
                cards,
                "Royal Flush",
            )
        return HandEvaluation(
            HandRank.STRAIGHT_FLUSH,
            (straight_high,),
            cards,
            f"Straight Flush, {_rank_name(straight_high)} high",
        )

    if counts[0][1] == 4:
        quads = counts[0][0]
        kicker = counts[1][0]
        return HandEvaluation(
            HandRank.FOUR_OF_A_KIND,
            (quads, kicker),
            cards,
            f"Four of a Kind, {_rank_name(quads)}s",
        )

    if counts[0][1] == 3 and counts[1][1] == 2:
        trips = counts[0][0]
        pair = counts[1][0]
        return HandEvaluation(
            HandRank.FULL_HOUSE,
            (trips, pair),
            cards,
            f"Full House, {_rank_name(trips)}s full of {_rank_name(pair)}s",
        )

    if is_flush:
        return HandEvaluation(
            HandRank.FLUSH,
            tuple(rank_values),
            cards,
            f"Flush, {_rank_name(rank_values[0])} high",
        )

    if is_straight:
        return HandEvaluation(
            HandRank.STRAIGHT,
            (straight_high,),
            cards,
            f"Straight, {_rank_name(straight_high)} high",
        )

    if counts[0][1] == 3:
        trips = counts[0][0]
        kickers = tuple(c[0] for c in counts[1:])
        return HandEvaluation(
            HandRank.THREE_OF_A_KIND,
            (trips,) + kickers,
            cards,
            f"Three of a Kind, {_rank_name(trips)}s",
        )

    if counts[0][1] == 2 and counts[1][1] == 2:
        high_pair = max(counts[0][0], counts[1][0])
        low_pair = min(counts[0][0], counts[1][0])
        kicker = counts[2][0]
        return HandEvaluation(
            HandRank.TWO_PAIR,
            (high_pair, low_pair, kicker),
            cards,
            f"Two Pair, {_rank_name(high_pair)}s and {_rank_name(low_pair)}s",
        )

    if counts[0][1] == 2:
        pair = counts[0][0]
        kickers = tuple(c[0] for c in counts[1:])
        return HandEvaluation(
            HandRank.ONE_PAIR,
            (pair,) + kickers,
            cards,
            f"One Pair, {_rank_name(pair)}s",
        )

    return HandEvaluation(
        HandRank.HIGH_CARD,
        tuple(rank_values),
        cards,
        f"High Card, {_rank_name(rank_values[0])}",
    )


def _combinations(items: list[Card], k: int) -> list[tuple[Card, ...]]:
    """Generate all k-combinations from items."""
    from itertools import combinations

    return list(combinations(items, k))


_RANK_VALUES: dict[Rank, int] = {
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


def _rank_name(value: int) -> str:
    """Convert a rank value to its name string."""
    names = {
        2: "Two", 3: "Three", 4: "Four", 5: "Five",
        6: "Six", 7: "Seven", 8: "Eight", 9: "Nine",
        10: "Ten", 11: "Jack", 12: "Queen", 13: "King", 14: "Ace",
    }
    return names.get(value, str(value))
