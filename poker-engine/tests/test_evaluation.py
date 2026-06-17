"""Tests for poker_engine.evaluation."""

from poker_engine.cards import Card
from poker_engine.evaluation import HandRank, compare_hands, evaluate


class TestEvaluate:
    def test_royal_flush(self):
        hole = [Card.from_str("Ah"), Card.from_str("Kh")]
        board = [
            Card.from_str("Qh"),
            Card.from_str("Jh"),
            Card.from_str("Th"),
            Card.from_str("2d"),
            Card.from_str("3c"),
        ]
        result = evaluate(hole, board)
        assert result.rank == HandRank.ROYAL_FLUSH

    def test_straight_flush(self):
        hole = [Card.from_str("9h"), Card.from_str("8h")]
        board = [
            Card.from_str("7h"),
            Card.from_str("6h"),
            Card.from_str("5h"),
            Card.from_str("2d"),
            Card.from_str("3c"),
        ]
        result = evaluate(hole, board)
        assert result.rank == HandRank.STRAIGHT_FLUSH

    def test_wheel_straight(self):
        """A-2-3-4-5 should be recognized as a straight (wheel)."""
        hole = [Card.from_str("Ah"), Card.from_str("2c")]
        board = [
            Card.from_str("3d"),
            Card.from_str("4h"),
            Card.from_str("5s"),
            Card.from_str("9c"),
            Card.from_str("Kd"),
        ]
        result = evaluate(hole, board)
        assert result.rank == HandRank.STRAIGHT

    def test_four_of_a_kind(self):
        hole = [Card.from_str("Ac"), Card.from_str("Ad")]
        board = [
            Card.from_str("Ah"),
            Card.from_str("As"),
            Card.from_str("5h"),
            Card.from_str("2d"),
            Card.from_str("3c"),
        ]
        result = evaluate(hole, board)
        assert result.rank == HandRank.FOUR_OF_A_KIND

    def test_full_house(self):
        hole = [Card.from_str("Ac"), Card.from_str("Ad")]
        board = [
            Card.from_str("Ah"),
            Card.from_str("Ks"),
            Card.from_str("Kd"),
            Card.from_str("2d"),
            Card.from_str("3c"),
        ]
        result = evaluate(hole, board)
        assert result.rank == HandRank.FULL_HOUSE

    def test_flush(self):
        hole = [Card.from_str("Ah"), Card.from_str("2h")]
        board = [
            Card.from_str("Qh"),
            Card.from_str("Jh"),
            Card.from_str("7h"),
            Card.from_str("2d"),
            Card.from_str("3c"),
        ]
        result = evaluate(hole, board)
        assert result.rank == HandRank.FLUSH

    def test_straight(self):
        hole = [Card.from_str("9c"), Card.from_str("8d")]
        board = [
            Card.from_str("7h"),
            Card.from_str("6s"),
            Card.from_str("5c"),
            Card.from_str("2d"),
            Card.from_str("Kc"),
        ]
        result = evaluate(hole, board)
        assert result.rank == HandRank.STRAIGHT

    def test_high_card(self):
        hole = [Card.from_str("Ah"), Card.from_str("2c")]
        board = [
            Card.from_str("Kd"),
            Card.from_str("Jc"),
            Card.from_str("9h"),
            Card.from_str("7s"),
            Card.from_str("5d"),
        ]
        result = evaluate(hole, board)
        assert result.rank == HandRank.HIGH_CARD

    def test_needs_at_least_5_cards(self):
        import pytest

        hole = [Card.from_str("Ah"), Card.from_str("Kh")]
        board = [Card.from_str("Qh"), Card.from_str("Jh")]
        with pytest.raises(ValueError):
            evaluate(hole, board)


class TestCompareHands:
    def test_ace_high_beats_king_high(self):
        hand1 = [Card.from_str("Ah"), Card.from_str("2c")]
        hand2 = [Card.from_str("Kh"), Card.from_str("Qc")]
        board = [
            Card.from_str("9d"),
            Card.from_str("7h"),
            Card.from_str("5s"),
            Card.from_str("4c"),
            Card.from_str("3d"),
        ]
        winners = compare_hands([hand1, hand2], board)
        assert winners == [0]

    def test_split_pot(self):
        """Two hands with identical value should split."""
        hand1 = [Card.from_str("Ah"), Card.from_str("Kh")]
        hand2 = [Card.from_str("As"), Card.from_str("Ks")]
        board = [
            Card.from_str("Qd"),
            Card.from_str("Jh"),
            Card.from_str("Ts"),
            Card.from_str("2c"),
            Card.from_str("3d"),
        ]
        winners = compare_hands([hand1, hand2], board)
        assert sorted(winners) == [0, 1]
