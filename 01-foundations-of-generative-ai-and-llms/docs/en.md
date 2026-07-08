# Lesson 01 — Foundations of Generative AI and LLMs

> One-line motto — Text in, tokens out: everything a large language model does is next-token prediction at scale.

## The Problem

Before you can build anything with generative AI, you need a working mental model of *what these systems actually are*. Without it, terms like "foundation model," "open source vs. proprietary," and "embedding" get used interchangeably and incorrectly, and it becomes impossible to pick the right model or the right architecture (prompt engineering vs. RAG vs. fine-tuning) for a given problem. This lesson builds that mental model from the ground up.

## The Concept

### A short history

Generative AI is not new — it is the latest link in a decades-long chain:

- **1950s–60s:** rule-based chatbots (e.g., ELIZA-style systems) that pattern-matched keywords against a hand-built knowledge base. They didn't scale because every new domain needed new hand-written rules.
- **1990s:** a statistical turn — machine learning algorithms that learned patterns directly from data instead of relying on explicit rules.
- **2000s–2010s:** neural networks and better hardware unlocked real natural language understanding, giving rise to virtual assistants that could interpret intent and trigger predefined actions.
- **2017 onward:** the **Transformer architecture** (the "T" in GPT) introduced the *attention mechanism*, which lets a model weigh the relevance of every other word in a sequence regardless of its position — solving the long-range dependency problems that older recurrent models struggled with. This is the architecture behind every modern LLM.

### Foundation models vs. LLMs

A **foundation model** is a large model pre-trained on broad data that can be adapted to many downstream tasks. To qualify, a model is generally:

1. Pre-trained on massive data
2. Generalized (not built for one narrow task)
3. Adaptable to new tasks with little extra data
4. Large (parameter count)
5. Self-supervised during training (it learns from the structure of the data itself, not hand-labeled examples)

**Every LLM is a foundation model, but not every foundation model is an LLM.** Some foundation models are multimodal — trained on images, audio, or video instead of (or in addition to) text — so they don't use a text tokenizer at all.

### Open source vs. proprietary models

| | Open source (Llama, Falcon, Mistral, …) | Proprietary (GPT-4 family, Claude, Gemini, …) |
|---|---|---|
| Access | Weights and/or code available, sometimes the full model | API-only, weights hidden |
| Control | Full control — inspect, fine-tune, self-host | Limited — you consume it as a service |
| Maintenance | You are responsible for updates, security patches | Provider maintains and updates it |
| Cost model | Infrastructure cost (compute, hosting) | Usage-based API pricing |
| Best for | Custom, regulated, or offline deployments | Fast time-to-market, low ops overhead |

### Model categories you'll encounter

- **Text-to-embedding models** — convert text into a numeric vector so it can be compared, searched, or clustered. This is the backbone of semantic search and RAG (see [Lesson 07](https://github.com/panteamkhh/llm-engineering-lab/tree/main/07-search-apps-and-vector-databases)).
- **Text generation models** — the "classic" LLM use case: prompt in, text (or code) out.
- **Image generation models** — prompt in, image out (see [Lesson 08](https://github.com/panteamkhh/llm-engineering-lab/tree/main/08-building-image-generation-apps)).

### Service vs. model (the deployment axis)

- **Consuming a model *as a service*** (a hosted API call) means you don't manage infrastructure — you send a prompt, get a completion, and the provider handles scaling and security. You trade control for convenience.
- **Hosting the model yourself** gives you full control over the pipeline (and the ability to fine-tune freely) but makes you responsible for servers, scaling, and uptime.

### Tokenization — how text becomes numbers

LLMs don't process raw text; they process numbers. The **tokenizer** breaks input text into chunks called **tokens** (roughly 4 characters / ¾ of a word in English) and maps each token to an integer **token ID**. The model then:

1. Takes a sequence of *n* input tokens (bounded by the model's **context window**).
2. Predicts the single next token.
3. Appends that predicted token to the input and repeats — an expanding-window loop that is why generation feels like the model is "typing" one token at a time.

This is also why **API pricing is usually per token** (input + output combined), and why the context window size is a hard limit on how much text (documents, chat history, instructions) you can pack into a single request.

### Choosing a deployment strategy

There is no single "best" approach — pick based on your constraints:

1. **Prompt engineering (zero-shot / one-shot / few-shot)** — cheapest, fastest to iterate, good default starting point.
2. **Retrieval-Augmented Generation (RAG)** — bolt external, up-to-date, or private data onto the prompt via a search/vector pipeline when the base model's training data isn't enough. See [Lesson 07](https://github.com/panteamkhh/llm-engineering-lab/tree/main/07-search-apps-and-vector-databases).
3. **Fine-tuning** — retrain part of the model's weights on your own labeled data when you need a specific style, format, or very low latency (no room for long context). See [Lesson 10](https://github.com/panteamkhh/llm-engineering-lab/tree/main/10-security-lifecycle-agents-and-fine-tuning).
4. **Training a model from scratch** — reserved for very large, well-resourced organizations with abundant domain-specific data.

These techniques are **complementary, not mutually exclusive** — production systems often combine prompt engineering + RAG, or RAG + a lightly fine-tuned model.

## Build It

A minimal "from scratch" illustration of tokenization and the next-token prediction loop, using nothing but Python, so you can see the mechanism before you touch any SDK.

```python
# code/tokenizer_from_scratch.py
# A toy whitespace/byte-pair-ish tokenizer to illustrate the *concept* of tokenization.
# Real tokenizers (e.g., tiktoken, SentencePiece) use byte-pair encoding trained on huge corpora.

def toy_tokenize(text: str) -> list[str]:
    """Splits on whitespace and punctuation — NOT how production tokenizers work,
    but useful to see 'text -> chunks -> ids' end to end."""
    import re
    return re.findall(r"\w+|[^\w\s]", text)

def build_vocab(tokens: list[str]) -> dict[str, int]:
    vocab = {}
    for tok in tokens:
        if tok not in vocab:
            vocab[tok] = len(vocab)
    return vocab

def encode(text: str, vocab: dict[str, int]) -> list[int]:
    tokens = toy_tokenize(text)
    return [vocab[t] for t in tokens if t in vocab]

if __name__ == "__main__":
    corpus = "Generative AI models predict the next token given previous tokens."
    tokens = toy_tokenize(corpus)
    vocab = build_vocab(tokens)
    ids = encode(corpus, vocab)

    print("Tokens:", tokens)
    print("Vocab size:", len(vocab))
    print("Token IDs:", ids)
```

## Use It

Now do the same thing with a real, production-grade tokenizer and a real completion API call.

```python
# code/real_tokenizer_and_completion.py
# pip install tiktoken openai --break-system-packages

import tiktoken
from openai import OpenAI

# 1. Real tokenization (byte-pair encoding, same family used by GPT models)
encoding = tiktoken.get_encoding("cl100k_base")
text = "Generative AI models predict the next token given previous tokens."
token_ids = encoding.encode(text)

print("Token count:", len(token_ids))
print("Token IDs:", token_ids)
print("Decoded back:", encoding.decode(token_ids))

# 2. A real next-token generation call (works with any OpenAI-compatible endpoint,
# including Azure OpenAI — just change base_url and the auth header)
client = OpenAI()  # reads OPENAI_API_KEY from the environment

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a concise AI education assistant."},
        {"role": "user", "content": "In one sentence, explain what a foundation model is."},
    ],
    max_tokens=60,
)

print(response.choices[0].message.content)
print("Tokens used:", response.usage.total_tokens)
```

## Ship It

**Artifact produced by this lesson:** `outputs/model-selection-checklist.md` — a one-page decision checklist a team can run through before choosing between prompt engineering, RAG, fine-tuning, or a from-scratch model for a new use case, plus an open-source-vs-proprietary tradeoff table they can paste into an ADR (Architecture Decision Record).

## Exercises

1. Use `tiktoken` to compare token counts for the same sentence in English vs. another language you speak. Which one uses more tokens, and why does that matter for API cost?
2. List three foundation models that are *not* LLMs (i.e., not primarily text-based). What modality do they operate on?
3. **Challenge:** Design a one-page decision tree that a developer could follow to choose between prompt engineering, RAG, and fine-tuning for a new feature request. Validate it against three hypothetical use cases (e.g., "customer support bot with access to today's order data," "generate marketing copy in brand voice," "summarize legal contracts with a strict latency budget").
