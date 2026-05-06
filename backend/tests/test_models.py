"""Unit tests for ORM models."""

import pytest

from app.models.category import Category
from app.models.game import Game


def test_game_creation() -> None:
    game = Game(title="Demo", game_path="demo", rating=4.5)
    assert game.title == "Demo"
    assert game.rating == 4.5


def test_invalid_game_rating() -> None:
    with pytest.raises(ValueError):
        Game(title="Bad", game_path="bad", rating=9)


def test_category_relationship(db_session) -> None:
    game = db_session.query(Game).first()
    assert game.category_id is not None


def test_game_timestamp(db_session) -> None:
    game = db_session.query(Game).first()
    assert game.created_at is not None
    assert game.updated_at is not None
