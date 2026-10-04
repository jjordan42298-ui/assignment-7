from groq import Groq
from tools import TOOL_SCHEMAS

def run_agent_loop(client: Groq, messages: list) -> tuple:
    """
    Drives a multi-turn chat interaction loop up to an iteration threshold.
    Returns (assistant_message_object, tool_calls_list_or_None)
    """
    MAX_ITERATIONS = 5
    iterations = 0
    
    while iterations < MAX_ITERATIONS:
        iterations += 1
        
        # Call the Qwen tool-supporting model with an explicit output token restriction
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=messages,
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
            max_tokens=150
        )
        
        # FIX: Index into the first choice element in the list array
        response_msg = response.choices[0].message
        
        # Stop loop and yield control to UI if tools need to execute
        if response_msg.tool_calls:
            messages.append(response_msg)
            return response_msg, response_msg.tool_calls
        else:
            # Reached a final textual solution
            return response_msg, None
            
    return None, None
