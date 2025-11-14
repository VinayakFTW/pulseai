from transformers import AutoModelForCausalLM, AutoTokenizer,AutoModelForSeq2SeqLM,pipeline
from dotenv import load_dotenv
import torch
from pulse_tools.general_tools import *
from pulse_tools.spotify_player import song_play
from pulse_tools.messaging import send_whatsapp_message

load_dotenv()


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

def tool_dispatcher(response):
    """
    Parses the LLM's tool command and calls the appropriate function.
    """
    if not response.strip().startswith("[TOOL:") or not response.strip().endswith("]"):
        return None, None

    print(f"Tool command received: {response}")
    command_str = response.strip()[6:-1]
    parts = command_str.split(',')
    
    tool_name = parts[0].strip()
    params = {}
    for part in parts[1:]:
        key, value = part.split(':', 1)
        params[key.strip()] = value.strip()

    if tool_name == "song_play":
        song_play(params.get('_query'))
        return tool_name, "Song is playing."
    elif tool_name == "screenshot":
        screenshot()
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
        
    return None, "Unknown tool."
