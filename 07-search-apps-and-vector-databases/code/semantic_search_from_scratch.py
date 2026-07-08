import math

def cosine_similarity(a: list, b: list) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

def fake_embed(text: str) -> list:
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
