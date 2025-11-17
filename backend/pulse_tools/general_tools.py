import datetime
import webbrowser as wb
from urllib.parse import quote_plus
import pyautogui
from PIL import ImageGrab
import os
from pulse_ear.speech_handler import speak
import subprocess

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


def take_screenshot_and_save():
    """
    This is RENAMED original screenshot function.
    It saves a screenshot for the user.
    """
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

def get_screenshot_for_analysis():
    img = ImageGrab.grab()
    return img

def mouse_click(x, y):
    try:
        pyautogui.click(x=int(x), y=int(y))
        return f"Clicked at ({x}, {y})."
    except Exception as e:
        return f"Error clicking: {e}"

def type_text(text):
    try:
        pyautogui.write(text)
        return f"Typed: '{text}'."
    except Exception as e:
        return f"Error typing: {e}"
    
def execute_shell_command(command):
    """
    Executes a given shell command in the terminal and returns its output or error.
    """
    if not command:
        return "No command provided to execute."
        
    try:
        print(f"Executing CLI command: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        
        output = result.stdout.strip()
        if not output:
            return "Command executed successfully with no output."
        return output
        
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e.stderr.strip()}")
        return f"Command failed with error: {e.stderr.strip()}"
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return f"An error occurred while executing command: {str(e)}"