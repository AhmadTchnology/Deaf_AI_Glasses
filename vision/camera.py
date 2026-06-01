import cv2
import numpy as np
from utils.logger import logger
from config import CAMERA_INDEX


class CameraStream:
    """Captures frames from a USB webcam via OpenCV.

    Designed for the user's USB camera (with built-in mic).
    The mic is handled separately by the audio module.
    """

    def __init__(self, camera_index: int = CAMERA_INDEX):
        self._index = camera_index
        self._cap: cv2.VideoCapture | None = None

    def open(self) -> None:
        self._cap = cv2.VideoCapture(self._index)
        if not self._cap.isOpened():
            raise RuntimeError(f"Cannot open camera at index {self._index}")
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        logger.info("Camera opened: index {}", self._index)

    def capture_frame(self) -> np.ndarray | None:
        """Capture a single frame. Returns BGR numpy array or None on failure."""
        if self._cap is None or not self._cap.isOpened():
            return None
        ret, frame = self._cap.read()
        if not ret:
            logger.warning("Failed to capture frame from camera")
            return None
        return frame

    def capture_jpeg(self, quality: int = 80) -> bytes | None:
        """Capture a frame and encode as JPEG bytes for API transmission."""
        frame = self.capture_frame()
        if frame is None:
            return None
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
        success, buffer = cv2.imencode(".jpg", frame, encode_params)
        if not success:
            logger.error("JPEG encoding failed")
            return None
        return buffer.tobytes()

    def close(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None
            logger.info("Camera closed")

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
