import json
import os
from pulse_config.prompts import chat_system_prompt
from datetime import datetime

HISTORY_FILE = "conversation_history.json"
LONG_TERM_MEMORY_FILE = ".pulse/long_term_memory.json"
MAX_WORKING_MEMORY_MESSAGES = 20

class MemoryManager:
    def __init__(self):
        self.history_file = HISTORY_FILE
        self.long_term_file = LONG_TERM_MEMORY_FILE
        self._ensure_directories()
        
    def _ensure_directories(self):
        os.makedirs(".pulse", exist_ok=True)
        if not os.path.exists(self.long_term_file):
            with open(self.long_term_file, "w") as f:
                json.dump([], f)

    def load_working_memory(self):
        """Loads the current session history, truncated to fit the context window."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
                    if not history or history[0].get('role') != 'system':
                        return [{"role": "system", "content": chat_system_prompt}]
                    
                    history[0]['content'] = chat_system_prompt
                    
                    # Truncate if too long, keeping system prompt and most recent messages
                    if len(history) > MAX_WORKING_MEMORY_MESSAGES:
                        history = [history[0]] + history[-(MAX_WORKING_MEMORY_MESSAGES-1):]
                    return history
            except (json.JSONDecodeError, IndexError):
                return [{"role": "system", "content": chat_system_prompt}]
        return [{"role": "system", "content": chat_system_prompt}]

    def save_working_memory(self, history):
        """Saves current session history."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=4)
        except Exception as e:
            print(f"Error saving working memory: {e}")

    def save_to_long_term(self, memory_text, source="reflection"):
        """Saves a learned fact or preference into long-term memory."""
        try:
            with open(self.long_term_file, "r") as f:
                ltm = json.load(f)
            
            ltm.append({
                "timestamp": datetime.now().isoformat(),
                "source": source,
                "content": memory_text
            })
            
            with open(self.long_term_file, "w") as f:
                json.dump(ltm, f, indent=4)
            print(f"Saved to Long Term Memory: {memory_text}")
        except Exception as e:
            print(f"Error saving to long term memory: {e}")

    def get_long_term_summary(self):
        """Retrieves a summarized string of long-term memories to inject into prompt."""
        try:
            with open(self.long_term_file, "r") as f:
                ltm = json.load(f)
            if not ltm:
                return ""
            
            summary = "Prior Knowledge & Learnings:\n"
            for mem in ltm[-10:]: # Get latest 10
                summary += f"- {mem['content']}\n"
            return summary
        except Exception:
            return ""

# Global instance
memory = MemoryManager()

# Backwards compatibility wrappers
def load_history():
    return memory.load_working_memory()

def save_history(history):
    memory.save_working_memory(history)
