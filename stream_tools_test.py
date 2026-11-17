"""
stream_tools_test.py
Demonstrates streamed tool calls and chunk reconstruction using SimpleNamespace.
Follows Video 11 of CodeWithMik AI Engineering playlist.
"""

import os
from types import SimpleNamespace
from dotenv import load_dotenv
from openai import OpenAI
from tools import TOOLS, run_tool

# 1. Load environment variables
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
MODEL = os.getenv("MODEL")

# 2. Initialize client
client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

# 3. Request a query requiring tool execution
prompt = "Tell me the weather of Pune and Delhi."
print(f"User: {prompt}\n")

stream = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "You are a helpful assistant with access to tools. Call get_city_weather for each city."},
        {"role": "user", "content": prompt}
    ],
    tools=TOOLS,
    stream=True
)

calls = {}  # Dictionary to aggregate streamed chunks by index: { index: SimpleNamespace(...) }

# 4. Stream and assemble chunks
for chunk in stream:
    if not chunk.choices:
        continue

    delta = chunk.choices[0].delta

    # Stream text response if any
    if delta.content:
        print(delta.content, end="", flush=True)

    # Stream and aggregate tool call chunks
    if delta.tool_calls:
        for tc in delta.tool_calls:
            index = tc.index

            # Fetch existing object or initialize a new empty one in the dictionary
            obj = calls.setdefault(
                index,
                SimpleNamespace(
                    id="",
                    function=SimpleNamespace(name="", arguments="")
                )
            )

            # Accumulate fields from partial chunks
            if tc.id:
                obj.id = tc.id
            if tc.function and tc.function.name:
                obj.function.name += tc.function.name
            if tc.function and tc.function.arguments:
                obj.function.arguments += tc.function.arguments

# 5. Reconstruct ordered list of complete tool calls
calls_list = [calls[k] for k in sorted(calls.keys())]

print("\n" + "=" * 50)
print(f"Total Tool Calls Reconstructed: {len(calls_list)}")
print("=" * 50)

# 6. Execute each reconstructed tool call using our modular run_tool()
for idx, call in enumerate(calls_list):
    print(f"\n[Tool Call #{idx + 1}]")
    print(f"  • ID: {call.id}")
    print(f"  • Function Name: {call.function.name}")
    print(f"  • Arguments JSON: {call.function.arguments}")

    # Execute with run_tool from tools.py
    result = run_tool(call)
    print(f"  • Execution Result: {result}")
