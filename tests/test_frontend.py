from fastapi.testclient import TestClient

from src import service
from src.main import app


def test_landing_page():
    response = TestClient(app).get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "<title>VaultDrop</title>" in response.text
    assert 'href="/style.css"' in response.text
    assert 'src="/sender.js" defer' in response.text
    assert 'method="post" action="/drops"' in response.text


def test_stylesheet():
    response = TestClient(app).get("/style.css")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/css")


def test_frontend_keeps_api_routes_reachable():
    client = TestClient(app)

    assert client.get("/health").json() == {"status": "ok"}
    assert client.post("/drops", json={}).status_code == 400
    assert client.get("/drops/too-short").status_code == 400


def test_missing_asset():
    assert TestClient(app).get("/missing.css").status_code == 404

def test_sender_and_recipient_scripts_are_served():
    client = TestClient(app)

    for path in ("/sender.js", "/open/open.js"):
        response = client.get(path)
        assert response.status_code == 200
        assert "javascript" in response.headers["content-type"]


def test_share_page_only_consumes_a_view_when_api_is_called(monkeypatch):
    token = "vaultdrop-token-for-test"
    created = []
    consumed = []

    def create(secret, max_views, ttl_seconds):
        created.append((secret, max_views, ttl_seconds))
        return token

    def consume(value):
        consumed.append(value)
        return "example secret"

    monkeypatch.setattr(service, "create_drop", create)
    monkeypatch.setattr(service, "consume_drop", consume)
    client = TestClient(app)

    response = client.post("/drops", json={
        "secret": "example secret",
        "max_views": 2,
        "ttl_seconds": 300,
    })
    assert response.status_code == 201
    assert response.json() == {"token": token}
    assert created == [("example secret", 2, 300)]

    landing = client.get("/open/")
    assert landing.status_code == 200
    assert 'src="/open/open.js" defer' in landing.text
    assert "example secret" not in landing.text
    assert consumed == []

    revealed = client.get(f"/drops/{token}")
    assert revealed.json() == {"secret": "example secret"}
    assert consumed == [token]
