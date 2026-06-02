import os
import numpy as np
from typing import Tuple, List, Optional
from utils.logger import logger

class SignClassifier:
    """Loads a trained LSTM model to predict dynamic sign language gestures.
    
    Expects a sequence of frames (e.g. 30 frames) of MediaPipe landmarks.
    """
    
    def __init__(self, model_path: str = "models/asl_lstm.h5", actions: List[str] = None):
        if actions is None:
            self.actions = ["hello", "thank_you", "please", "help"]
        else:
            self.actions = actions
            
        self.model = None
        
        if not os.path.exists(model_path):
            logger.warning("LSTM model not found at {}. Please run data collection and training first.", model_path)
            return
            
        try:
            # We import tensorflow here to avoid slowing down startup if this module isn't used
            import tensorflow as tf
            self.model = tf.keras.models.load_model(model_path)
            logger.info("Successfully loaded LSTM model from {}", model_path)
        except Exception as e:
            logger.error("Failed to load LSTM model: {}", e)
            
    def predict(self, sequence: np.ndarray, threshold: float = 0.8) -> Tuple[Optional[str], float]:
        """Predicts the gesture from a sequence of landmarks.
        
        Args:
            sequence: Numpy array of shape (sequence_length, 126).
            threshold: Minimum confidence score to return a valid prediction.
            
        Returns:
            A tuple of (predicted_action_string, confidence_score)
            Returns (None, 0.0) if prediction is below threshold or model is missing.
        """
        if self.model is None:
            return None, 0.0
            
        # The model expects a batch dimension: (1, sequence_length, 126)
        res = self.model.predict(np.expand_dims(sequence, axis=0), verbose=0)[0]
        
        best_idx = np.argmax(res)
        confidence = float(res[best_idx])
        
        if confidence > threshold:
            predicted_action = self.actions[best_idx]
            logger.debug("Predicted sign: {} (conf: {:.2f})", predicted_action, confidence)
            return predicted_action, confidence
            
        return None, confidence
