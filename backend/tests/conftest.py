"""Shared test fixtures."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.category import Category
from app.models.game import Game
from app.models.stats import GameStats

TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    action = Category(name="action", description="Action games")
    puzzle = Category(name="puzzle", description="Puzzle games")
    db.add_all([action, puzzle])
    db.flush()

    games = []
    for i in range(1, 16):
        games.append(
            Game(
                title=f"Game {i}",
                description=f"Description {i}",
                category_id=action.id if i % 2 == 0 else puzzle.id,
                thumbnail_url=f"/static/games/game{i}/thumbnail.png",
                game_path=f"game{i}",
                version="1.0.0",
                rating=float((i % 5) + 1),
                play_count=i,
            )
        )
    db.add_all(games)
    db.flush()
    db.add_all([GameStats(game_id=game.id, total_plays=game.play_count, total_time_played=100) for game in games])
    db.commit()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
