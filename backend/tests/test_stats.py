from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_db

API_KEY = "obrail-api-key-2026"
AUTH = {"X-API-Key": API_KEY}

MOCK_VOLUMES = {
    "total_trajets":    42,
    "total_jour":       30,
    "total_nuit":       12,
    "total_operateurs": 5,
    "total_gares":      20,
}

MOCK_JOUR_VS_NUIT = [
    {"type_service": "Jour", "total": 30, "co2_moyen": 3.2, "duree_moyenne_h": 2.5},
    {"type_service": "Nuit", "total": 12, "co2_moyen": 5.1, "duree_moyenne_h": 8.0},
]

MOCK_PAR_OPERATEUR = [
    {"operateur": "SNCF", "pays_code": "FR", "total_dessertes": 20, "nb_jour": 15, "nb_nuit": 5},
    {"operateur": "DB",   "pays_code": "DE", "total_dessertes": 12, "nb_jour": 8,  "nb_nuit": 4},
]

MOCK_PAR_PAYS = [
    {"pays_code": "FR", "total_gares": 10, "total_dessertes": 20},
    {"pays_code": "DE", "total_gares": 8,  "total_dessertes": 12},
]


def test_stats_sans_api_key():
    with TestClient(app) as client:
        r = client.get("/api/v1/stats/volumes")
    assert r.status_code == 401


def test_stats_volumes_retourne_200():
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    with patch("app.routers.stats.TrajetService.get_volumes", return_value=MOCK_VOLUMES):
        with TestClient(app) as client:
            r = client.get("/api/v1/stats/volumes", headers=AUTH)
    app.dependency_overrides.clear()
    assert r.status_code == 200


def test_stats_volumes_structure():
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    with patch("app.routers.stats.TrajetService.get_volumes", return_value=MOCK_VOLUMES):
        with TestClient(app) as client:
            r = client.get("/api/v1/stats/volumes", headers=AUTH)
    app.dependency_overrides.clear()
    data = r.json()
    assert "total_trajets" in data
    assert "total_jour" in data
    assert "total_nuit" in data
    assert "total_operateurs" in data
    assert "total_gares" in data


def test_stats_volumes_coherence_jour_nuit():
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    with patch("app.routers.stats.TrajetService.get_volumes", return_value=MOCK_VOLUMES):
        with TestClient(app) as client:
            r = client.get("/api/v1/stats/volumes", headers=AUTH)
    app.dependency_overrides.clear()
    data = r.json()
    assert data["total_jour"] + data["total_nuit"] == data["total_trajets"]


def test_stats_jour_vs_nuit_retourne_liste():
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    with patch("app.routers.stats.TrajetService.get_jour_vs_nuit", return_value=MOCK_JOUR_VS_NUIT):
        with TestClient(app) as client:
            r = client.get("/api/v1/stats/jour-vs-nuit", headers=AUTH)
    app.dependency_overrides.clear()
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_stats_jour_vs_nuit_contient_jour_et_nuit():
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    with patch("app.routers.stats.TrajetService.get_jour_vs_nuit", return_value=MOCK_JOUR_VS_NUIT):
        with TestClient(app) as client:
            r = client.get("/api/v1/stats/jour-vs-nuit", headers=AUTH)
    app.dependency_overrides.clear()
    types = [d["type_service"] for d in r.json()]
    assert "Jour" in types
    assert "Nuit" in types


def test_stats_par_operateur_retourne_liste():
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    with patch("app.routers.stats.TrajetService.get_par_operateur", return_value=MOCK_PAR_OPERATEUR):
        with TestClient(app) as client:
            r = client.get("/api/v1/stats/par-operateur", headers=AUTH)
    app.dependency_overrides.clear()
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert "operateur" in r.json()[0]
    assert "nb_jour" in r.json()[0]
    assert "nb_nuit" in r.json()[0]


def test_stats_par_pays_retourne_liste():
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    with patch("app.routers.stats.TrajetService.get_par_pays", return_value=MOCK_PAR_PAYS):
        with TestClient(app) as client:
            r = client.get("/api/v1/stats/par-pays", headers=AUTH)
    app.dependency_overrides.clear()
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    pays_codes = [d["pays_code"] for d in r.json()]
    assert "FR" in pays_codes


def test_stats_par_pays_structure():
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    with patch("app.routers.stats.TrajetService.get_par_pays", return_value=MOCK_PAR_PAYS):
        with TestClient(app) as client:
            r = client.get("/api/v1/stats/par-pays", headers=AUTH)
    app.dependency_overrides.clear()
    item = r.json()[0]
    assert "pays_code" in item
    assert "total_gares" in item
    assert "total_dessertes" in item
