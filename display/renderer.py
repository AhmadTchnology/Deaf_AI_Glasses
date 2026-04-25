import os
import sys
import pygame
from pathlib import Path
from gestures.database import GestureEntry
from config import DISPLAY_WIDTH, DISPLAY_HEIGHT, GESTURE_DATA_DIR
from utils.logger import logger


class GestureRenderer:
    """
    Renders pixel-art gesture animations on the connected display.
    Uses Pygame in framebuffer mode (no desktop required on RPi).
    """

    def __init__(self):
        is_rpi = sys.platform == "linux" and os.path.exists("/dev/fb0")

        if is_rpi:
            os.environ.setdefault("SDL_VIDEODRIVER", "fbcon")
            os.environ.setdefault("SDL_FBDEV", "/dev/fb0")

        pygame.init()

        flags = pygame.NOFRAME if is_rpi else 0
        self._screen = pygame.display.set_mode(
            (DISPLAY_WIDTH, DISPLAY_HEIGHT), flags
        )
        pygame.display.set_caption("Smart Glasses — Gesture Preview")
        self._clock = pygame.time.Clock()
        self._font = pygame.font.SysFont("monospace", 10)
        self._frame_cache: dict[str, list[pygame.Surface]] = {}
        mode = "framebuffer" if is_rpi else "windowed"
        logger.info("Renderer initialized: {}x{} ({})", DISPLAY_WIDTH, DISPLAY_HEIGHT, mode)

    def _load_frames(self, gesture: GestureEntry) -> list[pygame.Surface]:
        """Load and cache all frames for a gesture."""
        if gesture.word in self._frame_cache:
            return self._frame_cache[gesture.word]

        frames: list[pygame.Surface] = []
        frame_dir = Path(GESTURE_DATA_DIR) / gesture.frame_dir

        for i in range(1, gesture.frame_count + 1):
            frame_path = frame_dir / f"f{i}.png"
            if not frame_path.exists():
                logger.error("Frame not found: {}", frame_path)
                continue
            img = pygame.image.load(str(frame_path)).convert()
            img = pygame.transform.scale(img, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
            frames.append(img)

        self._frame_cache[gesture.word] = frames
        return frames

    def play_gesture(self, gesture: GestureEntry) -> None:
        """Play one gesture animation, blocking until complete."""
        frames = self._load_frames(gesture)
        if not frames:
            logger.error("No frames loaded for gesture: {}", gesture.word)
            self._show_text_fallback(gesture.word)
            return

        ms_per_frame = gesture.duration_ms
        for frame_surface in frames:
            self._screen.fill((0, 0, 0))
            self._screen.blit(frame_surface, (0, 0))

            # Word label at bottom
            label = self._font.render(gesture.word.upper(), True, (180, 180, 180))
            self._screen.blit(label, (4, DISPLAY_HEIGHT - 14))

            pygame.display.flip()
            pygame.time.delay(ms_per_frame)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

    def _show_text_fallback(self, word: str) -> None:
        """Show word as text when no frames are available."""
        self._screen.fill((0, 0, 0))
        label = self._font.render(word.upper(), True, (200, 200, 100))
        x = (DISPLAY_WIDTH - label.get_width()) // 2
        y = (DISPLAY_HEIGHT - label.get_height()) // 2
        self._screen.blit(label, (x, y))
        pygame.display.flip()
        pygame.time.delay(500)

    def clear(self) -> None:
        self._screen.fill((0, 0, 0))
        pygame.display.flip()

    def show_message(self, text: str) -> None:
        """Show a short status message (e.g., 'Listening...')."""
        self._screen.fill((0, 0, 0))
        label = self._font.render(text, True, (100, 200, 100))
        self._screen.blit(label, (4, DISPLAY_HEIGHT // 2 - 6))
        pygame.display.flip()

    def shutdown(self) -> None:
        pygame.quit()
        logger.info("Renderer shut down")
