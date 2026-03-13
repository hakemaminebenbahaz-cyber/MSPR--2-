from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_db

API_KEY = "obrail-api-key-2026"
AUTH = {"X-API-Key": API_KEY}


def make_mock_trajet(
    id="FR_001",
    nom_ligne="Paris - Lyon",
    type_service="Jour",
    type_ligne="Grande vitesse",
    distance_km=500,
    duree_h=2.0,
    emissions_co2_gkm=3.5,
    frequence_hebdo=14,
    traction="électrique",
    source_donnee="SNCF",
):
    trajet = MagicMock()
    trajet.id = id
    trajet.nom_ligne = nom_ligne
    trajet.type_service = type_service
    trajet.type_ligne = type_ligne
    trajet.heure_depart = None
    trajet.heure_arrivee = None
    trajet.distance_km = distance_km
    trajet.duree_h = duree_h
    trajet.emissions_co2_gkm = emissions_co2_gkm
    trajet.frequence_hebdo = frequence_hebdo
    trajet.traction = traction
    trajet.source_donnee = source_donnee
    trajet.operateur_id = 1
    trajet.gare_depart_id = 1
    trajet.gare_arrivee_id = 2

    op = MagicMock()
    op.id = 1
    op.nom = "SNCF"
    op.pays_code = "FR"
    trajet.operateur = op

    gare_dep = MagicMock()
    gare_dep.id = 1
    gare_dep.nom = "Paris Gare de Lyon"
    gare_dep.ville = "Paris"
    gare_dep.pays_code = "FR"
    gare_dep.latitude = 48.8448
    gare_dep.longitude = 2.3735
    trajet.gare_depart = gare_dep

    gare_arr = MagicMock()
    gare_arr.id = 2
    gare_arr.nom = "Lyon Part-Dieu"
    gare_arr.ville = "Lyon"
    gare_arr.pays_code = "FR"
    gare_arr.latitude = 45.7605
    gare_arr.longitude = 4.8596
    trajet.gare_arrivee = gare_arr

    return trajet


def test_trajets_sans_api_key():
    with TestClient(app) as client:
        r = client.get("/api/v1/trajets/")
    assert r.status_code == 401


def test_trajets_mauvaise_api_key():
    with TestClient(app) as client:
        r = client.get("/api/v1/trajets/", headers={"X-API-Key": "mauvaise-cle"})
    assert r.status_code == 401


def test_get_trajets_retourne_liste():
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    with patch("app.routers.trajets.TrajetService.get_all", return_value=[make_mock_trajet()]):
        with TestClient(app) as client:
            r = client.get("/api/v1/trajets/", headers=AUTH)
    app.dependency_overrides.clear()
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_trajets_structure_reponse():
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    with patch("app.routers.trajets.TrajetService.get_all", return_value=[make_mock_trajet()]):
        with TestClient(app) as client:
            r = client.get("/api/v1/trajets/", headers=AUTH)
    app.dependency_overrides.clear()
    trajet = r.json()[0]
    assert "id" in trajet
    assert "nom_ligne" in trajet
    assert "type_service" in trajet


def test_get_trajets_liste_vide():
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    with patch("app.routers.trajets.TrajetService.get_all", return_value=[]):
        with TestClient(app) as client:
            r = client.get("/api/v1/trajets/?depart=VilleInexistante", headers=AUTH)
    app.dependency_overrides.clear()
    assert r.status_code == 200
    assert r.json() == []


def test_get_trajets_filtre_type_service():
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    with patch("app.routers.trajets.TrajetService.get_all", return_value=[make_mock_trajet()]) as mock_svc:
        with TestClient(app) as client:
            r = client.get("/api/v1/trajets/?type_service=Jour", headers=AUTH)
        assert mock_svc.call_args.kwargs["type_service"] == "Jour"
    app.dependency_overrides.clear()
    assert r.status_code == 200


def test_get_trajets_pagination():
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    with patch("app.routers.trajets.TrajetService.get_all", return_value=[]) as mock_svc:
        with TestClient(app) as client:
            client.get("/api/v1/trajets/?skip=10&limit=5", headers=AUTH)
        assert mock_svc.call_args.kwargs["skip"] == 10
        assert mock_svc.call_args.kwargs["limit"] == 5
    app.dependency_overrides.clear()


def test_get_trajet_par_id_existant():
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    with patch("app.routers.trajets.TrajetService.get_by_id", return_value=make_mock_trajet(id="FR_001")):
        with TestClient(app) as client:
            r = client.get("/api/v1/trajets/FR_001", headers=AUTH)
    app.dependency_overrides.clear()
    assert r.status_code == 200
    assert r.json()["id"] == "FR_001"


def test_get_trajet_par_id_inexistant():
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    with patch("app.routers.trajets.TrajetService.get_by_id", return_value=None):
        with TestClient(app) as client:
            r = client.get("/api/v1/trajets/ID_INEXISTANT", headers=AUTH)
    app.dependency_overrides.clear()
    assert r.status_code == 404
    assert "introuvable" in r.json()["detail"]


def test_get_trajet_detail_contient_operateur():
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    with patch("app.routers.trajets.TrajetService.get_by_id", return_value=make_mock_trajet()):
        with TestClient(app) as client:
            r = client.get("/api/v1/trajets/FR_001", headers=AUTH)
    app.dependency_overrides.clear()
    assert r.json()["operateur"]["nom"] == "SNCF"


def test_get_trajet_detail_contient_gares():
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    with patch("app.routers.trajets.TrajetService.get_by_id", return_value=make_mock_trajet()):
        with TestClient(app) as client:
            r = client.get("/api/v1/trajets/FR_001", headers=AUTH)
    app.dependency_overrides.clear()
    assert r.json()["gare_depart"]["nom"] == "Paris Gare de Lyon"
    assert r.json()["gare_arrivee"]["nom"] == "Lyon Part-Dieu"
