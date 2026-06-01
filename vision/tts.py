import threading
from utils.logger import logger


class TextToSpeech:
    """Offline text-to-speech using pyttsx3.

    Runs speech in a background thread so it doesn't block
    the main rendering loop. Queues are handled internally by pyttsx3.
    """

    def __init__(self, rate: int = 160):
        import pyttsx3
        self._engine = pyttsx3.init()
        self._engine.setProperty("rate", rate)
        self._lock = threading.Lock()
        logger.info("TTS initialized, rate={}", rate)

    def speak(self, text: str) -> None:
        """Speak text in a background thread (non-blocking)."""
        thread = threading.Thread(target=self._speak_sync, args=(text,), daemon=True)
        thread.start()

    def _speak_sync(self, text: str) -> None:
        with self._lock:
            try:
                self._engine.say(text)
                self._engine.runAndWait()
            except Exception as e:
                logger.error("TTS error: {}", e)

    def stop(self) -> None:
        try:
            self._engine.stop()
        except Exception:
            pass
        logger.info("TTS stopped")
