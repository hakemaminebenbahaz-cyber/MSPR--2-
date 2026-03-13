import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app.main import app
from app.dependencies import get_db

API_KEY = "obrail-api-key-2026"
AUTH = {"X-API-Key": API_KEY}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def client_mock_db(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    with TestClient(app) as c:
        yield c, mock_db
    app.dependency_overrides.clear()
