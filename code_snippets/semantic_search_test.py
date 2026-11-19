"""
code_snippets/semantic_search_test.py
Demonstrates semantic search and Cosine Similarity calculation between embeddings
using NumPy and local Ollama 'nomic-embed-text'.
Follows Module 13 of the AI Engineering series.
"""

import os
from dotenv import load_dotenv
import numpy as np
from openai import OpenAI

# 1. Load environment configuration
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")

# 2. Initialize local client
client = OpenAI(base_url=BASE_URL, api_key=API_KEY)


def get_embedding(text: str):
    """Generates a 768-dimensional embedding vector for a given string."""
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=text
    )
    return response.data[0].embedding


def cosine_similarity(a, b):
    """
    Computes cosine similarity between two vectors:
    Cosine Similarity = (A . B) / (||A|| * ||B||)
    """
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    return dot_product / (norm_a * norm_b)


if __name__ == "__main__":
    print("=" * 65)
    print("DEMO: Semantic Search via Cosine Similarity")
    print("=" * 65)

    text_1 = "Python is a programming language."
    text_2 = "Python is used to write AI related code snippets."
    text_3 = "I love eating apples every morning."

    print("Sentences to Compare:")
    print(f"  • Text 1: \"{text_1}\"")
    print(f"  • Text 2: \"{text_2}\"")
    print(f"  • Text 3: \"{text_3}\"\n")

    print("Generating embeddings via local 'nomic-embed-text' model...")
    emb_1 = get_embedding(text_1)
    emb_2 = get_embedding(text_2)
    emb_3 = get_embedding(text_3)

    # Calculate similarity scores
    sim_1_2 = cosine_similarity(emb_1, emb_2)
    sim_1_3 = cosine_similarity(emb_1, emb_3)

    print("\n" + "=" * 65)
    print("SIMILARITY RESULTS:")
    print("=" * 65)
    print(f"Similarity (Text 1 <-> Text 2) [Related]:   {sim_1_2:.2f} (Raw: {sim_1_2:.4f})")
    print(f"Similarity (Text 1 <-> Text 3) [Unrelated]: {sim_1_3:.2f} (Raw: {sim_1_3:.4f})")
    print("=" * 65)

    print("\nInterpretation:")
    print(f"  • Score {sim_1_2:.2f} is close to 1.0 -> High semantic relatedness (both discuss Python/code).")
    print(f"  • Score {sim_1_3:.2f} is significantly lower -> Semantic divergence (apples vs. programming).")
