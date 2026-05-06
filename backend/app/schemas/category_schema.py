"""Category API schemas."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import TimestampedSchema


class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=10)


class CategoryCreate(CategoryBase):
    """Payload to create a category (admin flows)."""


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=10)


class CategoryOut(BaseModel):
    """Category response for list API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    icon: str | None = None
    game_count: int = 0


class CategoryResponse(CategoryBase, TimestampedSchema):
    """Extended category + timestamps (prompt naming)."""

    id: int
    game_count: int = 0

    model_config = ConfigDict(from_attributes=True)
