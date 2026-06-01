import os
import sys
import pygame
import numpy as np
from utils.logger import logger
from config import DISPLAY_WIDTH, DISPLAY_HEIGHT, DISPLAY_FPS, FULLSCREEN


# ── Neo-Brutalist Palette ──
BLACK = (5, 5, 5)
WHITE = (245, 245, 245)
DIM = (80, 80, 80)
ACCENT_ORANGE = (255, 69, 0)
ACCENT_YELLOW = (255, 215, 0)
ACCENT_GREEN = (50, 205, 50)

# Layout constants for 320x240
MAIN_W = 280
SIDE_W = 40
BORDER = 2


class Renderer:
    """Multi-screen Pygame renderer for 320×240 RPi5 display.
    
    Neo-Brutalist UI: Asymmetric 90/10 tension, zero border radius, maximum contrast.
    Screens: MENU | DEAF | BLIND
    """

    def __init__(self):
        is_rpi = sys.platform == "linux" and os.path.exists("/dev/fb0")

        if is_rpi:
            if os.environ.get("SDL_VIDEODRIVER") == "fbcon":
                del os.environ["SDL_VIDEODRIVER"]
            if "DISPLAY" not in os.environ and "WAYLAND_DISPLAY" not in os.environ:
                os.environ["DISPLAY"] = ":0"
                os.environ["WAYLAND_DISPLAY"] = "wayland-1"

        pygame.init()
        self._is_fullscreen = FULLSCREEN
        self._is_rpi = is_rpi
        self._width = DISPLAY_WIDTH
        self._height = DISPLAY_HEIGHT
        self._screen = self._create_display()
        pygame.display.set_caption("AI Smart Glasses")
        self._clock = pygame.time.Clock()
        self._fps = DISPLAY_FPS

        # Brutalist typography: bold, raw sans-serif
        self._font_title = pygame.font.SysFont("arial", 28, bold=True)
        self._font_large = pygame.font.SysFont("arial", 20, bold=True)
        self._font_medium = pygame.font.SysFont("arial", 14, bold=True)
        self._font_small = pygame.font.SysFont("arial", 12, bold=True)
        self._font_icon = pygame.font.SysFont("arial", 18, bold=True)

        self._menu_buttons: list[dict] = []
        self._back_button: dict | None = None
        self._fs_button: dict | None = None
        self._toggle_button: dict | None = None

        self._deaf_transcript: list[str] = []
        self._is_deaf_speaking: bool = False
        self._blind_description: str = ""
        self._blind_frame: np.ndarray | None = None

        logger.info("Renderer: {}x{} Neo-Brutalist initialized", self._width, self._height)

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

    # ─────────────────────────────────────────────
    #  MENU SCREEN (Asymmetric 90/10)
    # ─────────────────────────────────────────────
    def draw_menu(self) -> None:
        self._screen.fill(BLACK)
        self._menu_buttons.clear()
        
        mouse_pos = pygame.mouse.get_pos()

        # ── Main 90% Area ──
        # Title block
        pygame.draw.rect(self._screen, ACCENT_ORANGE, (0, 0, MAIN_W, 40))
        t = self._font_title.render("SYS.INIT", True, BLACK)
        self._screen.blit(t, (10, 5))

        # Deaf Mode Block
        deaf_rect = pygame.Rect(0, 45, MAIN_W, 90)
        self._draw_brutalist_block(deaf_rect, "DEAF", "MIC > STT > TEXT", ACCENT_ORANGE, "deaf", mouse_pos)

        # Blind Mode Block
        blind_rect = pygame.Rect(0, 140, MAIN_W, 90)
        self._draw_brutalist_block(blind_rect, "BLIND", "CAM > VLM > SPK", ACCENT_YELLOW, "blind", mouse_pos)

        # ── Side 10% Strip (Tension) ──
        side_rect = pygame.Rect(MAIN_W + 5, 0, SIDE_W - 5, self._height)
        pygame.draw.rect(self._screen, DIM, side_rect)
        
        # FS Button (rotated sideways conceptually, or just simple text)
        fs_rect = pygame.Rect(MAIN_W + 5, self._height - 60, SIDE_W - 5, 60)
        is_fs_hover = fs_rect.collidepoint(mouse_pos)
        pygame.draw.rect(self._screen, WHITE if is_fs_hover else BLACK, fs_rect, BORDER)
        
        fs_text = self._font_small.render("FS", True, BLACK if is_fs_hover else WHITE)
        self._screen.blit(fs_text, (fs_rect.x + 10, fs_rect.y + 20))
        self._fs_button = {"rect": fs_rect, "action": "fullscreen"}

        pygame.display.flip()

    def _draw_brutalist_block(self, rect: pygame.Rect, title: str, sub: str, color: tuple, action: str, mouse_pos: tuple):
        is_hover = rect.collidepoint(mouse_pos)
        
        # Solid fill if hover, outline if not
        if is_hover:
            pygame.draw.rect(self._screen, color, rect)
            t_color = BLACK
        else:
            pygame.draw.rect(self._screen, color, rect, BORDER)
            t_color = color

        t = self._font_title.render(title, True, t_color)
        self._screen.blit(t, (rect.x + 15, rect.y + 15))
        
        s = self._font_small.render(sub, True, t_color)
        self._screen.blit(s, (rect.x + 15, rect.y + 55))
        
        # Add a harsh geometric indicator
        pygame.draw.rect(self._screen, t_color, (rect.right - 40, rect.y + 35, 20, 20))

        self._menu_buttons.append({"rect": rect, "action": action})

    def get_menu_click(self, pos: tuple) -> str | None:
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

    def set_deaf_speaking(self, is_speaking: bool) -> None:
        self._is_deaf_speaking = is_speaking

    def draw_deaf_screen(self) -> None:
        self._screen.fill(BLACK)

        # Harsh top bar
        bar_color = ACCENT_GREEN if self._is_deaf_speaking else ACCENT_ORANGE
        pygame.draw.rect(self._screen, bar_color, (0, 0, self._width, 30))
        
        mode_text = "DEAF_MODE [SIGNING]" if self._is_deaf_speaking else "DEAF_MODE [HEARING]"
        title = self._font_large.render(mode_text, True, BLACK)
        self._screen.blit(title, (5, 5))

        # Pulsing square instead of circle
        pulse = int(abs(pygame.time.get_ticks() % 1000 - 500) / 500 * 255)
        pulse_color = (0, pulse, 0) if self._is_deaf_speaking else (pulse, 0, 0)
        pygame.draw.rect(self._screen, pulse_color, (self._width - 80, 5, 20, 20))
        
        self._back_button = self._draw_brutalist_back()

        # Draw toggle button at the bottom
        btn_rect = pygame.Rect(10, self._height - 40, 140, 30)
        mouse_pos = pygame.mouse.get_pos()
        is_hover = btn_rect.collidepoint(mouse_pos)
        
        btn_bg = WHITE if is_hover else BLACK
        btn_fg = BLACK if is_hover else WHITE
        
        pygame.draw.rect(self._screen, btn_bg, btn_rect)
        pygame.draw.rect(self._screen, btn_fg, btn_rect, BORDER)
        
        btn_text = "USE CAMERA" if not self._is_deaf_speaking else "USE MIC"
        txt = self._font_small.render(btn_text, True, btn_fg)
        txt_rect = txt.get_rect(center=btn_rect.center)
        self._screen.blit(txt, txt_rect)
        self._toggle_button = {"rect": btn_rect, "action": "toggle"}

        # Transcript area - Massive text
        y = 40
        if not self._deaf_transcript:
            waiting = self._font_large.render("AWAITING_INPUT...", True, DIM)
            self._screen.blit(waiting, (10, self._height // 2 - 20))
        else:
            # We want to display the latest text massively
            for i, line in enumerate(reversed(self._deaf_transcript[-4:])):
                # Fade out older text (brutalist style = just dimmer colors)
                color = WHITE if i == 0 else DIM
                wrapped = self._wrap_text(line, self._font_large, self._width - 20)
                
                for wline in reversed(wrapped):
                    rendered = self._font_large.render(wline, True, color)
                    # Draw from bottom up. Adjust y_pos to stay above the toggle button.
                    y_pos = self._height - 80 - (i * 50)
                    if y_pos > 30:
                        self._screen.blit(rendered, (10, y_pos))

        pygame.display.flip()

    # ─────────────────────────────────────────────
    #  BLIND MODE SCREEN
    # ─────────────────────────────────────────────
    def update_blind_detection(self, description: str, frame=None) -> None:
        self._blind_description = description
        if frame is not None:
            self._blind_frame = frame

    def draw_blind_screen(self) -> None:
        self._screen.fill(BLACK)

        cam_h = 140
        # Camera feed
        if self._blind_frame is not None:
            try:
                import cv2
                resized = cv2.resize(self._blind_frame, (self._width, cam_h))
                # Brutalist effect: convert to grayscale and high contrast if we want, but let's just show it
                rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
                surface = pygame.surfarray.make_surface(rgb.swapaxes(0, 1))
                self._screen.blit(surface, (0, 0))
            except Exception:
                pass
        
        # Harsh border around camera
        pygame.draw.rect(self._screen, ACCENT_YELLOW, (0, 0, self._width, cam_h), BORDER)
        
        # Mode tag overlapping the camera
        pygame.draw.rect(self._screen, ACCENT_YELLOW, (0, cam_h - 25, 120, 25))
        lbl = self._font_medium.render("BLIND_MODE", True, BLACK)
        self._screen.blit(lbl, (5, cam_h - 20))

        # Description text below
        if self._blind_description:
            wrapped = self._wrap_text(self._blind_description, self._font_large, self._width - 10)
            y = cam_h + 10
            for wline in wrapped[:3]:
                rendered = self._font_large.render(wline, True, WHITE)
                self._screen.blit(rendered, (5, y))
                y += 25

        self._back_button = self._draw_brutalist_back()
        pygame.display.flip()

    # ─────────────────────────────────────────────
    #  SHARED UI ELEMENTS
    # ─────────────────────────────────────────────
    def _draw_brutalist_back(self) -> dict:
        btn_rect = pygame.Rect(self._width - 45, 0, 45, 30)
        mouse_pos = pygame.mouse.get_pos()
        is_hover = btn_rect.collidepoint(mouse_pos)
        
        bg = WHITE if is_hover else BLACK
        fg = BLACK if is_hover else WHITE
        
        pygame.draw.rect(self._screen, bg, btn_rect)
        pygame.draw.rect(self._screen, fg, btn_rect, BORDER)
        
        txt = self._font_medium.render("X", True, fg)
        self._screen.blit(txt, (btn_rect.x + 15, btn_rect.y + 6))
        return {"rect": btn_rect, "action": "back"}

    def is_back_clicked(self, pos: tuple) -> bool:
        if self._back_button and self._back_button["rect"].collidepoint(pos):
            return True
        return False

    def is_deaf_toggle_clicked(self, pos: tuple) -> bool:
        if self._toggle_button and self._toggle_button["rect"].collidepoint(pos):
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
