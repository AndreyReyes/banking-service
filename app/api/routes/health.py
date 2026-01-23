from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.db.session import check_db_health, get_engine


router = APIRouter(prefix="/v1", tags=["health"])


@router.get("/health")
def health_check() -> dict:
    engine = get_engine()
    if not check_db_health(engine):
        raise HTTPException(status_code=503, detail="database unhealthy")

    return {
        "status": "ok",
        "database": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
