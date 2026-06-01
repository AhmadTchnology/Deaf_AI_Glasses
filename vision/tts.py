import threading
import subprocess
from utils.logger import logger


class TextToSpeech:
    """Offline text-to-speech using pyttsx3 or CLI fallback.

    Runs speech in a background thread so it doesn't block
    the main rendering loop.
    """

    def __init__(self, rate: int = 160):
        self._rate = rate
        self._use_cli = False
        self._engine = None
        self._lock = threading.Lock()

        try:
            import pyttsx3
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", rate)
            logger.info("TTS initialized (pyttsx3), rate={}", rate)
        except Exception as e:
            logger.warning("pyttsx3 init failed: {}. Falling back to CLI espeak.", e)
            self._use_cli = True

    def speak(self, text: str) -> None:
        """Speak text in a background thread (non-blocking)."""
        thread = threading.Thread(target=self._speak_sync, args=(text,), daemon=True)
        thread.start()

    def _speak_sync(self, text: str) -> None:
        with self._lock:
            try:
                if self._use_cli:
                    subprocess.run(["espeak", "-s", str(self._rate), text], check=False)
                else:
                    self._engine.say(text)
                    self._engine.runAndWait()
            except Exception as e:
                logger.error("TTS error: {}", e)

    def stop(self) -> None:
        if not self._use_cli and self._engine:
            try:
                self._engine.stop()
            except Exception:
                pass
        logger.info("TTS stopped")
