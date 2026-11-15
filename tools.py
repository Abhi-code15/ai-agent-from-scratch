from datetime import datetime
import requests

# ---------------------------------------------------------
# 1. Actual Python Functions (Executed locally by our code)
# ---------------------------------------------------------

def get_current_time():
    """Returns the current local date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_city_weather(city: str):
    """Fetches current weather for a given city using wttr.in."""
    url = f"https://wttr.in/{city}?format=3"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text.strip()

def get_user_city():
    """Returns the city where the user lives."""
    return "Bangalore"

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
                "required": ["city"]
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
    }
]

# ---------------------------------------------------------
# 3. Dispatch Map (Maps string names from LLM to Python functions)
# ---------------------------------------------------------

FUNCTION_NAME_TO_FUNCTION_MAP = {
    "get_current_time": get_current_time,
    "get_city_weather": get_city_weather,
    "get_user_city": get_user_city
}
