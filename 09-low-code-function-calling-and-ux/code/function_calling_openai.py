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
    response = client.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=tools)
    message = response.choices[0].message

    if message.tool_calls:
        tool_call = message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)
        result = get_weather(**args)
        messages.append(message)
        messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)})
        final = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
        return final.choices[0].message.content

    return message.content

if __name__ == "__main__":
    print(handle_user_message("What's the weather like in Paris?"))
