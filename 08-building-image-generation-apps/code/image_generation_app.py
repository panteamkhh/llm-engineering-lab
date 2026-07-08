# pip install openai requests --break-system-packages
from openai import OpenAI
import requests

client = OpenAI()

def generate_image(prompt: str, size: str = "1024x1024") -> str:
    response = client.images.generate(model="dall-e-3", prompt=prompt, size=size, n=1)
    return response.data[0].url

def download_image(url: str, path: str):
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    with open(path, "wb") as f:
        f.write(resp.content)

if __name__ == "__main__":
    prompt = (
        "a golden retriever puppy sitting in a meadow, digital painting, "
        "close-up, rule of thirds, soft morning light, highly detailed, 4k"
    )
    image_url = generate_image(prompt)
    download_image(image_url, "puppy.png")
    print("Saved to puppy.png")
