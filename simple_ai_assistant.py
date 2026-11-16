# 1. Standard Library Imports
import os

# 2. Third-Party Library Imports
from openai import OpenAI
from dotenv import load_dotenv

# 3. Local Application Imports
from tools import TOOLS, run_tool
from utilities.utilities import log

# Load environment configuration
load_dotenv()

# Initialize OpenAI-compatible local client
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

model_name = os.getenv("MODEL")
print(f"--- 🤖 Agent Initialized with Chained Tools ({model_name}) ---")
print("Type 'exit', 'quit', or 'bye' to end the session.\n")

# Safety boundary: Maximum allowed model rounds per user query
MAX_STEPS = 5

SYSTEM_PROMPT = (
    "Role: You are a helpful, concise AI Agent with real-time tool access. "
    "Task: Answer user questions accurately. Use the available tools when needed. "
    "If a question requires multiple steps (like looking up a user's city first, then checking its weather), call the tools sequentially. "
    "Constraints: Keep responses clear, concise, and factual."
)

messages = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

while True:
    try:
        user_input = input("\n👤 User: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\nSession ended.")
        break

    if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
        print("🤖 Assistant: Shutting down. Goodbye!")
        break

    if not user_input:
        continue

    messages.append({"role": "user", "content": user_input})

    # The Agent Loop: Allows chained (sequential) tool calls up to MAX_STEPS
    for step in range(MAX_STEPS):
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            tools=TOOLS
        )

        msg = response.choices[0].message

        # If no tool calls were requested, the model gave its final text answer!
        if not msg.tool_calls:
            # Safe fallback with (msg.content or "") to prevent TypeError when content is None
            reply = (msg.content or "").strip()
            print("🤖 Assistant: " + reply)
            messages.append({"role": "assistant", "content": reply})
            break

        # Model requested tool call(s)
        log(f"Step {step + 1}: model requested {len(msg.tool_calls)} tool call(s)")
        messages.append(msg)

        for tool_call in msg.tool_calls:
            # Execute tool through modular runner
            result = run_tool(tool_call)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

    else:
        # Python for-else: Only executes if loop finishes ALL steps without a 'break'
        fallback_msg = "Sorry, I could not complete your request within the maximum allowed step limit."
        print("🤖 Assistant: " + fallback_msg)
        messages.append({"role": "assistant", "content": fallback_msg})
