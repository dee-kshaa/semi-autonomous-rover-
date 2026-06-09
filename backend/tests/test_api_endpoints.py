from datetime import datetime, timezone
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.main import app


def test_auth_register_and_login(monkeypatch):
    from app.services.auth_service import AuthService

    monkeypatch.setattr(
        AuthService,
        "register",
        staticmethod(
            lambda db, payload: SimpleNamespace(
                id=1,
                email=payload.email,
                full_name=payload.full_name,
                is_active=True,
                created_at=datetime.now(timezone.utc),
            )
        ),
    )
    monkeypatch.setattr(AuthService, "login", staticmethod(lambda db, email, password: "test-token"))

    client = TestClient(app)
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": "demo@example.com", "password": "password123", "full_name": "Demo User"},
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "demo@example.com", "password": "password123"},
    )

    assert register_response.status_code == 200
    assert register_response.json()["email"] == "demo@example.com"
    assert login_response.status_code == 200
    assert login_response.json()["access_token"] == "test-token"


def test_analytics_endpoints(monkeypatch):
    from app.services.analytics_service import AnalyticsService

    monkeypatch.setattr(
        AnalyticsService,
        "summary",
        staticmethod(
            lambda db: {
                "total_samples": 10,
                "active_users": 2,
                "avg_rssi": -84.5,
                "quality_distribution": {"excellent": 1, "good": 3, "fair": 4, "poor": 2},
            }
        ),
    )
    monkeypatch.setattr(
        AnalyticsService,
        "trend",
        staticmethod(lambda db, hours: [{"bucket": "2026-01-01 00:00:00", "avg_rssi": -82.0}]),
    )
    monkeypatch.setattr(
        AnalyticsService,
        "heatmap",
        staticmethod(lambda db: [{"latitude": 12.9, "longitude": 77.6, "avg_rssi": -90.0, "sample_count": 5}]),
    )
    monkeypatch.setattr(
        AnalyticsService,
        "operator_comparison",
        staticmethod(
            lambda db: [
                {"operator_name": "Operator A", "avg_rssi": -80.0, "sample_count": 4, "dead_zone_rate": 0.1}
            ]
        ),
    )

    client = TestClient(app)
    assert client.get("/api/v1/analytics/summary").status_code == 200
    assert client.get("/api/v1/analytics/trend").status_code == 200
    assert client.get("/api/v1/analytics/heatmap").status_code == 200
    assert client.get("/api/v1/analytics/operator-comparison").status_code == 200


def test_signal_ingest_endpoint(monkeypatch):
    from app.services.prediction_service import PredictionService
    from app.services.signal_service import SignalService

    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=42)
    monkeypatch.setattr(
        SignalService,
        "create_signal_log",
        staticmethod(lambda db, user_id, payload: SimpleNamespace(id=11, operator=SimpleNamespace(name="Operator A"), rssi=payload.rssi)),
    )
    monkeypatch.setattr(
        PredictionService,
        "infer_and_store",
        staticmethod(
            lambda db, signal: SimpleNamespace(
                id=21,
                coverage_class="good",
                dead_zone_probability=0.2,
            )
        ),
    )

    client = TestClient(app)
    response = client.post(
        "/api/v1/signals/ingest",
        json={
            "rssi": -86,
            "network_type": "4G",
            "operator_name": "Operator A",
            "latitude": 12.9,
            "longitude": 77.6,
            "city": "Bengaluru",
            "timestamp": "2026-06-09T10:00:00Z",
            "device_model": "Pixel",
            "device_os": "Android",
            "speed_mps": 3.2,
        },
    )
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["coverage_class"] == "good"
