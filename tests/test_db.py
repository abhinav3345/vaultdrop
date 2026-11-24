from src.db import get_connection

def test_insert_and_read_drop(db):
    with get_connection() as conn:
        row = conn.execute(
            "INSERT INTO drops (token_hash, ciphertext, views_left, expires_at) "
            "VALUES ('h', 'x', 1, now() + interval '1 hour') "
            "RETURNING token_hash, views_left"
        ).fetchone()
    assert row == ("h", 1)
