import datetime
import os.path
import time
import webbrowser as wb
from urllib.parse import quote_plus
import pyautogui
import pyttsx3
import speech_recognition as sr
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer,AutoModelForSeq2SeqLM,pipeline
from dotenv import load_dotenv
import os
import json
import numpy as np
import sounddevice as sd
import queue
import vobject
import pywhatkit
import requests

load_dotenv()

cache_directory = os.environ.get("TRANSFORMER_CACHE")
#model_name = "openai/gpt-oss-20b" #cant run on my laptop
#model_name = "google/flan-t5-base" #summary model may implement later if i feel so
model_name = "meta-llama/Llama-3.2-3B-Instruct"
llm_pipeline = pipeline(
    "text-generation",
    model=model_name,
    model_kwargs={"dtype": torch.bfloat16},
    device_map="auto",
)
terminators = [
    llm_pipeline.tokenizer.eos_token_id,
    llm_pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
]
# tokenizer = AutoTokenizer.from_pretrained(model_name,cache_dir=cache_directory)
# model = AutoModelForCausalLM.from_pretrained(model_name,cache_dir=cache_directory,trust_remote_code=True)


chat_system_prompt = """You are Pulse, my personal AI agent integrated into this laptop. Your core mission is to function as a seamless, proactive, and intelligent extension of my mind and workflow. Your primary goal is to anticipate my needs, optimize my productivity, and manage my digital environment with maximum efficiency and security. You are more than a reactive assistant; you are a strategic partner.

Core Directives & Capabilities

1. Proactive & Context-Aware Assistance

    Anticipate Needs: Monitor my active applications, files, and schedule to anticipate what I need next. For example, if I'm working on a presentation file and open my browser, pre-emptively search for relevant statistics or high-quality images related to the presentation's topic. If I have a meeting in 30 minutes, automatically pull up the relevant documents, emails, and meeting notes.

    Smart Reminders: Don't just remind me what is due, but why it's important. Link reminders to relevant files, contacts, or project goals (e.g., "Reminder: Finalize the Q3 report in 1 hour. Here are the latest sales figures and your draft.").

    System Optimization: Proactively manage system resources. If you notice I'm running low on memory during a heavy task, suggest closing non-essential background processes. Alert me to low disk space with suggestions for files to archive or delete.

2. Deep System & Workflow Integration

    Master of the Machine: You have deep access to the operating system. Execute commands, manage files and folders, organize my desktop, and control system settings based on my natural language instructions. "Odyssey, find all PDFs related to the 'Project Titan' I reviewed last week, convert them to a single document, name it 'Titan Summary', and place it in the project folder."

    Workflow Automation: Learn my repetitive workflows and suggest or create automations. If you observe that every Friday I compile a report from three specific spreadsheets, offer to automate that entire process for me.

    Application Synergy: Act as the bridge between my applications. If I copy data from a spreadsheet, anticipate that I might need to paste it into a presentation slide and format it accordingly. Help me draft an email by pulling information directly from my notes, calendar, and recent documents.

3. Advanced Information & Communication Management

    Intelligent Summarizer: Summarize long articles, documents, email chains, or video transcripts into concise, actionable bullet points. Your summaries should highlight key decisions, action items, and main arguments.

    Communication Hub: Manage my communications. Draft emails in my style, schedule messages, sort my inbox by priority (not just by sender), and alert me only to what truly requires my immediate attention. "Odyssey, draft a polite but firm follow-up email to John about the overdue invoice."

    Research Powerhouse: When I ask you to research a topic, don't just return a list of links. Synthesize information from multiple reliable sources into a comprehensive, well-structured brief. Differentiate between fact, opinion, and speculation.

4. Persona & Interaction Style

    Professional & Concise: Your tone is calm, professional, and direct. You provide information without unnecessary conversational filler.

    Adaptive & Personalized: You learn my preferences, my language, and my work style. Over time, your suggestions and actions should become increasingly tailored to me.

    Assumes Competence: You operate on the assumption that I am a capable user. Present solutions and options, but execute the most logical one by default unless I specify otherwise.

Ethical Framework & Boundaries

    Privacy is Paramount: My personal data, files, and communications are your most sacred trust. You will never share my data with third parties. All processing should be done locally on this device whenever possible.

    Permission & Transparency: For any new automation or a highly impactful action (like deleting a large number of files), you must ask for my confirmation the first time. Be transparent about your actions and capabilities.

    Focus on Augmentation, Not Replacement: Your goal is to augment my intelligence and capabilities, not to replace my judgment. Present curated options and analyses, but the final decision is always mine.
"""

tool_system_prompt = """
You are a task-routing AI agent named Pulse. Your single purpose is to analyze a user's request and determine if it requires one of the available tools.

If the request can be fulfilled by a tool, you MUST respond with ONLY the tool command in the exact format:
[TOOL: function_name, parameter: value]

Do NOT add any conversational filler.

If the request is a simple conversational question or statement (e.g., "hello", "what is the capital of France?"), you MUST respond with the single word: [CHAT]
---
## Available Tools
- [TOOL: song_play, _query: song name] - Plays a song on Spotify.
- [TOOL: screenshot] - Takes a screenshot of the current screen.
- [TOOL: send_whatsapp_message, contact: person's name, message: the content] - Sends a WhatsApp message.
- [TOOL: web_search, query: search term] - Searches the web.
- [TOOL: open_browser] - Opens a new web browser window.

---
## Examples:
User: "Open the browser."
Your Response: "[TOOL: open_browser]"

User: "How are you today?"
Your Response: "[CHAT]"

User: "Play Changes by 2pac"
Your Response: "[TOOL: song_play, _query: Changes by 2pac]"

User: "What's the weather like?"
Your Response: "[TOOL: web_search, query: weather today]"
"""
name = 'Vinayak'

# Change how the Engine Sounds------------------------------------------------------------------------------------------
"""
voices = engine.getProperty('voices')
if len(voices) > 1:
    engine.setProperty('voice', voices[1].id)
else:
    engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 175)
"""

# --- Re-added audio constants for Whisper ---
SAMPLE_RATE = 16000  
BLOCK_SIZE = 800     # How many audio frames per block
CHANNELS = 1         # Mono audio
DTYPE = "float32"
SILENCE_THRESHOLD = 0.02  # Audio energy threshold to consider as speech
SILENCE_DURATION = 1.5

# Previous Conversation Context loading-----------------------------------------------------------------------------------
HISTORY_FILE = "conversation_history.json"
def save_history(history):
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=4)
    except Exception as e:
        print(f"Error saving history: {e}")

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
                
                if not history or history[0]['role'] != 'system':
                    return [{"role": "system", "content": chat_system_prompt}]
                
                history[0]['content'] = chat_system_prompt
                return history
        except (json.JSONDecodeError, IndexError):
            return [{"role": "system", "content": chat_system_prompt}]
    else:
        return [{"role": "system", "content": chat_system_prompt}]

# Engine Functions----------------------------------------------------------------------------
def speak(_audio=None):
    engine = pyttsx3.init()
    engine.say(_audio)
    engine.runAndWait()
    engine.stop()
    return _audio


def greet(_name):
    hour = datetime.datetime.now().hour
    if 6 <= hour < 12:
        speak(f"Good Morning, {_name}. Welcome to PulseAI! How may I help you?")
    elif 12 <= hour < 16:
        speak(f"Good Afternoon, {_name}. Welcome to PulseAI! How may I help you?")
    elif 16 <= hour <= 24:
        speak(f"Good Evening, {_name}. Welcome to PulseAI! How may I help you?")
    else:
        speak(f"Hello, {_name}. It's quite late! How can I assist you?")


def screenshot():
    image = pyautogui.screenshot()
    image_path = os.path.expanduser('~\\Pictures\\Screenshots\\PulseAI.png')
    image.save(image_path)
    os.startfile(image_path)

def check_internet_connection(url='http://www.google.com/', timeout=5):
    """Checks for a stable internet connection."""
    try:
        requests.get(url, timeout=timeout)
        return True
    except (requests.ConnectionError, requests.Timeout):
        return False

def command_google():
    """
    Listens using speech_recognition and uses Google's (ONLINE) Web Speech API.
    """
    _recog = sr.Recognizer()
    with sr.Microphone() as _source:
        print("Listening... (Google Online)")
        _recog.pause_threshold = 1
        _recog.adjust_for_ambient_noise(_source, duration=1)
        _audio = _recog.listen(_source)
    
    try:
        print("Recognizing... (Google Online)")
        _query = _recog.recognize_google(_audio)
        print(f"Recognized: {_query}")
        return _query
    except sr.UnknownValueError:
        print("Sorry, I didn't understand that")
        return "0"
    except sr.RequestError as error1:
        print(f"Google API request failed; {error1}")
        return "0"
    except Exception as error2:
        print(f"An error occurred: {error2}")
        return "0"

def command_whisper(asr_pipeline):
    """
    Listens for speech and transcribes it LOCALLY using Whisper.
    """
    audio_queue = queue.Queue()

    def audio_callback(indata, frames, time, status):
        if status:
            print(status, flush=True)
        audio_queue.put(bytes(indata))

    print("Listening... (Whisper Offline)")
    
    speech_data = []
    is_speaking = False
    silent_blocks = 0
    max_silent_blocks = int(SILENCE_DURATION * SAMPLE_RATE / BLOCK_SIZE)

    try:
        with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE, 
                               channels=CHANNELS, dtype=DTYPE, callback=audio_callback):
            while True:
                audio_chunk = audio_queue.get()
                audio_np = np.frombuffer(audio_chunk, dtype=DTYPE)

                rms = np.sqrt(np.mean(audio_np**2))

                if rms > SILENCE_THRESHOLD:
                    if not is_speaking:
                        print("Speaking detected...")
                    is_speaking = True
                    silent_blocks = 0
                elif is_speaking:
                    silent_blocks += 1
                
                if is_speaking:
                    speech_data.append(audio_chunk)

                if is_speaking and silent_blocks > max_silent_blocks:
                    print("Recognizing... (Whisper Offline)")
                    break
                    
    except Exception as e:
        print(f"An error occurred: {e}")
        return "0"

    if not speech_data:
        print("No speech detected.")
        return "0"

    full_audio = b"".join(speech_data)
    full_audio_np = np.frombuffer(full_audio, dtype=DTYPE)

    try:
        result = asr_pipeline(full_audio_np, generate_kwargs={"language": "en"})
        query = result["text"]
        print(f"Recognized: {query}")
        return query
    except Exception as e:
        print(f"Error during transcription: {e}")
        return "0"

def command(asr_pipeline):
    """
    Checks for internet and routes to Google (online) or Whisper (offline).
    """
    if check_internet_connection():
        return command_google()
    else:
        print("No internet connection. Falling back to local Whisper model.")
        return command_whisper(asr_pipeline)

def listen_for_wake_word_google(wake_word="pulse", duration=2):
    """Listens for wake word using Google (Online) Web Speech."""
    print(f"Listening for wake word '{wake_word}'... (Google Online)")
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = r.listen(source, timeout=3, phrase_time_limit=duration)
        except sr.WaitTimeoutError:
            return False

    try:
        transcribed_text = r.recognize_google(audio).lower().strip()
        if wake_word in transcribed_text:
            print(f"Wake word detected in: '{transcribed_text}'")
            return True
        return False
    except (sr.UnknownValueError, sr.RequestError):
        return False
    except Exception as e:
        print(f"An error occurred during wake word detection: {e}")
        return False

def listen_for_wake_word_whisper(asr_pipeline, wake_word="pulse", duration=2):
    """Listens for wake word using Whisper (Offline)."""
    print(f"Listening for wake word '{wake_word}'... (Whisper Offline)")
    try:
        audio_chunk = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype=DTYPE)
        sd.wait()

        audio_np = audio_chunk.flatten()

        result = asr_pipeline(
            audio_np,
            generate_kwargs={"task":"transcribe", "language": "en"}
        )
        
        transcribed_text = result["text"].lower().strip()

        if wake_word in transcribed_text:
            print(f"Wake word detected in: '{transcribed_text}'")
            return True
        
        return False
    except Exception as e:
            print(f"An error occurred during wake word detection: {e}")
            return False

def listen_for_wake_word(asr_pipeline, wake_word="pulse", duration=2):
    """
    Checks for internet and routes to Google (online) or Whisper (offline)
    for wake word detection.
    """
    if check_internet_connection():
        return listen_for_wake_word_google(wake_word, duration)
    else:
        return listen_for_wake_word_whisper(asr_pipeline, wake_word, duration)


def refine_query(_query):
    stop_words = {'play'}
    refined_query = [word for word in _query.split() if word not in stop_words]
    refined_query = " ".join(refined_query)
    return refined_query


def song_play(_query):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.environ.get("SPOTIPY_ID"),
        client_secret=os.environ.get("SPOTIPY_SECRET"),
        redirect_uri="http://localhost:8080",
        scope="user-modify-playback-state user-read-playback-state"
    ))

    def wait_for_device():
        print("Waiting for Spotify to become active...")
        for _ in range(10):
            devices = sp.devices()
            device_list = devices.get('devices', [])

            if device_list:

                for device in device_list:
                    print(f"Active Device Found: {device['name']}")
                    return device['id']

            time.sleep(10)

        print("No active device found. Make sure Spotify is running and logged in.")
        return None

    def play_song(_query):

        os.startfile(os.environ.get("SPOTIFY_PATH"))

        device_id = wait_for_device()
        if not device_id:
            return

        results = sp.search(q=_query, type="track", limit=1)
        tracks = results.get('tracks', {}).get('items', [])

        if tracks:
            track = tracks[0]
            track_name = track['name']
            track_artist = ", ".join(artist['name'] for artist in track['artists'])
            track_id = track['id']

            print(f"Found Track: {track_name} by {track_artist}")
            sp.start_playback(device_id=device_id, uris=[f"spotify:track:{track_id}"])
            print(f"Playing {track_name} by {track_artist}")
        else:
            print(f"No track found for '{_query}'.")

    play_song(_query)

def web_search(query):
    try:
        encoded_query = quote_plus(query)
        search_url = f"https.www.google.com/search?q={encoded_query}"
        print(f"Searching for: {query}")
        speak(f"Searching the web for {query}")
        wb.open(search_url)
    except Exception as e:
        print(f"Could not perform web search: {e}")
        speak("Sorry, I encountered an error while trying to search the web.")

def generate_response(_query, history, pipe, is_tool_check=False):
    """
    Generates a response using the Hugging Face text-generation pipeline.
    """
    try:
        if not is_tool_check:
            history.append({"role": "user", "content": _query})
        
        outputs = pipe(
            history,
            max_new_tokens=256,
            eos_token_id=terminators,
            do_sample=True,
            temperature=0.6,
            top_p=0.9,
        )
        
        response = outputs[0]["generated_text"][-1]["content"]
        
        if not is_tool_check:
            history.append({"role": "assistant", "content": response})

        return response, history
    
    except Exception as e:
        print(f"Error generating response: {e}")
        return "I seem to be having some trouble with my thoughts right now.", history

def get_vcf_contacts(file_path):
    """
    Parses a .vcf file and returns a dictionary of contacts.
    """
    contacts = {}
    try:
        with open(file_path, 'r') as f:
            for card in vobject.readComponents(f):
                if hasattr(card, 'fn'):
                    name = card.fn.value
                    phone = None
                    if hasattr(card, 'tel'):
                        phone = card.tel.value
                    contacts[name.lower()] = {
                        'name': name,
                        'phone': phone,
                        'email': None
                    }
        return contacts
    except Exception as e:
        print(f"Error parsing VCF file: {e}")
        return {}

def find_contact(name):
    return contacts.get(name.lower())

def send_whatsapp_message(contact_name, message):
    if not contact_name or not message:
        speak("I'm missing some information. Who should I message and what should it say?")
        return

    contact = find_contact(contact_name)
    if contact and contact['phone']:
        full_message = f"{message}\n**Sent by Pulse AI**"
        try:
            pywhatkit.sendwhatmsg_instantly(contact['phone'], full_message)
            speak("Message sent successfully!")
        except Exception as e:
            print(f"Error sending WhatsApp message: {e}")
            speak("Sorry, I couldn't send the message.")
    else:
        speak(f"Sorry, I couldn't find {contact_name} in your contacts.")


def tool_dispatcher(response):
    """
    Parses the LLM's tool command and calls the appropriate function.
    """
    if not response.strip().startswith("[TOOL:") or not response.strip().endswith("]"):
        return None, None

    print(f"Tool command received: {response}")
    command_str = response.strip()[6:-1]
    parts = command_str.split(',')
    
    tool_name = parts[0].strip()
    params = {}
    for part in parts[1:]:
        key, value = part.split(':', 1)
        params[key.strip()] = value.strip()

    if tool_name == "song_play":
        song_play(params.get('_query'))
        return tool_name, "Song is playing."
    elif tool_name == "screenshot":
        screenshot()
        return tool_name, "Screenshot taken."
    elif tool_name == "send_whatsapp_message":
        send_whatsapp_message(params.get('contact'), params.get('message'))
        return tool_name, "Message sent."
    elif tool_name == "web_search":
        web_search(params.get('query'))
        return tool_name, "Searching the web."
    elif tool_name == "open_browser":
        wb.open("https.www.google.com")
        return tool_name, "Browser opened."
        
    return None, "Unknown tool."

# def email(_msg):

if __name__ == '__main__':
    
    get_contacts = get_vcf_contacts("contacts.vcf")
    contacts = {**get_contacts}
    asr_pipeline = None
    if not check_internet_connection():
        print("Loading local speech recognition model (Whisper)...")
        device = "cuda"
        asr_pipeline = pipeline("automatic-speech-recognition", model="openai/whisper-small", device=device)
        print("Whisper model loaded.")
    
    greet(name)
    
    conversation_history = load_history()
    print("Conversation history loaded.")
    
    listening = True

    while True:
        if listening:
            query = command(asr_pipeline).lower().strip()
            
            if not query or query == "0":
                listening = False
                continue

            tool_check_history = [{"role": "system", "content": tool_system_prompt}, {"role": "user", "content": query}]
            initial_response, _ = generate_response(query, tool_check_history, llm_pipeline, is_tool_check=True)

            tool_name, tool_result = tool_dispatcher(initial_response)

            if tool_name:
                print(f"Executed tool: {tool_name}")
                speak(tool_result)
                time.sleep(1)
                
                conversation_history.append({"role": "user", "content": query})
                conversation_history.append({"role": "assistant", "content": f"Executed tool: {tool_name}"})
                save_history(conversation_history)
                listening = False
            
            elif "[CHAT]" in initial_response:
                
                print("Model designated as chat. Generating conversational response...")
                
                chat_response, conversation_history = generate_response(query, conversation_history, llm_pipeline)
                print(f"PulseAI: {chat_response}")
                speak(chat_response)
                time.sleep(1)
                save_history(conversation_history)
                
            else:
                print(f"PulseAI (Fallback): {initial_response}")
                speak("I'm not sure how to handle that.")
                listening = False
                
        else:
            if listen_for_wake_word(asr_pipeline, "pulse"):
                speak("Yes?")
                listening = True