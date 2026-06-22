from pulse_brain.cli_agent import start_cli_agent_loop
from pulse_brain.llm_interface import load_model

def cli_agent(task):
    # Retrieve local LLM client dynamically if needed
    client = load_model()
    return start_cli_agent_loop(task, client)
