"""Game API schemas."""

from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator


class PaginationParams(BaseModel):
    """Reusable pagination query params."""

    page: int = Field(default=1, gt=0)
    per_page: int = Field(default=12, gt=0, le=50)


class GameBase(BaseModel):
    """Shared game fields."""

    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    category: str | None = None
    thumbnail_url: str | None = None
    game_path: str
    version: str | None = None
    release_date: date | None = None
    rating: float = Field(default=0.0)

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, value: float) -> float:
        if value < 0 or value > 5:
            raise ValueError("rating must be between 0 and 5")
        return value


class GameCreate(GameBase):
    """Create game payload."""


class GameUpdate(BaseModel):
    """Update game payload."""

    description: str | None = None
    thumbnail_url: str | None = None
    version: str | None = None
    rating: float | None = None

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, value: float | None) -> float | None:
        if value is not None and (value < 0 or value > 5):
            raise ValueError("rating must be between 0 and 5")
        return value


class GameListItem(BaseModel):
    """Compact game item for listing/search."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None = None
    category: str | None = None
    category_id: int | None = None
    thumbnail_url: str | None = None
    game_path: str
    rating: float
    play_count: int
    version: str | None = None
    created_at: datetime


class GameStatsOut(BaseModel):
    """Embedded game stats response schema."""

    total_plays: int = 0
    total_time_played: int = 0
    average_rating: float = 0.0
    last_played: datetime | None = None


class GameDetailOut(GameListItem):
    """Detailed game response schema."""

    game_url: str
    release_date: date | None = None
    updated_at: datetime
    stats: GameStatsOut | None = None


class PlayUpdateIn(BaseModel):
    """Play counter update payload."""

    session_time: int = Field(default=0, ge=0)


class PaginationOut(BaseModel):
    """Pagination metadata."""

    total: int
    page: int
    per_page: int
    total_pages: int


class SuccessResponse(BaseModel):
    """Basic success response."""

    success: bool = True
    message: str


class ErrorResponse(BaseModel):
    """Unified error response."""

    success: bool = False
    error: str


# Aliases aligned with PROMPT_AGENT_BACKEND_GAME_WITH_UV.md naming
GameListResponse = GameListItem
GameDetailResponse = GameDetailOut
PlayCountUpdateRequest = PlayUpdateIn
