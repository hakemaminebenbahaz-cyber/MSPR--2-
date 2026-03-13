from fastapi import APIRouter
from app.database import test_connection
from app.config import settings
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """
    Vérifie l'état de l'API et de la connexion à la base de données.
    Endpoint public — aucune clé API requise.
    """
    db_status = "healthy" if test_connection() else "unreachable"
    return HealthResponse(
        status="healthy" if db_status == "healthy" else "degraded",
        service="ObRail API",
        version=settings.VERSION,
        database=db_status,
    )
