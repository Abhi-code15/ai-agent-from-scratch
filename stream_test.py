"""
stream_test.py
Demonstrates basic text streaming with an LLM using the OpenAI client.
Follows Video 11 of CodeWithMik AI Engineering playlist.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# 1. Load environment variables
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
MODEL = os.getenv("MODEL")

# 2. Initialize client
client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

# 3. Request a streaming response
prompt = "Explain what an API is in simple words in about 50 words."
print(f"User: {prompt}\n")
print("Assistant: ", end="", flush=True)

stream = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "You are a helpful assistant. Keep your response concise."},
        {"role": "user", "content": prompt}
    ],
    stream=True
)

full_response = ""

# 4. Stream and print chunks as they arrive
for chunk in stream:
    # Some servers may send empty chunks without choices
    if not chunk.choices:
        continue

    # Extract the delta piece
    piece = chunk.choices[0].delta.content

    # Filter out None (e.g., thinking models or role setup chunks)
    if piece:
        # flush=True prevents Python output buffering, ensuring real-time display
        print(piece, end="", flush=True)
        full_response += piece

print("\n")
print("-" * 50)
print(f"Full Response Captured ({len(full_response.split())} words):")
print(full_response)
