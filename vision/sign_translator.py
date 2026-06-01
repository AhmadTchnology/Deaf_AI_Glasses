import base64
import time
from abc import ABC, abstractmethod
from utils.logger import logger
from config import (
    VISION_PROVIDER, GEMINI_API_KEY, GEMINI_MODEL,
    NVIDIA_API_KEY, NVIDIA_VLM_MODEL, NVIDIA_VLM_BASE_URL,
)

SIGN_PROMPT = (
    "You are an AI assistant translating sign language for a deaf user. "
    "This is a single frame captured from a live video stream. "
    "Look at the hand gestures and translate the current sign or fingerspelled letter to spoken English. "
    "CRITICAL: You must respond with ONLY the exact translated word or letter. "
    "Do NOT include phrases like 'The letter', do NOT include punctuation, and do NOT provide any analysis. "
    "For example, if the sign is for the letter F, output exactly: F\n"
    "If no hands are visible or no gesture is being made, output exactly: NONE"
)


class SignProvider(ABC):
    """Abstract base for sign language translation providers."""

    @abstractmethod
    def translate(self, image_bytes: bytes) -> str | None:
        """Analyze image and return translated text. Returns None on failure."""
        ...


class GeminiSignClient(SignProvider):
    """Uses Gemini multimodal API for sign language translation."""

    def __init__(self):
        from google import genai
        self._client = genai.Client(api_key=GEMINI_API_KEY)
        self._model = GEMINI_MODEL
        logger.info("Gemini Sign Translator initialized: {}", self._model)

    def translate(self, image_bytes: bytes, retries: int = 2) -> str | None:
        from google import genai

        contents = [
            genai.types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            SIGN_PROMPT,
        ]

        for attempt in range(retries):
            try:
                response = self._client.models.generate_content(
                    model=self._model,
                    contents=contents,
                )
                result = response.text.strip()
                logger.debug("Sign translation result: '{}'", result)
                return result
            except Exception as e:
                wait = 2 ** attempt
                logger.warning(
                    "Gemini Sign attempt {}/{} failed: {}. Retry in {}s",
                    attempt + 1, retries, e, wait,
                )
                time.sleep(wait)

        logger.error("All Gemini Sign retries exhausted")
        return None


class NvidiaVLMSignClient(SignProvider):
    """Uses NVIDIA NIM API with VLM models for sign language translation."""

    def __init__(self):
        try:
            from openai import OpenAI
            self._client = OpenAI(
                api_key=NVIDIA_API_KEY,
                base_url=NVIDIA_VLM_BASE_URL,
            )
        except ImportError:
            raise RuntimeError(
                "openai package required for NVIDIA VLM. "
                "Run: pip install openai"
            )
        self._model = NVIDIA_VLM_MODEL
        logger.info("NVIDIA VLM Sign Translator initialized: {}", self._model)

    def translate(self, image_bytes: bytes, retries: int = 2) -> str | None:
        b64_image = base64.b64encode(image_bytes).decode("utf-8")

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{b64_image}",
                        },
                    },
                    {"type": "text", "text": SIGN_PROMPT},
                ],
            }
        ]

        for attempt in range(retries):
            try:
                response = self._client.chat.completions.create(
                    model=self._model,
                    messages=messages,
                    max_tokens=60,
                    temperature=0.2,
                )
                result = response.choices[0].message.content.strip()
                logger.debug("NVIDIA VLM Sign result: '{}'", result)
                return result
            except Exception as e:
                wait = 2 ** attempt
                logger.warning(
                    "NVIDIA VLM Sign attempt {}/{} failed: {}. Retry in {}s",
                    attempt + 1, retries, e, wait,
                )
                time.sleep(wait)

        logger.error("All NVIDIA VLM Sign retries exhausted")
        return None


def create_sign_provider() -> SignProvider:
    """Factory: create the configured sign language provider."""
    provider = VISION_PROVIDER.lower()

    if provider == "gemini":
        return GeminiSignClient()

    if provider == "nvidia":
        return NvidiaVLMSignClient()

    raise ValueError(
        f"Unknown VISION_PROVIDER: '{VISION_PROVIDER}'. "
        "Valid options: 'gemini', 'nvidia'"
    )
