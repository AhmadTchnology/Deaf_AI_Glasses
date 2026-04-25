import pytest
import sqlite3
from gestures.database import GestureDatabase, GestureEntry


@pytest.fixture
def db(tmp_path):
    """Create an in-memory gesture database with test data."""
    db_path = str(tmp_path / "test_gestures.db")
    gesture_db = GestureDatabase(db_path=db_path)
    gesture_db._conn.execute(
        "INSERT INTO gestures (word, frame_dir, frame_count, duration_ms, category) "
        "VALUES (?, ?, ?, ?, ?)",
        ("hello", "frames/hello", 4, 180, "greeting"),
    )
    gesture_db._conn.execute(
        "INSERT INTO gestures (word, frame_dir, frame_count, duration_ms, category) "
        "VALUES (?, ?, ?, ?, ?)",
        ("yes", "frames/yes", 3, 200, "common"),
    )
    gesture_db._conn.commit()
    return gesture_db


def test_lookup_existing_word(db):
    gesture = db.lookup("hello")
    assert gesture is not None
    assert gesture.word == "hello"
    assert gesture.frame_count == 4
    assert gesture.duration_ms == 180
    assert gesture.category == "greeting"


def test_lookup_missing_word(db):
    gesture = db.lookup("zzzzz")
    assert gesture is None


def test_lookup_case_insensitive(db):
    gesture = db.lookup("HELLO")
    assert gesture is not None
    assert gesture.word == "hello"


def test_get_all_words(db):
    words = db.get_all_words()
    assert "hello" in words
    assert "yes" in words
    assert len(words) == 2


def test_import_from_json(db, tmp_path):
    import json
    index_data = {
        "goodbye": {
            "frame_dir": "frames/goodbye",
            "frame_count": 4,
            "duration_ms": 180,
            "category": "greeting",
        }
    }
    index_path = tmp_path / "test_index.json"
    index_path.write_text(json.dumps(index_data))

    count = db.import_from_json(str(index_path))
    assert count == 1
    assert db.lookup("goodbye") is not None
