"""
RAG Engine (Retrieval-Augmented Generation)
-------------------------------------------
Module 16 (Phase 12): Agentic RAG Pipeline

Handles knowledge base ingestion, section chunking, embedding generation,
disk persistence (vector_store.json), and semantic search retrieval.
"""

import json
import os
from dotenv import load_dotenv
import numpy as np
from openai import OpenAI
from utilities.utilities import log

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:11434/v1")
API_KEY = os.getenv("API_KEY", "dummy_key")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
KB_FOLDER = os.getenv("KB_FOLDER", "knowledge_base")
VECTOR_STORE_FILE = os.getenv("VECTOR_STORE_FILE", "knowledge_base/vector_store.json")

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)


def get_embedding(text: str) -> list:
    """Generates high-dimensional embedding vector for given text."""
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


def load_documents(folder: str) -> list:
    """Reads all .txt files from knowledge base folder with strict UTF-8 encoding."""
    documents = []
    if not os.path.exists(folder):
        return documents

    for filename in sorted(os.listdir(folder)):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                documents.append({
                    "source": filename,
                    "text": f.read()
                })
    return documents


def chunk_document(document: dict) -> list:
    """Splits single document into sections using double newline (\\n\\n) boundary."""
    chunks = []
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
    """Loads all knowledge base documents and splits each into section chunks."""
    documents = load_documents(KB_FOLDER)
    chunks = []
    for doc in documents:
        doc_chunks = chunk_document(doc)
        chunks.extend(doc_chunks)
    return chunks


def add_embeddings(chunks: list) -> list:
    """Embeds each chunk's text and attaches a 'vector' key."""
    for chunk in chunks:
        chunk["vector"] = get_embedding(chunk["text"])
    return chunks


def save_vector_store(chunks: list) -> None:
    """Persists chunks with vectors to disk as indented JSON."""
    os.makedirs(os.path.dirname(VECTOR_STORE_FILE), exist_ok=True)
    with open(VECTOR_STORE_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=4)


def load_vector_store() -> list:
    """Loads previously saved chunks and vectors from disk."""
    with open(VECTOR_STORE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_chunks() -> list:
    """Loads chunks from persistent store or creates and embeds them on first boot."""
    if os.path.exists(VECTOR_STORE_FILE):
        chunks = load_vector_store()
        log(f"Loaded {len(chunks)} chunks from {VECTOR_STORE_FILE}")
        return chunks
    else:
        chunks = create_chunks()
        chunks = add_embeddings(chunks)
        save_vector_store(chunks)
        log(f"Created and embedded {len(chunks)} chunks and saved to {VECTOR_STORE_FILE}")
        return chunks


# Preload chunks into memory once on module import
CHUNKS = load_chunks()


def search(query: str, top_k: int = 2) -> list:
    """Searches knowledge base chunks and returns top-K results sorted by similarity."""
    query_vector = get_embedding(query)
    results = []

    for chunk in CHUNKS:
        score = cosine_similarity(query_vector, chunk["vector"])
        results.append({
            "score": float(score),
            "source": chunk["source"],
            "chunk_id": chunk["chunk_id"],
            "text": chunk["text"],
            "size": len(chunk["text"])
        })

    results.sort(key=lambda rec: rec["score"], reverse=True)
    return results[:top_k]
