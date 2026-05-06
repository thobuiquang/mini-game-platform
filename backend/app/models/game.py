"""Game ORM model."""

from datetime import date, datetime
from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.models.base import Base, utc_now


class Game(Base):
    """Main game entity."""

    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), index=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(255))
    game_path: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    version: Mapped[str | None] = mapped_column(String(50))
    release_date: Mapped[date | None] = mapped_column(Date)
    play_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)
    rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now, nullable=False
    )

    category = relationship("Category", back_populates="games")
    stats = relationship("GameStats", uselist=False, back_populates="game", cascade="all, delete-orphan")

    @validates("rating")
    def validate_rating(self, _key: str, value: float) -> float:
        """Constrain rating in [0, 5]."""
        if value < 0 or value > 5:
            raise ValueError("Rating must be between 0 and 5")
        return value
