from enum import Enum
from typing import Callable
from utils.logger import logger


class AppMode(Enum):
    MENU = "menu"
    DEAF = "deaf"
    BLIND = "blind"


class ModeManager:
    """State machine for application mode transitions.

    Manages the current mode and notifies listeners when modes change.
    Thread-safe via simple flag — actual mode logic runs on the main thread.
    """

    def __init__(self):
        self._current_mode = AppMode.MENU
        self._on_enter_callbacks: dict[AppMode, list[Callable]] = {
            mode: [] for mode in AppMode
        }
        self._on_exit_callbacks: dict[AppMode, list[Callable]] = {
            mode: [] for mode in AppMode
        }
        logger.info("ModeManager initialized, starting in MENU")

    @property
    def current_mode(self) -> AppMode:
        return self._current_mode

    def on_enter(self, mode: AppMode, callback: Callable) -> None:
        self._on_enter_callbacks[mode].append(callback)

    def on_exit(self, mode: AppMode, callback: Callable) -> None:
        self._on_exit_callbacks[mode].append(callback)

    def switch_to(self, new_mode: AppMode) -> None:
        if new_mode == self._current_mode:
            return

        old_mode = self._current_mode
        logger.info("Mode transition: {} → {}", old_mode.value, new_mode.value)

        for cb in self._on_exit_callbacks[old_mode]:
            try:
                cb()
            except Exception as e:
                logger.error("Error in exit callback for {}: {}", old_mode.value, e)

        self._current_mode = new_mode

        for cb in self._on_enter_callbacks[new_mode]:
            try:
                cb()
            except Exception as e:
                logger.error("Error in enter callback for {}: {}", new_mode.value, e)

    def is_mode(self, mode: AppMode) -> bool:
        return self._current_mode == mode
