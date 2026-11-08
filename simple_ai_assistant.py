import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. Load environment variables from .env
load_dotenv()

# 2. Initialize the OpenAI client pointing to Ollama's local port
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

model_name = os.getenv("MODEL")
print(f"--- Assistant Initialized with model: {model_name} ---")
print("Type 'exit', 'quit', or 'bye' to end the conversation.\n")

# 3. Interactive conversational loop
while True:
    try:
        user_input = input("\nUser: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nExiting...")
        break

    # Graceful exit handling
    if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
        print("Assistant: Goodbye!")
        break

    # Ignore empty inputs
    if not user_input:
        continue

    # 4. Send the user query to the local LLM
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": user_input
            }
        ]
    )

    # 5. Extract and print the response
    reply = response.choices[0].message.content
    print("Assistant: " + reply)