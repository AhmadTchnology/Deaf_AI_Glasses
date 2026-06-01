import pytest
from unittest.mock import MagicMock, patch


class TestRenderer:
    """Tests for the v2.0 multi-screen Renderer."""

    def _make_renderer(self):
        from display.renderer import Renderer
        renderer = Renderer.__new__(Renderer)
        renderer._screen = MagicMock()
        renderer._clock = MagicMock()
        renderer._width = 320
        renderer._height = 240
        renderer._fps = 30
        renderer._is_fullscreen = False
        renderer._is_rpi = False
        renderer._menu_buttons = []
        renderer._back_button = None
        renderer._fs_button = None
        renderer._deaf_transcript = []
        renderer._blind_description = ""
        renderer._blind_frame = None
        renderer._font_title = MagicMock()
        renderer._font_large = MagicMock()
        renderer._font_medium = MagicMock()
        renderer._font_small = MagicMock()
        renderer._font_icon = MagicMock()
        for f in (
            renderer._font_title, renderer._font_large, renderer._font_medium,
            renderer._font_small, renderer._font_icon,
        ):
            f.render.return_value = MagicMock(
                get_width=lambda: 40, get_height=lambda: 16,
            )
            f.size.return_value = (40, 16)
        return renderer

    def test_renderer_imports(self):
        from display.renderer import Renderer
        assert Renderer is not None

    @patch("display.renderer.pygame")
    def test_clear(self, _mock_pg):
        renderer = self._make_renderer()
        renderer.clear()
        renderer._screen.fill.assert_called_with((5, 5, 5))

    @patch("display.renderer.pygame")
    def test_draw_menu(self, mock_pg):
        mock_pg.mouse.get_pos.return_value = (0, 0)
        mock_pg.Rect = MagicMock(side_effect=lambda *a: MagicMock(collidepoint=lambda p: False))
        mock_pg.time.get_ticks.return_value = 500
        renderer = self._make_renderer()
        renderer.draw_menu()
        renderer._screen.fill.assert_called()
        assert len(renderer._menu_buttons) == 2

    @patch("display.renderer.pygame")
    def test_menu_click_detection(self, mock_pg):
        renderer = self._make_renderer()
        deaf_rect = MagicMock()
        deaf_rect.collidepoint.return_value = True
        renderer._menu_buttons = [{"rect": deaf_rect, "action": "deaf"}]
        renderer._fs_button = None
        result = renderer.get_menu_click((100, 100))
        assert result == "deaf"

    @patch("display.renderer.pygame")
    def test_menu_click_miss(self, mock_pg):
        renderer = self._make_renderer()
        deaf_rect = MagicMock()
        deaf_rect.collidepoint.return_value = False
        renderer._menu_buttons = [{"rect": deaf_rect, "action": "deaf"}]
        renderer._fs_button = None
        result = renderer.get_menu_click((0, 0))
        assert result is None

    @patch("display.renderer.pygame")
    def test_update_deaf_transcript(self, _mock_pg):
        renderer = self._make_renderer()
        renderer.update_deaf_transcript(["hello world", "testing"])
        assert renderer._deaf_transcript == ["hello world", "testing"]

    @patch("display.renderer.pygame")
    def test_draw_deaf_screen(self, mock_pg):
        mock_pg.Rect = MagicMock(side_effect=lambda *a: MagicMock(
            collidepoint=lambda p: False, x=0, y=0, w=42, h=22
        ))
        mock_pg.time.get_ticks.return_value = 500
        renderer = self._make_renderer()
        renderer._deaf_transcript = ["hello world"]
        renderer.draw_deaf_screen()
        renderer._screen.fill.assert_called()

    @patch("display.renderer.pygame")
    def test_update_blind_detection(self, _mock_pg):
        renderer = self._make_renderer()
        renderer.update_blind_detection("Chair ahead, door on left")
        assert renderer._blind_description == "Chair ahead, door on left"

    @patch("display.renderer.pygame")
    def test_back_button_click(self, _mock_pg):
        renderer = self._make_renderer()
        back_rect = MagicMock()
        back_rect.collidepoint.return_value = True
        renderer._back_button = {"rect": back_rect, "action": "back"}
        assert renderer.is_back_clicked((280, 10)) is True

    @patch("display.renderer.pygame")
    def test_back_button_miss(self, _mock_pg):
        renderer = self._make_renderer()
        back_rect = MagicMock()
        back_rect.collidepoint.return_value = False
        renderer._back_button = {"rect": back_rect, "action": "back"}
        assert renderer.is_back_clicked((0, 0)) is False

    @patch("display.renderer.pygame")
    def test_wrap_text_short(self, _mock_pg):
        renderer = self._make_renderer()
        font = MagicMock()
        font.size.return_value = (50, 16)
        result = renderer._wrap_text("hello world", font, 300)
        assert len(result) >= 1
        assert "hello" in result[0]

    @patch("display.renderer.pygame")
    def test_wrap_text_long(self, _mock_pg):
        renderer = self._make_renderer()
        font = MagicMock()
        call_count = [0]
        def size_side_effect(text):
            return (len(text) * 10, 16)
        font.size.side_effect = size_side_effect
        result = renderer._wrap_text(
            "this is a very long sentence that should wrap around", font, 100,
        )
        assert len(result) > 1
