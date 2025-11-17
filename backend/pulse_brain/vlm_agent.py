import json
from PIL import Image
# from pulse_config.config import VLM_SYSTEM_PROMPT
from pulse_tools.general_tools import get_screenshot_for_analysis, mouse_click, type_text
from pulse_ear.speech_handler import speak
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

try:
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    vlm_model = genai.GenerativeModel('gemini-2.5-flash')
    print("Gemini VLM model loaded.")
except Exception as e:
    print(f"Error loading Gemini VLM: {e}. Vision tasks will fail.")
    vlm_model = None

def vlm_tool_executor(action: str, args: dict) -> str:
    """Executes the UI tools chosen by the VLM."""
    if action == "mouse_click":
        # Ensure coordinates are integers if they are provided
        x = args.get('x')
        y = args.get('y')
        return mouse_click(int(x) if x is not None else None, int(y) if y is not None else None)
    elif action == "type_text":
        return type_text(args.get('text'))
    return f"Unknown VLM tool: {action}"

def start_vision_agent_loop(task_description: str) -> str:
    """
    This is the "Observe-Think-Act" loop for the VLM.
    """
    if not vlm_model:
        speak("The vision model is not loaded. Cannot perform UI tasks.")
        return "Vision model not loaded."

    print(f"Vision Agent Activated. Task: {task_description}")
    speak(f"Starting vision task: {task_description}")
    
    # This list will store the *full* chat history for the VLM
    vlm_history = [
        {'role': 'user', 'parts': [VLM_SYSTEM_PROMPT]},
        {'role': 'model', 'parts': ["OK. I am ready to start the task."]}
    ]
    
    for _ in range(10): # Safety break after 10 steps
        try:
            # 1. OBSERVE
            img = get_screenshot_for_analysis()
            
            # 2. THINK
            prompt_parts = [
                f"Current Task: {task_description}\n\nBased on the history and this current screen, what is the next single action to perform?",
                img
            ]
            
            # Send the *entire* history plus the new prompt
            response = vlm_model.generate_content(
                contents=[*vlm_history, {'role': 'user', 'parts': prompt_parts}],
                generation_config={"response_mime_type": "application/json"}
            )

            vlm_history.append({'role': 'user', 'parts': prompt_parts})
            vlm_history.append({'role': 'model', 'parts': [response.text]})


            try:
                ai_decision = json.loads(response.text)
                thought = ai_decision.get("thought", "...")
                action = ai_decision.get("action")
                args = ai_decision.get("arguments", {})
            except json.JSONDecodeError:
                print(f"Error: VLM did not return valid JSON. Response: {response.text}")
                speak("My vision processing returned an invalid format. Stopping.")
                # Add the error as an observation and let the loop continue
                vlm_history.append({'role': 'user', 'parts': [f"Tool Output: Invalid JSON response received: {response.text}"]})
                continue

            print(f"VLM Thought: {thought}")
            
            # 3. ACT
            if action == "finish":
                print("Vision Task Complete.")
                speak("Vision task complete.")
                return "Vision task finished."

            if not action:
                print(f"Error: VLM did not provide an action. Response: {response.text}")
                speak("My vision processing failed to provide an action. Stopping.")
                vlm_history.append({'role': 'user', 'parts': [f"Tool Output: No action provided in response: {response.text}"]})
                continue

            tool_output = vlm_tool_executor(action, args)
            print(f"VLM Observation: {tool_output}")
            
            vlm_history.append({'role': 'user', 'parts': [f"Tool Output: {tool_output}"]})

        except Exception as e:
            print(f"Error in VLM loop: {e}")
            speak("I ran into an error with my vision. Stopping the task.")
            return f"Error in VLM loop: {e}"
            
    speak("Task step limit reached. Stopping.")
    return "Vision task step limit reached."


VLM_SYSTEM_PROMPT = """
You are an expert UI automation agent. You will be given a high-level task and a screenshot.
Your job is to look at the screenshot and decide the SINGLE next action to perform.
You have access to these tools:
- [mouse_click, x: int, y: int]: Clicks the mouse.
- [type_text, text: string]: Types text.
- [finish]: Call this when the task is complete.

RESPONSE FORMAT:
You MUST respond with a JSON object.
{
  "thought": "Your step-by-step reasoning for this single action.",
  "action": "function_name",
  "arguments": {"arg1": "value1"}
}

EXAMPLE:
User Task: "Type 'hello' in the text field."
(User sends screenshot)
{
  "thought": "I see a text field. I need to click it before I can type. I will estimate its coordinates.",
  "action": "mouse_click",
  "arguments": {"x": 450, "y": 300}
}
(After the click, the loop runs again with a new screenshot)
{
  "thought": "The cursor is now blinking in the text field. I can now type.",
  "action": "type_text",
  "arguments": {"text": "hello"}
}
"""