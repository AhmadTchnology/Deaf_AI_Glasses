import os
import sys
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import TensorBoard

# Add parent directory to path so we can import project modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import logger
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical

# Configuration
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sequences")
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
ACTIONS = np.array(["hello", "thank_you", "please", "help"])
no_sequences = 30
sequence_length = 30

def train_model():
    logger.info("Loading data from {}", DATA_PATH)

    # Auto-detect which actions actually have collected data
    available_actions = []
    for action in ACTIONS:
        action_dir = os.path.join(DATA_PATH, action)
        if os.path.isdir(action_dir) and os.listdir(action_dir):
            available_actions.append(action)

    if len(available_actions) < 2:
        logger.error("Need data for at least 2 actions to train. Found: {}", available_actions)
        logger.info("Run 'py scripts/collect_data.py' and record at least 2 different signs.")
        return

    logger.info("Found data for {} actions: {}", len(available_actions), available_actions)
    available_actions = np.array(available_actions)
    label_map = {label: num for num, label in enumerate(available_actions)}
    sequences, labels = [], []

    for action in available_actions:
        action_dir = os.path.join(DATA_PATH, action)
        for seq_name in sorted(os.listdir(action_dir)):
            seq_dir = os.path.join(action_dir, seq_name)
            if not os.path.isdir(seq_dir):
                continue

            window = []
            complete = True
            for frame_num in range(sequence_length):
                npy_file = os.path.join(seq_dir, f"{frame_num}.npy")
                if not os.path.exists(npy_file):
                    complete = False
                    break
                res = np.load(npy_file)
                window.append(res)

            if complete and len(window) == sequence_length:
                sequences.append(window)
                labels.append(label_map[action])
            else:
                logger.warning("Skipping incomplete sequence: {}/{}", action, seq_name)

    if len(sequences) < 2:
        logger.error("Not enough complete sequences to train. Found: {}", len(sequences))
        return

    X = np.array(sequences)
    y = to_categorical(labels, num_classes=len(available_actions)).astype(int)

    logger.info("Total sequences: {}, Shape: {}", len(sequences), X.shape)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1)

    logger.info("Building LSTM model ({} classes)...", len(available_actions))
    model = Sequential()
    # input_shape = (sequence_length, features per frame) -> (30, 126)
    model.add(LSTM(64, return_sequences=True, activation='relu', input_shape=(30, 126)))
    model.add(LSTM(128, return_sequences=True, activation='relu'))
    model.add(LSTM(64, return_sequences=False, activation='relu'))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(len(available_actions), activation='softmax'))

    model.compile(optimizer='Adam', loss='categorical_crossentropy', metrics=['categorical_accuracy'])

    log_dir = os.path.join(os.path.dirname(__file__), 'Logs')
    tb_callback = TensorBoard(log_dir=log_dir)

    logger.info("Training model...")
    model.fit(X_train, y_train, epochs=200, callbacks=[tb_callback])

    # Evaluate
    loss, accuracy = model.evaluate(X_test, y_test)
    logger.info("Test Accuracy: {:.2f}%", accuracy * 100)

    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    model_path = os.path.join(MODEL_DIR, 'asl_lstm.h5')
    model.save(model_path)
    logger.info("Model saved to {}", model_path)

    # Save the label list so the classifier knows which actions were trained
    labels_path = os.path.join(MODEL_DIR, 'asl_labels.npy')
    np.save(labels_path, available_actions)
    logger.info("Labels saved to {} -> {}", labels_path, list(available_actions))

if __name__ == "__main__":
    train_model()
