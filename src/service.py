import hashlib
import secrets
from src.crypto import decrypt, encrypt
from src.db import get_connection

class DropNotFound(Exception):
    pass

class DropGone(Exception):
    pass

def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def create_drop(secret: str, max_views: int, ttl_seconds: int) -> str:
    token = secrets.token_urlsafe(32)
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO drops (token_hash, ciphertext, views_left, expires_at) "
            "VALUES (%s, %s, %s, now() + %s * interval '1 second')",
            (_hash(token), encrypt(secret), max_views, ttl_seconds),
        )
    return token

def consume_drop(token: str) -> str:
    h = _hash(token)
    gone = False
    plaintext = None
    with get_connection() as conn:
        row = conn.execute(
            "SELECT ciphertext, views_left, expires_at > now() "
            "FROM drops WHERE token_hash = %s FOR UPDATE",
            (h,),
        ).fetchone()
        if row is None:
            raise DropNotFound
        ciphertext, views_left, alive = row
        if views_left == 0 or not alive:
            conn.execute(
                "UPDATE drops SET ciphertext = ''::bytea, views_left = 0 "
                "WHERE token_hash = %s",
                (h,),
            )
            gone = True
        else:
            conn.execute(
                "UPDATE drops SET views_left = views_left - 1, "
                "ciphertext = CASE WHEN views_left = 1 THEN ''::bytea "
                "ELSE ciphertext END WHERE token_hash = %s",
                (h,),
            )
            plaintext = decrypt(bytes(ciphertext))
    if gone:
        raise DropGone
    return plaintext

def purge_expired() -> int:
    with get_connection() as conn:
        return conn.execute("DELETE FROM drops WHERE expires_at < now()").rowcount
