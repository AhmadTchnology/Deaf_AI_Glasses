import sqlite3
import json
from dataclasses import dataclass
from config import GESTURE_DB_PATH, GESTURE_DATA_DIR
from utils.logger import logger


@dataclass
class GestureEntry:
    word: str
    frame_dir: str
    frame_count: int
    duration_ms: int
    category: str = "general"


class GestureDatabase:
    """SQLite-backed gesture lookup. Falls back to fingerspelling if word not found."""

    def __init__(self, db_path: str = GESTURE_DB_PATH):
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS gestures (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                word        TEXT NOT NULL UNIQUE,
                frame_dir   TEXT NOT NULL,
                frame_count INTEGER NOT NULL,
                duration_ms INTEGER NOT NULL,
                category    TEXT DEFAULT 'general'
            )
        """)
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_word ON gestures(word)"
        )
        self._conn.commit()

    def lookup(self, word: str) -> GestureEntry | None:
        """Find a gesture by word. Returns None if not found."""
        cursor = self._conn.execute(
            "SELECT word, frame_dir, frame_count, duration_ms, category "
            "FROM gestures WHERE word = ?",
            (word.lower(),),
        )
        row = cursor.fetchone()
        if row:
            return GestureEntry(**dict(row))
        logger.warning("No gesture found for word: '{}'", word)
        return None

    def import_from_json(self, index_path: str) -> int:
        """Import gestures from a JSON index file. Returns count imported."""
        with open(index_path) as f:
            data = json.load(f)

        for word, info in data.items():
            self._conn.execute(
                """INSERT OR REPLACE INTO gestures
                   (word, frame_dir, frame_count, duration_ms, category)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    word,
                    info["frame_dir"],
                    info["frame_count"],
                    info["duration_ms"],
                    info.get("category", "general"),
                ),
            )
        self._conn.commit()
        logger.info("Imported {} gestures from {}", len(data), index_path)
        return len(data)

    def get_all_words(self) -> list[str]:
        """Return all words in the gesture database."""
        cursor = self._conn.execute("SELECT word FROM gestures ORDER BY word")
        return [row["word"] for row in cursor.fetchall()]

    def close(self) -> None:
        self._conn.close()
