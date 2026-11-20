"""
code_snippets/doc_search.py
Demonstrates naive document-level knowledge base construction and vector search.
Exposes the 4 critical limitations that mandate Chunking in production RAG.
Follows Module 14 of the AI Engineering series.
"""

import os
from dotenv import load_dotenv
import numpy as np
from openai import OpenAI

# 1. Load environment variables
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
KB_FOLDER = os.getenv("KB_FOLDER", "knowledge_base")

# 2. Initialize local client
client = OpenAI(base_url=BASE_URL, api_key=API_KEY)


# Step 1: Load all raw documents from the Knowledge Base folder
def load_documents(folder=KB_FOLDER):
    """
    Reads all .txt files from the target knowledge base directory.
    Uses UTF-8 encoding as a standard rulebook across operating systems.
    Returns: List[dict] containing 'source' and 'text'.
    """
    documents = []
    for filename in sorted(os.listdir(folder)):
        if not filename.endswith(".txt"):
            continue

        path = os.path.join(folder, filename)
        with open(path, "r", encoding="utf-8") as f:
            documents.append({
                "source": filename,
                "text": f.read()
            })

    return documents


# Step 2: Generate vector embedding using local embedding model
def get_embedding(text: str):
    """Generates a 768-dimensional float embedding vector using nomic-embed-text."""
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=text
    )
    return response.data[0].embedding


# Step 3: Compute Cosine Similarity between two vectors
def cosine_similarity(a, b):
    """
    Computes cosine similarity: (A . B) / (||A|| * ||B||)
    Measures the directional angle between two vector arrows in 768-D space.
    """
    dot_prod = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    denom = norm_a * norm_b
    if denom == 0:
        return 0.0
    return float(dot_prod / denom)


# Step 4: Add vector embeddings to all loaded documents
def add_embeddings(documents):
    """
    Iterates over each document and embeds the ENTIRE document text as a single vector.
    Note: In Module 14, we deliberately embed whole files to inspect the limitations of unchunked RAG.
    """
    for document in documents:
        vector = get_embedding(document["text"])
        document["vector"] = vector
    return documents


# Step 5: Search the top-K most semantically similar documents
def search(query, documents, top_k=3):
    """
    Embeds the user query and computes cosine similarity against all document vectors.
    Sorts in descending order of similarity score and returns the top-K matches.
    """
    query_vector = get_embedding(query)
    results = []

    for document in documents:
        score = cosine_similarity(query_vector, document["vector"])
        results.append({
            "score": float(score),
            "source": document["source"],
            "text": document["text"],
            "size": len(document["text"])
        })

    # Custom sort descending by score using a lambda function
    results.sort(key=lambda rec: rec["score"], reverse=True)
    return results[:top_k]


# Step 6: Testing & Observation Runner
def test(user_query, documents, top_k=3):
    print(f"User Query: \"{user_query}\"")
    results = search(user_query, documents, top_k=top_k)
    for r in results:
        print(f"  {r['score']:.2f} - {r['source']} - {r['size']} characters")
    print()


if __name__ == "__main__":
    print("=" * 65)
    print("DEMO: Naive Document-Level Knowledge Base Search (Module 14)")
    print("=" * 65)

    print(f"Loading documents from folder: '{KB_FOLDER}'...")
    documents = load_documents()
    print(f"Loaded {len(documents)} document(s).\n")

    print(f"Embedding whole documents using '{EMBED_MODEL}'...")
    documents = add_embeddings(documents)
    print(f"We have embedded {len(documents)} documents.\n")

    print("-" * 65)
    print("TEST 1: Relevant HR Query (Expected: leave_policy.txt on top)")
    print("-" * 65)
    test("How many days I will get for maternity leave ?", documents, top_k=3)

    print("-" * 65)
    print("TEST 2: Completely Irrelevant Query (Exposing Limitation #4: False Positives)")
    print("-" * 65)
    test("Who is my best friend in my office?", documents, top_k=3)
