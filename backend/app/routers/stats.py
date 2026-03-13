from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.dependencies import get_db
from app.config import settings
from app.services.trajet_service import TrajetService
from app.schemas.trajet import StatsVolumesResponse


def verify_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Clé API manquante ou invalide.")
    return x_api_key


router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.get("/volumes", response_model=StatsVolumesResponse, summary="Volumes globaux")
def get_volumes(db: Session = Depends(get_db)):
    """Retourne les volumes globaux : nombre total de trajets, répartition jour/nuit, opérateurs et gares."""
    return TrajetService.get_volumes(db)


@router.get("/jour-vs-nuit", summary="Comparaison Jour vs Nuit")
def get_jour_vs_nuit(db: Session = Depends(get_db)):
    """Compare les trains de jour et de nuit : nombre, CO₂ moyen, durée moyenne."""
    return TrajetService.get_jour_vs_nuit(db)


@router.get("/par-operateur", summary="Statistiques par opérateur")
def get_par_operateur(db: Session = Depends(get_db)):
    """Répartition Jour/Nuit par opérateur ferroviaire, trié par volume décroissant."""
    return TrajetService.get_par_operateur(db)


@router.get("/par-pays", summary="Statistiques par pays")
def get_par_pays(db: Session = Depends(get_db)):
    """Nombre de gares et de trajets par pays."""
    return TrajetService.get_par_pays(db)
