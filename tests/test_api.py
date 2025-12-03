from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from kandidate.models import AppConfig, RepositoryConfig
from kandidate.services.api import create_app


def _app(tmp_path: Path) -> TestClient:
    config = AppConfig(repository=RepositoryConfig(path=tmp_path / "results.json"))
    return TestClient(create_app(config))


def test_health_endpoint(tmp_path: Path) -> None:
    client = _app(tmp_path)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_candidate_crud(tmp_path: Path) -> None:
    client = _app(tmp_path)
    payload = {"name": "Sara", "text": "Deep Python knowledge and FastAPI"}
    created = client.post("/candidates", json=payload)
    assert created.status_code == 201
    listing = client.get("/candidates")
    assert listing.status_code == 200
    assert listing.json()[0]["document"]["name"] == "Sara"


def test_candidate_validation(tmp_path: Path) -> None:
    client = _app(tmp_path)
    response = client.post("/candidates", json={"name": "Empty", "text": "   "})
    assert response.status_code == 400
