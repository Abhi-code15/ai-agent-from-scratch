# 1. Standard Library Imports
import os
from types import SimpleNamespace

# 2. Third-Party Library Imports
from dotenv import load_dotenv
from openai import OpenAI

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

# Safety boundary: Maximum allowed model rounds per user query
MAX_STEPS = 5

SYSTEM_PROMPT = (
    "You are a helpful, humble assistant. Answer general questions like programming, science, or advice using your knowledge. "
    "Use a tool ONLY when the user asks for current time, the weather, or their city. "
    "Keep answers under 100 words."
)

messages = [
    {"role": "system", "content": SYSTEM_PROMPT}
]


def build_tool_calls_payload(tool_calls):
    """
    Converts collected SimpleNamespace tool calls into the exact list of dictionaries
    expected by the OpenAI API spec inside an assistant message.
    """
    payload = []
    for tc in tool_calls:
        payload.append({
            "id": tc.id,
            "type": "function",
            "function": {
                "name": tc.function.name,
                "arguments": tc.function.arguments
            }
        })
    return payload


def stream_chat(messages_history):
    """
    Streams response chunks from the model, printing text tokens in real time
    and reconstructing fragmented tool calls.
    Handles KeyboardInterrupt (Ctrl+C) gracefully to allow safe cancellation.
    Returns: (full_response: str, calls_list: list)
    """
    stream = client.chat.completions.create(
        model=model_name,
        messages=messages_history,
        tools=TOOLS,
        stream=True
    )

    full_response = ""
    calls = {}
    label_printed = False

    try:
        for chunk in stream:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            # 1. Handle live text streaming
            if delta.content:
                if not label_printed:
                    print("🤖 Assistant: ", end="", flush=True)
                    label_printed = True
                print(delta.content, end="", flush=True)
                full_response += delta.content

            # 2. Handle partial tool call chunks
            if delta.tool_calls:
                for tc in delta.tool_calls:
                    index = tc.index
                    obj = calls.setdefault(
                        index,
                        SimpleNamespace(
                            id="",
                            function=SimpleNamespace(name="", arguments="")
                        )
                    )
                    if tc.id:
                        obj.id = tc.id
                    if tc.function and tc.function.name:
                        obj.function.name += tc.function.name
                    if tc.function and tc.function.arguments:
                        obj.function.arguments += tc.function.arguments

    except KeyboardInterrupt:
        print("\n\n⏹️ [Stopped by you]")
        calls.clear()
        return full_response, []

    # Clean newline after streamed text output finishes
    if label_printed:
        print()

    calls_list = [calls[k] for k in sorted(calls.keys())]
    return full_response, calls_list


if __name__ == "__main__":
    print(f"--- 🤖 Agent Initialized with Streaming & Chained Tools ({model_name}) ---")
    print("Type 'exit', 'quit', or 'bye' to end the session.\n")

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
            full_response, tool_calls = stream_chat(messages)

            # If no tool calls were requested, the model gave its final text answer (already streamed live!)
            if not tool_calls:
                if full_response.strip():
                    messages.append({"role": "assistant", "content": full_response})
                else:
                    fallback = "I didn't quite catch that. Could you please rephrase?"
                    print("🤖 Assistant: " + fallback)
                    messages.append({"role": "assistant", "content": fallback})
                break

            # Model requested tool call(s)
            log(f"Step {step + 1}: model requested {len(tool_calls)} tool call(s)")
            messages.append({
                "role": "assistant",
                "content": full_response or None,
                "tool_calls": build_tool_calls_payload(tool_calls)
            })

            for tool_call in tool_calls:
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
