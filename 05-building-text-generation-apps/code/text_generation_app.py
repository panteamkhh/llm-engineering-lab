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
            print(delta, end="", flush=True)
    print()
    return "".join(chunks)

if __name__ == "__main__":
    generate_text("Write a one-sentence product description for a smart water bottle.")
