"""SQLAlchemy ORM models for the database schema."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from backend.src.database import Base


class Session(Base):
    """A playing session — a contiguous block of hands at a single table."""

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    site = Column(String(50), nullable=False)
    table_name = Column(String(100), nullable=False)
    stake_sb = Column(Float, nullable=False)
    stake_bb = Column(Float, nullable=False)
    game_type = Column(String(20), nullable=False, default="Holdem")
    max_players = Column(Integer, nullable=False, default=6)
    hero_name = Column(String(100), nullable=False)
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    hands_count = Column(Integer, nullable=False, default=0)
    net_result = Column(Float, nullable=False, default=0.0)

    hands = relationship("Hand", back_populates="session", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("site", "table_name", "started_at", name="uq_session"),
    )


class Player(Base):
    """A poker player, unique on (name, site)."""

    __tablename__ = "players"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    site = Column(String(50), nullable=False)
    first_seen = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_seen = Column(DateTime, nullable=False, default=datetime.utcnow)

    hand_players = relationship("HandPlayer", back_populates="player")

    __table_args__ = (
        UniqueConstraint("name", "site", name="uq_player_name_site"),
    )


class Hand(Base):
    """A single Texas Hold'em hand."""

    __tablename__ = "hands"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hand_number = Column(String(50), nullable=False)
    site = Column(String(50), nullable=False)
    table_name = Column(String(100), nullable=False)
    stake_sb = Column(Float, nullable=False)
    stake_bb = Column(Float, nullable=False)
    game_type = Column(String(20), nullable=False, default="Holdem")
    max_players = Column(Integer, nullable=False, default=6)
    played_at = Column(DateTime, nullable=False)
    board_cards = Column(String(20), nullable=True)  # Space-separated e.g. "Ah Kd 3s 8c 2h"
    total_pot = Column(Float, nullable=False, default=0.0)
    rake = Column(Float, nullable=False, default=0.0)
    hero_name = Column(String(100), nullable=False)
    hero_position = Column(String(5), nullable=True)
    hero_net_won = Column(Float, nullable=False, default=0.0)
    raw_text = Column(Text, nullable=True)
    session_id = Column(
        Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=True
    )

    session = relationship("Session", back_populates="hands")
    hand_players = relationship("HandPlayer", back_populates="hand", cascade="all, delete-orphan")
    actions = relationship("Action", back_populates="hand", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("hand_number", "site", name="uq_hand_number_site"),
    )


class HandPlayer(Base):
    """A player's participation in a specific hand."""

    __tablename__ = "hand_players"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hand_id = Column(Integer, ForeignKey("hands.id", ondelete="CASCADE"), nullable=False)
    player_id = Column(
        Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False
    )
    seat_number = Column(Integer, nullable=False)
    position = Column(String(5), nullable=False)
    starting_stack = Column(Float, nullable=False, default=0.0)
    hole_card_1 = Column(String(2), nullable=True)  # e.g. "Ah" or null if unknown
    hole_card_2 = Column(String(2), nullable=True)
    net_won = Column(Float, nullable=False, default=0.0)
    is_hero = Column(Integer, nullable=False, default=0)  # SQLite boolean

    hand = relationship("Hand", back_populates="hand_players")
    player = relationship("Player", back_populates="hand_players")

    __table_args__ = (
        UniqueConstraint("hand_id", "player_id", name="uq_hand_player"),
    )


class Action(Base):
    """A single action taken during a hand."""

    __tablename__ = "actions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hand_id = Column(Integer, ForeignKey("hands.id", ondelete="CASCADE"), nullable=False)
    player_name = Column(String(100), nullable=False)
    action_type = Column(String(10), nullable=False)  # fold, check, call, bet, raise
    amount = Column(Float, nullable=False, default=0.0)
    street = Column(String(10), nullable=False)  # preflop, flop, turn, river
    action_order = Column(Integer, nullable=False)
    is_all_in = Column(Integer, nullable=False, default=0)  # SQLite boolean

    hand = relationship("Hand", back_populates="actions")


class ImportLog(Base):
    """Log of hand history imports."""

    __tablename__ = "import_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String(255), nullable=False)
    site = Column(String(50), nullable=False)
    hands_found = Column(Integer, nullable=False, default=0)
    hands_imported = Column(Integer, nullable=False, default=0)
    hands_skipped = Column(Integer, nullable=False, default=0)
    errors = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
