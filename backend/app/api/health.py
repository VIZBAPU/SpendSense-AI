import httpx
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.config import settings
from app.db.session import engine

router = APIRouter(tags=["Health"])


def check_db() -> bool:
    """Return True if Postgres answers a trivial query, False otherwise."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def check_ollama() -> bool:
    """Return True if Ollama answers a trivial query, False otherwise."""
    try:
        response = httpx.get(f"{settings.ollama_base_url}/api/tags", timeout=2.0)
        return response.status_code == 200
    except httpx.HTTPError:
        return False


@router.get("/health")
def health_check() -> JSONResponse:
    db_up = check_db()
    ollama_up = check_ollama()

    if not db_up:
        status, code = "down", 503
    elif not ollama_up:
        status, code = "degraded", 200
    else:
        status, code = "ok", 200

    return JSONResponse(
        status_code=code,
        content={
            "status": status,
            "db": "up" if db_up else "down",
            "ollama": "up" if ollama_up else "down",
            "model": settings.ollama_model,
        },
    )
