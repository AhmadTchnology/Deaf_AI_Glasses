from gestures.database import GestureDatabase, GestureEntry
from utils.logger import logger


class GestureMapper:
    """Resolves keyword lists to gesture entries with fingerspelling fallback."""

    def __init__(self, db: GestureDatabase):
        self._db = db

    def resolve(self, keywords: list[str]) -> list[GestureEntry | str]:
        """
        Map each keyword to a GestureEntry.
        Returns GestureEntry for known words, or the raw string for fingerspelling.
        """
        results: list[GestureEntry | str] = []
        for word in keywords:
            gesture = self._db.lookup(word)
            if gesture:
                results.append(gesture)
            else:
                logger.info("Fingerspell fallback for: '{}'", word)
                results.append(word)
        return results

    def get_letter_gestures(self, word: str) -> list[GestureEntry]:
        """Get individual letter gestures for fingerspelling."""
        letters: list[GestureEntry] = []
        for char in word.upper():
            if not char.isalpha():
                continue
            gesture = self._db.lookup(f"letter_{char}")
            if gesture:
                letters.append(gesture)
        return letters
