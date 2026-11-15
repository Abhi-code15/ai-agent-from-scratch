import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from tools import TOOLS, FUNCTION_NAME_TO_FUNCTION_MAP

# 1. Load environment variables
load_dotenv()

# 2. Initialize client
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

model_name = os.getenv("MODEL")
print(f"--- Tool-Enabled Assistant Initialized ({model_name}) ---")
print("Type 'exit', 'quit', or 'bye' to end the session.\n")

SYSTEM_PROMPT = (
    "Role: You are a helpful and concise AI Assistant with real-time tool access. "
    "Task: Answer user questions accurately. Use the provided tools whenever external or real-time information (like live time or weather) is needed. "
    "Constraints: Keep responses clear, concise, and factual."
)

messages = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

while True:
    try:
        user_input = input("\nUser: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nSession ended.")
        break

    if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
        print("Assistant: Goodbye!")
        break

    if not user_input:
        continue

    messages.append({"role": "user", "content": user_input})

    # 3. First API Call: Send history + tool definitions
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        tools=TOOLS
    )

    msg = response.choices[0].message

    # 4. Check if the model decided to call any tools
    if msg.tool_calls:
        # Append the assistant's tool_call request message to history
        messages.append(msg)

        # Loop through every tool the model requested
        for tool_call in msg.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments or "{}")

            # Look up and execute the local Python function
            fn = FUNCTION_NAME_TO_FUNCTION_MAP[func_name]
            result = fn(**func_args)

            # Append the tool's output back to history with role="tool"
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

        # 5. Second API Call: Let the LLM read the tool output and answer the user
        second_response = client.chat.completions.create(
            model=model_name,
            messages=messages
        )
        final_reply = second_response.choices[0].message.content or ""
        print("Assistant: " + final_reply)
        messages.append({"role": "assistant", "content": final_reply})

    else:
        # Normal text reply (no tools needed)
        reply = msg.content or ""
        print("Assistant: " + reply)
        messages.append({"role": "assistant", "content": reply})
