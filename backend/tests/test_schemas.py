"""Unit tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.category_schema import CategoryCreate
from app.schemas.game_schema import GameCreate


def test_schema_rating_validation() -> None:
    with pytest.raises(ValidationError):
        GameCreate(title="T", game_path="t", rating=6)


def test_schema_required_title() -> None:
    with pytest.raises(ValidationError):
        GameCreate(title="", game_path="x")


def test_category_create_valid() -> None:
    cat = CategoryCreate(name="action", description="Action games", icon="⚔️")
    assert cat.name == "action"


def test_category_create_empty_name() -> None:
    with pytest.raises(ValidationError):
        CategoryCreate(name="", description="Action")
