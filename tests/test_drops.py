from src import service
from src.db import get_connection

def make(client, **extra):
    return client.post("/drops", json={"secret": "hunter2", **extra})

def test_create_returns_token(client):
    r = make(client)
    assert r.status_code == 201
    assert len(r.json()["token"]) >= 20

def test_open_returns_secret_then_410(client):
    token = make(client).json()["token"]
    first = client.get(f"/drops/{token}")
    assert first.status_code == 200
    assert first.json() == {"secret": "hunter2"}
    assert client.get(f"/drops/{token}").status_code == 410

def test_max_views_respected(client):
    token = make(client, max_views=2).json()["token"]
    assert client.get(f"/drops/{token}").status_code == 200
    assert client.get(f"/drops/{token}").status_code == 200
    assert client.get(f"/drops/{token}").status_code == 410

def test_unknown_token_returns_404(client):
    assert client.get("/drops/" + "x" * 43).status_code == 404

def test_short_token_returns_400(client):
    assert client.get("/drops/abc").status_code == 400

def test_create_rejects_bad_input(client):
    assert client.post("/drops", json={}).status_code == 400
    assert make(client, secret="").status_code == 400
    assert make(client, max_views=0).status_code == 400
    assert make(client, ttl_seconds=0).status_code == 400

def test_expired_drop_returns_410(client):
    token = make(client).json()["token"]
    with get_connection() as conn:
        conn.execute("UPDATE drops SET expires_at = now() - interval '1 second'")
    assert client.get(f"/drops/{token}").status_code == 410

def test_secret_encrypted_at_rest_and_wiped(client):
    token = make(client).json()["token"]
    with get_connection() as conn:
        stored = bytes(conn.execute("SELECT ciphertext FROM drops").fetchone()[0])
    assert b"hunter2" not in stored
    client.get(f"/drops/{token}")
    with get_connection() as conn:
        wiped = bytes(conn.execute("SELECT ciphertext FROM drops").fetchone()[0])
    assert wiped == b""

def test_purge_removes_expired(client):
    make(client)
    with get_connection() as conn:
        conn.execute("UPDATE drops SET expires_at = now() - interval '1 second'")
    assert service.purge_expired() == 1
