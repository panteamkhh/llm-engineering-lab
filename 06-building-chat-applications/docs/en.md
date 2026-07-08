# Lesson 06 — Building Chat Applications

> One-line motto — A chatbot follows a script; a generative chat application follows a conversation.

## The Problem

Traditional chatbots use predefined decision trees and pattern matching — cheap to run but rigid and unable to handle novel phrasing. Generative AI chat applications can handle open-ended conversation, but they introduce new engineering problems: how do you maintain conversation state, control cost as history grows, and keep responses on-topic and safe over many turns?

## The Concept

### Chatbot vs. generative AI chat application

| | Traditional chatbot | Generative AI chat app |
|---|---|---|
| Response generation | Predefined scripts/decision trees | Model-generated, dynamic |
| Handling novel input | Fails or falls back to "I don't understand" | Generalizes reasonably well |
| Setup cost | High (many rules to author) | Lower (prompt + system message) |
| Consistency | Very high (deterministic) | Needs active constraint (temperature, grounding) |

### Conversation state and message history

LLM chat APIs are stateless per call — the model has no memory between requests. Your application must send the **entire relevant conversation history** as part of the messages array on every call. This has two direct consequences:

1. **Cost and latency grow** with conversation length, since token count grows with history.
2. **Context window limits** mean you eventually must summarize or truncate older turns rather than sending the full history forever.

### Managing growing history

Common strategies:

- **Sliding window** — keep only the last *N* turns.
- **Summarization** — periodically summarize older turns into a compact system-message-style recap and drop the raw turns.
- **Retrieval-based memory** — store past turns in a vector store and retrieve only the relevant ones for the current turn (a chat-specific application of RAG, see [Lesson 07](https://github.com/panteamkhh/llm-engineering-lab/tree/main/07-search-apps-and-vector-databases)).

### Enhancing the user experience

- **Streaming responses** token-by-token dramatically improves perceived responsiveness.
- **Typing indicators / "thinking" states** manage user expectations during generation.
- **Clear AI disclosure** ("You're chatting with an AI assistant") supports the transparency principle from [Lesson 02](https://github.com/panteamkhh/llm-engineering-lab/tree/main/02-responsible-generative-ai).
- **Conversation reset / "start over"** affordances give users an escape hatch when the conversation goes off track.

### Capturing performance metrics

Track, per conversation and in aggregate:

- Latency (time-to-first-token and total completion time)
- Token usage (input/output, cost)
- User satisfaction signals (thumbs up/down, session length, drop-off point)
- Safety-system trigger rate (from [Lesson 02](https://github.com/panteamkhh/llm-engineering-lab/tree/main/02-responsible-generative-ai)'s mitigation layer)

### Responsible AI in chat specifically

Because chat is multi-turn, harmful content can emerge gradually across turns even if each individual message looks benign. Safety checks should run on the *combined recent context*, not only the latest message in isolation.

## Build It

Implement a minimal, in-memory chat session manager with a sliding-window history strategy, built from scratch before reaching for a framework's session abstraction.

```python
# code/chat_session_from_scratch.py
from dataclasses import dataclass, field

@dataclass
class ChatSession:
    system_prompt: str
    max_turns: int = 6  # keep the last N user/assistant turn PAIRS
    history: list = field(default_factory=list)  # list of {"role", "content"} dicts

    def add_user_message(self, content: str):
        self.history.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str):
        self.history.append({"role": "assistant", "content": content})
        self._trim()

    def _trim(self):
        max_messages = self.max_turns * 2
        if len(self.history) > max_messages:
            self.history = self.history[-max_messages:]

    def build_messages(self) -> list:
        return [{"role": "system", "content": self.system_prompt}] + self.history


if __name__ == "__main__":
    session = ChatSession(system_prompt="You are a friendly support assistant.")
    session.add_user_message("My order hasn't arrived yet.")
    session.add_assistant_message("I'm sorry to hear that! Can you share your order number?")
    session.add_user_message("It's 12345.")

    for msg in session.build_messages():
        print(f"{msg['role']}: {msg['content']}")
```

## Use It

Connect the session manager to a real streaming chat completion API with response-level safety checks.

```python
# code/chat_app.py
# pip install openai --break-system-packages
from openai import OpenAI

client = OpenAI()

class ChatSession:
    def __init__(self, system_prompt: str, max_turns: int = 6):
        self.system_prompt = system_prompt
        self.max_turns = max_turns
        self.history = []

    def add_user_message(self, content: str):
        self.history.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str):
        self.history.append({"role": "assistant", "content": content})
        max_messages = self.max_turns * 2
        if len(self.history) > max_messages:
            self.history = self.history[-max_messages:]

    def build_messages(self):
        return [{"role": "system", "content": self.system_prompt}] + self.history

def send_turn(session: ChatSession, user_message: str) -> str:
    session.add_user_message(user_message)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=session.build_messages(),
        temperature=0.5,
        max_tokens=200,
    )
    reply = response.choices[0].message.content
    session.add_assistant_message(reply)
    return reply

if __name__ == "__main__":
    session = ChatSession(system_prompt="You are a friendly support assistant for an e-commerce store.")
    print(send_turn(session, "My order hasn't arrived yet."))
    print(send_turn(session, "It's order number 12345."))
```

## Ship It

**Artifact produced by this lesson:** `outputs/chat-app-metrics-dashboard-spec.md` — a spec for a metrics dashboard (latency, token cost, safety-trigger rate, satisfaction signals) plus the reusable `ChatSession` class from Build It, ready to drop into a chat backend.

## Exercises

1. Implement summarization-based history management: when the conversation exceeds N turns, ask the model to summarize the oldest turns into a single system-message recap instead of dropping them outright.
2. Add streaming to the `send_turn` function and measure time-to-first-token vs. total completion time.
3. **Challenge:** Add a response-level safety check that evaluates the *last 3 turns combined*, not just the latest assistant message, and demonstrate a case where checking only the latest message would miss an issue that checking the combined context catches.
