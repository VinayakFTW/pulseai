import json
from PIL import Image
import io
import base64
# from pulse_config.config import VLM_SYSTEM_PROMPT
from pulse_tools.general_tools import get_screenshot_for_analysis, mouse_click, type_text
from pulse_ear.speech_handler import speak
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

try:
    openai_client = OpenAI(
        base_url="http://127.0.0.1:31415/v1",
        api_key=os.environ.get("OPENAI_API_KEY")
    )
    VISION_MODEL_ID = "glm-4.6v-flash" 
    print("OpenAI Vision agent initialized.")
except Exception as e:
    print(f"Error loading OpenAI Vision client: {e}. Vision tasks will fail.")
    openai_client = None

def encode_pil_to_base64(pil_img):
    """Converts a PIL Image object into a base64 string for OpenAI's API."""
    buffered = io.BytesIO()
    pil_img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')
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
    if not openai_client:
        speak("The vision model is not loaded. Cannot perform UI tasks.")
        return "Vision model not loaded."

    print(f"Vision Agent Activated. Task: {task_description}")
    speak(f"Starting vision task: {task_description}")
    
    vlm_history = [
        {'role': 'user', 'parts': [VLM_SYSTEM_PROMPT]},
        {'role': 'model', 'parts': ["OK. I am ready to start the task."]}
    ]
    
    for _ in range(20): # Safety break after 20 steps
        try:
            # 1. OBSERVE
            img = get_screenshot_for_analysis()
            base64_image = encode_pil_to_base64(img)
            
            # 2. THINK
            prompt_parts = [
                f"Current Task: {task_description}\n\nBased on the history and this current screen, what is the next single action to perform?",
                img
            ]
            current_prompt_content = [
                {
                    "type": "text",
                    "text": f"Current Task: {task_description}\n\nBased on the history and this current screen, what is the next single action to perform?"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"
                    }
                }
            ]
            current_turn = {'role': 'user', 'content': current_prompt_content}
            messages_payload = [*vlm_history, current_turn]

            response = openai_client.chat.completions.create(
                model=VISION_MODEL_ID,
                messages=messages_payload,
                response_format={"type": "json_object"},
                max_tokens=256,
                temperature=0.4
            )

            vlm_history.append({'role': 'user', 'parts': prompt_parts})
            vlm_history.append({'role': 'model', 'parts': [response.choices[0].message.content]})

            response_text = response.choices[0].message.content

            try:
                ai_decision = json.loads(response_text)
                thought = ai_decision.get("thought", "...")
                action = ai_decision.get("action")
                args = ai_decision.get("arguments", {})
            except json.JSONDecodeError:
                print(f"Error: VLM did not return valid JSON. Response: {response_text}")
                speak("My vision processing returned an invalid format. Stopping.")
                # Add the error as an observation and let the loop continue
                vlm_history.append({'role': 'user', 'parts': [f"Tool Output: Invalid JSON response received: {response_text}"]})
                continue

            print(f"VLM Thought: {thought}")
            
            # 3. ACT
            if action == "finish":
                print("Vision Task Complete.")
                speak("Vision task complete.")
                return "Vision task finished."

            if not action:
                print(f"Error: VLM did not provide an action. Response: {response_text}")
                speak("My vision processing failed to provide an action. Stopping.")
                vlm_history.append({'role': 'user', 'parts': [f"Tool Output: No action provided in response: {response_text}"]})
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