import threading
from audio.capture import MicrophoneStream
from audio.vad import VoiceActivityDetector
from audio.chunker import AudioChunker
from speech.factory import create_stt_provider
from vision.camera import CameraStream
from vision.tts import TextToSpeech
from vision.sign_translator import create_sign_provider
from utils.logger import logger
from utils.profiler import Profiler
from config import STT_PROVIDER
import time
import cv2


class DeafMode:
    """Deaf assistance mode: captures speech and displays transcript text.

    Pipeline: MIC → VAD → Chunker → STT → text on screen
    The transcript is stored as a scrolling buffer of recent lines.
    """

    MAX_TRANSCRIPT_LINES = 8

    def __init__(self):
        self._mic = MicrophoneStream()
        self._vad = VoiceActivityDetector()
        self._chunker = AudioChunker()
        self._stt = create_stt_provider()
        self._profiler = Profiler()
        
        # Speaking mode components
        self._camera = CameraStream()
        self._sign_translator = create_sign_provider()
        self._tts = TextToSpeech()
        self._is_speaking_mode = False
        self._camera_thread: threading.Thread | None = None
        
        self._running = False
        self._thread: threading.Thread | None = None
        self._transcript_lines: list[str] = []
        self._on_transcript = None
        self._on_mode_change = None
        self._lock = threading.Lock()
        logger.info("DeafMode initialized (STT: {})", STT_PROVIDER)

    def set_transcript_callback(self, callback) -> None:
        """Set callback: called with list[str] of transcript lines on each update."""
        self._on_transcript = callback

    def set_mode_change_callback(self, callback) -> None:
        """Set callback: called with bool (is_speaking_mode) when mode changes."""
        self._on_mode_change = callback

    @property
    def transcript_lines(self) -> list[str]:
        with self._lock:
            return list(self._transcript_lines)

    @property
    def is_speaking_mode(self) -> bool:
        with self._lock:
            return self._is_speaking_mode

    def toggle_speaking_mode(self) -> bool:
        """Toggles between speaking mode (camera) and hearing mode (mic)."""
        with self._lock:
            self._is_speaking_mode = not self._is_speaking_mode
            is_speaking = self._is_speaking_mode

        if is_speaking:
            logger.info("DeafMode: Switching to Speaking Mode (Camera)")
            self._camera.open()
            self._camera_thread = threading.Thread(target=self._camera_loop, daemon=True)
            self._camera_thread.start()
        else:
            logger.info("DeafMode: Switching to Hearing Mode (Mic)")
            if self._camera_thread:
                self._camera_thread.join(timeout=3.0)
                self._camera_thread = None
            self._camera.close()

        if self._on_mode_change:
            try:
                self._on_mode_change(is_speaking)
            except Exception as e:
                logger.error("Mode change callback error: {}", e)

        return is_speaking

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._transcript_lines.clear()
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        logger.info("DeafMode started")

    def stop(self) -> None:
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=5.0)
            self._thread = None
            
        with self._lock:
            if self._is_speaking_mode:
                self._is_speaking_mode = False
                if self._camera_thread:
                    self._camera_thread.join(timeout=3.0)
                    self._camera_thread = None
                self._camera.close()
                
        self._tts.stop()
        logger.info("DeafMode stopped")

    def _capture_loop(self) -> None:
        try:
            for audio_chunk in self._mic.stream_chunks():
                if not self._running:
                    break
                    
                # Skip processing microphone audio if in speaking mode
                if self._is_speaking_mode:
                    continue

                self._profiler.start("vad")
                is_speech = self._vad.is_speech(audio_chunk)
                self._profiler.end("vad")

                if not is_speech:
                    continue

                logger.debug("Speech detected — sending to STT ({})", STT_PROVIDER)

                self._profiler.start("stt")
                wav_data = self._chunker.to_wav_bytes(audio_chunk)
                transcript = self._stt.transcribe(wav_data)
                self._profiler.end("stt")

                if not transcript:
                    continue

                self._add_transcript(transcript)
                self._profiler.log_summary()

        except Exception as e:
            if self._running:
                logger.exception("DeafMode capture error: {}", e)
        finally:
            self._mic.close()

    def _camera_loop(self) -> None:
        last_process_time = 0.0
        while self._running and self._is_speaking_mode:
            try:
                frame = self._camera.capture_frame()
                if frame is None:
                    time.sleep(0.1)
                    continue

                now = time.time()
                if now - last_process_time >= 5.0:
                    last_process_time = now
                    # Encode the fresh frame
                    success, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                    if success:
                        jpeg_bytes = buffer.tobytes()
                        text = self._sign_translator.translate(jpeg_bytes)
                        if text and text.upper() != "NONE":
                            logger.info("Sign detected: '{}'", text)
                            self._tts.speak(text)
                            self._add_transcript(f"[Sign] {text}")
            except Exception as e:
                logger.error("DeafMode camera error: {}", e)
                time.sleep(0.1)

    def _add_transcript(self, text: str) -> None:
        with self._lock:
            self._transcript_lines.append(text)
            if len(self._transcript_lines) > self.MAX_TRANSCRIPT_LINES:
                self._transcript_lines.pop(0)

        if self._on_transcript:
            try:
                self._on_transcript(self.transcript_lines)
            except Exception as e:
                logger.error("Transcript callback error: {}", e)
