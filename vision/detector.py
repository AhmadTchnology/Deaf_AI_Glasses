import base64
import time
from abc import ABC, abstractmethod
from utils.logger import logger
from config import (
    VISION_PROVIDER, GEMINI_API_KEY, GEMINI_MODEL,
    NVIDIA_API_KEY, NVIDIA_VLM_MODEL, NVIDIA_VLM_BASE_URL,
)

DETECTION_PROMPT = (
    "You are an assistive device for a blind person. "
    "Describe the main objects directly in front of the user. "
    "Be very concise — max 10 words. Focus on obstacles, people, and important items. "
    "Example: 'Chair ahead, door on left, person approaching'"
)


class VisionProvider(ABC):
    """Abstract base for vision/object detection providers."""

    @abstractmethod
    def detect(self, image_bytes: bytes) -> str | None:
        """Analyze image and return a short description. Returns None on failure."""
        ...


class GeminiVisionClient(VisionProvider):
    """Uses Gemini multimodal API for object detection."""

    def __init__(self):
        from google import genai
        self._client = genai.Client(api_key=GEMINI_API_KEY)
        self._model = GEMINI_MODEL
        logger.info("Gemini Vision initialized: {}", self._model)

    def detect(self, image_bytes: bytes, retries: int = 2) -> str | None:
        from google import genai

        contents = [
            genai.types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            DETECTION_PROMPT,
        ]

        for attempt in range(retries):
            try:
                response = self._client.models.generate_content(
                    model=self._model,
                    contents=contents,
                )
                result = response.text.strip()
                logger.debug("Vision result: '{}'", result)
                return result
            except Exception as e:
                wait = 2 ** attempt
                logger.warning(
                    "Gemini Vision attempt {}/{} failed: {}. Retry in {}s",
                    attempt + 1, retries, e, wait,
                )
                time.sleep(wait)

        logger.error("All Gemini Vision retries exhausted")
        return None


class NvidiaVLMClient(VisionProvider):
    """Uses NVIDIA NIM API with VLM models (e.g., Qwen2.5-VL) for object detection."""

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
        logger.info("NVIDIA VLM initialized: {}", self._model)

    def detect(self, image_bytes: bytes, retries: int = 2) -> str | None:
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
                    {"type": "text", "text": DETECTION_PROMPT},
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
                logger.debug("NVIDIA VLM result: '{}'", result)
                return result
            except Exception as e:
                wait = 2 ** attempt
                logger.warning(
                    "NVIDIA VLM attempt {}/{} failed: {}. Retry in {}s",
                    attempt + 1, retries, e, wait,
                )
                time.sleep(wait)

        logger.error("All NVIDIA VLM retries exhausted")
        return None


def create_vision_provider() -> VisionProvider:
    """Factory: create the configured vision provider."""
    provider = VISION_PROVIDER.lower()

    if provider == "gemini":
        return GeminiVisionClient()

    if provider == "nvidia":
        return NvidiaVLMClient()

    raise ValueError(
        f"Unknown VISION_PROVIDER: '{VISION_PROVIDER}'. "
        "Valid options: 'gemini', 'nvidia'"
    )
