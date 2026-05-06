#!/usr/bin/env python3
"""Create tables and sync games from STATIC_PATH into SQLite. Run: uv run python seed_database.py"""

from __future__ import annotations

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.utils.game_scanner import scan_games_folder, seed_default_categories


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print("Seeding default categories...")
        seed_default_categories(db)
        print("Scanning games folder...")
        result = scan_games_folder(settings.static_path, db)
        print(result)
    finally:
        db.close()


if __name__ == "__main__":
    main()
