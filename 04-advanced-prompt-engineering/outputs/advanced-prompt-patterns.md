# Advanced Prompt Patterns Reference

1. **Persona prompting** — system message assigns a role to shape tone/depth.
2. **Chain-of-thought** — "think step by step" before the final answer.
3. **Permission to say "I don't know"** — reduces confident hallucination.
4. **Delimiters** — separate instructions from untrusted content (e.g. <user_input> tags).
5. **Structured output** — explicit JSON schema + JSON-mode/structured-output API features.
6. **Negative instructions** — pair with positive framing ("Only output X, do not include Y").

See code/prompt_evaluator_from_scratch.py for a reusable A/B evaluation harness.
