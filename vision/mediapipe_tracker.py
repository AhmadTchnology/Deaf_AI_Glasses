import cv2
import mediapipe as mp
import numpy as np
from collections import deque
from typing import List, Tuple, Optional
from utils.logger import logger

class MediaPipeTracker:
    """Extracts 3D hand landmarks using MediaPipe and buffers them into sequences.
    
    This is designed for dynamic sign language recognition where the model
    needs a sequence of frames (e.g. 30 frames) to predict a gesture.
    """
    
    def __init__(self, sequence_length: int = 30, max_num_hands: int = 2):
        self.sequence_length = sequence_length
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        # A sliding window queue of landmarks
        self.sequence_buffer = deque(maxlen=sequence_length)
        
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """Processes a single BGR frame.
        
        Returns:
            processed_frame: The frame with landmarks drawn on it.
            landmarks_array: A flattened numpy array of the landmarks for this frame, 
                             or None if no hands were detected.
        """
        # Convert BGR to RGB for MediaPipe
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)
        
        # We need a fixed size feature vector for the LSTM. 
        # Assume max 2 hands. Each hand has 21 landmarks * 3 coords (x,y,z) = 63 features.
        # Total features per frame = 63 * 2 = 126.
        # If only 1 hand is detected, we pad the second hand with zeros.
        # If no hands, return None.
        
        landmarks_array = np.zeros(21 * 3 * 2) 
        hands_detected = False
        
        if results.multi_hand_landmarks:
            hands_detected = True
            for i, hand_lms in enumerate(results.multi_hand_landmarks):
                if i >= 2: # We only process up to 2 hands
                    break
                
                # Draw landmarks on the frame
                self.mp_draw.draw_landmarks(frame, hand_lms, self.mp_hands.HAND_CONNECTIONS)
                
                # Extract coordinates
                hand_features = []
                for lm in hand_lms.landmark:
                    hand_features.extend([lm.x, lm.y, lm.z])
                    
                # Place features in the correct position of the 126-element array
                start_idx = i * 63
                end_idx = start_idx + 63
                landmarks_array[start_idx:end_idx] = hand_features

        if hands_detected:
            self.sequence_buffer.append(landmarks_array)
            return frame, landmarks_array
        else:
            # If no hands, we can either append zeros or do nothing.
            # Usually, for real-time inference, if no hands, we might clear the buffer 
            # or append zeros. Appending zeros signifies "hands left the frame".
            self.sequence_buffer.append(np.zeros(21 * 3 * 2))
            return frame, None
            
    def get_sequence(self) -> Optional[np.ndarray]:
        """Returns the current sequence if the buffer is full, else None."""
        if len(self.sequence_buffer) == self.sequence_length:
            return np.array(self.sequence_buffer) # Shape: (sequence_length, 126)
        return None
        
    def clear_buffer(self) -> None:
        """Clears the sequence buffer."""
        self.sequence_buffer.clear()
        
    def close(self):
        self.hands.close()
