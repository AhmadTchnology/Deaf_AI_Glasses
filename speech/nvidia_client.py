import io
import time
import wave
from speech.base import STTProvider
from config import NVIDIA_API_KEY, NVIDIA_MODEL, NVIDIA_BASE_URL, AUDIO_SAMPLE_RATE
from utils.logger import logger

try:
    import riva.client
    RIVA_AVAILABLE = True
except ImportError:
    RIVA_AVAILABLE = False


class NvidiaNIMClient(STTProvider):
    """
    NVIDIA NIM STT client using the Riva gRPC API.

    Supports nemotron-asr-streaming and parakeet-tdt ASR models.
    Audio input: 16-bit mono PCM WAV at 16kHz (matches project config).
    """

    def __init__(self):
        if not RIVA_AVAILABLE:
            raise ImportError(
                "nvidia-riva-client is required for NVIDIA NIM STT. "
                "Install with: pip install nvidia-riva-client"
            )

        metadata = [
            ("authorization", f"Bearer {NVIDIA_API_KEY}"),
            ("function-id", NVIDIA_MODEL),
        ]
        self._auth = riva.client.Auth(
            None,
            use_ssl=True,
            uri=NVIDIA_BASE_URL,
            metadata_args=metadata,
        )
        self._asr_service = riva.client.ASRService(self._auth)
        logger.info("NVIDIA NIM STT initialized — model: {}, endpoint: {}", NVIDIA_MODEL, NVIDIA_BASE_URL)

    def transcribe(self, audio_bytes: bytes, retries: int = 3) -> str | None:
        """
        Transcribe WAV audio bytes using NVIDIA NIM ASR.
        Returns lowercase transcript or None on failure.
        """
        for attempt in range(retries):
            try:
                config = riva.client.RecognitionConfig(
                    encoding=riva.client.AudioEncoding.LINEAR_PCM,
                    sample_rate_hertz=AUDIO_SAMPLE_RATE,
                    language_code="en-US",
                    max_alternatives=1,
                    audio_channel_count=1,
                    # model=NVIDIA_MODEL,
                )

                response = self._asr_service.offline_recognize(
                    audio_bytes,
                    config,
                )

                if not response.results:
                    logger.debug("NVIDIA NIM: no speech detected")
                    return None

                transcript = " ".join(
                    alt.transcript
                    for result in response.results
                    for alt in result.alternatives
                    if alt.transcript.strip()
                ).strip().lower()

                if not transcript:
                    return None

                logger.debug("NVIDIA NIM transcript: '{}'", transcript)
                return transcript

            except Exception as e:
                wait = 2 ** attempt
                logger.warning(
                    "NVIDIA NIM attempt {}/{} failed: {}. Retrying in {}s",
                    attempt + 1, retries, e, wait,
                )
                time.sleep(wait)

        logger.error("All NVIDIA NIM retries exhausted")
        return None
