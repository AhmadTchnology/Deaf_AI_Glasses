import webrtcvad
from config import AUDIO_SAMPLE_RATE, VAD_AGGRESSIVENESS

FRAME_DURATION_MS = 30
SPEECH_THRESHOLD = 0.4


class VoiceActivityDetector:
    """Filters audio chunks — returns True if voice is detected."""

    def __init__(self, aggressiveness: int = VAD_AGGRESSIVENESS):
        self._vad = webrtcvad.Vad(aggressiveness)

    def is_speech(self, audio_chunk: bytes) -> bool:
        """Check if at least SPEECH_THRESHOLD of frames contain speech."""
        frame_size = int(AUDIO_SAMPLE_RATE * FRAME_DURATION_MS / 1000) * 2
        speech_frames = 0
        total_frames = 0

        for i in range(0, len(audio_chunk) - frame_size, frame_size):
            frame = audio_chunk[i : i + frame_size]
            if len(frame) < frame_size:
                break
            if self._vad.is_speech(frame, AUDIO_SAMPLE_RATE):
                speech_frames += 1
            total_frames += 1

        if total_frames == 0:
            return False

        return (speech_frames / total_frames) > SPEECH_THRESHOLD
