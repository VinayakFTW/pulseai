from openai import OpenAI
from pulse_tools.general_tools import *
from pulse_tools.spotify_player import song_play
from pulse_tools.messaging import send_whatsapp_message, find_contact
from pulse_brain.vlm_agent import start_vision_agent_loop
from pulse_brain.cli_agent import start_cli_agent_loop
import re


def load_model():
    """
    Initializes and returns the OpenAI client.
    """
    client = OpenAI(
        base_url="http://127.0.0.1:31415/v1",
        api_key=os.environ.get("OPENAI_API_KEY")
    )
    return client

def generate_response(_query, history, client, is_tool_check=False):
    """
    Generates a response using OpenAI's chat completions API endpoint.
    """
    try:
        if not is_tool_check:
            history.append({"role": "user", "content": _query})
        
        response = client.chat.completions.create(
            model="auto",
            messages=history,
            temperature=0.6,
            top_p=0.9
        )
        
        response_text = response.choices[0].message.content
        
        if not is_tool_check:
            history.append({"role": "assistant", "content": response_text})

        return response_text, history
    
    except Exception as e:
        print(f"Error generating response from OpenAI: {e}")
        return "I seem to be having some trouble with my thoughts right now.", history

import json

def parse_tool_call(response):
    """
    Parses the JSON tool command.
    """
    try:
        # Try to find JSON block if there is extra text
        json_str = response.strip()
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0].strip()

        print(f"Parsing JSON command: {json_str}")
        data = json.loads(json_str)
        
        action = data.get("action")
        arguments = data.get("arguments", {})
        
        if action == "chat":
            return "[CHAT]", {}
            
        return action, arguments
    except json.JSONDecodeError as e:
        print(f"Error parsing tool command as JSON: {e}. Full response: {response}")
        return None, None
    except Exception as e:
        print(f"Unexpected error parsing tool command: {e}")
        return None, None

def tool_dispatcher(response,llm_pipeline):
    """
    Parses the LLM's tool command and calls the appropriate function.
    """
    tool_name, params = parse_tool_call(response)

    if tool_name == "[CHAT]":
        return "[CHAT]", ""

    if not tool_name:
        print(f"Unknown or invalid JSON format: {response}")
        return None, None
    
    if tool_name == "song_play":
        song_play(params.get('_query'))
        return tool_name, "Song is playing."
    elif tool_name == "screenshot":
        result_message = take_screenshot_and_save()
        return tool_name, "Screenshot taken."
    elif tool_name == "find_contact":
        contact_info = find_contact(params.get('name'))
        if contact_info:
            return tool_name, f"Contact info: {contact_info}"
        else:   
            return tool_name, "Contact not found."
    elif tool_name == "send_whatsapp_message":
        flag = send_whatsapp_message(params.get('contact'), params.get('message'))
        if flag:
            return tool_name, "Message sent."
        else:
            return tool_name, "Failed to send message."
    elif tool_name == "web_search":
        web_search(params.get('query'))
        return tool_name, "Searching the web."
    elif tool_name == "open_browser":
        wb.open("https.www.google.com")
        return tool_name, "Browser opened."
    elif tool_name == "vision_agent":
        task_description = params.get('task')
        result_message = start_vision_agent_loop(task_description)
        return tool_name, result_message
    elif tool_name == "cli_agent":
        task_description = params.get('task')
        result_message = start_cli_agent_loop(task_description, llm_pipeline)
        return tool_name, result_message
        
    return None, "Unknown tool."
