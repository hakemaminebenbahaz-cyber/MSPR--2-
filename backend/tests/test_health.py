from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_retourne_200():
    with patch("app.routers.health.test_connection", return_value=True):
        r = client.get("/health")
    assert r.status_code == 200


def test_health_structure_reponse():
    with patch("app.routers.health.test_connection", return_value=True):
        r = client.get("/health")
    data = r.json()
    assert "status" in data
    assert "service" in data
    assert "version" in data
    assert "database" in data


def test_health_db_ok():
    with patch("app.routers.health.test_connection", return_value=True):
        r = client.get("/health")
    data = r.json()
    assert data["status"] == "healthy"
    assert data["database"] == "healthy"


def test_health_db_ko():
    with patch("app.routers.health.test_connection", return_value=False):
        r = client.get("/health")
    data = r.json()
    assert data["status"] == "degraded"
    assert data["database"] == "unreachable"


def test_health_sans_api_key():
    with patch("app.routers.health.test_connection", return_value=True):
        r = client.get("/health")
    assert r.status_code == 200


def test_health_service_name():
    with patch("app.routers.health.test_connection", return_value=True):
        r = client.get("/health")
    assert r.json()["service"] == "ObRail API"


def test_root_sans_api_key():
    r = client.get("/")
    assert r.status_code == 200


def test_root_contient_endpoints():
    r = client.get("/")
    data = r.json()
    assert "endpoints" in data
    assert "trajets" in data["endpoints"]
    assert "health" in data["endpoints"]
