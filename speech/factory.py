from speech.base import STTProvider
from config import STT_PROVIDER
from utils.logger import logger


def create_stt_provider() -> STTProvider:
    """Factory: create the configured STT provider."""
    provider = STT_PROVIDER.lower()

    if provider == "nvidia":
        from speech.nvidia_client import NvidiaNIMClient
        return NvidiaNIMClient()

    if provider == "gemini":
        from speech.gemini_client import GeminiSpeechClient
        return GeminiSpeechClient()

    raise ValueError(
        f"Unknown STT_PROVIDER: '{STT_PROVIDER}'. "
        "Valid options: 'gemini', 'nvidia'"
    )
