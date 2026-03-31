import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

COLUMNS = ["general_news", "business_news", "finance_report", "sports_news"]

def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY,
                email         TEXT UNIQUE NOT NULL,
                general_news  INTEGER DEFAULT 1,
                business_news INTEGER DEFAULT 1,
                finance_report INTEGER DEFAULT 1,
                sports_news   INTEGER DEFAULT 1
            )
        """)

def get_all_users() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM users").fetchall()
    return [dict(row) for row in rows]

def get_user(email: str) -> dict | None:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    return dict(row) if row else None

def add_user(email: str, prefs: dict) -> None:
    if get_user(email):
        raise ValueError(f"Email already registered: {email}")
    values = {col: int(prefs.get(col, True)) for col in COLUMNS}
    with _connect() as conn:
        conn.execute(
            "INSERT INTO users (email, general_news, business_news, finance_report, sports_news) VALUES (?, ?, ?, ?, ?)",
            (email, values["general_news"], values["business_news"], values["finance_report"], values["sports_news"])
        )

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
