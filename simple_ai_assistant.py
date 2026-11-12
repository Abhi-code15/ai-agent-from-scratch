import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()

# 2. Initialize client
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

model_name = os.getenv("MODEL")
print(f"--- Assistant Initialized with model: {model_name} ---")
print("Type 'exit', 'quit', or 'bye' to end the conversation.\n")

# 3. Initialize conversation history OUTSIDE the loop
messages = []

# 4. Interactive conversational loop
while True:
    try:
        user_input = input("\nUser: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nSession ended.")
        break

    # Graceful exit check
    if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
        print("Assistant: Goodbye!")
        break

    if not user_input:
        continue

    # 5. Append the user's message to history
    messages.append({
        "role": "user",
        "content": user_input
    })

    # 6. Send the ENTIRE conversation history to the model
    response = client.chat.completions.create(
        model=model_name,
        messages=messages
    )

    reply = response.choices[0].message.content
    print("Assistant: " + reply)

    # 7. Append the assistant's reply to history so it remembers what it said
    messages.append({
        "role": "assistant",
        "content": reply
    })