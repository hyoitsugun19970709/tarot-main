import pytest
from . import rider_weite

def test_deck_initialization():
    """Test that a new deck is properly initialized"""
    deck = rider_weite._RIDER_WEITE_DECK()
    assert len(deck._deck_full) == 78
    assert len(deck._deck_major) == 22
    assert len(deck._deck_minor) == 56
    assert len(deck._deck_drawn) == 0


def test_draw_cards_basic():
    """Test basic card drawing functionality"""
    deck = rider_weite._RIDER_WEITE_DECK()
    cards = deck.draw_cards(num=3, arcana="full")
    assert len(cards) == 3
    assert all(isinstance(card, rider_weite._RIDER_WEITE_CARD) for card in cards)


def test_multiple_draws_are_continuous():
    """Test that multiple draws from the same deck instance are continuous"""
    deck = rider_weite._RIDER_WEITE_DECK()
    cards_first_draw = deck.draw_cards(num=5, arcana="full", pop=True)
    initial_remaining = len(deck._deck_full)
    
    cards_second_draw = deck.draw_cards(num=3, arcana="full", pop=True)
    assert len(cards_second_draw) == 3
    assert len(deck._deck_full) == initial_remaining - 3


def test_drawn_cards_not_in_pool():
    """Test that drawn cards do not appear again in the remaining card pool"""
    deck = rider_weite._RIDER_WEITE_DECK()
    cards_first = deck.draw_cards(num=10, arcana="full", pop=True)
    
    cards_second = deck.draw_cards(num=10, arcana="full", pop=True)
    second_draw_indices = [card.index for card in cards_second]
    drawn_indices = deck._deck_drawn
    
    for idx in drawn_indices:
        assert idx not in deck._deck_full
        assert idx not in deck._deck_major
        assert idx not in deck._deck_minor


def test_separate_deck_instances():
    """Test that different deck instances are independent"""
    deck1 = rider_weite._RIDER_WEITE_DECK()
    deck2 = rider_weite._RIDER_WEITE_DECK()
    
    cards1 = deck1.draw_cards(num=5, arcana="full", pop=True)
    assert len(deck1._deck_full) == 73
    assert len(deck2._deck_full) == 78
    
    cards2 = deck2.draw_cards(num=5, arcana="full", pop=True)
    assert len(deck1._deck_drawn) == 5
    assert len(deck2._deck_drawn) == 5


def test_deck_reset():
    """Test that deck reset works properly"""
    deck = rider_weite._RIDER_WEITE_DECK()
    deck.draw_cards(num=20, arcana="full", pop=True)
    assert len(deck._deck_drawn) == 20
    
    deck.reset_deck()
    assert len(deck._deck_full) == 78
    assert len(deck._deck_drawn) == 0


def test_draw_more_than_available_raises_error():
    """Test that drawing more cards than available raises ValueError"""
    deck = rider_weite._RIDER_WEITE_DECK()
    with pytest.raises(ValueError, match="Not enough card to draw"):
        deck.draw_cards(num=100, arcana="full")


def test_draw_without_pop():
    """Test that drawing without popping does not remove cards from deck"""
    deck = rider_weite._RIDER_WEITE_DECK()
    initial_count_full = len(deck._deck_full)
    initial_count_major = len(deck._deck_major)
    initial_count_minor = len(deck._deck_minor)
    deck.draw_cards(num=5, arcana="full", pop=False)
    assert len(deck._deck_full) == initial_count_full
    assert len(deck._deck_major) == initial_count_major
    assert len(deck._deck_minor) == initial_count_minor
    assert len(deck._deck_drawn) == 5