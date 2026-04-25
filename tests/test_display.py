import pytest
from unittest.mock import MagicMock, patch
from gestures.database import GestureEntry


class TestGestureRenderer:
    """Tests for the renderer — uses __new__ to skip pygame.init()."""

    def _make_renderer(self):
        from display.renderer import GestureRenderer
        renderer = GestureRenderer.__new__(GestureRenderer)
        renderer._screen = MagicMock()
        renderer._font = MagicMock()
        renderer._font.render.return_value = MagicMock(
            get_width=lambda: 20, get_height=lambda: 10
        )
        renderer._clock = MagicMock()
        renderer._frame_cache = {}
        return renderer

    def test_renderer_imports(self):
        from display.renderer import GestureRenderer
        assert GestureRenderer is not None

    @patch("display.renderer.pygame")
    def test_show_message(self, _mock_pg):
        renderer = self._make_renderer()
        renderer.show_message("Test")
        renderer._screen.fill.assert_called_with((0, 0, 0))
        renderer._font.render.assert_called_with("Test", True, (100, 200, 100))

    @patch("display.renderer.pygame")
    def test_clear(self, _mock_pg):
        renderer = self._make_renderer()
        renderer.clear()
        renderer._screen.fill.assert_called_with((0, 0, 0))

    @patch("display.renderer.pygame")
    def test_play_gesture_no_frames(self, _mock_pg):
        renderer = self._make_renderer()
        gesture = GestureEntry(
            word="missing", frame_dir="frames/missing",
            frame_count=0, duration_ms=200,
        )
        renderer._frame_cache["missing"] = []
        renderer.play_gesture(gesture)
        renderer._screen.fill.assert_called()
