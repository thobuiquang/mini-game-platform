"""Unit tests for utilities (scanner, helpers)."""

import json
import shutil
from pathlib import Path

import pytest
from sqlalchemy import select

from app.models.category import Category
from app.models.game import Game
from app.models.stats import GameStats
from app.utils.game_scanner import parse_metadata, scan_games_folder
from app.utils.helpers import game_play_url
from app.utils.validators import clamp_int


def test_game_scanner_parse_metadata(tmp_path: Path) -> None:
    metadata_file = tmp_path / "game.json"
    metadata_file.write_text(json.dumps({"title": "X", "version": "1.0.0"}), encoding="utf-8")
    parsed = parse_metadata(metadata_file)
    assert parsed is not None
    assert parsed["title"] == "X"


def test_game_scanner_parse_metadata_numeric_version_zero(tmp_path: Path) -> None:
    metadata_file = tmp_path / "game.json"
    metadata_file.write_text(json.dumps({"title": "X", "version": 0}), encoding="utf-8")
    parsed = parse_metadata(metadata_file)
    assert parsed is not None
    assert parsed["version"] == "0"


def test_game_scanner_parse_metadata_empty_title_rejected(tmp_path: Path) -> None:
    metadata_file = tmp_path / "game.json"
    metadata_file.write_text(json.dumps({"title": "", "version": "1.0.0"}), encoding="utf-8")
    assert parse_metadata(metadata_file) is None


def test_game_scanner_parse_metadata_whitespace_only_title_rejected(tmp_path: Path) -> None:
    metadata_file = tmp_path / "game.json"
    metadata_file.write_text(json.dumps({"title": "   ", "version": "1.0.0"}), encoding="utf-8")
    assert parse_metadata(metadata_file) is None


def test_game_scanner_parse_metadata_empty_version_rejected(tmp_path: Path) -> None:
    metadata_file = tmp_path / "game.json"
    metadata_file.write_text(json.dumps({"title": "OK", "version": ""}), encoding="utf-8")
    assert parse_metadata(metadata_file) is None


def test_game_scanner_invalid_json(tmp_path: Path) -> None:
    metadata_file = tmp_path / "game.json"
    metadata_file.write_text("{bad json}", encoding="utf-8")
    assert parse_metadata(metadata_file) is None


def test_clamp_int() -> None:
    assert clamp_int(5, 1, 10) == 5
    assert clamp_int(0, 1, 10) == 1
    assert clamp_int(99, 1, 10) == 10


def test_game_play_url() -> None:
    assert game_play_url("game1") == "/static/games/game1/index.html"


def test_search_query_builder() -> None:
    q = "mario"
    pattern = f"%{q}%"
    assert pattern == "%mario%"


def test_scan_games_folder_missing_path(db_session) -> None:
    result = scan_games_folder("this-folder-does-not-exist", db_session)
    assert result == {"added": 0, "updated": 0, "deleted": 0}


def test_scan_games_folder_add_update_delete(tmp_path: Path, db_session) -> None:
    db_session.query(GameStats).delete()
    db_session.query(Game).delete()
    db_session.query(Category).delete()
    db_session.commit()

    game_dir = tmp_path / "new-game"
    game_dir.mkdir(parents=True)
    (game_dir / "game.json").write_text(
        json.dumps(
            {
                "title": "New Game",
                "description": "fresh",
                "category": "action",
                "thumbnail": "thumb.png",
                "version": "1.0.0",
            }
        ),
        encoding="utf-8",
    )

    first = scan_games_folder(str(tmp_path), db_session)
    assert first["added"] == 1

    (game_dir / "game.json").write_text(
        json.dumps(
            {
                "title": "New Game",
                "description": "updated",
                "category": "puzzle",
                "thumbnail": "cover.jpg",
                "version": "1.0.1",
            }
        ),
        encoding="utf-8",
    )
    second = scan_games_folder(str(tmp_path), db_session)
    assert second["updated"] >= 1
    row = db_session.execute(select(Game).where(Game.game_path == "new-game")).scalar_one()
    assert row.title == "New Game"
    assert row.thumbnail_url == "/static/games/new-game/cover.jpg"

    (game_dir / "game.json").write_text(
        json.dumps(
            {
                "title": "Renamed Game",
                "description": "updated",
                "category": "puzzle",
                "thumbnail": "cover.jpg",
                "version": "1.0.2",
            }
        ),
        encoding="utf-8",
    )
    renamed = scan_games_folder(str(tmp_path), db_session)
    assert renamed["updated"] >= 1
    row = db_session.execute(select(Game).where(Game.game_path == "new-game")).scalar_one()
    assert row.title == "Renamed Game"

    shutil.rmtree(game_dir)
    third = scan_games_folder(str(tmp_path), db_session)
    assert third["deleted"] >= 1


def test_scan_games_folder_invalid_metadata_skipped(tmp_path: Path, db_session) -> None:
    bad = tmp_path / "bad-game"
    bad.mkdir(parents=True)
    (bad / "game.json").write_text("{bad}", encoding="utf-8")
    result = scan_games_folder(str(tmp_path), db_session)
    assert result["added"] == 0


def test_scan_games_folder_invalid_metadata_does_not_delete_existing_game(tmp_path: Path, db_session) -> None:
    db_session.query(GameStats).delete()
    db_session.query(Game).delete()
    db_session.query(Category).delete()
    db_session.commit()

    game_dir = tmp_path / "persist-game"
    game_dir.mkdir(parents=True)
    metadata_path = game_dir / "game.json"
    metadata_path.write_text(
        json.dumps(
            {
                "title": "Persist Game",
                "description": "stable",
                "category": "action",
                "thumbnail": "thumb.png",
                "version": "1.0.0",
            }
        ),
        encoding="utf-8",
    )

    first = scan_games_folder(str(tmp_path), db_session)
    assert first["added"] == 1

    # Corrupt metadata should skip updates, not delete the existing game record.
    metadata_path.write_text("{bad json}", encoding="utf-8")
    second = scan_games_folder(str(tmp_path), db_session)
    assert second["deleted"] == 0
    game = db_session.execute(select(Game).where(Game.game_path == "persist-game")).scalar_one_or_none()
    stats = db_session.execute(select(GameStats).where(GameStats.game_id == game.id)).scalar_one_or_none() if game else None
    assert game is not None
    assert stats is not None


def test_scan_games_folder_creates_category(tmp_path: Path, db_session) -> None:
    game_dir = tmp_path / "cat-game"
    game_dir.mkdir(parents=True)
    (game_dir / "game.json").write_text(
        json.dumps({"title": "Cat Game", "version": "1.0.0", "category": "arcade"}),
        encoding="utf-8",
    )
    scan_games_folder(str(tmp_path), db_session)
    category = db_session.execute(select(Category).where(Category.name == "arcade")).scalar_one_or_none()
    assert category is not None
