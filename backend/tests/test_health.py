from fastapi.testclient import TestClient

from app.api import health
from app.main import app

client = TestClient(app)


def test_health_ok_when_everything_is_up(monkeypatch):
    monkeypatch.setattr(health, "check_db", lambda: True)
    monkeypatch.setattr(health, "check_ollama", lambda: True)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_degraded_when_ollama_is_down(monkeypatch):
    monkeypatch.setattr(health, "check_db", lambda: True)
    monkeypatch.setattr(health, "check_ollama", lambda: False)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "degraded"
    assert response.json()["ollama"] == "down"


def test_health_down_when_db_is_down(monkeypatch):
    monkeypatch.setattr(health, "check_db", lambda: False)
    monkeypatch.setattr(health, "check_ollama", lambda: True)

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json()["db"] == "down"
