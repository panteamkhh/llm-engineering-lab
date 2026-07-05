# Toy tokenizer illustrating the concept of tokenization (see docs/en.md - Build It)
import re

def toy_tokenize(text: str) -> list:
    return re.findall(r"\w+|[^\w\s]", text)

def build_vocab(tokens: list) -> dict:
    vocab = {}
    for tok in tokens:
        if tok not in vocab:
            vocab[tok] = len(vocab)
    return vocab

def encode(text: str, vocab: dict) -> list:
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
