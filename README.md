# Deaf AI Glasses 👓

An AI-powered smart glasses project built for Raspberry Pi 5. This project provides real-time speech-to-sign-language visualization, listening to spoken words and displaying corresponding American Sign Language (ASL) pixel-art gestures on an OLED display (or windowed application on PC).

## Features
- **Real-Time Speech Detection**: Built-in VAD (Voice Activity Detection) listens only when someone is speaking.
- **Multiple AI Models**: Swap between Gemini GenAI and NVIDIA NIM cloud models.
- **NLP Processing**: Converts speech transcripts into the root ASL signs using SpaCy.
- **Pixel-Art Renderer**: Optimized custom PyGame renderer for Raspberry Pi Framebuffer (`fbcon`), easily falling back to Windowed mode on Windows/macOS.
- **Modular Pipeline**: Clean abstraction with Factory Patterns for STT Providers.

---

## 📸 Demo overview
The pipeline runs continuously in real-time:
`Audio Capture` ➔ `VAD` ➔ `NVIDIA/Gemini STT` ➔ `NLP (SpaCy)` ➔ `Queued Gestures` ➔ `PyGame OLED Render`

## ⚙️ Hardware Requirements
- **Raspberry Pi 5**
- **USB Microphone**
- **I2C/SPI OLED Display (e.g. SSD1306, SH1106) compatible with Linux Framebuffer**

---

## 🛠️ Software Setup

### 1. Prerequisites
Ensure you have Python 3.10+ installed.

```bash
# On Raspberry Pi (Debian/Ubuntu):
sudo apt install python3-pyaudio portaudio19-dev libasound2-dev
```

### 2. Environment Variables & Credentials
Copy the `.env.example` into a new `.env` file at the root of the project:

```bash
# STT Provider ("gemini" or "nvidia")
STT_PROVIDER=gemini

# For Gemini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash

# For NVIDIA NIM (Cloud)
NVIDIA_API_KEY=nvapi-your_nvidia_key
NVIDIA_MODEL=d3fe9151-442b-4204-a70d-5fcc597fd610  # parakeet-tdt-0.6b-v2 function ID
NVIDIA_BASE_URL=grpc.nvcf.nvidia.com:443
```

### 3. Installation

Activate your virtual environment and install the required packages:

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 4. Running the Project

#### On Windows / Mac (Testing Mode)
The display automatically detects it's not running on a Linux framebuffer and opens a Pygame window:
```bash
python main.py
```

#### On Raspberry Pi (OLED Mode)
The application will automatically pipe Pygame to the Linux `/dev/fb0` Framebuffer:
```bash
python main.py
```

## 🧪 Running Tests
The project features 23 tests ensuring robustness across audio processing, STT APIs, queueing, and display modules.
```bash
pytest tests/ -v
```

## 📝 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

##

### Made With ❤️ By AhmadTchnology