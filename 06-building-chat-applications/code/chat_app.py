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
