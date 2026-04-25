import base64
import time
from google import genai
from speech.base import STTProvider
from config import GEMINI_API_KEY, GEMINI_MODEL
from utils.logger import logger

TRANSCRIPTION_PROMPT = (
    "Transcribe the speech in this audio exactly. "
    "Return only the spoken words, no punctuation, "
    "no commentary, no formatting."
)


class GeminiSpeechClient(STTProvider):
    """Sends audio chunks to Gemini and returns transcript text."""

    def __init__(self):
        self._client = genai.Client(api_key=GEMINI_API_KEY)
        self._model = GEMINI_MODEL
        logger.info("Gemini STT initialized with model: {}", self._model)

    def transcribe(self, audio_bytes: bytes, retries: int = 3) -> str | None:
        contents = [
            genai.types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"),
            TRANSCRIPTION_PROMPT,
        ]

        for attempt in range(retries):
            try:
                response = self._client.models.generate_content(
                    model=self._model,
                    contents=contents,
                )
                transcript = response.text.strip().lower()
                logger.debug("Transcript: '{}'", transcript)
                return transcript
            except Exception as e:
                wait = 2 ** attempt
                logger.warning(
                    "Gemini attempt {}/{} failed: {}. Retrying in {}s",
                    attempt + 1, retries, e, wait,
                )
                time.sleep(wait)

        logger.error("All Gemini retries exhausted")
        return None
