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

zero_shot = ask(
    system="You are a sentiment classification assistant. Reply with exactly one word: Positive, Negative, or Neutral.",
    user="The support team never responded to my emails.",
)

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
