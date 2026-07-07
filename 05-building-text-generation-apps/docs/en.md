# Lesson 05 — Building Text Generation Applications

> One-line motto — An LLM plus a completion call is not an application; parameters, error handling, and iteration are what make it one.

## The Problem

Calling `chat.completions.create(...)` once in a script is trivial. Turning that into a reliable application — one where output length, creativity, and consistency are controllable, and where failures are handled gracefully — requires understanding the *generation parameters* and structuring your code around them.

## The Concept

### The core generation parameters

- **`temperature`** (typically 0–2) — controls randomness in token selection. Low values (0–0.3) make output deterministic and focused; higher values (0.7–1+) make it more varied and creative, at the cost of consistency.
- **`top_p`** (nucleus sampling) — restricts token selection to the smallest set of tokens whose cumulative probability exceeds `top_p`. Often used as an alternative to `temperature` (most guidance suggests adjusting one or the other, not both aggressively).
- **`max_tokens`** — the hard cap on how many tokens the completion can contain. This is your primary cost- and latency-control lever, and also protects against runaway generations.
- **`frequency_penalty`** — discourages the model from repeating the same token/phrase too often.
- **`presence_penalty`** — discourages the model from repeating any token it has already used at all, encouraging it to introduce new topics/words.
- **`stop` sequences** — strings that, when generated, tell the model to stop immediately (useful for controlling structured outputs, like stopping after a closing bracket).

### Choosing parameters for your use case

| Use case | temperature | max_tokens | notes |
|---|---|---|---|
| Code generation | 0–0.2 | task-dependent | want determinism and correctness |
| Creative writing/brainstorming | 0.7–1.0 | larger | want variety |
| Structured data extraction | 0 | tight to schema size | want exact repeatability |
| Chat/conversational | 0.3–0.7 | moderate | balance naturalness and coherence |

### Designing the generation loop

A production text-generation feature typically needs:

1. **Input validation** — reject empty or malformed input before spending a token budget.
2. **Prompt assembly** — combine a system message, any retrieved context, and the user input (see Lessons 03–04, 07).
3. **The API call**, with sensible parameter defaults and a timeout.
4. **Retry logic with backoff** for transient errors (rate limits, timeouts) — never retry blindly on content-related failures.
5. **Post-processing** — trimming, format validation, and (per Lesson 02) a safety check on the output before it's shown to the user.
6. **Streaming** (optional but common) — many providers support streaming tokens back as they're generated, which dramatically improves perceived latency for longer outputs.

### Handling failure modes gracefully

- **Rate limiting (HTTP 429):** back off exponentially and retry a bounded number of times.
- **Context length exceeded:** truncate or summarize older content rather than crashing.
- **Empty or malformed model output:** have a fallback message rather than surfacing a raw error to the user.

## Build It

Build the generation loop and a minimal retry-with-backoff mechanism from scratch, so you can see exactly what a "text generation SDK" is doing under the hood before relying on one.

```python
# code/generation_loop_from_scratch.py
import time
import random

class TransientError(Exception):
    pass

def call_model_with_retry(call_fn, max_retries: int = 3, base_delay: float = 0.5):
    """Retries call_fn() with exponential backoff on TransientError."""
    for attempt in range(max_retries):
        try:
            return call_fn()
        except TransientError as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt) + random.uniform(0, 0.1)
            print(f"Transient error ({e}); retrying in {delay:.2f}s...")
            time.sleep(delay)

def fake_flaky_model_call(prompt: str) -> str:
    """Simulates a model call that fails the first time, succeeds the second."""
    if not hasattr(fake_flaky_model_call, "_called"):
        fake_flaky_model_call._called = True
        raise TransientError("simulated rate limit")
    return f"Generated response for: {prompt}"

if __name__ == "__main__":
    prompt = "Write a one-sentence product description for a smart water bottle."
    result = call_model_with_retry(lambda: fake_flaky_model_call(prompt))
    print(result)
```

## Use It

Wire the same retry pattern around a real streaming completion call, tuning generation parameters for a creative-writing use case.

```python
# code/text_generation_app.py
# pip install openai tenacity --break-system-packages
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

client = OpenAI()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=4))
def generate_text(prompt: str) -> str:
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a creative marketing copywriter."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.8,
        max_tokens=120,
        presence_penalty=0.3,
        stream=True,
    )
    chunks = []
    for event in stream:
        delta = event.choices[0].delta.content
        if delta:
            chunks.append(delta)
            print(delta, end="", flush=True)  # streamed output for perceived latency
    print()
    return "".join(chunks)

if __name__ == "__main__":
    generate_text("Write a one-sentence product description for a smart water bottle.")
```

## Ship It

**Artifact produced by this lesson:** `outputs/text-generation-parameter-guide.md` — a parameter tuning cheat sheet (temperature/top_p/max_tokens/penalties) mapped to five common use cases, plus the reusable `call_model_with_retry` helper for any future integration.

## Exercises

1. Generate the same prompt at `temperature=0`, `0.5`, and `1.0` five times each. Observe and describe how consistency changes.
2. Add a `stop` sequence to force a generation to end right after a closing JSON bracket, and verify it works on 3 different prompts.
3. **Challenge:** Extend `call_model_with_retry` to differentiate between a rate-limit error (retry) and a content-policy rejection (do not retry, surface immediately), and write tests for both branches.
