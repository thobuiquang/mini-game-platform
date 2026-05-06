"""Register CORS middleware."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


def add_cors_middleware(app: FastAPI) -> None:
    """Apply CORS policy from settings.

    Per Fetch/CORS: ``Access-Control-Allow-Origin: *`` must not be combined with
    ``Access-Control-Allow-Credentials: true``. When using a wildcard origin,
    credentials are disabled; list explicit origins in ``CORS_ORIGINS`` to send
    cookies / Authorization with cross-origin requests.
    """
    wildcard = settings.cors_origins.strip() == "*"
    origins = ["*"] if wildcard else [x.strip() for x in settings.cors_origins.split(",") if x.strip()]
    allow_credentials = not wildcard
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )
