from transformers import AutoModelForCausalLM, AutoTokenizer,AutoModelForSeq2SeqLM,pipeline
import torch
from pulse_tools.general_tools import *
from pulse_tools.spotify_player import song_play
from pulse_tools.messaging import send_whatsapp_message
from pulse_brain.vlm_agent import start_vision_agent_loop
from pulse_brain.cli_agent import start_cli_agent_loop
import re


def load_model(model_name,cache_directory=None):
    llm_pipeline = pipeline(
        "text-generation",
        model=model_name,
        model_kwargs={"dtype": torch.bfloat16},
        device_map="auto",
    )
    terminators = [
        llm_pipeline.tokenizer.eos_token_id,
        llm_pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]
    # tokenizer = AutoTokenizer.from_pretrained(model_name,cache_dir=cache_directory)
    # model = AutoModelForCausalLM.from_pretrained(model_name,cache_dir=cache_directory,trust_remote_code=True)
    return llm_pipeline, terminators

def generate_response(_query, history, pipe, terminators, is_tool_check=False):
    """
    Generates a response using the Hugging Face text-generation pipeline.
    """
    try:
        if not is_tool_check:
            history.append({"role": "user", "content": _query})
        
        outputs = pipe(
            history,
            max_new_tokens=256,
            eos_token_id=terminators,
            do_sample=True,
            temperature=0.6,
            top_p=0.9,
        )
        
        response = outputs[0]["generated_text"][-1]["content"]
        
        if not is_tool_check:
            history.append({"role": "assistant", "content": response})

        return response, history
    
    except Exception as e:
        print(f"Error generating response: {e}")
        return "I seem to be having some trouble with my thoughts right now.", history

def parse_tool_call(response):
    """
    More robustly parses the [TOOL: ...] string, even with complex params.
    """
    try:
        if not response.strip().startswith("[TOOL:") or not response.strip().endswith("]"):
            return None, None

        print(f"Tool command received: {response}")
        command_str = response.strip()[6:-1]

        match = re.match(r"^\s*([a-zA-Z0-9_]+)\s*,?(.*)", command_str, re.S)
        if not match:
            return None, None
            
        tool_name = match.group(1).strip()
        params_str = match.group(2).strip()
        params = {}

        if not params_str and tool_name in ["open_browser", "screenshot"]:
             return tool_name, {}
    
        if tool_name in ["cli_agent", "vision_agent", "song_play", "web_search"]:
            if ':' in params_str:
                key, value = params_str.split(':', 1)
                params[key.strip()] = value.strip()
            return tool_name, params
        

        # Handle multi-parameter tools like send_whatsapp_message
        if tool_name == "send_whatsapp_message":
            # Find the last 'message:' parameter
            match_msg = re.search(r"message:\s*(.+)", params_str, re.S)
            if not match_msg:
                return tool_name, {} # Failed to parse
                
            params['message'] = match_msg.group(1).strip()
            
            # Find the contact
            contact_part = params_str.split(',')[0]
            if "contact:" in contact_part:
                 params['contact'] = contact_part.split(':', 1)[1].strip()

            return tool_name, params

        return tool_name, params
    except Exception as e:
        print(f"Error parsing tool command: {e}. Full response: {response}")
        return None, None

def tool_dispatcher(response,llm_pipeline, terminators):
    """
    Parses the LLM's tool command and calls the appropriate function.
    """
    tool_name, params = parse_tool_call(response)

    if not tool_name:
        if response != "[CHAT]":
            print(f"Unknown tool format: {response}")
        return None, None
    
    if tool_name == "song_play":
        song_play(params.get('_query'))
        return tool_name, "Song is playing."
    elif tool_name == "screenshot":
        result_message = take_screenshot_and_save()
        return tool_name, "Screenshot taken."
    elif tool_name == "send_whatsapp_message":
        send_whatsapp_message(params.get('contact'), params.get('message'))
        return tool_name, "Message sent."
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
        result_message = start_cli_agent_loop(task_description, llm_pipeline, terminators)
        return tool_name, result_message
        
    return None, "Unknown tool."
