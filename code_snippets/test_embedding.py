"""
code_snippets/test_embedding.py
Demonstrates generating vector embeddings using the OpenAI-compatible Ollama client
with the local 'nomic-embed-text' model (768 dimensions).
Follows Module 13 of the AI Engineering series.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# 1. Load environment configuration
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")

# 2. Initialize local OpenAI-compatible client
client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

# -------------------------------------------------------------
# Test 1: Single Input String
# -------------------------------------------------------------
print("=" * 60)
print("TEST 1: Generating Embedding for a Single String")
print("=" * 60)

single_input = "I am a good person"
print(f"Input: '{single_input}'\n")

response = client.embeddings.create(
    model=EMBED_MODEL,
    input=single_input
)

# Extract embedding vector (768 floating-point numbers)
embedding_vector = response.data[0].embedding
print(f"Embedding Vector Length: {len(embedding_vector)} dimensions")
print(f"First 5 Float Dimensions: {embedding_vector[:5]}")
print()

# -------------------------------------------------------------
# Test 2: Batch / Multiple Input Strings
# -------------------------------------------------------------
print("=" * 60)
print("TEST 2: Generating Embeddings for Multiple Batch Inputs")
print("=" * 60)

batch_inputs = [
    "I am a good boy",
    "Python is a good language",
    "He is a good coder"
]

batch_response = client.embeddings.create(
    model=EMBED_MODEL,
    input=batch_inputs
)

print(f"Received {len(batch_response.data)} embedding vectors for {len(batch_inputs)} inputs:\n")

for i, item in enumerate(batch_response.data):
    emb = item.embedding
    print(f"Embedding #{i} | Text: '{batch_inputs[i]}'")
    print(f"  • Dimensions: {len(emb)}")
    print(f"  • Preview (first 5 floats): {emb[:5]}\n")
