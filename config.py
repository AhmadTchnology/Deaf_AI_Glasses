import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def _env_int(key: str, default: int) -> int:
    val = os.getenv(key)
    if val is None:
        return default
    try:
        return int(val)
    except ValueError:
        return default


def _env_float(key: str, default: float) -> float:
    val = os.getenv(key)
    if val is None:
        return default
    try:
        return float(val)
    except ValueError:
        return default


def _env_bool(key: str, default: bool) -> bool:
    val = os.getenv(key)
    if val is None:
        return default
    return val.lower() in ("true", "1", "yes")


# ── STT Provider Toggle ──
# Options: "gemini" or "nvidia"
STT_PROVIDER: str = os.getenv("STT_PROVIDER", "gemini")

# ── Gemini API ──
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# ── NVIDIA NIM API ──
NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_MODEL: str = os.getenv("NVIDIA_MODEL", "")
NVIDIA_BASE_URL: str = os.getenv("NVIDIA_BASE_URL", "grpc.nvcf.nvidia.com:443")

# ── Vision Provider Toggle ──
# Options: "gemini" or "nvidia"
VISION_PROVIDER: str = os.getenv("VISION_PROVIDER", "gemini")
NVIDIA_VLM_MODEL: str = os.getenv("NVIDIA_VLM_MODEL", "qwen/qwen2.5-vl-72b-instruct")
NVIDIA_VLM_BASE_URL: str = os.getenv("NVIDIA_VLM_BASE_URL", "https://integrate.api.nvidia.com/v1")

# ── Audio ──
AUDIO_SAMPLE_RATE: int = 16000
AUDIO_CHUNK_DURATION_S: float = 0.5
VAD_AGGRESSIVENESS: int = _env_int("VAD_AGGRESSIVENESS", 2)

# ── Display ──
DISPLAY_WIDTH: int = _env_int("DISPLAY_WIDTH", 320)
DISPLAY_HEIGHT: int = _env_int("DISPLAY_HEIGHT", 240)
DISPLAY_FPS: int = _env_int("DISPLAY_FPS", 30)
FULLSCREEN: bool = _env_bool("FULLSCREEN", True)

# ── Mode ──
DEFAULT_MODE: str = os.getenv("DEFAULT_MODE", "menu")

# ── Camera (Blind Mode) ──
CAMERA_INDEX: int = _env_int("CAMERA_INDEX", 0)
DETECTION_INTERVAL_S: float = _env_float("DETECTION_INTERVAL_S", 3.0)

# ── Paths ──
BASE_DIR = Path(__file__).parent
GESTURE_DATA_DIR = BASE_DIR / "gestures" / "data"
GESTURE_DB_PATH = str(GESTURE_DATA_DIR / "gestures.db")
GESTURE_INDEX_PATH = str(GESTURE_DATA_DIR / "index.json")
