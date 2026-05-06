"""Application configuration."""

from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseModel):
    """Runtime settings loaded from environment variables."""

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./games.db")
    api_version: str = os.getenv("API_VERSION", "v1")
    api_title: str = os.getenv("API_TITLE", "Mini Game Platform API")
    api_description: str = os.getenv("API_DESCRIPTION", "Backend API for HTML5 web game platform")
    environment: str = os.getenv("ENVIRONMENT", "development")
    static_path: str = os.getenv("STATIC_PATH", "./games")
    cors_origins: str = os.getenv("CORS_ORIGINS", "*")
    frontend_path: str | None = os.getenv("FRONTEND_PATH") or None


settings = Settings()
