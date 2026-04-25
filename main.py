import signal
import sys
from audio.capture import MicrophoneStream
from audio.vad import VoiceActivityDetector
from audio.chunker import AudioChunker
from speech.factory import create_stt_provider
from nlp.processor import TextProcessor
from gestures.database import GestureDatabase
from gestures.queue_manager import GestureQueueManager
from display.renderer import GestureRenderer
from utils.logger import logger
from utils.profiler import Profiler
from config import GESTURE_INDEX_PATH, STT_PROVIDER


def main() -> None:
    logger.info("=== AI Smart Glasses Starting ===")

    # Initialize all components
    mic = MicrophoneStream()
    vad = VoiceActivityDetector()
    chunker = AudioChunker()
    stt = create_stt_provider()
    nlp_proc = TextProcessor()
    db = GestureDatabase()
    renderer = GestureRenderer()
    queue_mgr = GestureQueueManager(db, renderer)
    profiler = Profiler()

    # Import gestures on first run
    if not db.get_all_words():
        logger.info("Importing gesture database from index...")
        db.import_from_json(GESTURE_INDEX_PATH)

    queue_mgr.start()
    renderer.show_message("Listening...")

    def shutdown(sig, frame) -> None:
        logger.info("Shutting down...")
        queue_mgr.stop()
        renderer.shutdown()
        db.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Main pipeline loop
    logger.info("Entering main pipeline loop")
    try:
        for audio_chunk in mic.stream_chunks():
            # Stage 1: Voice Activity Detection
            profiler.start("vad")
            is_speech = vad.is_speech(audio_chunk)
            profiler.end("vad")

            if not is_speech:
                continue

            logger.debug("Speech detected — sending to STT ({})", STT_PROVIDER)

            # Stage 2: Convert to WAV and transcribe
            profiler.start("stt")
            wav_data = chunker.to_wav_bytes(audio_chunk)
            transcript = stt.transcribe(wav_data)
            profiler.end("stt")

            if not transcript:
                continue

            # Stage 3: NLP processing
            profiler.start("nlp")
            keywords = nlp_proc.process(transcript)
            profiler.end("nlp")

            if not keywords:
                continue

            # Stage 4: Queue for display
            queue_mgr.enqueue(keywords)
            profiler.log_summary()

    except Exception as e:
        logger.exception("Fatal error in main loop: {}", e)
        shutdown(None, None)


if __name__ == "__main__":
    main()
