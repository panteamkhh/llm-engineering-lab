# Real tokenizer + real completion call (see docs/en.md - Use It)
# pip install tiktoken openai --break-system-packages
import tiktoken
from openai import OpenAI

encoding = tiktoken.get_encoding("cl100k_base")
text = "Generative AI models predict the next token given previous tokens."
token_ids = encoding.encode(text)

print("Token count:", len(token_ids))
print("Token IDs:", token_ids)
print("Decoded back:", encoding.decode(token_ids))

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a concise AI education assistant."},
        {"role": "user", "content": "In one sentence, explain what a foundation model is."},
    ],
    max_tokens=60,
)

print(response.choices[0].message.content)
print("Tokens used:", response.usage.total_tokens)