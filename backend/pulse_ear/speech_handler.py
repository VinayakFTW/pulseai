import pyttsx3
import speech_recognition as sr
from transformers import AutoModelForCausalLM, AutoTokenizer,AutoModelForSeq2SeqLM,pipeline
import numpy as np
import sounddevice as sd
import queue
import requests


# --- audio constants for Whisper ---
SAMPLE_RATE = 16000  
BLOCK_SIZE = 800     # How many audio frames per block/chunk
CHANNELS = 1         # Mono audio
DTYPE = "float32"
SILENCE_THRESHOLD = 0.02  # Audio energy threshold to consider as speech
SILENCE_DURATION = 3.5



# Change how the Engine Sounds-------xXunderconstructionXx-------------------------------------------------------------------

"""
def voice_change(voice_index=None):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    try:
        if len(voices) > voice_index:
            engine.setProperty('voice', voices[voice_index].id)
        else:
            print(f"Invalid voice index. Available voices: {list(range(len(voices)))}")
    except Exception as e:
        print(f"Error setting voice: {e}")
        engine.setProperty('voice', voices[0].id)
    return engine
"""

def speak(_audio=None,voice_change=False):
    # if voice_change:
    #     engine = voice_change(voice_index)
    # else:
    #     engine = pyttsx3.init()
    engine = pyttsx3.init()
    engine.say(_audio)
    engine.runAndWait()
    engine.stop()
    return _audio


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
        _recog.pause_threshold = 3
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

def listen_for_wake_word_google(wake_word="wake", duration=2):
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

def listen_for_wake_word_whisper(asr_pipeline, wake_word="wake", duration=2):
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

def listen_for_wake_word(asr_pipeline, wake_word="wake", duration=2):
    """
    Checks for internet and routes to Google (online) or Whisper (offline)
    for wake word detection.
    """
    if check_internet_connection():
        return listen_for_wake_word_google(wake_word, duration)
    else:
        return listen_for_wake_word_whisper(asr_pipeline, wake_word, duration)

def load_asr_pipe(model_name="openai/whisper-small",asr_pipeline=None):
    if not check_internet_connection():
        print(f"Loading local speech recognition model ({model_name})...")
        device = "cuda"
        asr_pipeline = pipeline("automatic-speech-recognition", model=model_name, device=device)
        print("ASR model loaded.")
    return asr_pipeline