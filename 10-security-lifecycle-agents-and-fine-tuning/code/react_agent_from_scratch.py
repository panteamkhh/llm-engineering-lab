FUNCTION_REGISTRY = {}

def register(name):
    def decorator(fn):
        FUNCTION_REGISTRY[name] = fn
        return fn
    return decorator

@register("search_docs")
def search_docs(query: str) -> str:
    return f"[fake search result for '{query}']: Refunds are processed within 5 business days."

@register("calculate")
def calculate(expression: str) -> str:
    return str(eval(expression, {"__builtins__": {}}))  # toy example only

def fake_planner(goal: str, observations: list) -> dict:
    if not observations:
        return {"action": "search_docs", "args": {"query": goal}, "done": False}
    return {"action": None, "args": {}, "done": True,
            "final_answer": f"Based on research: {observations[-1]}"}

def run_agent(goal: str, max_steps: int = 4) -> str:
    observations = []
    for step in range(max_steps):
        decision = fake_planner(goal, observations)
        if decision["done"]:
            return decision["final_answer"]
        fn = FUNCTION_REGISTRY[decision["action"]]
        result = fn(**decision["args"])
        observations.append(result)
        print(f"Step {step}: called {decision['action']} -> {result}")
    return "Max steps reached without a final answer."

if __name__ == "__main__":
    print(run_agent("How long do refunds take?"))
