# Deaf AI Glasses 👓

An AI-powered smart glasses project built for Raspberry Pi 5. This project provides bidirectional communication: **Hearing Mode** (real-time speech-to-sign-language visualization) and **Speaking Mode** (real-time ASL detection to spoken words via TTS).

## Quick Start

### 1. Hardware Requirements
- **Raspberry Pi 5** (or PC/Mac for testing)
- **USB Microphone** & **Speaker**
- **USB Camera** (facing downwards towards your hands)
- **I2C/SPI OLED Display** (e.g. SSD1306, SH1106) compatible with Linux Framebuffer

### 2. Software Setup
Ensure you have Python 3.10+ installed. On Raspberry Pi (Debian/Ubuntu), install system dependencies:
```bash
sudo apt install python3-pyaudio portaudio19-dev libasound2-dev
```

Clone the repo, set up a virtual environment, and install requirements:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Environment Variables
Copy `.env.example` to `.env` and fill in your API keys (Gemini or NVIDIA NIM for Speech-to-Text).

### 4. Train Your Custom Sign Language Model (Speaking Mode)
Because the camera points downwards, you must train a personalized model for your signs.
1. Run data collection: `python scripts/collect_data.py` (Follow the on-screen PyGame instructions)
2. Train the LSTM model: `python scripts/train_model.py` (Outputs to `models/asl_lstm.h5`)

### 5. Run the Application
```bash
python main.py
```
* **Menu**: Press `1` for Deaf Mode, `2` for Blind Mode (WIP).
* **Deaf Mode**: Listens to speech and displays text/pixel-art. Press `Space` to toggle into **Speaking Mode** (camera activates, detects your signs, and speaks them aloud).

## Features

- **Hearing Mode (Speech-to-Text)**: Built-in VAD (Voice Activity Detection) listens to speakers and translates speech into text via NVIDIA NIM or Gemini cloud models. NLP extracts root signs using SpaCy.
- **Speaking Mode (Sign-to-Speech)**: 100% offline, real-time ASL detection using **MediaPipe** (3D hand landmarks) and a custom **LSTM Neural Network** to recognize dynamic gestures. Uses `pyttsx3` to speak the detected words aloud.
- **Pixel-Art Renderer**: Optimized custom PyGame renderer for Raspberry Pi Framebuffer (`fbcon`), smoothly falling back to a Windowed application on Windows/macOS.
- **Robust Data Pipeline**: Includes `collect_data.py` and `train_model.py` to easily add new words to your vocabulary.

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `STT_PROVIDER` | Speech-to-text backend (`gemini` or `nvidia`) | `gemini` |
| `GEMINI_API_KEY` | Your Google Gemini API Key | |
| `NVIDIA_API_KEY` | Your NVIDIA NIM API Key | |
| `DEFAULT_MODE` | Set to automatically boot into a mode (`deaf` or `blind`) | `None` |

## Documentation

- **[Code Architecture & Agent Protocol](.agent/skills/)**: See the `.agent` folder for internal guidelines and documentation regarding the AI agents that helped build this project.
- **Scripts**: 
  - `collect_data.py`: Gathers 30-frame sequence data of hand landmarks.
  - `train_model.py`: Trains the Keras LSTM model on collected data.

## Running Tests
The project features 23 tests ensuring robustness across audio processing, STT APIs, queueing, and display modules.
```bash
pytest tests/ -v
```

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

---
### Made With ❤️ By AhmadTchnology