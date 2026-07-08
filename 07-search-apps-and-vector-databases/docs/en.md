# Lesson 07 — Building Search Apps, Vector Databases, and Retrieval-Augmented Generation (RAG)

> One-line motto — Embeddings turn meaning into geometry, and RAG uses that geometry to give the model a memory it never trained on.

## The Problem

An LLM only "knows" what was in its training data — it can't answer questions about your private documents, today's data, or anything created after its training cutoff. Keyword search doesn't fully solve this either, since it matches literal words, not meaning ("car" won't match "automobile"). This lesson covers **semantic search** via embeddings and vector databases, and how to combine that search with generation to build **RAG** systems.

## The Concept

### Keyword search vs. semantic search

- **Keyword search** matches literal terms (with optional stemming/synonyms) — fast and simple, but blind to meaning.
- **Semantic search** compares the *meaning* of a query against the *meaning* of documents by comparing their vector representations, so a query about "automobile maintenance" can retrieve a document about "car repair" even without shared keywords.

### Vectors and embeddings

An **embedding** is a fixed-length numeric vector that represents the semantic meaning of a piece of text (or image, audio, etc.), produced by an embedding model. Texts with similar meaning end up with vectors that are close together in that vector space, typically measured with **cosine similarity** or **dot product**.

### Vector stores

A **vector database/store** indexes embeddings for fast approximate nearest-neighbor search at scale (millions+ of vectors), which naive brute-force comparison can't do efficiently. Examples include Azure AI Search, Cosmos DB (vector search), Pinecone, Weaviate, and pgvector for Postgres. They typically support:

- Storing a vector alongside metadata (source document, URL, timestamp)
- Nearest-neighbor search with a similarity threshold or top-k limit
- Hybrid search — combining keyword and vector search for the best of both

### What is RAG, precisely?

**Retrieval-Augmented Generation** is a prompt-engineering pattern (see Lessons 03–04) that:

1. Takes the user's query.
2. Embeds it and searches a vector store (or a hybrid search pipeline) for the most relevant chunks of your own documents.
3. Inserts those chunks into the prompt as **context**.
4. Asks the LLM to answer **using that context**, ideally instructed to say "I don't know" if the answer isn't present.

This lets you ground the model in current, private, or domain-specific data **without retraining or fine-tuning it** — and it substantially reduces (though doesn't eliminate) hallucination, since the model is asked to synthesize from provided text rather than recall from parametric memory alone.

### Why chunking matters

Documents must be split into chunks before embedding, because:

- Embedding models have input length limits.
- Smaller, semantically coherent chunks (a paragraph, not an entire book) retrieve more precisely, since a chunk about one topic won't get diluted by unrelated content.

Common strategies: fixed-size chunking with overlap, sentence/paragraph-boundary chunking, or structure-aware chunking (e.g., splitting a markdown doc by headers).

### The RAG pipeline end-to-end

```
Documents → Chunk → Embed → Store in vector DB
                                     ↑
User query → Embed → Search (top-k) → Retrieved chunks → Prompt template → LLM → Answer
```

## Build It

Build a minimal in-memory semantic search engine from scratch — no vector database, just cosine similarity over a small corpus — to see exactly what a vector store does before using a managed one.

```python
# code/semantic_search_from_scratch.py
import math

def cosine_similarity(a: list, b: list) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

def fake_embed(text: str) -> list:
    """Extremely crude 'embedding': a bag-of-words hash vector, just to
    illustrate the geometry idea without needing a real embedding model."""
    vocab = ["car", "automobile", "repair", "recipe", "cake", "engine"]
    text_lower = text.lower()
    return [1.0 if word in text_lower else 0.0 for word in vocab]

def semantic_search(query: str, documents: list, top_k: int = 2) -> list:
    query_vec = fake_embed(query)
    scored = [(doc, cosine_similarity(query_vec, fake_embed(doc))) for doc in documents]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:top_k]

if __name__ == "__main__":
    documents = [
        "How to change your car's engine oil.",
        "A recipe for chocolate cake.",
        "Automobile repair tips for beginners.",
    ]
    results = semantic_search("automobile maintenance", documents)
    for doc, score in results:
        print(f"{score:.2f} — {doc}")
```

## Use It

Now build a real RAG pipeline: real embeddings, a vector store, and a grounded generation call.

```python
# code/rag_pipeline.py
# pip install openai numpy --break-system-packages
# (swap in a real vector DB client for production; using in-memory numpy here for clarity)
import numpy as np
from openai import OpenAI

client = OpenAI()

def embed(text: str) -> np.ndarray:
    response = client.embeddings.create(model="text-embedding-3-small", input=text)
    return np.array(response.data[0].embedding)

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

class InMemoryVectorStore:
    def __init__(self):
        self.docs = []
        self.vectors = []

    def add(self, text: str):
        self.docs.append(text)
        self.vectors.append(embed(text))

    def search(self, query: str, top_k: int = 3) -> list:
        query_vec = embed(query)
        scored = [(doc, cosine_sim(query_vec, vec)) for doc, vec in zip(self.docs, self.vectors)]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [doc for doc, _ in scored[:top_k]]

def rag_answer(query: str, store: InMemoryVectorStore) -> str:
    context_chunks = store.search(query, top_k=3)
    context = "\n---\n".join(context_chunks)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": (
                "Answer using only the context below. "
                "If the answer isn't in the context, say 'I don't know'."
            )},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
        ],
        temperature=0,
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    store = InMemoryVectorStore()
    store.add("Our return policy allows returns within 30 days of purchase.")
    store.add("Shipping typically takes 3-5 business days within the country.")
    store.add("We offer a 10% discount for first-time customers.")

    print(rag_answer("How long do I have to return an item?", store))
```

## Ship It

**Artifact produced by this lesson:** `outputs/rag-architecture-diagram-and-checklist.md` — an end-to-end RAG pipeline diagram (as text/mermaid) plus a chunking-strategy decision checklist a team can use when indexing a new document source.

## Exercises

1. Replace the crude `fake_embed` in Build It with real embeddings from `text-embedding-3-small` on the same 3 documents and compare which results rank higher.
2. Implement fixed-size chunking with 20% overlap for a long document, and explain in your own words why overlap helps avoid losing context at chunk boundaries.
3. **Challenge:** Extend `InMemoryVectorStore` to support metadata filtering (e.g., only search documents from a specific `category`), and add a hybrid scoring function that blends cosine similarity with a keyword-match boost.
