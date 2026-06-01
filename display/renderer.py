import os
import sys
import pygame
import numpy as np
from utils.logger import logger
from config import DISPLAY_WIDTH, DISPLAY_HEIGHT, DISPLAY_FPS, FULLSCREEN


# ── Color Palette ──
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_BG = (18, 18, 24)
CARD_BG = (30, 32, 44)
CARD_HOVER = (42, 45, 62)

# Deaf mode: warm teal accent
DEAF_ACCENT = (0, 200, 180)
DEAF_BG = (12, 28, 32)
DEAF_TEXT = (200, 240, 235)

# Blind mode: warm amber accent
BLIND_ACCENT = (255, 180, 40)
BLIND_BG = (32, 24, 12)
BLIND_TEXT = (255, 240, 210)

# UI elements
BUTTON_RADIUS = 8
TITLE_COLOR = (220, 225, 240)
SUBTITLE_COLOR = (140, 145, 165)
BACK_BTN_COLOR = (80, 85, 105)
FULLSCREEN_BTN_COLOR = (60, 65, 85)
STATUS_GREEN = (60, 220, 140)
STATUS_DIM = (80, 85, 100)


class Renderer:
    """Multi-screen Pygame renderer for 320×240 RPi5 display.

    Screens: MENU | DEAF | BLIND
    Features: fullscreen toggle, touch-friendly buttons, RPi framebuffer support.
    """

    def __init__(self):
        is_rpi = sys.platform == "linux" and os.path.exists("/dev/fb0")

        if is_rpi:
            os.environ.setdefault("SDL_VIDEODRIVER", "fbcon")
            os.environ.setdefault("SDL_FBDEV", "/dev/fb0")

        pygame.init()

        self._is_fullscreen = FULLSCREEN
        self._is_rpi = is_rpi
        self._width = DISPLAY_WIDTH
        self._height = DISPLAY_HEIGHT
        self._screen = self._create_display()
        pygame.display.set_caption("AI Smart Glasses")
        self._clock = pygame.time.Clock()
        self._fps = DISPLAY_FPS

        self._font_large = pygame.font.SysFont("arial", 22, bold=True)
        self._font_medium = pygame.font.SysFont("arial", 16)
        self._font_small = pygame.font.SysFont("arial", 12)
        self._font_tiny = pygame.font.SysFont("arial", 10)
        self._font_icon = pygame.font.SysFont("segoeuisymbol", 32)

        self._menu_buttons: list[dict] = []
        self._back_button: dict | None = None
        self._fs_button: dict | None = None

        self._deaf_transcript: list[str] = []
        self._blind_description: str = ""
        self._blind_frame: np.ndarray | None = None

        mode = "framebuffer" if is_rpi else "windowed"
        fs = "fullscreen" if self._is_fullscreen else "windowed"
        logger.info("Renderer: {}x{} ({}, {})", self._width, self._height, mode, fs)

    def _create_display(self) -> pygame.Surface:
        flags = 0
        if self._is_rpi:
            flags |= pygame.NOFRAME
        if self._is_fullscreen:
            flags |= pygame.FULLSCREEN
        return pygame.display.set_mode((self._width, self._height), flags)

    def toggle_fullscreen(self) -> None:
        self._is_fullscreen = not self._is_fullscreen
        self._screen = self._create_display()
        state = "fullscreen" if self._is_fullscreen else "windowed"
        logger.info("Display toggled: {}", state)

    # ─────────────────────────────────────────────
    #  MENU SCREEN
    # ─────────────────────────────────────────────
    def draw_menu(self) -> None:
        self._screen.fill(DARK_BG)
        self._menu_buttons.clear()

        # Title
        title = self._font_large.render("AI Smart Glasses", True, TITLE_COLOR)
        tx = (self._width - title.get_width()) // 2
        self._screen.blit(title, (tx, 16))

        # Subtitle
        sub = self._font_tiny.render("Select assistance mode", True, SUBTITLE_COLOR)
        sx = (self._width - sub.get_width()) // 2
        self._screen.blit(sub, (sx, 42))

        # ── Deaf Mode Button ──
        deaf_rect = pygame.Rect(20, 65, self._width - 40, 65)
        self._draw_mode_card(
            deaf_rect, DEAF_ACCENT, "Deaf Mode",
            "Mic + STT  transcript on screen",
            "deaf",
        )

        # ── Blind Mode Button ──
        blind_rect = pygame.Rect(20, 140, self._width - 40, 65)
        self._draw_mode_card(
            blind_rect, BLIND_ACCENT, "Blind Mode",
            "Camera  detect objects  speaker",
            "blind",
        )

        # ── Fullscreen toggle ──
        fs_rect = pygame.Rect(self._width - 70, self._height - 28, 60, 20)
        fs_label = "Window" if self._is_fullscreen else "Fullscr"
        pygame.draw.rect(self._screen, FULLSCREEN_BTN_COLOR, fs_rect, border_radius=4)
        fs_text = self._font_tiny.render(fs_label, True, SUBTITLE_COLOR)
        self._screen.blit(
            fs_text,
            (fs_rect.x + (fs_rect.w - fs_text.get_width()) // 2,
             fs_rect.y + (fs_rect.h - fs_text.get_height()) // 2),
        )
        self._fs_button = {"rect": fs_rect, "action": "fullscreen"}

        # Version tag
        ver = self._font_tiny.render("v2.0", True, STATUS_DIM)
        self._screen.blit(ver, (10, self._height - 24))

        pygame.display.flip()

    def _draw_mode_card(
        self, rect: pygame.Rect, accent: tuple, title: str, desc: str, mode_id: str,
    ) -> None:
        mouse_pos = pygame.mouse.get_pos()
        is_hover = rect.collidepoint(mouse_pos)
        bg = CARD_HOVER if is_hover else CARD_BG

        pygame.draw.rect(self._screen, bg, rect, border_radius=BUTTON_RADIUS)
        pygame.draw.rect(self._screen, accent, rect, width=2, border_radius=BUTTON_RADIUS)

        # Accent bar on the left
        bar_rect = pygame.Rect(rect.x, rect.y + 6, 4, rect.h - 12)
        pygame.draw.rect(self._screen, accent, bar_rect, border_radius=2)

        # Title
        t = self._font_medium.render(title, True, accent)
        self._screen.blit(t, (rect.x + 16, rect.y + 12))

        # Description
        d = self._font_small.render(desc, True, SUBTITLE_COLOR)
        self._screen.blit(d, (rect.x + 16, rect.y + 36))

        self._menu_buttons.append({"rect": rect, "action": mode_id})

    def get_menu_click(self, pos: tuple) -> str | None:
        """Check if a menu button was clicked. Returns mode id or action."""
        for btn in self._menu_buttons:
            if btn["rect"].collidepoint(pos):
                return btn["action"]
        if self._fs_button and self._fs_button["rect"].collidepoint(pos):
            return "fullscreen"
        return None

    # ─────────────────────────────────────────────
    #  DEAF MODE SCREEN
    # ─────────────────────────────────────────────
    def update_deaf_transcript(self, lines: list[str]) -> None:
        self._deaf_transcript = lines

    def draw_deaf_screen(self) -> None:
        self._screen.fill(DEAF_BG)

        # Header bar
        header_rect = pygame.Rect(0, 0, self._width, 30)
        pygame.draw.rect(self._screen, (20, 38, 42), header_rect)

        title = self._font_small.render("DEAF MODE", True, DEAF_ACCENT)
        self._screen.blit(title, (10, 7))

        # Status indicator
        status = self._font_tiny.render("LISTENING", True, STATUS_GREEN)
        self._screen.blit(status, (self._width - status.get_width() - 40, 10))

        # Pulsing dot
        dot_x = self._width - 28
        pulse = int(abs(pygame.time.get_ticks() % 1000 - 500) / 500 * 255)
        pygame.draw.circle(self._screen, (0, min(220, 100 + pulse), 0), (dot_x, 16), 4)

        # Back button
        self._back_button = self._draw_back_button()

        # Transcript area
        y = 40
        if not self._deaf_transcript:
            waiting = self._font_medium.render("Waiting for speech...", True, STATUS_DIM)
            wx = (self._width - waiting.get_width()) // 2
            wy = (self._height - waiting.get_height()) // 2
            self._screen.blit(waiting, (wx, wy))
        else:
            for line in self._deaf_transcript:
                wrapped = self._wrap_text(line, self._font_medium, self._width - 20)
                for wline in wrapped:
                    if y + 20 > self._height - 10:
                        break
                    rendered = self._font_medium.render(wline, True, DEAF_TEXT)
                    self._screen.blit(rendered, (10, y))
                    y += 22

        pygame.display.flip()

    # ─────────────────────────────────────────────
    #  BLIND MODE SCREEN
    # ─────────────────────────────────────────────
    def update_blind_detection(self, description: str, frame=None) -> None:
        self._blind_description = description
        if frame is not None:
            self._blind_frame = frame

    def draw_blind_screen(self) -> None:
        self._screen.fill(BLIND_BG)

        # Camera feed (top portion)
        cam_area_h = self._height - 70
        if self._blind_frame is not None:
            try:
                import cv2
                resized = cv2.resize(self._blind_frame, (self._width, cam_area_h))
                rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
                surface = pygame.surfarray.make_surface(rgb.swapaxes(0, 1))
                self._screen.blit(surface, (0, 0))
                # Dark overlay for text readability
                overlay = pygame.Surface((self._width, cam_area_h), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 80))
                self._screen.blit(overlay, (0, 0))
            except Exception as e:
                logger.error("Frame render error: {}", e)
        else:
            no_cam = self._font_medium.render("Camera starting...", True, STATUS_DIM)
            cx = (self._width - no_cam.get_width()) // 2
            self._screen.blit(no_cam, (cx, cam_area_h // 2))

        # Detection result bar at bottom
        bar_rect = pygame.Rect(0, cam_area_h, self._width, 70)
        pygame.draw.rect(self._screen, (32, 28, 16), bar_rect)
        pygame.draw.line(
            self._screen, BLIND_ACCENT, (0, cam_area_h), (self._width, cam_area_h), 2
        )

        # Mode label
        label = self._font_tiny.render("BLIND MODE", True, BLIND_ACCENT)
        self._screen.blit(label, (10, cam_area_h + 4))

        # Description text
        if self._blind_description:
            wrapped = self._wrap_text(
                self._blind_description, self._font_medium, self._width - 20,
            )
            y = cam_area_h + 20
            for wline in wrapped[:2]:
                rendered = self._font_medium.render(wline, True, BLIND_TEXT)
                self._screen.blit(rendered, (10, y))
                y += 20

        # Back button
        self._back_button = self._draw_back_button()

        pygame.display.flip()

    # ─────────────────────────────────────────────
    #  SHARED UI ELEMENTS
    # ─────────────────────────────────────────────
    def _draw_back_button(self) -> dict:
        btn_rect = pygame.Rect(self._width - 50, 4, 42, 22)
        pygame.draw.rect(self._screen, BACK_BTN_COLOR, btn_rect, border_radius=4)
        txt = self._font_tiny.render("BACK", True, WHITE)
        self._screen.blit(
            txt,
            (btn_rect.x + (btn_rect.w - txt.get_width()) // 2,
             btn_rect.y + (btn_rect.h - txt.get_height()) // 2),
        )
        return {"rect": btn_rect, "action": "back"}

    def is_back_clicked(self, pos: tuple) -> bool:
        if self._back_button and self._back_button["rect"].collidepoint(pos):
            return True
        return False

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> list[str]:
        words = text.split()
        lines: list[str] = []
        current = ""
        for word in words:
            test = f"{current} {word}".strip()
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines if lines else [text]

    def tick(self) -> None:
        self._clock.tick(self._fps)

    def clear(self) -> None:
        self._screen.fill(BLACK)
        pygame.display.flip()

    def shutdown(self) -> None:
        pygame.quit()
        logger.info("Renderer shut down")
