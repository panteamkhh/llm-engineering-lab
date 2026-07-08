# Lesson 09 — Low-Code AI, Function Calling, and Designing UX for AI Applications

> One-line motto — The model decides *what* to do; function calling and good UX decide *how the user actually experiences that decision*.

## The Problem

Once you can generate text, chat, search, and images, the next gap is connecting a model to the *outside world* (real systems, real actions) and presenting all of this to *real users* in a way they can trust and use effectively — without necessarily writing a full custom application from scratch every time. This lesson covers three connected topics: low-code platforms, function calling, and UX design for AI apps.

## The Concept

### Part 1 — Low-code / no-code generative AI

Low-code platforms (e.g., Microsoft Power Platform, with AI Builder and Copilot Studio-style capabilities) let non-developers or citizen developers:

- Build a **conversational agent/chatbot** on top of an LLM using a visual designer instead of code.
- Use **AI Builder** prebuilt models (e.g., document processing, sentiment analysis, prediction) alongside generative AI prompts inside a workflow/automation (e.g., "when a new support ticket arrives, summarize it and route it").
- Connect the AI capability to hundreds of prebuilt connectors (email, databases, CRM) without writing integration code.

**When to reach for low-code vs. custom code:** low-code is well suited for internal tools, rapid prototyping, and workflow automation where the team lacks deep engineering resources; custom code is better when you need fine-grained control over prompts, latency, cost, or a bespoke UX.

### Part 2 — Function calling (connecting models to external systems)

**Function calling** lets you describe a set of functions (name, description, parameter schema) to the model. Instead of only returning text, the model can respond by indicating *which function to call and with what arguments*, based on the user's request. Your application code then actually executes that function (e.g., call a weather API, query a database) and feeds the result back to the model to produce a final natural-language answer.

**Why this matters:** it turns an LLM from a "text-only" system into one that can take real actions and retrieve real-time data it wasn't trained on — the foundation for AI agents (see [Lesson 10](https://github.com/panteamkhh/llm-engineering-lab/tree/main/10-security-lifecycle-agents-and-fine-tuning)).

**Function calling flow:**

1. Define functions with a JSON-schema-like description of their parameters.
2. Send the user's message plus the function definitions to the model.
3. If the model decides a function call is needed, it returns a structured call (name + arguments) instead of a plain text answer.
4. Your code executes the real function with those arguments.
5. You send the function's result back to the model in a follow-up message.
6. The model produces a final natural-language response incorporating the result.

**When to use function calling vs. RAG:** RAG retrieves *static or semi-static knowledge* (documents); function calling triggers *actions or fetches live, structured data* (current weather, account balance, creating a calendar event). Many real applications use both.

### Part 3 — Designing UX for AI applications

**User experience** is the entire journey a user has interacting with your application — not just the chat window's visuals.

Key UX considerations specific to generative AI apps:

- **Set expectations up front.** Disclose that the user is interacting with AI, and be honest about its limitations (it can be wrong, it can be current only up to a point).
- **Design for uncertainty.** Show confidence signals where possible, offer sources/citations for grounded answers (from RAG), and make it easy to verify claims.
- **Provide control and recovery.** Let users edit/regenerate a response, undo an action taken via function calling, or escalate to a human.
- **Reduce blank-page anxiety.** Suggested prompts, example queries, or templates help users who don't know what to ask.
- **Give feedback loops.** Thumbs up/down or explicit correction mechanisms both improve the product and satisfy the accountability principle from [Lesson 02](https://github.com/panteamkhh/llm-engineering-lab/tree/main/02-responsible-generative-ai).
- **Match latency expectations to the UI.** Streaming text and progress indicators for slower operations (image generation, function calls to slow APIs) keep users engaged rather than confused by silence.

## Build It

Build a minimal function-calling dispatcher from scratch, so you understand the actual control flow before relying on a specific SDK's function-calling feature.

```python
# code/function_calling_dispatcher_from_scratch.py
import json

# A tiny registry mapping function names to real Python callables.
FUNCTION_REGISTRY = {}

def register(name):
    def decorator(fn):
        FUNCTION_REGISTRY[name] = fn
        return fn
    return decorator

@register("get_weather")
def get_weather(city: str) -> dict:
    """Stand-in for a real weather API call."""
    fake_data = {"Paris": "18C, cloudy", "Tokyo": "24C, sunny"}
    return {"city": city, "weather": fake_data.get(city, "unknown")}

def fake_model_decides_function_call(user_message: str) -> dict:
    """Stand-in for a real model's function-calling decision.
    A real model returns this structure based on function schemas you gave it."""
    if "weather" in user_message.lower():
        city = "Paris" if "paris" in user_message.lower() else "Tokyo"
        return {"name": "get_weather", "arguments": {"city": city}}
    return {}

def handle_user_message(user_message: str) -> str:
    decision = fake_model_decides_function_call(user_message)
    if not decision:
        return "I can help with weather questions right now."

    fn = FUNCTION_REGISTRY[decision["name"]]
    result = fn(**decision["arguments"])
    # In a real system, you'd feed `result` back to the model for a natural
    # language final answer. Here we format it directly for illustration.
    return f"The weather in {result['city']} is {result['weather']}."

if __name__ == "__main__":
    print(handle_user_message("What's the weather like in Paris?"))
```

## Use It

Wire the same registry pattern to a real model's native function/tool calling feature.

```python
# code/function_calling_openai.py
# pip install openai --break-system-packages
import json
from openai import OpenAI

client = OpenAI()

def get_weather(city: str) -> dict:
    fake_data = {"Paris": "18C, cloudy", "Tokyo": "24C, sunny"}
    return {"city": city, "weather": fake_data.get(city, "unknown")}

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        },
    }
]

def handle_user_message(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]

    response = client.chat.completions.create(
        model="gpt-4o-mini", messages=messages, tools=tools,
    )
    message = response.choices[0].message

    if message.tool_calls:
        tool_call = message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)
        result = get_weather(**args)

        messages.append(message)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result),
        })

        final = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
        return final.choices[0].message.content

    return message.content

if __name__ == "__main__":
    print(handle_user_message("What's the weather like in Paris?"))
```

## Ship It

**Artifact produced by this lesson:** `outputs/ai-app-ux-checklist.md` — a UX review checklist for generative AI features (disclosure, uncertainty handling, control/recovery, feedback loops, latency handling) plus the reusable function-registry pattern from Build It.

## Exercises

1. Add a second function (e.g., `get_stock_price`) to the registry pattern and extend the model prompt/tool schema so it can choose between the two functions correctly.
2. Design (in a short written spec, no code required) the UX for what happens when a function call fails (e.g., the weather API times out) — what does the user see, and what recovery options do they have?
3. **Challenge:** Build a low-code-style automation on paper: sketch a workflow (trigger → AI Builder-style step → generative AI summarization step → routing action) for "summarize and route incoming support tickets," and identify which step should be low-code vs. custom code and why.
