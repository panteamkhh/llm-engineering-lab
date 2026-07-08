# pip install openai --break-system-packages
import json
from openai import OpenAI

client = OpenAI()

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

uploaded = client.files.create(file=open("training_data.jsonl", "rb"), purpose="fine-tune")
job = client.fine_tuning.jobs.create(training_file=uploaded.id, model="gpt-4o-mini-2024-07-18")
print(f"Fine-tuning job created: {job.id}. Poll client.fine_tuning.jobs.retrieve(job.id) for status.")

# Once complete:
# fine_tuned_model_id = client.fine_tuning.jobs.retrieve(job.id).fine_tuned_model
# response = client.chat.completions.create(model=fine_tuned_model_id, messages=[...])
