"""SQLAlchemy ORM models for characters, parties, and game sessions."""

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Float,
    DateTime,
    ForeignKey,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship

from models.database import Base


class Party(Base):
    """A party of adventurers."""

    __tablename__ = "parties"

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name: str = Column(String(128), nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    characters = relationship("Character", back_populates="party", lazy="selectin")
    sessions = relationship("GameSession", back_populates="party", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Party(id={self.id}, name='{self.name}')>"


class Character(Base):
    """A player character following AD&D 1st Edition rules."""

    __tablename__ = "characters"

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name: str = Column(String(128), nullable=False)
    race: str = Column(String(32), nullable=False)
    class_name: str = Column(String(64), nullable=False)
    level: int = Column(Integer, default=1, nullable=False)
    alignment: str = Column(String(32), nullable=False)

    # Ability scores
    str: int = Column(Integer, nullable=False)
    int: int = Column(Integer, nullable=False)
    wis: int = Column(Integer, nullable=False)
    dex: int = Column(Integer, nullable=False)
    con: int = Column(Integer, nullable=False)
    cha: int = Column(Integer, nullable=False)

    # Derived / combat stats
    hp: int = Column(Integer, nullable=False)
    max_hp: int = Column(Integer, nullable=False)
    ac: int = Column(Integer, default=10, nullable=False)
    xp: int = Column(Integer, default=0, nullable=False)
    gold: float = Column(Float, default=0.0, nullable=False)

    # Metadata
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Foreign keys
    party_id: int | None = Column(Integer, ForeignKey("parties.id"), nullable=True)

    # Relationships
    party = relationship("Party", back_populates="characters")

    def __repr__(self) -> str:
        return (
            f"<Character(id={self.id}, name='{self.name}', "
            f"race='{self.race}', class='{self.class_name}', level={self.level})>"
        )


class GameSession(Base):
    """A saved game session containing dungeon and map state."""

    __tablename__ = "game_sessions"

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name: str = Column(String(128), nullable=False)
    party_id: int | None = Column(Integer, ForeignKey("parties.id"), nullable=True)

    dungeon_state: dict | None = Column(JSON, nullable=True)
    map_state: dict | None = Column(JSON, nullable=True)

    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: datetime = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    auto_save: bool = Column(Boolean, default=True, nullable=False)

    # Relationships
    party = relationship("Party", back_populates="sessions")

    def __repr__(self) -> str:
        return f"<GameSession(id={self.id}, name='{self.name}')>"
