import sqlite3
import os
import secrets
import hashlib

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

COLUMNS = ["general_news", "business_news", "finance_report", "sports_news"]

def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def init_db():
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id             INTEGER PRIMARY KEY,
                email          TEXT UNIQUE NOT NULL,
                token_hash     TEXT NOT NULL,
                general_news   INTEGER DEFAULT 1,
                business_news  INTEGER DEFAULT 1,
                finance_report INTEGER DEFAULT 1,
                sports_news    INTEGER DEFAULT 1
            )
        """)
        # migrate existing rows that lack a token_hash (no-op if column exists)
        try:
            conn.execute("ALTER TABLE users ADD COLUMN token_hash TEXT")
        except Exception:
            pass
    # backfill any rows with no token (from before auth was added)
    with _connect() as conn:
        rows = conn.execute("SELECT email FROM users WHERE token_hash IS NULL").fetchall()
        for row in rows:
            conn.execute(
                "UPDATE users SET token_hash = ? WHERE email = ?",
                (_hash_token(secrets.token_urlsafe(32)), row["email"])
            )

def get_all_users() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM users").fetchall()
    return [dict(row) for row in rows]

def get_user(email: str) -> dict | None:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    return dict(row) if row else None

def add_user(email: str, prefs: dict) -> str:
    if get_user(email):
        raise ValueError(f"Email already registered: {email}")
    token = secrets.token_urlsafe(32)
    values = {col: int(prefs.get(col, True)) for col in COLUMNS}
    with _connect() as conn:
        conn.execute(
            "INSERT INTO users (email, token_hash, general_news, business_news, finance_report, sports_news) VALUES (?, ?, ?, ?, ?, ?)",
            (email, _hash_token(token), values["general_news"], values["business_news"], values["finance_report"], values["sports_news"])
        )
    return token

def verify_token(email: str, token: str) -> bool:
    user = get_user(email)
    if not user:
        return False
    return user["token_hash"] == _hash_token(token)

def update_user(email: str, prefs: dict) -> None:
    if not get_user(email):
        raise ValueError(f"Email not found: {email}")
    updates = {k: int(v) for k, v in prefs.items() if k in COLUMNS and v is not None}
    if not updates:
        return
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    with _connect() as conn:
        conn.execute(f"UPDATE users SET {set_clause} WHERE email = ?", (*updates.values(), email))

def delete_user(email: str) -> None:
    if not get_user(email):
        raise ValueError(f"Email not found: {email}")
    with _connect() as conn:
        conn.execute("DELETE FROM users WHERE email = ?", (email,))
