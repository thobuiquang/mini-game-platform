"""ORM models for games and scores."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)


class Score(Base):
    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    game_name: Mapped[str] = mapped_column(ForeignKey("games.name", ondelete="CASCADE"), nullable=False, index=True)
    player_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    level: Mapped[int | None] = mapped_column(Integer)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)
