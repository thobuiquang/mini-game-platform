"""Game API routes (list, detail, play — search lives in routes/search.py)."""

from datetime import datetime, timezone
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.category import Category
from app.models.game import Game
from app.models.stats import GameStats
from app.schemas.game_schema import GameDetailOut, GameListItem, PlayUpdateIn

router = APIRouter(prefix="/games", tags=["games"])


def _build_sort_clause(sort_by: str):
    mapping = {
        "date": desc(Game.created_at),
        "rating": desc(Game.rating),
        "name": asc(Game.title),
        "plays": desc(Game.play_count),
    }
    return mapping.get(sort_by, desc(Game.created_at))


@router.get("", response_model=dict)
def list_games(
    page: int = Query(default=1, gt=0),
    per_page: int = Query(default=12, gt=0, le=50),
    category: str | None = Query(default=None),
    sort_by: str = Query(default="date", pattern="^(name|rating|date|plays)$"),
    db: Session = Depends(get_db),
) -> dict:
    """List games with pagination, filtering, and sorting."""
    base_stmt = select(Game, Category.name.label("category_name")).outerjoin(Category, Game.category_id == Category.id)
    if category:
        base_stmt = base_stmt.where(func.lower(Category.name) == category.lower())

    total = db.execute(select(func.count()).select_from(base_stmt.subquery())).scalar_one()
    offset = (page - 1) * per_page
    rows = db.execute(base_stmt.order_by(_build_sort_clause(sort_by)).offset(offset).limit(per_page)).all()

    data = [
        GameListItem(
            id=game.id,
            title=game.title,
            description=game.description,
            category=category_name,
            category_id=game.category_id,
            thumbnail_url=game.thumbnail_url,
            game_path=game.game_path,
            rating=game.rating,
            play_count=game.play_count,
            version=game.version,
            created_at=game.created_at,
        ).model_dump()
        for game, category_name in rows
    ]
    return {
        "success": True,
        "data": data,
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": ceil(total / per_page) if total else 0,
        },
    }


@router.get("/{game_id}", response_model=dict)
def get_game_detail(game_id: int, db: Session = Depends(get_db)) -> dict:
    """Fetch detailed game data (read-only; play counts use POST /play)."""
    row = db.execute(
        select(Game, Category.name.label("category_name"), GameStats)
        .outerjoin(Category, Game.category_id == Category.id)
        .outerjoin(GameStats, GameStats.game_id == Game.id)
        .where(Game.id == game_id)
    ).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")

    game, category_name, stats = row

    payload = GameDetailOut(
        id=game.id,
        title=game.title,
        description=game.description,
        category=category_name,
        category_id=game.category_id,
        thumbnail_url=game.thumbnail_url,
        game_path=game.game_path,
        rating=game.rating,
        play_count=game.play_count,
        version=game.version,
        created_at=game.created_at,
        game_url=f"/static/games/{game.game_path}/index.html",
        release_date=game.release_date,
        updated_at=game.updated_at,
        stats={
            "total_plays": stats.total_plays if stats else 0,
            "total_time_played": stats.total_time_played if stats else 0,
            "average_rating": stats.average_rating if stats else 0.0,
            "last_played": stats.last_played if stats else None,
        },
    ).model_dump()
    return {"success": True, "data": payload}


@router.post("/{game_id}/play", response_model=dict)
def update_play_count(game_id: int, body: PlayUpdateIn, db: Session = Depends(get_db)) -> dict:
    """Update play counters for a game."""
    game = db.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")

    stats = db.execute(select(GameStats).where(GameStats.game_id == game.id)).scalar_one_or_none()
    if not stats:
        stats = GameStats(game_id=game.id)
        db.add(stats)

    game.play_count += 1
    stats.total_plays += 1
    stats.total_time_played += body.session_time
    stats.last_played = datetime.now(timezone.utc)
    db.commit()
    db.refresh(game)
    return {"success": True, "message": "Play count updated", "new_play_count": game.play_count}
