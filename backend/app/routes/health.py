"""Health check routes (root + API-versioned)."""

from datetime import datetime, timezone

from fastapi import APIRouter

root_router = APIRouter(tags=["Health"])
api_router = APIRouter(tags=["health"])


def _health_payload() -> dict[str, str]:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@root_router.get("/health")
def health_root() -> dict[str, str]:
    """GET /health — spec root health."""
    return _health_payload()


@api_router.get("/health")
def health_under_api_prefix() -> dict[str, str]:
    """GET /api/v1/health — backward compatible."""
    return _health_payload()
