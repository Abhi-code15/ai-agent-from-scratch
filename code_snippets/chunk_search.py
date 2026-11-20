"""
Chunk Search & Local Vector Store Implementation
------------------------------------------------
Phase 11 (Module 15): Intelligent Document Chunking & Vector Store Persistence

This module implements paragraph-level chunking (one section = one chunk)
and disk persistence (vector_store.json) to eliminate the context flooding
and in-memory re-embedding bottlenecks of naive RAG.
"""

import json
import os
from dotenv import load_dotenv
import numpy as np
from openai import OpenAI

# 1. Environment & Client Configuration
load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:11434/v1")
API_KEY = os.getenv("API_KEY", "dummy_key")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
KB_FOLDER = os.getenv("KB_FOLDER", "knowledge_base")
VECTOR_STORE_FILE = os.getenv("VECTOR_STORE_FILE", "knowledge_base/vector_store.json")

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)


# 2. Embedding & Vector Math Operations
def get_embedding(text: str) -> list:
    """Fetches high-dimensional embedding vector for given text from local embedding model."""
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=text
    )
    return response.data[0].embedding


def cosine_similarity(vec1: list, vec2: list) -> float:
    """Calculates cosine similarity between two numeric vectors."""
    v1 = np.array(vec1, dtype=np.float32)
    v2 = np.array(vec2, dtype=np.float32)

    denom = np.linalg.norm(v1) * np.linalg.norm(v2)
    if denom == 0:
        return 0.0

    return float(np.dot(v1, v2) / denom)


# 3. Document Ingestion & Section-Level Chunking
def load_documents(folder: str) -> list:
    """Reads all .txt files from knowledge base directory with strict UTF-8 encoding."""
    documents = []
    if not os.path.exists(folder):
        print(f"Warning: Folder '{folder}' does not exist.")
        return documents

    for filename in sorted(os.listdir(folder)):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                documents.append({
                    "source": filename,
                    "text": content
                })
    return documents


def chunk_document(document: dict) -> list:
    """Splits single document into sections using double newline (\\n\\n) boundary.
    
    Strategy: One section = One chunk.
    Stores source filename, zero-indexed chunk_id, and raw section text.
    """
    chunks = []
    # Split text on double newline boundary separating logical sections
    parts = document["text"].split("\n\n")
    chunk_id = 0

    for part in parts:
        clean_part = part.strip()
        if clean_part:
            chunks.append({
                "source": document["source"],
                "chunk_id": chunk_id,
                "text": clean_part
            })
            chunk_id += 1

    return chunks


def create_chunks() -> list:
    """Loads all knowledge base documents and splits each into semantic section chunks."""
    documents = load_documents(KB_FOLDER)
    chunks = []
    for doc in documents:
        doc_chunks = chunk_document(doc)
        chunks.extend(doc_chunks)
    return chunks


def add_embeddings(chunks: list) -> list:
    """Embeds each chunk's text and attaches a 'vector' key."""
    for chunk in chunks:
        vector = get_embedding(chunk["text"])
        chunk["vector"] = vector
    return chunks


# 4. Local Vector Store Persistence
def save_vector_store(chunks: list) -> None:
    """Persists chunks (with text, metadata, and vectors) to disk as JSON."""
    os.makedirs(os.path.dirname(VECTOR_STORE_FILE), exist_ok=True)
    with open(VECTOR_STORE_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=4)


def load_vector_store() -> list:
    """Loads previously saved chunks and embedding vectors from disk."""
    with open(VECTOR_STORE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# 5. Semantic Chunk Retrieval & Search
def search(query: str, chunks: list, top_k: int = 3) -> list:
    """Ranks chunks by cosine similarity against user query vector."""
    query_vector = get_embedding(query)
    results = []

    for chunk in chunks:
        score = cosine_similarity(query_vector, chunk["vector"])
        results.append({
            "score": float(score),
            "source": chunk["source"],
            "chunk_id": chunk["chunk_id"],
            "text": chunk["text"],
            "size": len(chunk["text"])
        })

    # Sort candidates descending by cosine similarity score
    results.sort(key=lambda rec: rec["score"], reverse=True)
    return results[:top_k]


def test(user_query: str, chunks: list, top_k: int = 3) -> None:
    """Executes semantic chunk search and prints detailed ranking telemetry."""
    print(f"\nUser Query: \"{user_query}\"")
    results = search(user_query, chunks, top_k=top_k)

    for rank, r in enumerate(results, 1):
        print(f"Rank {rank}: [Score: {r['score']:.4f}] - {r['source']} (Chunk #{r['chunk_id']}, {r['size']} chars)")
        print(f"  Snippet: {r['text']}")
        print()


# 6. Execution Lifecycle
if __name__ == "__main__":
    chunks = []

    # Check if persistent vector store already exists on disk
    if os.path.exists(VECTOR_STORE_FILE):
        chunks = load_vector_store()
        print(f"Loaded {len(chunks)} chunks from vector store file: {VECTOR_STORE_FILE}")
    else:
        print("Vector store not found. Generating chunks and embeddings from scratch...")
        chunks = create_chunks()
        chunks = add_embeddings(chunks)
        save_vector_store(chunks)
        print(f"Created and embedded {len(chunks)} chunks and saved to vector store file: {VECTOR_STORE_FILE}")

    # Test multi-intent query across documents
    test("What are the benefits of maternity leaves?", chunks, top_k=3)
