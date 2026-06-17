"""Tests for poker_engine.cards."""

import pytest

from poker_engine.cards import Card, Deck, Rank, Suit


class TestRank:
    def test_comparison(self):
        assert Rank.ACE > Rank.KING
        assert Rank.KING > Rank.QUEEN
        assert Rank.TWO < Rank.THREE
        assert Rank.TEN > Rank.NINE

    def test_ordering_between_face_and_number(self):
        assert Rank.TEN > Rank.NINE
        assert Rank.JACK > Rank.TEN
        assert Rank.QUEEN > Rank.JACK
        assert Rank.KING > Rank.QUEEN


class TestCard:
    def test_from_str(self):
        card = Card.from_str("Ah")
        assert card.rank == Rank.ACE
        assert card.suit == Suit.HEARTS

    def test_from_str_case_insensitive(self):
        card = Card.from_str("td")
        assert card.rank == Rank.TEN
        assert card.suit == Suit.DIAMONDS

    def test_invalid_length(self):
        with pytest.raises(ValueError):
            Card.from_str("A")

    def test_str_representation(self):
        card = Card.from_str("Ah")
        assert str(card) == "Ah"

    def test_equality(self):
        assert Card.from_str("Ah") == Card.from_str("Ah")
        assert Card.from_str("Ah") != Card.from_str("As")
        assert Card.from_str("Ah") != Card.from_str("Kh")


class TestDeck:
    def test_new_deck_has_52_cards(self):
        deck = Deck()
        assert len(deck) == 52

    def test_draw_reduces_size(self):
        deck = Deck()
        card = deck.draw()
        assert len(deck) == 51
        assert isinstance(card, Card)

    def test_draw_empty_deck_raises(self):
        deck = Deck()
        for _ in range(52):
            deck.draw()
        with pytest.raises(IndexError):
            deck.draw()

    def test_draw_many(self):
        deck = Deck()
        cards = deck.draw_many(5)
        assert len(cards) == 5
        assert len(deck) == 47

    def test_seeded_deck_deterministic(self):
        d1 = Deck(seed=42)
        d2 = Deck(seed=42)
        assert d1.draw() == d2.draw()
