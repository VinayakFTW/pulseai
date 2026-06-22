from dotenv import load_dotenv
load_dotenv()
import time
from pulse_ear.speech_handler import listen_for_wake_word,command,load_asr_pipe,speak
from pulse_config.prompts import tool_system_prompt
from pulse_brain.llm_interface import tool_dispatcher,load_model,generate_response
from pulse_brain.memory_manager import *
from pulse_tools.general_tools import greet

from pulse_brain.execution_loop import execute_autonomous_loop

if __name__ == '__main__':
    asr_pipeline = load_asr_pipe()
    client = load_model()
    greet("Vinayak")
    
    print("Conversation history loaded.")
    
    listening = True
    mode = input("Select mode: (1) Voice\t(2) Text ").strip()
    
    while True:
        if listening:
            if mode == "1":
                query = command(asr_pipeline).lower().strip()
            else:
                query = input(">").lower().strip()

            if not query or query == "0":
                listening = False
                continue

            execute_autonomous_loop(client, initial_query=query)
            listening = False
            
        else:
            if listen_for_wake_word(asr_pipeline, "wake"):
                speak("Yes?")
                listening = True