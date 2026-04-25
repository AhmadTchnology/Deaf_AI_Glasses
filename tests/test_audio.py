import struct
import pytest
from audio.vad import VoiceActivityDetector
from audio.chunker import AudioChunker


def _generate_silent_audio(duration_ms: int = 500, sample_rate: int = 16000) -> bytes:
    """Generate silent audio (all zeros)."""
    num_samples = int(sample_rate * duration_ms / 1000)
    return struct.pack(f"<{num_samples}h", *([0] * num_samples))


def _generate_noise_audio(duration_ms: int = 500, sample_rate: int = 16000) -> bytes:
    """Generate loud noise audio (high amplitude sine-like pattern)."""
    import math
    num_samples = int(sample_rate * duration_ms / 1000)
    samples = [int(20000 * math.sin(2 * math.pi * 440 * i / sample_rate)) for i in range(num_samples)]
    return struct.pack(f"<{num_samples}h", *samples)


class TestVoiceActivityDetector:

    def test_silence_not_detected_as_speech(self):
        vad = VoiceActivityDetector(aggressiveness=2)
        audio = _generate_silent_audio()
        assert vad.is_speech(audio) is False

    def test_empty_audio_not_speech(self):
        vad = VoiceActivityDetector(aggressiveness=2)
        assert vad.is_speech(b"") is False


class TestAudioChunker:

    def test_to_wav_bytes_produces_valid_wav(self):
        chunker = AudioChunker()
        pcm = _generate_silent_audio(100)
        wav = chunker.to_wav_bytes(pcm)
        assert wav[:4] == b"RIFF"
        assert b"WAVE" in wav[:12]

    def test_combine_chunks(self):
        chunker = AudioChunker()
        chunk1 = _generate_silent_audio(50)
        chunk2 = _generate_silent_audio(50)
        wav = chunker.combine_chunks([chunk1, chunk2])
        assert wav[:4] == b"RIFF"

    def test_get_rms_silence(self):
        audio = _generate_silent_audio(100)
        rms = AudioChunker.get_rms(audio)
        assert rms == 0.0

    def test_get_rms_noise(self):
        audio = _generate_noise_audio(100)
        rms = AudioChunker.get_rms(audio)
        assert rms > 0
