import pyaudio
from typing import Generator
from utils.logger import logger
from config import AUDIO_SAMPLE_RATE, AUDIO_CHUNK_DURATION_S

CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = AUDIO_SAMPLE_RATE


class MicrophoneStream:
    """Captures audio from the default microphone as a stream of PCM chunks."""

    def __init__(self):
        self._audio = pyaudio.PyAudio()
        self._stream = None

    def open(self) -> None:
        self._stream = self._audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE,
        )
        logger.info("Microphone stream opened at {}Hz", RATE)

    def close(self) -> None:
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
        self._audio.terminate()
        logger.info("Microphone stream closed")

    def read_chunk(self) -> bytes:
        """Read one AUDIO_CHUNK_DURATION_S worth of audio."""
        frames_needed = int(RATE * AUDIO_CHUNK_DURATION_S)
        frames: list[bytes] = []
        frames_read = 0

        while frames_read < frames_needed:
            data = self._stream.read(CHUNK_SIZE, exception_on_overflow=False)
            frames.append(data)
            frames_read += CHUNK_SIZE

        return b"".join(frames)

    def stream_chunks(self) -> Generator[bytes, None, None]:
        """Continuously yield audio chunks."""
        self.open()
        try:
            while True:
                yield self.read_chunk()
        finally:
            self.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
