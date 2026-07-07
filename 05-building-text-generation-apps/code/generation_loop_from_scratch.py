import time
import random

class TransientError(Exception):
    pass

def call_model_with_retry(call_fn, max_retries: int = 3, base_delay: float = 0.5):
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
    if not hasattr(fake_flaky_model_call, "_called"):
        fake_flaky_model_call._called = True
        raise TransientError("simulated rate limit")
    return f"Generated response for: {prompt}"

if __name__ == "__main__":
    prompt = "Write a one-sentence product description for a smart water bottle."
    result = call_model_with_retry(lambda: fake_flaky_model_call(prompt))
    print(result)
