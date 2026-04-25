from abc import ABC, abstractmethod


class STTProvider(ABC):
    """Abstract base for speech-to-text providers."""

    @abstractmethod
    def transcribe(self, audio_bytes: bytes) -> str | None:
        """Transcribe audio bytes and return text. Returns None on failure."""
        ...
