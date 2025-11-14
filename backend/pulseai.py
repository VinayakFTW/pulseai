import time
from pulse_ear.speech_handler import listen_for_wake_word,command,load_asr_pipe,speak
from pulse_config.config import *
from pulse_brain.llm_interface import tool_dispatcher
from pulse_tools.general_tools import greet

if __name__ == '__main__':
    
    asr_pipeline = load_asr_pipe()

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
            if listen_for_wake_word(asr_pipeline, "wake"):
                speak("Yes?")
                listening = True