from fastapi.testclient import TestClient

from app.analysis import service
from app.main import app


class DummySettings:
    app_name = "DevWindmark"
    analysis_period_start = "2026-01-01"
    analysis_period_end = "2026-01-31"
    generation_unit = "MW"
    decision_timezone = "Europe/London"
    decision_cutoff_time = "09:20"
    decision_offset_days = 1
    cors_origin_list = ["http://localhost:5173"]


def test_health_endpoint(monkeypatch):
    monkeypatch.setattr(service, "get_settings", lambda: DummySettings())
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["application"] == "DevWindmark"
    assert body["analysis_period_start"] == "2026-01-01"


def test_invalid_delivery_date_is_rejected():
    client = TestClient(app)
    response = client.get("/api/forecasts", params={"delivery_date": "2025-12-01"})
    assert response.status_code == 400


def test_invalid_date_format_is_rejected():
    client = TestClient(app)
    response = client.get("/api/summary", params={"delivery_date": "01-01-2026"})
    assert response.status_code == 422
