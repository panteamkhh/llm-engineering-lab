# pip install openai numpy --break-system-packages
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
