import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── STT Provider Toggle ──
# Options: "gemini" or "nvidia"
STT_PROVIDER: str = os.getenv("STT_PROVIDER")

# ── Gemini API ──
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL")

# ── NVIDIA NIM API ──
NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY")
NVIDIA_MODEL: str = os.getenv("NVIDIA_MODEL")
NVIDIA_BASE_URL: str = os.getenv("NVIDIA_BASE_URL", "grpc.nvcf.nvidia.com:443")

# ── Audio ──
AUDIO_SAMPLE_RATE: int = 16000
AUDIO_CHUNK_DURATION_S: float = 0.5
VAD_AGGRESSIVENESS: int = int(os.getenv("VAD_AGGRESSIVENESS"))

# ── Display ──
DISPLAY_WIDTH: int = int(os.getenv("DISPLAY_WIDTH"))
DISPLAY_HEIGHT: int = int(os.getenv("DISPLAY_HEIGHT"))
DISPLAY_FPS: int = int(os.getenv("DISPLAY_FPS"))

# ── Paths ──
BASE_DIR = Path(__file__).parent
GESTURE_DATA_DIR = BASE_DIR / "gestures" / "data"
GESTURE_DB_PATH = str(GESTURE_DATA_DIR / "gestures.db")
GESTURE_INDEX_PATH = str(GESTURE_DATA_DIR / "index.json")
