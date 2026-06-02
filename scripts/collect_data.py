import os
import cv2
import numpy as np
import sys
import pygame

# Add parent directory to path so we can import vision
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from vision.camera import CameraStream
from vision.mediapipe_tracker import MediaPipeTracker
from utils.logger import logger

# Configuration
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sequences")
ACTIONS = np.array(["hello", "thank_you", "please", "help"])
no_sequences = 30     # 30 videos worth of data per action
sequence_length = 30  # 30 frames per video

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480


def ensure_dirs():
    """Create directory structure for data collection."""
    for action in ACTIONS:
        for sequence in range(no_sequences):
            try:
                os.makedirs(os.path.join(DATA_PATH, action, str(sequence)))
            except FileExistsError:
                pass


def frame_to_surface(frame):
    """Convert an OpenCV BGR frame to a pygame Surface."""
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_rgb = cv2.resize(frame_rgb, (WINDOW_WIDTH, WINDOW_HEIGHT))
    # numpy array (H, W, 3) -> pygame surface
    return pygame.surfarray.make_surface(np.transpose(frame_rgb, (1, 0, 2)))


def draw_text(screen, text, pos, size=32, color=(0, 255, 0)):
    """Draw text onto the pygame screen."""
    font = pygame.font.SysFont("consolas", size)
    surface = font.render(text, True, color)
    screen.blit(surface, pos)


def collect_data():
    ensure_dirs()
    logger.info("Starting data collection...")

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Data Collection")
    clock = pygame.time.Clock()

    tracker = MediaPipeTracker(sequence_length=sequence_length)

    with CameraStream() as cam:
        for action in ACTIONS:
            # ── Wait screen: press S to start, Q to quit ──
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        tracker.close()
                        pygame.quit()
                        return
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_s:
                            waiting = False
                        elif event.key == pygame.K_q:
                            tracker.close()
                            pygame.quit()
                            return

                frame = cam.capture_frame()
                if frame is None:
                    continue

                surf = frame_to_surface(frame)
                screen.blit(surf, (0, 0))
                draw_text(screen, f"Ready to collect: {action}", (20, 30), 28, (0, 255, 0))
                draw_text(screen, "Press S to Start, Q to Quit", (20, 70), 24, (0, 255, 255))
                pygame.display.flip()
                clock.tick(30)

            # ── Loop through sequences (videos) ──
            for sequence in range(no_sequences):
                for frame_num in range(sequence_length):
                    # Handle quit events during collection
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            tracker.close()
                            pygame.quit()
                            return
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                            tracker.close()
                            pygame.quit()
                            return

                    frame = cam.capture_frame()
                    if frame is None:
                        continue

                    # Extract landmarks
                    processed_frame, landmarks = tracker.process_frame(frame)

                    if landmarks is None:
                        landmarks = np.zeros(126)  # Fallback if no hands

                    # Display
                    surf = frame_to_surface(processed_frame)
                    screen.blit(surf, (0, 0))

                    if frame_num == 0:
                        draw_text(screen, "STARTING COLLECTION", (100, 200), 36, (0, 255, 0))
                        draw_text(screen, f"{action}  Video {sequence}/{no_sequences}", (15, 10), 22, (255, 80, 80))
                        pygame.display.flip()
                        pygame.time.wait(1500)  # 1.5 second pause between sequences
                    else:
                        draw_text(screen, f"{action}  Video {sequence}/{no_sequences}  Frame {frame_num}/{sequence_length}", (15, 10), 22, (255, 80, 80))
                        pygame.display.flip()

                    # Save keypoints
                    npy_path = os.path.join(DATA_PATH, action, str(sequence), str(frame_num))
                    np.save(npy_path, landmarks)

                    clock.tick(30)

    tracker.close()
    pygame.quit()
    logger.info("Data collection complete! You can now run train_model.py")


if __name__ == "__main__":
    collect_data()
