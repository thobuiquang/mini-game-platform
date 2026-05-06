"""Search games API (separate module per project layout)."""

from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import String, asc, cast, func, or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.category import Category
from app.models.game import Game
from app.schemas.game_schema import GameListItem

router = APIRouter(prefix="/games", tags=["search"])


def _escape_like(term: str) -> str:
    """Escape SQL LIKE wildcards so user input is treated literally."""
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


@router.get("/search", response_model=dict)
def search_games(
    q: str = Query(max_length=100),
    page: int = Query(default=1, gt=0),
    per_page: int = Query(default=20, gt=0, le=50),
    db: Session = Depends(get_db),
) -> dict:
    """Search games by title, description, or category name."""
    query = q.strip()
    if len(query) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query must be at least 2 characters after trimming spaces",
        )

    escaped_query = _escape_like(query.lower())
    pattern = f"%{escaped_query}%"
    base_stmt = (
        select(Game, Category.name.label("category_name"))
        .outerjoin(Category, Game.category_id == Category.id)
        .where(
            or_(
                func.lower(Game.title).like(pattern, escape="\\"),
                func.lower(cast(Game.description, String)).like(pattern, escape="\\"),
                func.lower(cast(Category.name, String)).like(pattern, escape="\\"),
            )
        )
    )
    total = db.execute(select(func.count()).select_from(base_stmt.subquery())).scalar_one()
    per_page = min(per_page, 50)
    offset = (page - 1) * per_page
    rows = db.execute(base_stmt.order_by(asc(Game.title)).offset(offset).limit(per_page)).all()

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
