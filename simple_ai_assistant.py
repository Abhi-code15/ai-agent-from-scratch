import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()

# 2. Initialize client pointing to Ollama
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

model_name = os.getenv("MODEL")
print(f"--- Assistant Initialized with model: {model_name} ---")
print("Type 'exit', 'quit', or 'bye' to end the conversation.\n")

# 3. Define the System Prompt (RCTEF Framework)
SYSTEM_PROMPT = (
    "Role: You are a concise, humble, and practical AI Engineering Mentor. "
    "Context: You are helping a developer build AI agents from scratch in Python. "
    "Task: Answer questions clearly with practical reasoning. "
    "Constraints: Keep every response under 60 words. Use bullet points when listing steps."
)

# 4. Initialize conversation history with the System Prompt pinned at index 0
messages = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]

# 5. Interactive conversational loop
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

    # Append user message
    messages.append({
        "role": "user",
        "content": user_input
    })

    # Send entire history (System Prompt + Conversation)
    response = client.chat.completions.create(
        model=model_name,
        messages=messages
    )

    reply = response.choices[0].message.content
    print("Assistant: " + reply)

    # Append assistant reply
    messages.append({
        "role": "assistant",
        "content": reply
    })