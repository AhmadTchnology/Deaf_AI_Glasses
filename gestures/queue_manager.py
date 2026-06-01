import threading
import queue
from gestures.database import GestureEntry, GestureDatabase
from display.renderer import Renderer
from utils.logger import logger


class GestureQueueManager:
    """
    Thread-safe queue that receives keyword lists from the NLP pipeline
    and plays gesture animations sequentially on the display.

    Producer thread: NLP pipeline pushes keyword lists
    Consumer thread: renderer pops and plays animations
    """

    def __init__(self, db: GestureDatabase, renderer: Renderer):
        self._db = db
        self._renderer = renderer
        self._queue: queue.Queue[list[str]] = queue.Queue(maxsize=10)
        self._running = False
        self._thread = threading.Thread(target=self._consumer_loop, daemon=True)

    def start(self) -> None:
        self._running = True
        self._thread.start()
        logger.info("Gesture queue manager started")

    def stop(self) -> None:
        self._running = False
        self._queue.put([])  # unblock consumer
        self._thread.join(timeout=5.0)
        logger.info("Gesture queue manager stopped")

    def enqueue(self, keywords: list[str]) -> None:
        """Push a list of keywords onto the queue (non-blocking, drops if full)."""
        try:
            self._queue.put_nowait(keywords)
            logger.debug("Queued {} keywords: {}", len(keywords), keywords)
        except queue.Full:
            logger.warning("Gesture queue full — dropping keywords: {}", keywords)

    def _consumer_loop(self) -> None:
        while self._running:
            try:
                keywords = self._queue.get(timeout=1.0)
            except queue.Empty:
                continue

            if not keywords:
                continue

            for word in keywords:
                if not self._running:
                    break
                gesture = self._db.lookup(word)
                if gesture:
                    logger.info("Playing gesture: '{}'", word)
                    self._renderer.play_gesture(gesture)
                else:
                    self._fingerspell(word)

            self._queue.task_done()

    def _fingerspell(self, word: str) -> None:
        """Play individual letter gestures (fingerspelling) as fallback."""
        logger.info("Fingerspelling: '{}'", word)
        for letter in word.upper():
            if not letter.isalpha():
                continue
            gesture = self._db.lookup(f"letter_{letter}")
            if gesture:
                self._renderer.play_gesture(gesture)
