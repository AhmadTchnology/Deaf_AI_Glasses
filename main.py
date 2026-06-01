import signal
import sys
import pygame
from modes.mode_manager import ModeManager, AppMode
from modes.deaf_mode import DeafMode
from modes.blind_mode import BlindMode
from display.renderer import Renderer
from utils.logger import logger
from config import DEFAULT_MODE


def main() -> None:
    logger.info("=== AI Smart Glasses v2.0 Starting ===")

    renderer = Renderer()
    mode_mgr = ModeManager()
    deaf_mode = DeafMode()
    blind_mode = BlindMode()

    # Wire callbacks: mode pipelines update the renderer
    deaf_mode.set_transcript_callback(renderer.update_deaf_transcript)
    deaf_mode.set_mode_change_callback(renderer.set_deaf_speaking)
    blind_mode.set_detection_callback(renderer.update_blind_detection)

    # Mode enter/exit handlers
    mode_mgr.on_enter(AppMode.DEAF, deaf_mode.start)
    mode_mgr.on_exit(AppMode.DEAF, deaf_mode.stop)
    mode_mgr.on_enter(AppMode.BLIND, blind_mode.start)
    mode_mgr.on_exit(AppMode.BLIND, blind_mode.stop)

    def shutdown(sig=None, frame=None) -> None:
        logger.info("Shutting down...")
        if mode_mgr.is_mode(AppMode.DEAF):
            deaf_mode.stop()
        elif mode_mgr.is_mode(AppMode.BLIND):
            blind_mode.stop()
        renderer.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Auto-enter mode if configured
    if DEFAULT_MODE == "deaf":
        mode_mgr.switch_to(AppMode.DEAF)
    elif DEFAULT_MODE == "blind":
        mode_mgr.switch_to(AppMode.BLIND)

    # ── Main event loop ──
    logger.info("Entering main event loop")
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if mode_mgr.is_mode(AppMode.MENU):
                        running = False
                    else:
                        mode_mgr.switch_to(AppMode.MENU)

                elif event.key == pygame.K_F11:
                    renderer.toggle_fullscreen()

                elif event.key == pygame.K_1 and mode_mgr.is_mode(AppMode.MENU):
                    mode_mgr.switch_to(AppMode.DEAF)

                elif event.key == pygame.K_2 and mode_mgr.is_mode(AppMode.MENU):
                    mode_mgr.switch_to(AppMode.BLIND)

                elif event.key == pygame.K_SPACE and mode_mgr.is_mode(AppMode.DEAF):
                    deaf_mode.toggle_speaking_mode()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos

                if mode_mgr.is_mode(AppMode.MENU):
                    action = renderer.get_menu_click(pos)
                    if action == "deaf":
                        mode_mgr.switch_to(AppMode.DEAF)
                    elif action == "blind":
                        mode_mgr.switch_to(AppMode.BLIND)
                    elif action == "fullscreen":
                        renderer.toggle_fullscreen()

                elif renderer.is_back_clicked(pos):
                    mode_mgr.switch_to(AppMode.MENU)

                elif mode_mgr.is_mode(AppMode.DEAF) and renderer.is_deaf_toggle_clicked(pos):
                    deaf_mode.toggle_speaking_mode()

        # ── Render current screen ──
        if mode_mgr.is_mode(AppMode.MENU):
            renderer.draw_menu()
        elif mode_mgr.is_mode(AppMode.DEAF):
            renderer.draw_deaf_screen()
        elif mode_mgr.is_mode(AppMode.BLIND):
            renderer.draw_blind_screen()

        renderer.tick()

    shutdown()


if __name__ == "__main__":
    main()
