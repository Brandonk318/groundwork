from app import registry


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200 and r.json() == {"ok": True, "app": "Groundwork"}


def test_app_name_from_one_setting(db):
    from fastapi.testclient import TestClient
    from app.config import Settings
    from app.main import create_app
    with TestClient(create_app(Settings(jwt_secret="t" * 40, app_name="Commissary Club"), db=db)) as c:
        assert c.get("/api/health").json()["app"] == "Commissary Club"


def test_features_endpoint(client):
    body = client.get("/api/features").json()
    assert body["count"] == 45 and len(body["features"]) == 45


def test_every_feature_has_a_stub_route(client):
    for f in registry.FEATURES:
        r = client.get(f"/api/{f.group}/{f.id}")
        assert r.status_code == 501, f.id
        assert r.json()["feature"]["id"] == f.id


def test_plans(client):
    body = client.get("/api/plans").json()
    assert "crisis_button" in body["free"] and "document_vault" in body["paid"]
