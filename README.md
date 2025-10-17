# PulseAI Voice-Activated Assistant

PulseAI is a voice-activated AI assistant developed in Python. It uses speech recognition and a local large language model to interact with users and perform various tasks like opening websites, providing conversational responses, fetching information from Wikipedia, playing songs(Beta), taking screenshots, and remembering user notes. Designed for a more personalized experience, PulseAI uses your name and responds based on the time of day.

## Features

- **Voice Commands**: Listens to user commands, interprets them, and takes appropriate actions.
- **Intelligent Responses**: Uses a local LLM (Llama 3.2) to provide intelligent and context-aware responses.
- **Greeting**: Customizes greetings based on the time of day.
- **Website Navigation**: Opens popular websites by name (e.g., Google, YouTube, Wikipedia).
- **Information Retrieval**: Fetches summaries from Wikipedia for "what is" queries.
- **Screenshot Capture**: Takes a screenshot and saves it to the user’s Pictures directory.
- **Memory**: Remembers information upon request and recalls it when asked.
- **Conversational Responses**: Provides responses for casual conversations.
- **Music Search**: Finds and plays songs on spotify using the Spotify Web API.
- **Date and Time**: Reads the current date and time upon request.

## Requirements

To use PulseAI, make sure you have the following Python packages installed:

```bash
    pip install -r requirements.txt 
```
Additionally, you'll need 'Torch' specifically the cuda enabled version for efficient proccessing.

## CUDA Installation 

https://developer.nvidia.com/cuda-toolkit

Use the above link to download the Nvidia developer CUDA Toolkit.
After downloading the CUDA Toolkit
Download specific torch distribution for the toolkit

*Current project toolkit version and torch version*

CUDA 13.0
torch==2.8.0+cu129
torchvision==0.23.0+cu129

install this torch distribution from the command line using the following command

```bash
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cu129
```


Also, PulseAI is configured to use Firefox for web searches. Ensure Firefox is installed, or modify the path in the code to your preferred browser.

## Usage
0. Configuration:

- <p>create a .env file with your own spotify dev api keys and set transformer cache path and spotify path<br>
use the variable names as follows in the .env file<br>
SPOTIPY_ID = "your cliend id"<br>
SPOTIPY_SECRET = "your client secret"<br>
SPOTIFY_PATH = "path to spotify.exe on your device"<br>
BROWSER_PATH = "path to firefox.exe on your device"<br>
TRANSFORMER_CACHE = "your path here"<br>
<p>

1. Initialize:

- Run the program and enter your name when prompted to personalize the experience.

2. Commands:

- Greet: Just say "Hello," "Hi," or "Good Morning," etc.
- Ask the Time or Date: Use "What time is it?" or "What’s today’s date?"
- Open Websites: Say "Open [website name]" (e.g., "Open Google").
- Wikipedia Search: Say "What is [topic]" to get a Wikipedia summary.
- Take a Screenshot: Just say "Take a screenshot."
- Remember Notes: Say "Remember that [note]" to save information.
- Recall Notes: Use "Do you remember?" to hear stored information.
- Play a Song: Say "Play [song name]" to play a song on spotify.
- End Session: Say "Power off" to exit PulseAI.

3. Error Handling:

- If speech recognition fails or the request cannot be completed, PulseAI will inform you with a spoken error message.

## File Structure

1. main.py: The main file containing the code for the assistant.

2. conversation_history.json: Stores old conversations as context so it always remembers almost everything


## Code Overview

1. Initialization: Configures the pyttsx3 engine and registers Brave Browser.

2. Main Functions:
    - speak(): Text-to-speech for spoken responses.
    - command(): Listens for user commands.
    - greet(): Provides time-based greetings.
    - song_play(): Plays a song on spotify.
        - wait_for_device(): A helper function to open spotify on a device if not already open.<br>
            **IF DOWNLOADED FROM MICROSOFT STORE THEN REPLACE THE PATH WITH "start spotify"<br>if downloaded from the spotify website then simply replace with spotify.exe path on your system**
        - play_song(): The helper function that actually plays the song after connecting to the spotify api.<br>
            **REPLACE THE "client_id" AND "client_secret" WITH YOUR ID AND API FROM https://developer.spotify.com**

3. Loop Execution: The main loop listens for commands and checks them against a set of conditions for executing specific tasks.

## Customization

You can customize PulseAI by:

- Adding more websites to the websites dictionary.<br>
    **THIS WILL BE REPLACED BY A MORE GENERALISED WAY TO REDUCE EFFORT AND ASSIST BETTER**

- Expanding conversational_responses with additional responses.<br>
    **THIS WILL BE REPLACED BY A GPT IN FUTURE UPDATES**

- Adjusting the speech rate or voice type in the speak() function.


**Troubleshooting**

- No Response to Commands: Ensure your microphone is working and configured correctly.

- Incorrect Recognition: If speech recognition accuracy is low, try speaking more clearly or adjusting recog.pause_threshold in the command() function.

- Problems with browser search: Make sure you have an internet connection for fetching data from Internet.

## Spotify API Usage

This project utilizes the Spotify Web API to search for and play music. To use this application, you will need to generate your own API credentials from the <a href = "https://developer.spotify.com">Spotify Developer Dashboard.</a>

**Data Handling and Compliance**

- **No Data Ingestion**:This application does not ingest, store, cache, or copy any data returned by the Spotify API. All API calls are made in real-time to fulfill a user's direct action (e.g., searching for a song).

- **User Responsibility**:As a user of this project, you are responsible for creating and managing your own Spotify API keys and adhering to the <a href = "https://developer.spotify.com/terms">Spotify Developer Terms of Service.</a>
