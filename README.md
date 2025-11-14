# PulseAI 🎙️🤖

<div align="center">

**An Intelligent Voice-Activated AI Assistant with Local LLM Integration**

*Your proactive AI companion that understands, learns, and executes*

</div>

## 🌟 Overview

PulseAI is a sophisticated voice-activated AI assistant that runs locally on your machine, featuring advanced natural language processing powered by Meta's Llama 3.2 model. Unlike traditional voice assistants, PulseAI is designed to be a proactive strategic partner that anticipates your needs, automates workflows, and seamlessly integrates with your digital ecosystem.

## ✨ Key Features

- 🎤 **Hybrid Speech Recognition** - Automatic fallback between Google Web Speech API (online) and Whisper (offline)
- 🧠 **Local LLM Processing** - Privacy-focused AI using Llama 3.2 3B Instruct model
- 🎵 **Spotify Integration** - Voice-controlled music playback (including Liked Songs)
- 💬 **WhatsApp Automation** - Send messages via voice commands
- 🔍 **Web Search** - Intelligent web queries with contextual understanding
- 📸 **Screenshot Capture** - Quick screen captures on demand (with timestamped filenames)
- 🔄 **Conversation Memory** - Persistent context across sessions
- 🌐 **Internet-Aware** - Seamless online/offline mode switching
- 🛠️ **Tool Routing System** - Smart command classification and execution

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- CUDA-compatible GPU (recommended for optimal performance)
- 8GB+ RAM (16GB recommended)
- Spotify Premium Account
- Active internet connection (for initial setup and online features)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/VinayakFTW/pulseai.git
cd pulseai/backend
```

2. **Install dependencies**
```bash
pip install torch transformers
pip install spotipy pyttsx3 speechrecognition pyautogui
pip install sounddevice numpy vobject pywhatkit requests python-dotenv difflib
```

3. **Set up environment variables**

Create a `.env` file in the backend directory:
```env
TRANSFORMER_CACHE=/path/to/cache
SPOTIPY_ID=your_spotify_client_id
SPOTIPY_SECRET=your_spotify_client_secret
SPOTIFY_PATH=C:\Path\To\Spotify.exe
```

4. **Add your contacts (Optional)**

Place a `contacts.vcf` file in the backend directory for WhatsApp integration.

5. **Run PulseAI**
```bash
# Make sure you are in the 'backend' directory
python pulseai.py
```

## 🎯 Usage

### Wake Word Activation

PulseAI listens for the wake word "wake" to activate:

```
You: "wake"
PulseAI: "Yes?"
You: "Play my liked songs"
PulseAI: *Plays your liked songs on Spotify*
```

### Available Commands

| Command | Example | Description |
|---------|---------|-------------|
| Play Music | "Play Bohemian Rhapsody" | Searches and plays songs on Spotify |
| Play Liked Songs | "Play my liked songs" | Plays your Spotify Liked Songs |
| Take Screenshot | "Take a screenshot" | Captures current screen |
| Send WhatsApp | "Send message to John saying hello" | Sends WhatsApp message to contact |
| Web Search | "Search for Python tutorials" | Opens Google search |
| Open Browser | "Open the browser" | Launches default web browser |
| Conversation | "What's the weather like?" | Engages in natural dialogue |

### Conversation Mode

PulseAI maintains context across conversations:

```
You: "What's machine learning?"
PulseAI: *Provides detailed explanation*
You: "Give me an example"
PulseAI: *Continues with relevant example based on previous context*
```

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────┐
│                   Wake Word Detector                 │
│            (Google API / Whisper Local)              │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│              Command Processor                       │
│        (Speech Recognition Pipeline)                 │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│              Tool Routing System                     │
│         (Llama 3.2 Classification)                   │
└─────────┬───────────────────────────┬───────────────┘
          │                           │
┌─────────▼─────────┐       ┌────────▼────────────────┐
│   Tool Executor   │       │   Chat Generator        │
│  (Actions/APIs)   │       │  (Conversational AI)    │
└───────────────────┘       └─────────────────────────┘
```

### Core Technologies

- **LLM**: Meta Llama 3.2 3B Instruct (via Hugging Face Transformers)
- **ASR**: Google Web Speech API / OpenAI Whisper Small
- **TTS**: pyttsx3 (Cross-platform text-to-speech)
- **APIs**: Spotify Web API, WhatsApp via pywhatkit

## 🛠️ Configuration

### Spotify Setup

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Copy Client ID and Client Secret to `.env`
4. Add `http://localhost:8080` as redirect URI

### Model Configuration

Edit the model selection in `backend/pulse_config/config.py`:

```python
# In backend/pulse_config/config.py
llm_pipeline, terminators = load_model("meta-llama/Llama-3.2-3B-Instruct") # Current default
```

### Speech Recognition Modes

- **Online Mode**: Uses Google Web Speech API (accurate, requires internet)
- **Offline Mode**: Uses Whisper (privacy-focused, works without internet)

The system automatically switches based on internet connectivity.

## 🧩 Project Structure

```
pulseai/
├── backend/
│   ├── pulseai.py              # Main application file
│   ├── pulse_brain/
│   │   └── llm_interface.py    # LLM loading and tool dispatcher
│   ├── pulse_config/
│   │   └── config.py           # System prompts, history, config
│   ├── pulse_ear/
│   │   └── speech_handler.py   # ASR and TTS functions
│   ├── pulse_tools/
│   │   ├── general_tools.py    # Screenshot, web search, etc.
│   │   ├── messaging.py        # WhatsApp integration
│   │   └── spotify_player.py   # Spotify integration
│   ├── conversation_history.json # Persistent conversation context
│   ├── contacts.vcf            # WhatsApp contacts (user-provided)
│   └── .env                    # Environment variables
├── .gitignore
├── README.md                   # This file
└── CHANGELOG.md
```

## 🔧 Development

### Adding New Tools

1. **Define the tool in the tool system prompt:**

Edit `backend/pulse_config/config.py`:
```python
tool_system_prompt = """
...
- [TOOL: your_tool, param: description] - Tool description
...
"""
```

2. **Implement the tool function:**

Add your function to a new or existing file in `backend/pulse_tools/`:
```python
# e.g., in backend/pulse_tools/general_tools.py
def your_tool(param):
    # Your implementation
    pass
```

3. **Add to tool dispatcher:**

Edit `backend/pulse_brain/llm_interface.py`:
```python
# Import your new function
from pulse_tools.general_tools import your_tool

def tool_dispatcher(response):
    # ... existing code ...
    elif tool_name == "your_tool":
        your_tool(params.get('param'))
        return tool_name, "Tool executed."
```

### Conversation History

Conversations are automatically saved to `backend/conversation_history.json` with the following structure:

```json
[
  {"role": "system", "content": "System prompt..."},
  {"role": "user", "content": "User query"},
  {"role": "assistant", "content": "AI response"}
]
```

## 🔒 Privacy & Security

- ✅ **Local Processing**: All LLM inference runs on your machine
- ✅ **No Data Sharing**: Conversations stay on your device
- ✅ **Offline Capable**: Core features work without internet
- ⚠️ **API Usage**: Spotify and WhatsApp integrations require external services

## 📋 Requirements

### Hardware

- **CPU**: Multi-core processor (Intel i5/Ryzen 5 or better)
- **RAM**: 8GB minimum (16GB recommended)
- **GPU**: NVIDIA GPU with CUDA support (optional but recommended)
- **Storage**: 10GB free space for models

### Software

- **Operating System**: Windows 10/11, Linux, macOS
- **Python**: 3.8 or higher
- **CUDA Toolkit**: 11.8+ (for GPU acceleration)

## 🐛 Troubleshooting

### Model Loading Issues
```bash
# Clear transformer cache
rm -rf ~/.cache/huggingface/transformers
```

### Microphone Not Detected
```python
# List available devices
import sounddevice as sd
print(sd.query_devices())
```

### Spotify Connection Failed
- Ensure Spotify is running and logged in
- Check redirect URI matches dashboard settings
- Verify client credentials in `.env`

## 🗺️ Roadmap

- [x] Multi-language support
- [ ] Email integration
- [ ] Calendar management
- [ ] File organization automation
- [ ] Custom workflow creation
- [ ] Mobile companion app
- [ ] Plugin system for extensibility

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is proprietary software. See the [LICENSE.md](LICENSE.md) file for details.

Unauthorized copying, distribution, or use of this software is strictly prohibited.

## 🙏 Acknowledgments

- Meta AI for Llama 3.2
- Hugging Face for Transformers library
- OpenAI for Whisper model
- Spotify for Web API

## 📧 Contact

- **Project Maintainer**: [Vinayak Varshney]
- **GitHub**: @VinayakFTW
- **Email**: vinayak.varshney.dev@gmail.com

---

<div align="center">

⭐ **Star this repo if you find it helpful!**

*Made with ❤️*

</div>