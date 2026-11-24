import os
import psycopg

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/vaultdrop"
)

def get_connection():
    return psycopg.connect(DATABASE_URL)

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS drops (
                token_hash TEXT PRIMARY KEY,
                ciphertext BYTEA NOT NULL,
                views_left INTEGER NOT NULL CHECK (views_left >= 0),
                expires_at TIMESTAMPTZ NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
        """)
