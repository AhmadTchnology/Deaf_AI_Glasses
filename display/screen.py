import os
from abc import ABC, abstractmethod
from utils.logger import logger


class DisplayDriver(ABC):
    """Abstract display driver for different output devices."""

    @abstractmethod
    def init(self, width: int, height: int) -> None:
        ...

    @abstractmethod
    def draw_frame(self, frame_data: bytes, width: int, height: int) -> None:
        ...

    @abstractmethod
    def clear(self) -> None:
        ...

    @abstractmethod
    def shutdown(self) -> None:
        ...


class FramebufferDriver(DisplayDriver):
    """Pygame framebuffer driver for OLED/TFT displays on RPi."""

    def init(self, width: int, height: int) -> None:
        os.environ.setdefault("SDL_VIDEODRIVER", "fbcon")
        os.environ.setdefault("SDL_FBDEV", "/dev/fb0")
        logger.info("Framebuffer driver initialized: {}x{}", width, height)

    def draw_frame(self, frame_data: bytes, width: int, height: int) -> None:
        pass  # Handled by Renderer directly via pygame

    def clear(self) -> None:
        pass

    def shutdown(self) -> None:
        logger.info("Framebuffer driver shut down")


class DesktopDriver(DisplayDriver):
    """Desktop windowed driver for development/testing."""

    def init(self, width: int, height: int) -> None:
        os.environ["SDL_VIDEODRIVER"] = "x11"
        logger.info("Desktop driver initialized: {}x{}", width, height)

    def draw_frame(self, frame_data: bytes, width: int, height: int) -> None:
        pass

    def clear(self) -> None:
        pass

    def shutdown(self) -> None:
        logger.info("Desktop driver shut down")


def get_display_driver() -> DisplayDriver:
    """Auto-detect the appropriate display driver."""
    if os.path.exists("/dev/fb0"):
        return FramebufferDriver()
    return DesktopDriver()
