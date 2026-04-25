import io
import struct
import wave
from config import AUDIO_SAMPLE_RATE
from utils.logger import logger


class AudioChunker:
    """Assembles raw PCM audio bytes into a WAV-formatted buffer for the API."""

    def __init__(self, sample_rate: int = AUDIO_SAMPLE_RATE, channels: int = 1, sample_width: int = 2):
        self._sample_rate = sample_rate
        self._channels = channels
        self._sample_width = sample_width

    def to_wav_bytes(self, pcm_data: bytes) -> bytes:
        """Wrap raw PCM data in a WAV header."""
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(self._channels)
            wf.setsampwidth(self._sample_width)
            wf.setframerate(self._sample_rate)
            wf.writeframes(pcm_data)
        return buf.getvalue()

    def combine_chunks(self, chunks: list[bytes]) -> bytes:
        """Combine multiple PCM chunks into a single WAV buffer."""
        combined = b"".join(chunks)
        logger.debug("Combined {} chunks ({} bytes) into WAV", len(chunks), len(combined))
        return self.to_wav_bytes(combined)

    @staticmethod
    def get_rms(audio_chunk: bytes) -> float:
        """Calculate RMS amplitude for noise gating."""
        if len(audio_chunk) < 2:
            return 0.0
        samples = struct.unpack(f"<{len(audio_chunk) // 2}h", audio_chunk)
        mean_sq = sum(s * s for s in samples) / len(samples)
        return mean_sq ** 0.5
