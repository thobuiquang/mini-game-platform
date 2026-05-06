"""Category API routes."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from app.database import get_db
from app.models.category import Category
from app.models.game import Game
from app.schemas.category_schema import CategoryOut

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=dict)
def list_categories(db: Session = Depends(get_db)) -> dict:
    """Return all categories with game count."""
    stmt = (
        select(Category, func.count(Game.id).label("game_count"))
        .outerjoin(Game, Game.category_id == Category.id)
        .group_by(Category.id)
        .order_by(Category.name.asc())
    )
    rows = db.execute(stmt).all()
    data = [
        CategoryOut(
            id=cat.id,
            name=cat.name,
            description=cat.description,
            icon=cat.icon,
            game_count=game_count,
        ).model_dump()
        for cat, game_count in rows
    ]
    return {"success": True, "data": data}
