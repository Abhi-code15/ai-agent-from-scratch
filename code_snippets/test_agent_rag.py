"""
Agentic RAG Test Suite
----------------------
Tests autonomous tool selection:
1. Company query -> search_knowledge_base with citation
2. Weather query -> get_city_weather
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from tools import TOOLS, run_tool

load_dotenv()
client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))
model_name = os.getenv("MODEL")

SYSTEM_PROMPT = (
    "You are a helpful assistant for Zorvex Technologies employees. "
    "Use get_current_time, get_city_weather, and get_user_city only for time, weather, or city. "
    "Use search_knowledge_base whenever the user asks about company policies, leave, maternity, benefits, medical insurance, HR, hiring, tech, or expenses. "
    "When answering based on search_knowledge_base, cite the source file and chunk like (leave_policy.txt #3). "
    "Keep answers under 100 words."
)


def run_agent_turn(user_query: str, history: list = None):
    if history is None:
        history = [{"role": "system", "content": SYSTEM_PROMPT}]

    history.append({"role": "user", "content": user_query})
    print(f"\n==================================================")
    print(f"👤 User: {user_query}")
    print(f"==================================================")

    max_steps = 5
    for step in range(max_steps):
        response = client.chat.completions.create(
            model=model_name,
            messages=history,
            tools=TOOLS
        )
        msg = response.choices[0].message

        if not msg.tool_calls:
            print(f"🤖 Assistant:\n{msg.content}")
            history.append({"role": "assistant", "content": msg.content})
            return msg.content

        print(f"Step {step + 1}: Model requested {len(msg.tool_calls)} tool call(s)")
        history.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                }
                for tc in msg.tool_calls
            ]
        })

        for tc in msg.tool_calls:
            print(f"🔧 Executing: {tc.function.name}({tc.function.arguments})")
            tool_output = run_tool(tc)
            history.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": str(tool_output)
            })


if __name__ == "__main__":
    # Test 1: Company query triggering Agentic RAG
    run_agent_turn("What are the benefits of maternity leaves in Zorvex Technologies?")

    # Test 2: Existing tool calling (weather)
    run_agent_turn("What is the weather in Pune?")
