from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import time


# ───────────────────────────────────────────
# OPERATEURS
# ───────────────────────────────────────────

class OperateurResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:        int
    nom:       str
    pays_code: str


# ───────────────────────────────────────────
# GARES
# ───────────────────────────────────────────

class GareResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:        int
    nom:       str
    ville:     Optional[str] = None
    pays_code: str
    latitude:  Optional[float] = None
    longitude: Optional[float] = None


# ───────────────────────────────────────────
# TRAJETS
# ───────────────────────────────────────────

class TrajetDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:                str
    nom_ligne:         str
    type_ligne:        Optional[str] = None
    type_service:      str
    heure_depart:      Optional[time] = None
    heure_arrivee:     Optional[time] = None
    distance_km:       Optional[int] = None
    duree_h:           Optional[float] = None
    emissions_co2_gkm: Optional[float] = None
    frequence_hebdo:   Optional[int] = None
    traction:          Optional[str] = None
    source_donnee:     Optional[str] = None
    operateur:         Optional[OperateurResponse] = None
    gare_depart:       Optional[GareResponse] = None
    gare_arrivee:      Optional[GareResponse] = None


# ───────────────────────────────────────────
# STATS
# ───────────────────────────────────────────

class StatsVolumesResponse(BaseModel):
    total_trajets:    int
    total_jour:       int
    total_nuit:       int
    total_operateurs: int
    total_gares:      int


class StatsServiceResponse(BaseModel):
    type_service:    str
    total:           int
    co2_moyen:       Optional[float] = None
    duree_moyenne_h: Optional[float] = None


class StatsOperateurResponse(BaseModel):
    operateur:       str
    pays_code:       str
    total_dessertes: int
    nb_jour:         int
    nb_nuit:         int


class StatsPayResponse(BaseModel):
    pays_code:       str
    total_gares:     int
    total_dessertes: int
