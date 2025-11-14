import datetime
import webbrowser as wb
from urllib.parse import quote_plus
import pyautogui
import os
from pulse_ear.speech_handler import speak

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
    if not os.path.exists(os.path.expanduser('~\\PulseAI\\Pictures\\Screenshots')):
        os.makedirs(os.path.expanduser('~\\PulseAI\\Pictures\\Screenshots'))
    image_path = os.path.expanduser(f'~\\PulseAI\\Pictures\\Screenshots\\PulseAI{datetime.datetime.now().timestamp()}.png')
    image.save(image_path)
    os.startfile(image_path)


def refine_query(_query):
    stop_words = {'play'}
    refined_query = [word for word in _query.split() if word not in stop_words]
    refined_query = " ".join(refined_query)
    return refined_query


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

