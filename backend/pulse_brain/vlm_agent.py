import json
from PIL import Image
import io
import base64
from pulse_config.prompts import VLM_SYSTEM_PROMPT
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
    VISION_MODEL_ID = "llama-4-maverick"
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
        {'role': 'system', 'content': VLM_SYSTEM_PROMPT},
        {'role': 'assistant', 'content': "OK. I am ready to start the task."}
    ]
    while True:
        try:
            # 1. OBSERVE
            img = get_screenshot_for_analysis()
            base64_image = encode_pil_to_base64(img)
            
            # 2. THINK
            current_turn = {
                'role': 'user', 
                'content': [
                    {
                        "type": "text",
                        "text": f"Current Task: {task_description}\n\nBased on the history and this current screen, what is the next single action to perform?\nIMPORTANT: Respond strictly with a single, valid JSON object. Do not include markdown code blocks (like ```json), conversational filler, or any text outside the JSON boundaries."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
                
            messages_payload = vlm_history + [current_turn]

            response = openai_client.chat.completions.create(
                model=VISION_MODEL_ID,
                messages=messages_payload,
                response_format={"type": "json_object"},
                max_tokens=256,
                temperature=0.4
            )

            # update history with the user's image query and the assistant's response
            vlm_history.append(current_turn)
            response_text = response.choices[0].message.content
            vlm_history.append({'role': 'assistant', 'content': response_text})

            try:
                ai_decision = json.loads(response_text)
                thought = ai_decision.get("thought", "...")
                action = ai_decision.get("action")
                args = ai_decision.get("arguments", {})
            except json.JSONDecodeError:
                print(f"Error: VLM did not return valid JSON. Response: {response_text}")
                speak("My vision processing returned an invalid format. Stopping.")
                vlm_history.append({'role': 'user', 'content': f"Tool Output: Invalid JSON response received: {response_text}"})
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
                vlm_history.append({'role': 'user', 'content': f"Tool Output: No action provided in response: {response_text}"})
                
                continue

            tool_output = vlm_tool_executor(action, args)
            print(f"VLM Observation: {tool_output}")
                
            # Append the tool output strictly as text
            vlm_history.append({'role': 'user', 'content': f"Tool Output: {tool_output}"})

        except Exception as e:
            print(f"Error in VLM loop: {e}")
            speak("I ran into an error with my vision. Stopping the task.")
            return f"Error in VLM loop: {e}"