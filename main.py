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


system_prompt = """You are Pulse, my personal AI agent integrated into this laptop. Your core mission is to function as a seamless, proactive, and intelligent extension of my mind and workflow. Your primary goal is to anticipate my needs, optimize my productivity, and manage my digital environment with maximum efficiency and security. You are more than a reactive assistant; you are a strategic partner.

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

    Focus on Augmentation, Not Replacement: Your goal is to augment my intelligence and capabilities, not replace my judgment. Present curated options and analyses, but the final decision is always mine.

Final Note
In addition to your other capabilities, you have the ability to search the web. If you do not know the answer to a question or need up-to-date information, you must respond with ONLY the following command:
[SEARCH: your search query here]

For example, if the user asks "What's the weather like today?", you should respond with:
[SEARCH: weather today] 
"""

handled = False
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

#audio input------------------------------------------------------------------------------------------------------------------------
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
                    return [{"role": "system", "content": system_prompt}]
                return history
        except (json.JSONDecodeError, IndexError):
            return [{"role": "system", "content": system_prompt}]
    else:
        return [{"role": "system", "content": system_prompt}]

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


def command(asr_pipeline):
    """
    Listens for speech from the microphone in a continuous stream,
    detects when the user stops talking, and transcribes the utterance locally.
    """
    audio_queue = queue.Queue()

    def audio_callback(indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, flush=True)
        audio_queue.put(bytes(indata))

    print("Listening...")
    
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
                    # If loud enough we consider it speech
                    if not is_speaking:
                        print("Speaking detected...")
                    is_speaking = True
                    silent_blocks = 0
                    speech_data.append(audio_chunk)
                elif is_speaking:
                    # If we were speaking but now its silent
                    silent_blocks += 1
                    speech_data.append(audio_chunk) #the silence at the end

                    if silent_blocks > max_silent_blocks:
                        # If silence then stiop
                        print("Recognizing...")
                        break
    except Exception as e:
        print(f"An error occurred: {e}")
        return "0"

    # --- Transcription ---
    if not speech_data:
        print("No speech detected.")
        return "0"

    full_audio = b"".join(speech_data)
    full_audio_np = np.frombuffer(full_audio, dtype=DTYPE)

    try:
        result = asr_pipeline(full_audio_np,generate_kwargs={"language":"en"})
        query = result["text"]
        print(f"Recognized: {query}")
        return query
    except Exception as e:
        print(f"Error during transcription: {e}")
        return "0"


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
        search_url = f"https://www.google.com/search?q={encoded_query}"
        print(f"Searching for: {query}")
        speak(f"Searching the web for {query}")
        wb.open(search_url)
    except Exception as e:
        print(f"Could not perform web search: {e}")
        speak("Sorry, I encountered an error while trying to search the web.")

def generate_response(_query, history, pipe):
    """
    Generates a response using the Hugging Face text-generation pipeline.
    """
    try:
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
        
        history.append({"role": "assistant", "content": response})

        return response, history
    
    except Exception as e:
        print(f"Error generating response: {e}")
        #crash hora tha errors mai so returned two vals
        return "I seem to be having some trouble with my thoughts right now.", history

def listen_for_wake_word(asr_pipeline, wake_word="pulse", duration=2):
    """
    Listens for a short duration and uses Whisper to check for a specific wake word.
    """
    print(f"Listening for wake word '{wake_word}'...")
    try:
        audio_chunk = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype=DTYPE)
        sd.wait()

        audio_np = audio_chunk.flatten()

        result = asr_pipeline(
            audio_np,
            generate_kwargs={"language":"en"}
        )
        
        transcribed_text = result["text"].lower().strip()

        if wake_word in transcribed_text:
            print(f"Wake word detected in: '{transcribed_text}'")
            return True
        
        return False
    except Exception as e:
            print(f"An error occurred during wake word detection: {e}")
            return False

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

def send_whatsapp_message(_query):
    
    contact_name = _query.lower().split()
    contact_name.remove("send")
    contact_name.remove("a")
    contact_name.remove("message")
    contact_name.remove("to")
    contact_name = " ".join(contact_name)
    if '.' in contact_name:
        contact_name = contact_name.split('.')[0]
        print(contact_name)
    if contact_name and contact_name != "0":
        contact = find_contact(contact_name)
        if contact and contact['phone']:
            print(f"phone number found : {contact['phone']}")
            speak("What should the message say?")
            message = command(asr_pipeline)
            message += "\n**THIS MESSAGE WAS SENT BY PULSE(VINAYAK'S AI ASSISTANT)**"
            if message and message != "0":
                print(f"message : {message}")
                try:
                    pywhatkit.sendwhatmsg_instantly(contact['phone'], message)
                    speak("Message sent successfully!")
                except Exception as e:
                    print(f"Error sending WhatsApp message: {e}")
                    speak("Sorry, I couldn't send the message.")
        else:
            speak("Sorry, I couldn't find that contact or they don't have a phone number.")


# def email(_msg):

if __name__ == '__main__':
    
    get_contacts = get_vcf_contacts("contacts.vcf")
    contacts = {**get_contacts}
    device = "cpu"
    asr_pipeline = pipeline("automatic-speech-recognition", model="openai/whisper-small", device=device)
    greet(name)
    
    conversation_history = load_history()
    print("Conversation history loaded.")
    
    listening = True

    while True:
        if listening:
            query = command(asr_pipeline)
            handled = False
            if not query or query == "0":
                continue

            elif 'play' in query.lower():
                query = refine_query(query)
                song_play(query)
                listening = False
                handled = True
            elif 'screenshot' in query.lower():
                screenshot()
                listening = False
                handled = True

            elif 'send a message' in query.lower():
                send_whatsapp_message(query)
                listening = False
                handled = True
            
            elif 'power off' in query.lower():
                print("Goodbye!")
                speak("Goodbye!")
                quit()

            if not handled:
                response, conversation_history = generate_response(query, conversation_history, llm_pipeline)
                
                print(f"PulseAI: {response}")
                time.sleep(0.1)
                speak(response)
                
                if response.strip().startswith("[SEARCH:") and response.strip().endswith("]"):
                    search_query = response.strip()[8:-1].strip()
                    web_search(search_query)
                    listening = False
                    handled = True

                elif response.strip().startswith("[OPEN BROWSER") and response.strip().endswith("]"):
                    wb.open("https://www.google.com")
                    listening = False
                    handled = True
                
                save_history(conversation_history)
                print("Conversation history saved.")
        else:
            if listen_for_wake_word(asr_pipeline, "pulse"):
                speak("Yes?")
                listening = True