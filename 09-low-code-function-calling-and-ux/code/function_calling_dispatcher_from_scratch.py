import json

FUNCTION_REGISTRY = {}

def register(name):
    def decorator(fn):
        FUNCTION_REGISTRY[name] = fn
        return fn
    return decorator

@register("get_weather")
def get_weather(city: str) -> dict:
    fake_data = {"Paris": "18C, cloudy", "Tokyo": "24C, sunny"}
    return {"city": city, "weather": fake_data.get(city, "unknown")}

def fake_model_decides_function_call(user_message: str) -> dict:
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
    return f"The weather in {result['city']} is {result['weather']}."

if __name__ == "__main__":
    print(handle_user_message("What's the weather like in Paris?"))
