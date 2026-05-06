"""Scan games folder and sync metadata into database."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.game import Game
from app.models.stats import GameStats

logger = logging.getLogger(__name__)


def parse_metadata(metadata_path: Path) -> dict[str, Any] | None:
    """Parse and validate a game metadata JSON file."""
    try:
        data = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    title = data.get("title")
    version = data.get("version")
    if title is None or version is None:
        return None
    title_str = title.strip() if isinstance(title, str) else str(title).strip()
    version_str = version.strip() if isinstance(version, str) else str(version).strip()
    if not title_str or not version_str:
        return None
    data["title"] = title_str
    data["version"] = version_str
    return data


def scan_games_folder(games_path: str, db: Session) -> dict[str, int]:
    """Scan game folders and upsert records."""
    root = Path(games_path)
    if not root.exists():
        return {"added": 0, "updated": 0, "deleted": 0}

    added = updated = deleted = 0
    existing_games = {game.game_path: game for game in db.execute(select(Game)).scalars().all()}
    found_paths: set[str] = set()

    for game_dir in [d for d in root.iterdir() if d.is_dir()]:
        # Track folders seen on disk before metadata validation so corrupted files
        # are skipped without being interpreted as a deleted game directory.
        found_paths.add(game_dir.name)
        metadata = parse_metadata(game_dir / "game.json")
        if not metadata:
            logger.warning("Skipping invalid metadata for %s", game_dir.name)
            continue

        category_name = metadata.get("category", "uncategorized")
        category = db.execute(select(Category).where(Category.name == category_name)).scalar_one_or_none()
        if not category:
            category = Category(name=category_name, description=f"{category_name} games")
            db.add(category)
            db.flush()

        game = existing_games.get(game_dir.name)
        if not game:
            game = Game(
                title=metadata["title"],
                description=metadata.get("description"),
                category_id=category.id,
                thumbnail_url=f"/static/games/{game_dir.name}/{metadata.get('thumbnail', 'thumbnail.png')}",
                game_path=game_dir.name,
                version=metadata["version"],
            )
            db.add(game)
            db.flush()
            if db.execute(select(GameStats).where(GameStats.game_id == game.id)).scalar_one_or_none() is None:
                db.add(GameStats(game_id=game.id))
            added += 1
            logger.info("Added game %s", metadata["title"])
        else:
            game.title = metadata["title"]
            game.description = metadata.get("description")
            game.category_id = category.id
            game.thumbnail_url = f"/static/games/{game_dir.name}/{metadata.get('thumbnail', 'thumbnail.png')}"
            game.version = metadata["version"]
            updated += 1
            logger.info("Updated game %s", metadata["title"])

    for game_path, game in existing_games.items():
        if game_path not in found_paths:
            db.delete(game)
            deleted += 1
            logger.info("Deleted game %s", game.title)

    db.commit()
    return {"added": added, "updated": updated, "deleted": deleted}


def seed_default_categories(db: Session) -> None:
    """Insert default categories when missing (optional bootstrap)."""
    defaults = [
        {"name": "action", "description": "Action-packed games", "icon": "⚔️"},
        {"name": "casual", "description": "Casual games for everyone", "icon": "🎮"},
        {"name": "puzzle", "description": "Brain teaser games", "icon": "🧩"},
        {"name": "strategy", "description": "Strategy games", "icon": "♟️"},
        {"name": "sports", "description": "Sports games", "icon": "⚽"},
    ]
    for row in defaults:
        existing = db.execute(select(Category).where(Category.name == row["name"])).scalar_one_or_none()
        if not existing:
            db.add(Category(name=row["name"], description=row["description"], icon=row["icon"]))
    db.commit()