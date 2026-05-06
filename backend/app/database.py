"""Database engine and session helpers."""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.models.base import Base

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
pool_kw: dict = {}
if "sqlite" in settings.database_url:
    pool_kw["poolclass"] = StaticPool

engine = create_engine(settings.database_url, connect_args=connect_args, future=True, **pool_kw)


def _set_sqlite_pragma(dbapi_conn, _connection_record) -> None:
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


if settings.database_url.startswith("sqlite"):
    event.listen(engine, "connect", _set_sqlite_pragma)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db():
    """Yield a request-scoped database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
