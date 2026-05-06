"""Database initialization utilities."""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


def create_sqlite_engine(database_url: str):
    engine = create_engine(database_url, connect_args={"check_same_thread": False}, future=True)

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, _record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def create_session_local(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
