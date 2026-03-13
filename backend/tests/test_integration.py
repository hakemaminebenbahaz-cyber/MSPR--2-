"""
Tests d'intégration — nécessitent une connexion réelle à la base PostgreSQL Azure.
Les variables DATABASE_URL et DB_PASSWORD doivent être définies dans le fichier .env

Lancer avec : pytest tests/test_integration.py -v
"""
from fastapi.testclient import TestClient
from app.main import app

API_KEY = "obrail-api-key-2026"
AUTH = {"X-API-Key": API_KEY}

client = TestClient(app)


# ── Health ────────────────────────────────────────────────────────────────────

def test_integration_health_db_accessible():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["database"] == "healthy"


# ── Trajets ───────────────────────────────────────────────────────────────────

def test_integration_get_trajets():
    r = client.get("/api/v1/trajets/?limit=10", headers=AUTH)
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) > 0


def test_integration_get_trajets_type_jour():
    r = client.get("/api/v1/trajets/?type_service=Jour&limit=20", headers=AUTH)
    assert r.status_code == 200
    for trajet in r.json():
        assert trajet["type_service"] == "Jour"


def test_integration_get_trajets_type_nuit():
    r = client.get("/api/v1/trajets/?type_service=Nuit&limit=20", headers=AUTH)
    assert r.status_code == 200
    for trajet in r.json():
        assert trajet["type_service"] == "Nuit"


def test_integration_get_trajet_par_id():
    r_list = client.get("/api/v1/trajets/?limit=1", headers=AUTH)
    assert r_list.status_code == 200
    trajet_id = r_list.json()[0]["id"]

    r = client.get(f"/api/v1/trajets/{trajet_id}", headers=AUTH)
    assert r.status_code == 200
    assert r.json()["id"] == trajet_id


def test_integration_get_trajet_id_inexistant():
    r = client.get("/api/v1/trajets/ID_INEXISTANT_XYZ", headers=AUTH)
    assert r.status_code == 404


def test_integration_trajet_detail_contient_gares():
    r_list = client.get("/api/v1/trajets/?limit=1", headers=AUTH)
    trajet_id = r_list.json()[0]["id"]
    r = client.get(f"/api/v1/trajets/{trajet_id}", headers=AUTH)
    data = r.json()
    assert data.get("gare_depart") is not None
    assert data.get("gare_arrivee") is not None


# ── Stats ─────────────────────────────────────────────────────────────────────

def test_integration_stats_volumes():
    r = client.get("/api/v1/stats/volumes", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["total_trajets"] > 0
    assert data["total_jour"] + data["total_nuit"] == data["total_trajets"]
    assert data["total_operateurs"] > 0
    assert data["total_gares"] > 0


def test_integration_stats_jour_vs_nuit():
    r = client.get("/api/v1/stats/jour-vs-nuit", headers=AUTH)
    assert r.status_code == 200
    types = [d["type_service"] for d in r.json()]
    assert "Jour" in types
    assert "Nuit" in types


def test_integration_stats_par_operateur():
    r = client.get("/api/v1/stats/par-operateur", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert len(data) > 0
    assert "operateur" in data[0]
    assert "nb_jour" in data[0]
    assert "nb_nuit" in data[0]


def test_integration_stats_par_pays():
    r = client.get("/api/v1/stats/par-pays", headers=AUTH)
    assert r.status_code == 200
    pays_codes = [d["pays_code"] for d in r.json()]
    assert "FR" in pays_codes


# ── Sécurité ──────────────────────────────────────────────────────────────────

def test_integration_sans_api_key_retourne_401():
    r = client.get("/api/v1/trajets/")
    assert r.status_code == 401


def test_integration_mauvaise_api_key_retourne_401():
    r = client.get("/api/v1/trajets/", headers={"X-API-Key": "fausse-cle"})
    assert r.status_code == 401


def test_integration_health_public():
    r = client.get("/health")
    assert r.status_code == 200
