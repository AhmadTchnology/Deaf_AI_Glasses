import threading
from audio.capture import MicrophoneStream
from audio.vad import VoiceActivityDetector
from audio.chunker import AudioChunker
from speech.factory import create_stt_provider
from utils.logger import logger
from utils.profiler import Profiler
from config import STT_PROVIDER


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
        self._running = False
        self._thread: threading.Thread | None = None
        self._transcript_lines: list[str] = []
        self._on_transcript = None
        self._lock = threading.Lock()
        logger.info("DeafMode initialized (STT: {})", STT_PROVIDER)

    def set_transcript_callback(self, callback) -> None:
        """Set callback: called with list[str] of transcript lines on each update."""
        self._on_transcript = callback

    @property
    def transcript_lines(self) -> list[str]:
        with self._lock:
            return list(self._transcript_lines)

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
        logger.info("DeafMode stopped")

    def _capture_loop(self) -> None:
        try:
            for audio_chunk in self._mic.stream_chunks():
                if not self._running:
                    break

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
