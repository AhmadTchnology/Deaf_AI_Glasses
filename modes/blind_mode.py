import threading
import time
from vision.camera import CameraStream
from vision.detector import create_vision_provider
from vision.tts import TextToSpeech
from utils.logger import logger
from config import DETECTION_INTERVAL_S, VISION_PROVIDER


class BlindMode:
    """Blind assistance mode: detects objects via camera and announces them.

    Pipeline: CAMERA → capture frame → Vision API → description → TTS + display
    Runs detection at a configurable interval (default 3s).
    """

    def __init__(self):
        self._camera = CameraStream()
        self._detector = create_vision_provider()
        self._tts = TextToSpeech()
        self._running = False
        self._thread: threading.Thread | None = None
        self._last_description: str = "Starting camera..."
        self._on_detection = None
        self._current_frame = None
        self._lock = threading.Lock()
        logger.info(
            "BlindMode initialized (Vision: {}, interval: {}s)",
            VISION_PROVIDER, DETECTION_INTERVAL_S,
        )

    def set_detection_callback(self, callback) -> None:
        """Set callback: called with (description_str, frame_ndarray) on each detection."""
        self._on_detection = callback

    @property
    def last_description(self) -> str:
        with self._lock:
            return self._last_description

    @property
    def current_frame(self):
        with self._lock:
            return self._current_frame

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._camera.open()
        self._thread = threading.Thread(target=self._detection_loop, daemon=True)
        self._thread.start()
        logger.info("BlindMode started")

    def stop(self) -> None:
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=10.0)
            self._thread = None
        self._camera.close()
        self._tts.stop()
        logger.info("BlindMode stopped")

    def _detection_loop(self) -> None:
        while self._running:
            try:
                frame = self._camera.capture_frame()
                if frame is None:
                    time.sleep(1.0)
                    continue

                with self._lock:
                    self._current_frame = frame.copy()

                jpeg_bytes = self._camera.capture_jpeg(quality=70)
                if jpeg_bytes is None:
                    time.sleep(1.0)
                    continue

                description = self._detector.detect(jpeg_bytes)
                if description:
                    with self._lock:
                        self._last_description = description
                    self._tts.speak(description)
                    logger.info("Detected: '{}'", description)

                    if self._on_detection:
                        try:
                            self._on_detection(description, frame)
                        except Exception as e:
                            logger.error("Detection callback error: {}", e)

            except Exception as e:
                if self._running:
                    logger.error("BlindMode detection error: {}", e)

            time.sleep(DETECTION_INTERVAL_S)
