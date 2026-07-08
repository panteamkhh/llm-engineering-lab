from dataclasses import dataclass, field

@dataclass
class ChatSession:
    system_prompt: str
    max_turns: int = 6
    history: list = field(default_factory=list)

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
