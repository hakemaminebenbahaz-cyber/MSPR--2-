from sqlalchemy.orm import Session, joinedload, aliased
from sqlalchemy import func
from typing import Optional, List

from app.models.trajet import Desserte, Gare, Operateur


class TrajetService:
    """Service centralisant toute la logique métier liée aux trajets."""

    @staticmethod
    def get_all(
        db: Session,
        depart: Optional[str] = None,
        arrivee: Optional[str] = None,
        type_service: Optional[str] = None,
        type_ligne: Optional[str] = None,
        operateur: Optional[str] = None,
        pays_code: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Desserte]:
        GareDep = aliased(Gare, name="gare_dep")
        GareArr = aliased(Gare, name="gare_arr")

        query = (
            db.query(Desserte)
            .options(
                joinedload(Desserte.operateur),
                joinedload(Desserte.gare_depart),
                joinedload(Desserte.gare_arrivee),
            )
            .join(GareDep, Desserte.gare_depart_id == GareDep.id)
            .join(GareArr, Desserte.gare_arrivee_id == GareArr.id)
        )

        if depart:
            query = query.filter(GareDep.nom.ilike(f"%{depart}%"))
        if arrivee:
            query = query.filter(GareArr.nom.ilike(f"%{arrivee}%"))
        if type_service:
            query = query.filter(Desserte.type_service == type_service)
        if type_ligne:
            query = query.filter(Desserte.type_ligne.ilike(f"%{type_ligne}%"))
        if operateur:
            query = query.join(Desserte.operateur).filter(Operateur.nom.ilike(f"%{operateur}%"))
        if pays_code:
            query = query.filter(GareDep.pays_code == pays_code.upper())

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, trajet_id: str) -> Optional[Desserte]:
        return (
            db.query(Desserte)
            .options(
                joinedload(Desserte.operateur),
                joinedload(Desserte.gare_depart),
                joinedload(Desserte.gare_arrivee),
            )
            .filter(Desserte.id == trajet_id)
            .first()
        )

    @staticmethod
    def get_volumes(db: Session) -> dict:
        return {
            "total_trajets":    db.query(func.count(Desserte.id)).scalar(),
            "total_jour":       db.query(func.count(Desserte.id)).filter(Desserte.type_service == "Jour").scalar(),
            "total_nuit":       db.query(func.count(Desserte.id)).filter(Desserte.type_service == "Nuit").scalar(),
            "total_operateurs": db.query(func.count(Operateur.id)).scalar(),
            "total_gares":      db.query(func.count(Gare.id)).scalar(),
        }

    @staticmethod
    def get_jour_vs_nuit(db: Session) -> list:
        rows = (
            db.query(
                Desserte.type_service,
                func.count(Desserte.id).label("total"),
                func.avg(Desserte.emissions_co2_gkm).label("co2_moyen"),
                func.avg(Desserte.duree_h).label("duree_moyenne_h"),
            )
            .group_by(Desserte.type_service)
            .all()
        )
        return [
            {
                "type_service":    r.type_service,
                "total":           r.total,
                "co2_moyen":       round(float(r.co2_moyen), 2) if r.co2_moyen else None,
                "duree_moyenne_h": round(float(r.duree_moyenne_h), 2) if r.duree_moyenne_h else None,
            }
            for r in rows
        ]

    @staticmethod
    def get_par_operateur(db: Session) -> list:
        result = []
        for op in db.query(Operateur).all():
            total = db.query(func.count(Desserte.id)).filter(Desserte.operateur_id == op.id).scalar()
            if total == 0:
                continue
            nb_jour = db.query(func.count(Desserte.id)).filter(
                Desserte.operateur_id == op.id,
                Desserte.type_service == "Jour",
            ).scalar()
            result.append({
                "operateur":       op.nom,
                "pays_code":       op.pays_code,
                "total_dessertes": total,
                "nb_jour":         nb_jour,
                "nb_nuit":         total - nb_jour,
            })
        return sorted(result, key=lambda x: x["total_dessertes"], reverse=True)

    @staticmethod
    def get_par_pays(db: Session) -> list:
        gares_stats = (
            db.query(Gare.pays_code, func.count(Gare.id).label("total_gares"))
            .group_by(Gare.pays_code)
            .all()
        )
        dessertes_stats = (
            db.query(Gare.pays_code, func.count(Desserte.id).label("total_dessertes"))
            .join(Desserte, Gare.id == Desserte.gare_depart_id)
            .group_by(Gare.pays_code)
            .all()
        )
        dest_map = {r.pays_code: r.total_dessertes for r in dessertes_stats}
        return [
            {
                "pays_code":       r.pays_code,
                "total_gares":     r.total_gares,
                "total_dessertes": dest_map.get(r.pays_code, 0),
            }
            for r in gares_stats
        ]