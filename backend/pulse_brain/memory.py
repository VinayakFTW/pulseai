import json
import os
from pulse_config.prompts import chat_system_prompt

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
