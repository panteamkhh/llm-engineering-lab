# Lesson 03 — Understanding Prompt Engineering Fundamentals

> One-line motto — The prompt is the interface: how you ask is most of what determines what you get.

## The Problem

Two developers can send the exact same model two different prompts asking for "the same thing" and get wildly different quality of output. Without a shared vocabulary and a repeatable method for writing prompts, teams end up trial-and-erroring their way to mediocre results. This lesson gives you the core terms and a practical method.

## The Concept

### Quick recap of terms from [Lesson 01](https://github.com/panteamkhh/llm-engineering-lab/tree/main/01-foundations-of-generative-ai-and-llms)

- **Token** — the basic unit of text a model reads/writes.
- **Context window** — the maximum number of tokens (input + output) a model can consider at once.
- **Completion** — the model's generated continuation of your prompt.

### What is a prompt, really?

A prompt is the *entire input* you send a model: instructions, context, examples, and the actual question or task, formatted so the model can predict the most useful continuation.

### Why prompt engineering matters

- It is the **cheapest and fastest** lever you have to improve output quality (compare to RAG or fine-tuning).
- It requires no additional infrastructure or training data.
- Small wording changes can produce large quality differences, because the model is doing statistical pattern completion, and different phrasing activates different patterns learned during training.

### The core learning shapes: zero-shot, one-shot, few-shot

- **Zero-shot** — you give an instruction with no examples ("Summarize this email in one sentence."). Works well for tasks the model has seen a lot of during training.
- **One-shot** — you give exactly one example of the input/output pattern you want before the real task.
- **Few-shot** — you give multiple examples, which is the most reliable way to lock in a specific format, tone, or style, especially for less-common tasks.

**Rule of thumb:** the more context and detail you provide, the better the model understands your intent — but every extra token also costs money and context-window space, so context should be *relevant*, not just *abundant*.

### Anatomy of a good prompt

1. **Instruction** — the specific task, stated as a clear, direct command ("Translate the following text to French" rather than "Can you maybe translate this?").
2. **Context** — background information the model needs (a document, prior conversation, a persona/system message).
3. **Input data** — the actual content to operate on.
4. **Output indicator** — a hint about the desired format (e.g., "Return a JSON object with keys `title` and `summary`.").

### Common prompt engineering techniques

- **Be specific and unambiguous.** "Write a short paragraph" is weaker than "Write exactly 3 sentences, no more than 60 words total."
- **Assign a persona / role** via a system message ("You are a senior technical writer...") to steer tone and depth.
- **Break complex tasks into steps** rather than asking for everything in one giant instruction.
- **Ask for a specific output format** (bullet list, JSON, table) when the output will be consumed programmatically.
- **Iterate.** Prompt engineering is empirical — write, test, observe failure modes, refine.

### The three providers you'll commonly use to experiment

- **OpenAI API** — direct API access to OpenAI's models.
- **Azure OpenAI Service** — the same family of models, consumed through Azure with enterprise networking, compliance, and regional deployment options.
- **Open-source model hubs** (e.g., Hugging Face) — for self-hosting or experimenting with open models like Llama or Mistral.

## Build It

Build a tiny "prompt template engine" from scratch — the underlying idea behind every prompt-management library — so you understand what's happening before reaching for a framework.

```python
# code/prompt_template_from_scratch.py
# A minimal prompt templating system: instruction + context + input + output indicator.

from dataclasses import dataclass, field

@dataclass
class PromptTemplate:
    instruction: str
    output_indicator: str = ""
    examples: list = field(default_factory=list)  # list of (input, output) tuples

    def render(self, input_data: str) -> str:
        parts = [self.instruction.strip()]

        if self.examples:
            parts.append("\nExamples:")
            for i, (ex_in, ex_out) in enumerate(self.examples, start=1):
                parts.append(f"Input {i}: {ex_in}\nOutput {i}: {ex_out}")

        parts.append(f"\nInput: {input_data}")
        if self.output_indicator:
            parts.append(self.output_indicator)

        return "\n".join(parts)


if __name__ == "__main__":
    # Few-shot example: sentiment classification
    template = PromptTemplate(
        instruction="Classify the sentiment of the input as Positive, Negative, or Neutral.",
        output_indicator="Output:",
        examples=[
            ("I love this product!", "Positive"),
            ("This is the worst experience I've had.", "Negative"),
            ("The package arrived on Tuesday.", "Neutral"),
        ],
    )

    prompt = template.render("The support team never responded to my emails.")
    print(prompt)
```

## Use It

Send that same prompt through a real chat completion API and compare zero-shot vs. few-shot quality.

```python
# code/prompt_engineering_openai.py
# pip install openai --break-system-packages
from openai import OpenAI

client = OpenAI()

def ask(system: str, user: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content

# Zero-shot
zero_shot = ask(
    system="You are a sentiment classification assistant. Reply with exactly one word: Positive, Negative, or Neutral.",
    user="The support team never responded to my emails.",
)

# Few-shot (built from the PromptTemplate in Build It)
few_shot_prompt = (
    "Classify the sentiment of the input as Positive, Negative, or Neutral.\n\n"
    "Examples:\n"
    "Input 1: I love this product!\nOutput 1: Positive\n"
    "Input 2: This is the worst experience I've had.\nOutput 2: Negative\n"
    "Input 3: The package arrived on Tuesday.\nOutput 3: Neutral\n\n"
    "Input: The support team never responded to my emails.\nOutput:"
)
few_shot = ask(system="You are a helpful classification assistant.", user=few_shot_prompt)

print("Zero-shot:", zero_shot)
print("Few-shot:", few_shot)
```

## Ship It

**Artifact produced by this lesson:** `outputs/prompt-engineering-cheatsheet.md` — a one-page reference card of the instruction/context/input/output-indicator pattern plus 5 reusable prompt skeletons (classification, summarization, extraction, rewriting, Q&A) that a team can drop into any project.

## Exercises

1. Write a zero-shot prompt and a few-shot prompt for the same task (e.g., extracting dates from unstructured text). Run both and compare accuracy on 5 test inputs.
2. Rewrite this weak prompt to be specific and testable: "Tell me about dogs." Include an instruction, context, and output indicator.
3. **Challenge:** Build a small prompt library (5+ reusable templates) for a domain of your choice (customer support, code review, content moderation) using the `PromptTemplate` class from Build It, and write unit tests that check the rendered prompt contains all required sections.
