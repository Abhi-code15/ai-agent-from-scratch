"""
ChromaDB Fundamentals & Integration Demo
----------------------------------------
Module 17 (Phase 13): Vector Databases in AI Agents

Demonstrates:
1. Basic ChromaDB: In-memory client, default embedding model download, and L2 distance.
2. Custom Model Integration: Using local nomic-embed-text via Ollama + HNSW with cosine distance.
3. Persistent Vector Database: Using PersistentClient, get_or_create_collection, and upsert.
"""

import os
from dotenv import load_dotenv
import chromadb
from openai import OpenAI

# 1. Environment & Local Model Setup
load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:11434/v1")
API_KEY = os.getenv("API_KEY", "dummy_key")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)


def get_embedding(text: str) -> list:
    """Generates embedding vector for given text using local Ollama model."""
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=text
    )
    return response.data[0].embedding


# Sample knowledge base chunks from Zorvex Technologies
CHUNKS = {
    "c0": "Leave Policy - Maternity Leave\nMaternity leave is 26 weeks of paid leave for the first two children.",
    "c1": "Medical Policy - Group Health Insurance\nCoverage of up to 500,000 rupees per year for all full-time employees.",
    "c2": "Travel Expense - Flight Booking\nDomestic flights must be booked at least 14 days in advance.",
    "c3": "Tech Doc - Production Deployment\nProduction deployments are allowed only Tuesday through Thursday between 10 AM and 2 PM."
}


# =====================================================================
# Stage 1: Basic ChromaDB (Default In-Memory & Auto-Downloaded Model)
# =====================================================================
def demo_1_chroma_default():
    print("\n--- [Demo 1] Default In-Memory ChromaDB (Default Model & L2 Distance) ---")
    chroma = chromadb.Client()

    # Create collection
    collection = chroma.create_collection(name="zorvex_default_demo")

    # Add raw documents and IDs (Chroma auto-embeds using all-MiniLM-L6-v2)
    ids = list(CHUNKS.keys())
    documents = list(CHUNKS.values())
    collection.add(ids=ids, documents=documents)
    print(f"Added {len(ids)} documents to in-memory collection.")

    # Query with plain text
    query = "When is production deployment allowed?"
    print(f"Query: \"{query}\"")
    results = collection.query(query_texts=[query], n_results=1)

    top_doc = results["documents"][0][0]
    top_id = results["ids"][0][0]
    top_dist = results["distances"][0][0]
    print(f"Top Result [{top_id}] (Distance: {top_dist:.4f}):\n{top_doc}\n")


# =====================================================================
# Stage 2: Custom Embeddings (nomic-embed-text + HNSW Cosine Distance)
# =====================================================================
def demo_2_chroma_custom_embeddings():
    print("\n--- [Demo 2] Custom Embedding Model (nomic-embed-text + HNSW Cosine) ---")
    chroma = chromadb.Client()

    # Configure HNSW index space to use 'cosine' similarity
    collection = chroma.create_collection(
        name="zorvex_custom_demo",
        metadata={"hnsw:space": "cosine"}
    )

    ids = list(CHUNKS.keys())
    documents = list(CHUNKS.values())

    # Precompute embeddings locally using our Ollama model
    print("Generating embeddings using local model...")
    embeddings = [get_embedding(doc) for doc in documents]

    # Pass precomputed embeddings explicitly to ChromaDB
    collection.add(ids=ids, documents=documents, embeddings=embeddings)
    print(f"Added {len(ids)} documents with custom 768-D embeddings.")

    # Embed the query vector using the SAME model
    query = "When is production deployment allowed?"
    print(f"Query: \"{query}\"")
    query_vector = get_embedding(query)

    results = collection.query(query_embeddings=[query_vector], n_results=1)

    top_doc = results["documents"][0][0]
    top_id = results["ids"][0][0]
    top_dist = results["distances"][0][0]
    print(f"Top Result [{top_id}] (Cosine Distance: {top_dist:.4f}):\n{top_doc}\n")


# =====================================================================
# Stage 3: Persistent Vector Store (PersistentClient + Upsert)
# =====================================================================
def demo_3_chroma_persistent(storage_path: str = "./chromadb_storage"):
    print(f"\n--- [Demo 3] Persistent ChromaDB (Disk Storage: {storage_path}) ---")
    chroma = chromadb.PersistentClient(path=storage_path)

    # get_or_create_collection avoids crashes on repeated runs
    collection = chroma.get_or_create_collection(
        name="zorvex_persistent_demo",
        metadata={"hnsw:space": "cosine"}
    )

    ids = list(CHUNKS.keys())
    documents = list(CHUNKS.values())
    embeddings = [get_embedding(doc) for doc in documents]

    # upsert: updates existing chunk IDs in-place or inserts new ones cleanly
    collection.upsert(ids=ids, documents=documents, embeddings=embeddings)
    print(f"Upserted {len(ids)} documents to persistent storage at: {storage_path}")

    query = "When is production deployment allowed?"
    print(f"Query: \"{query}\"")
    query_vector = get_embedding(query)

    results = collection.query(query_embeddings=[query_vector], n_results=1)

    top_doc = results["documents"][0][0]
    top_id = results["ids"][0][0]
    top_dist = results["distances"][0][0]
    print(f"Top Result [{top_id}] (Cosine Distance: {top_dist:.4f}):\n{top_doc}\n")


if __name__ == "__main__":
    # Stage 2: Custom embeddings test
    demo_2_chroma_custom_embeddings()

    # Stage 3: Persistent storage test
    demo_3_chroma_persistent()

    # Stage 1: Default Chroma test
    demo_1_chroma_default()
