import os
import pytest
import db

TEST_DB = "test_users.db"

@pytest.fixture(autouse=True)
def clean_db(monkeypatch, tmp_path):
    test_db = str(tmp_path / "test.db")
    monkeypatch.setattr(db, "DB_PATH", test_db)
    db.init_db()
    yield
    if os.path.exists(test_db):
        os.remove(test_db)

def test_add_and_get_user():
    db.add_user("test@example.com", {})
    user = db.get_user("test@example.com")
    assert user["email"] == "test@example.com"
    assert user["general_news"] == 1

def test_add_duplicate_raises():
    db.add_user("test@example.com", {})
    with pytest.raises(ValueError):
        db.add_user("test@example.com", {})

def test_get_nonexistent_returns_none():
    assert db.get_user("nobody@example.com") is None

def test_update_user():
    db.add_user("test@example.com", {})
    db.update_user("test@example.com", {"general_news": False})
    user = db.get_user("test@example.com")
    assert user["general_news"] == 0

def test_update_nonexistent_raises():
    with pytest.raises(ValueError):
        db.update_user("nobody@example.com", {"general_news": False})

def test_delete_user():
    db.add_user("test@example.com", {})
    db.delete_user("test@example.com")
    assert db.get_user("test@example.com") is None

def test_delete_nonexistent_raises():
    with pytest.raises(ValueError):
        db.delete_user("nobody@example.com")

def test_get_all_users():
    db.add_user("a@example.com", {})
    db.add_user("b@example.com", {"finance_report": False})
    users = db.get_all_users()
    assert len(users) == 2
    emails = [u["email"] for u in users]
    assert "a@example.com" in emails
    assert "b@example.com" in emails
