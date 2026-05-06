"""FastAPI entrypoint."""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.database import Base, engine
from app.middleware.cors import add_cors_middleware
from app.routes.categories import router as categories_router
from app.routes.games import router as games_router
from app.routes.health import api_router as health_api_router, root_router as health_root_router
from app.routes.search import router as search_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
)

add_cors_middleware(app)

api_prefix = f"/api/{settings.api_version}"

app.include_router(health_root_router)
app.include_router(health_api_router, prefix=api_prefix)
app.include_router(search_router, prefix=api_prefix)
app.include_router(games_router, prefix=api_prefix)
app.include_router(categories_router, prefix=api_prefix)

static_root = Path(settings.static_path).resolve()
static_root.mkdir(parents=True, exist_ok=True)
app.mount("/static/games", StaticFiles(directory=str(static_root), html=True), name="games-static")


def _frontend_dir() -> Path:
    """Resolve folder containing static frontend (index.html, style.css)."""
    if settings.frontend_path:
        return Path(settings.frontend_path).resolve()
    return Path(__file__).resolve().parent.parent.parent / "frontend"


frontend_dir = _frontend_dir()
if frontend_dir.is_dir():
    app.mount("/ui", StaticFiles(directory=str(frontend_dir), html=True), name="frontend-static")


@app.get("/", response_model=None)
def root() -> RedirectResponse | dict:
    """Send users to the UI when bundled with repo frontend."""
    if frontend_dir.is_dir():
        return RedirectResponse(url="/ui/")
    return {"detail": "Frontend folder not found", "docs": "/docs", "api": api_prefix, "health": "/health"}


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Convert framework HTTP errors to unified schema."""
    return JSONResponse(status_code=exc.status_code, content={"success": False, "error": str(exc.detail)})


@app.exception_handler(Exception)
async def generic_exception_handler(_request: Request, _exc: Exception) -> JSONResponse:
    """Return generic 500 response without leaking details."""
    return JSONResponse(status_code=500, content={"success": False, "error": "Internal server error"})
