import json
from datetime import datetime
import requests
from utilities.utilities import log
from rag import search

# ---------------------------------------------------------
# 1. Actual Python Functions (Executed locally by our code)
# ---------------------------------------------------------

def get_current_time():
    """Returns the current local date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_city_weather(city: str):
    """Fetches current weather for a given city using wttr.in."""
    if not city or not city.strip():
        raise ValueError("City name is required.")
    url = f"https://wttr.in/{city.strip()}?format=3"
    response = requests.get(url, timeout=10)
    response.raise_for_status()  # Raises HTTPError for 4xx/5xx responses
    return response.text.strip()


def get_user_city():
    """Returns the city where the user lives."""
    return "Bangalore"


def search_knowledge_base(query: str) -> str:
    """Searches the company knowledge base for policy or procedural information."""
    log(f"🔍 Knowledge Base Search: '{query}'")
    results = search(query, top_k=2)

    for r in results:
        log(f"   [{r['score']:.2f}] - {r['source']} #{r['chunk_id']}")

    blocks = []
    for r in results:
        header = f"[{r['source']} #{r['chunk_id']}]"
        block = f"{header}\n{r['text']}"
        blocks.append(block)

    return "\n\n".join(blocks)


# ---------------------------------------------------------
# 2. JSON Schema Definitions (The "Menu" sent to the LLM)
# ---------------------------------------------------------

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Returns the current local date and time. Use this whenever the user asks for current time, date, or clock.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_city_weather",
            "description": "Returns the current live weather of a given city. Use this whenever the user asks about weather, conditions, or temperature in a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The name of the city to get the weather for (e.g., Delhi, Seattle)."
                    }
                },
                "required": ["city"]  # Explicitly tell the LLM that 'city' is mandatory!
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_city",
            "description": "Returns the user's home city (e.g. Bangalore). MUST be called when user asks about 'where I live', 'my city', or their location.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "Searches the Zorvex Technologies company knowledge base (leave policy, medical policy, HR, hiring, tech processes, incident reports, and travel expense policies). Use for any questions about company policies or documents. Returns the most relevant passages with their source.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to look up in company policies (e.g., 'maternity leave benefits', 'hospitalization reimbursement limit')."
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# ---------------------------------------------------------
# 3. Dispatch Map (Maps string names from LLM to Python functions)
# ---------------------------------------------------------

FUNCTION_NAME_TO_FUNCTION_MAP = {
    "get_current_time": get_current_time,
    "get_city_weather": get_city_weather,
    "get_user_city": get_user_city,
    "search_knowledge_base": search_knowledge_base
}


# ---------------------------------------------------------
# 4. Modular Tool Runner (Executes, handles errors & logs)
# ---------------------------------------------------------

def run_tool(tool_call):
    """Executes a single tool call from the model, logs execution, and safely handles errors."""
    func_name = tool_call.function.name
    func_args = {}
    try:
        func_args = json.loads(tool_call.function.arguments or "{}")
        log(f"🔧 {func_name}({func_args})")
        fn = FUNCTION_NAME_TO_FUNCTION_MAP[func_name]
        result = fn(**func_args)
    except Exception as e:
        result = f"Error while running {func_name}: {e}"

    log(f"   ↳ {result}")
    return str(result)
