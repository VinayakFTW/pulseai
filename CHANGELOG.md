# Changelog

All notable changes to PulseAI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v1.2.0] - 2025-10-24

### Added
- **Hybrid Speech Recognition System**: Implemented automatic fallback between Google Web Speech API (online) and Whisper (offline) based on internet connectivity
- **Internet Connection Detection**: Added `check_internet_connection()` function to dynamically route between online and offline ASR modes
- **Intelligent Tool Routing System**: Introduced a two-stage LLM processing pipeline:
  - First stage: Tool classification using a dedicated system prompt
  - Second stage: Conversational response generation or tool execution
- **Tool Dispatcher**: Created a centralized `tool_dispatcher()` function to parse and execute tool commands
- **Web Search Functionality**: Added `web_search()` function with URL encoding and browser integration
- **Screenshot Tool**: Implemented `screenshot()` function with automatic file saving to Pictures folder
- **Open Browser Command**: Added ability to open web browser via voice command
- **Persistent System Prompts**: Separated chat and tool routing system prompts for better modularity
- **Enhanced Conversation Context**: System prompt now persists and updates correctly across sessions

### Changed
- **Refactored Speech Recognition**: Split `command()` function to support both Google and Whisper ASR
- **Refactored Wake Word Detection**: Split `listen_for_wake_word()` to support both online and offline modes
- **Improved LLM Response Generation**: Enhanced `generate_response()` with `is_tool_check` parameter for dual-purpose usage
- **Optimized Conversation History**: System prompt now updates on load to ensure latest instructions
- **Better Audio Processing**: Refined silence detection threshold and duration for Whisper pipeline
- **Enhanced Error Messages**: More descriptive error handling throughout the codebase

### Fixed
- **Conversation History Corruption**: Fixed issue where system prompt wasn't properly maintained across sessions
- **Spotify Device Detection**: Increased wait time and retry logic for Spotify device availability

### Technical
- **Dependencies**: Added `requests` library for internet connectivity checking
- **Audio Constants**: Defined global constants for Whisper audio processing (SAMPLE_RATE, BLOCK_SIZE, etc.)
- **Code Organization**: Improved function ordering and documentation
- **Performance**: Optimized model loading with proper device mapping

---

## [v1.1.1] - 2025-10-19

### Removed
- **Mobile Call Functionality**: Removed code that was causing model crashes when attempting to place calls on mobile devices

### Notes
- Mobile calling feature may be re-implemented in future updates with improved stability

---

## [v1.1.0] - 2025-10-19

### Added
- **WhatsApp Messaging Integration**: Assistant can now send WhatsApp messages to contacts using voice commands
  - Added `send_whatsapp_message()` function
  - Integrated VCF file parsing for contact extraction with `get_vcf_contacts()`
  - Added `find_contact()` helper function for contact lookup
- **Contact Management**: Support for `.vcf` contact file format

### Dependencies
- Added `vobject` for VCF file parsing
- Added `pywhatkit` for WhatsApp automation

---

## [v1.0.0] - 2025-10-18

### Added
- **Local LLM Integration**: Integrated Meta's Llama 3.2 3B Instruct model for intelligent, context-aware responses
  - Replaced hardcoded conversational responses with dynamic LLM generation
  - Added support for natural language understanding and generation
- **Whisper-Based Speech Recognition**: Implemented local OpenAI Whisper ASR pipeline
  - Improved accuracy and performance over previous system
  - Added offline speech recognition capability
- **Conversation History System**: 
  - Implemented persistent conversation memory across sessions
  - Added `save_history()` and `load_history()` functions
  - Created JSON-based storage for conversation context
- **Enhanced Model Configuration**: Support for multiple model options (Llama, FLAN-T5)
- **Advanced Prompt Engineering**: Detailed system prompts for AI personality and capabilities

### Changed
- **Wake Word**: Changed from "wake up"/"resume" to "Pulse" for branded experience
- **Speech Recognition Pipeline**: Complete overhaul from basic speech_recognition to Whisper-based system
- **Response Generation**: Migrated from rule-based to LLM-based conversational AI

### Dependencies
- Added `torch` for PyTorch deep learning framework
- Added `transformers` for Hugging Face model integration
- Added `sounddevice` for audio capture
- Added `python-dotenv` for environment variable management
- Added `numpy` for audio processing

### Fixed
- **Error Handling**: Improved robustness of LLM and speech-to-text pipelines
- **Crash Prevention**: Added comprehensive exception handling to prevent unexpected crashes
- **User Feedback**: Better error messages and status updates

### Technical
- **Model Architecture**: Implemented text-generation pipeline with custom terminators
- **Conversation Format**: Structured messages with role-based formatting (system, user, assistant)
- **Audio Processing**: Added real-time audio stream processing with silence detection

---

## [v0.5.0] - 2024-06-12

### Changed
- **Code Formatting**: Comprehensive code restructuring for improved readability and maintainability
- **Spotify Integration**: Updated `play_song()` feature to work with voice commands
  - Songs can now be played on Spotify using natural voice input
  - Improved song search and playback functionality

### Technical
- Refactored multiple functions for better code organization
- Enhanced PEP 8 compliance

---

## [v0.2.0] - 2024-11-25

### Added
- **Wake Word Functionality**: Implemented pause/resume capability with wake words "wake up" or "resume"
  - Assistant now pauses after completing tasks
  - Requires wake word activation for subsequent commands

### Changed
- **Code Formatting**: Minor improvements to code structure and readability
- **Play Songs Feature**: Properly implemented song playback functionality
  - Natural language support: "play <song_name>"
  - Improved accuracy with artist name inclusion

### Notes
- For best results, include artist name when requesting songs (e.g., "play Changes by 2pac")

---

## [v0.1.7] - 2024-11-18

### Fixed
- **Empty Query Handling**: Fixed bug where assistant would attempt to search Google with empty strings
  - Similar to Google fallback bug from v0.1.5
  - Added query validation handler before web search
  - Prevents unnecessary Google search prompts for unrecognized input

---

## [v0.1.5] - 2024-11-16

### Added
- **Google Search Fallback**: Implemented fallback mechanism for unrecognized commands
  - Prompts user to search unrecognized queries on Google
  - Provides graceful degradation for unknown commands

### Fixed
- **Greeting Logic**: Corrected flaw in `greet()` function
  - Previously only greeted users between 6 AM - 12 PM
  - Now properly handles all time periods (morning, afternoon, evening, late night)
  - Improved time-based greeting messages

### Changed
- **Code Formatting**: General code cleanup and beautification
  - Improved consistency across codebase
  - Better indentation and spacing

---

## Legend

- **Added**: New features or functionality
- **Changed**: Changes to existing functionality
- **Deprecated**: Features that will be removed in upcoming releases
- **Removed**: Features removed in this release
- **Fixed**: Bug fixes
- **Security**: Security vulnerability fixes
- **Technical**: Behind-the-scenes improvements
- **Dependencies**: New or updated library requirements

---

## Links

- [Repository](https://github.com/VinayakFTW/pulseai)
- [Issue Tracker](https://github.com/VinayakFTW/pulseai/issues)
- [Documentation](https://github.com/VinayakFTW/pulseai#readme)

---
