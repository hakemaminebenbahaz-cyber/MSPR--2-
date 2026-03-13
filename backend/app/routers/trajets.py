from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from typing import List, Optional

from app.dependencies import get_db
from app.config import settings
from app.services.trajet_service import TrajetService
from app.schemas.trajet import TrajetDetailResponse


def verify_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")):
    if x_api_key != settings.API_KEY:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Clé API manquante ou invalide.")
    return x_api_key


router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.get("/", response_model=List[TrajetDetailResponse], summary="Liste des trajets ferroviaires")
def get_trajets(
    depart:       Optional[str] = Query(None, description="Nom partiel de la gare de départ"),
    arrivee:      Optional[str] = Query(None, description="Nom partiel de la gare d'arrivée"),
    type_service: Optional[str] = Query(None, description="Jour ou Nuit"),
    type_ligne:   Optional[str] = Query(None, description="Grande vitesse, Intercité, Train de nuit..."),
    operateur:    Optional[str] = Query(None, description="Nom partiel de l'opérateur"),
    pays_code:    Optional[str] = Query(None, description="Code pays de la gare de départ (FR, DE...)"),
    skip:         int           = Query(0,   ge=0),
    limit:        int           = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """
    Retourne la liste des trajets ferroviaires avec filtres optionnels.
    Les trajets incluent les détails de l'opérateur, la gare de départ et d'arrivée.
    """
    return TrajetService.get_all(
        db=db,
        depart=depart,
        arrivee=arrivee,
        type_service=type_service,
        type_ligne=type_ligne,
        operateur=operateur,
        pays_code=pays_code,
        skip=skip,
        limit=limit,
    )


@router.get("/{trajet_id}", response_model=TrajetDetailResponse, summary="Détail d'un trajet")
def get_trajet(trajet_id: str, db: Session = Depends(get_db)):
    """Retourne le détail complet d'un trajet par son identifiant."""
    trajet = TrajetService.get_by_id(db, trajet_id)
    if not trajet:
        raise HTTPException(status_code=404, detail=f"Trajet '{trajet_id}' introuvable")
    return trajet
