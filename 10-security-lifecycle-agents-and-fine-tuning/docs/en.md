# Lesson 10 — Securing, Operating, Extending, and Customizing Generative AI Applications

> One-line motto — Shipping the demo is the easy 20%; securing it, operating it, letting it act autonomously, and customizing the model are the other 80%.

## The Problem

Everything covered so far (Lessons 01–09) gets you to a working prototype. Turning that prototype into a production system that's secure, maintainable over time, capable of autonomous multi-step behavior, and — when truly needed — customized at the model-weights level, requires four more disciplines: security, LLMOps/lifecycle management, agents, and fine-tuning.

## The Concept

### Part 1 — Securing generative AI applications

Generative AI applications inherit traditional application-security risks (auth, injection, data leakage) **plus** AI-specific risks:

- **Prompt injection** — malicious instructions hidden in user input or retrieved documents attempt to override your system prompt (see Lesson 04). Mitigate with delimiters, input/output filtering, and never letting model output alone trigger high-privilege actions without validation.
- **Data leakage** — a model might reveal sensitive information from its context (e.g., another user's data accidentally included in a shared prompt, or secrets embedded in a system prompt). Mitigate with strict data segregation per user/tenant and by never putting long-lived secrets in prompts.
- **Excessive agency** — giving a model too much unchecked ability to take real-world actions (via function calling, see Lesson 09) without human approval or guardrails on scope.
- **Model/output abuse** — using your application as a cheap way to generate spam, malware, or disallowed content at scale. Mitigate with rate limiting, abuse monitoring, and the content-safety layer from Lesson 02.

A practical security checklist mirrors general app security plus these AI-specific additions: least-privilege for any function-calling capability, output validation before it's used programmatically or shown to other users, logging/auditing of prompts and completions for incident investigation, and periodic red-teaming.

### Part 2 — The generative AI application lifecycle (LLMOps)

**LLMOps** extends MLOps/DevOps practices to the specific concerns of LLM-based applications:

1. **Experimentation** — try prompts, models, and RAG configurations against an evaluation set.
2. **Evaluation** — measure quality (accuracy, relevance, safety) systematically, not just by eyeballing a few outputs.
3. **Deployment** — promote a specific prompt + model + configuration version to production, ideally behind a staged rollout.
4. **Monitoring** — track quality, cost, and latency metrics in production continuously (extending the metrics from Lesson 06).
5. **Iteration** — because model providers update models, and because your data and users evolve, LLMOps is a **continuous loop**, not a one-time deployment.

Treat prompts, RAG configurations, and evaluation datasets as **versioned artifacts** in source control, the same way you version code — this is what makes it possible to detect and roll back regressions.

### Part 3 — AI agents

An **AI agent** is a system built around an LLM that can autonomously plan and execute a sequence of steps — including deciding which tools/functions to call (Lesson 09) and in what order — to accomplish a goal, rather than producing a single one-shot response.

Common agent frameworks provide:

- A **planning loop** (the agent reasons about what to do next, acts, observes the result, and repeats — sometimes called a ReAct-style loop: Reason, Act, Observe).
- **Tool/function integration** so the agent can call external systems.
- **Memory** (short-term within a run, and sometimes long-term across runs, often backed by a vector store as in Lesson 07).

**When to use an agent vs. a simpler function-calling pattern:** if the task requires a fixed, known sequence of one or two actions, plain function calling is simpler, cheaper, and more predictable. Reach for an agent when the sequence of steps needed to solve a task can't be predetermined and must be decided dynamically based on intermediate results — with the tradeoff that agents are harder to test, more expensive (multiple model calls per task), and require stronger guardrails against "excessive agency" (see Part 1).

### Part 4 — Fine-tuning LLMs

**Fine-tuning** further trains a pre-trained foundation model on your own labeled examples, producing a new model with updated weights specialized for your task.

**When fine-tuning is worth it:**

- You need a **specific output format or tone** so consistently that prompting alone can't guarantee it.
- You have **strict latency requirements** that a large in-context prompt (few-shot examples, RAG context) would violate.
- You have **high-quality labeled data** and the ability to maintain it over time.
- You've already tried and outgrown prompt engineering and RAG for this specific need.

**When to prefer RAG or prompt engineering instead:** if the underlying need is "the model doesn't know X fact," that's a knowledge problem RAG solves more cheaply than fine-tuning; fine-tuning is for *behavior/format/style* problems, not primarily for injecting facts.

**The fine-tuning workflow:**

1. **Prepare data** in the required format (commonly JSONL, one training example per line, each with the input/output pair or full conversation).
2. **Upload** the training file to the provider.
3. **Create a fine-tuning job** against a base model.
4. **Monitor** the job — training can fail due to data-format validation errors, so getting the format right matters.
5. **Evaluate** the resulting fine-tuned model against the base foundation model side by side (e.g., in a playground) on the same prompts, comparing quality, latency, and token cost.
6. **Deploy and use it** — a fine-tuned model typically gets its own model ID and is called exactly like any other model afterward.
7. **Maintain it** — when the underlying foundation model improves, you are responsible for deciding whether and how to re-tune your custom model to keep pace.

## Build It

Build a minimal, from-scratch ReAct-style agent loop (reason → act → observe → repeat) using the function registry pattern from Lesson 09, so you can see the control flow that agent frameworks automate for you.

```python
# code/react_agent_from_scratch.py
FUNCTION_REGISTRY = {}

def register(name):
    def decorator(fn):
        FUNCTION_REGISTRY[name] = fn
        return fn
    return decorator

@register("search_docs")
def search_docs(query: str) -> str:
    return f"[fake search result for '{query}']: Refunds are processed within 5 business days."

@register("calculate")
def calculate(expression: str) -> str:
    return str(eval(expression, {"__builtins__": {}}))  # toy example only — never eval untrusted input in production

def fake_planner(goal: str, observations: list) -> dict:
    """Stand-in for an LLM deciding the next step. A real agent asks the model
    'given the goal and what's been observed so far, what should I do next?'"""
    if not observations:
        return {"action": "search_docs", "args": {"query": goal}, "done": False}
    return {"action": None, "args": {}, "done": True,
            "final_answer": f"Based on research: {observations[-1]}"}

def run_agent(goal: str, max_steps: int = 4) -> str:
    observations = []
    for step in range(max_steps):
        decision = fake_planner(goal, observations)
        if decision["done"]:
            return decision["final_answer"]
        fn = FUNCTION_REGISTRY[decision["action"]]
        result = fn(**decision["args"])
        observations.append(result)
        print(f"Step {step}: called {decision['action']} -> {result}")
    return "Max steps reached without a final answer."

if __name__ == "__main__":
    print(run_agent("How long do refunds take?"))
```

## Use It

Prepare and submit a real fine-tuning job, then compare it against the base model — the production analog of "Ship It" for a customized model.

```python
# code/fine_tuning_workflow.py
# pip install openai --break-system-packages
import json
from openai import OpenAI

client = OpenAI()

# 1. Prepare data in JSONL chat format
training_examples = [
    {"messages": [
        {"role": "system", "content": "You are a factual assistant that always cites a source in brackets."},
        {"role": "user", "content": "Tell me about gold."},
        {"role": "assistant", "content": "Gold is a dense, corrosion-resistant metal used in jewelry and electronics. [source: general chemistry]"},
    ]},
]

with open("training_data.jsonl", "w") as f:
    for example in training_examples:
        f.write(json.dumps(example) + "\n")

# 2. Upload the file
uploaded = client.files.create(file=open("training_data.jsonl", "rb"), purpose="fine-tune")

# 3. Create the fine-tuning job
job = client.fine_tuning.jobs.create(training_file=uploaded.id, model="gpt-4o-mini-2024-07-18")

# 4. Poll for completion (in real code, poll with backoff or use webhooks)
print(f"Fine-tuning job created: {job.id}. Poll client.fine_tuning.jobs.retrieve(job.id) for status.")

# 5 & 6. Once complete, use the fine-tuned model exactly like any other model:
# fine_tuned_model_id = client.fine_tuning.jobs.retrieve(job.id).fine_tuned_model
# response = client.chat.completions.create(model=fine_tuned_model_id, messages=[...])
```

## Ship It

**Artifact produced by this lesson:** `outputs/production-readiness-checklist.md` — a combined checklist covering security review, LLMOps versioning, agent guardrails, and a fine-tuning-vs-RAG-vs-prompting decision guide, meant to be run before any generative AI feature goes to production.

## Exercises

1. For a support-ticket-routing feature, list at least two prompt-injection scenarios and the specific mitigation you'd apply for each.
2. Sketch (in prose or a diagram) what a versioned "prompt registry" would look like for a team running 5 different generative AI features, including how you'd detect a quality regression after a prompt change.
3. **Challenge:** Extend the `run_agent` function from Build It to support a maximum-action-count guardrail *per function* (e.g., `search_docs` can be called at most 2 times per run) to prevent excessive agency/runaway loops, and write a test that verifies the guardrail actually stops the loop.
