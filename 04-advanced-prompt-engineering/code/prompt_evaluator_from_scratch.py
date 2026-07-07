from dataclasses import dataclass

@dataclass
class EvalCase:
    input_text: str
    expected_contains: str

@dataclass
class PromptVariant:
    name: str
    build_prompt: callable

def score_variant(variant: PromptVariant, cases: list, model_call) -> float:
    correct = 0
    for case in cases:
        prompt = variant.build_prompt(case.input_text)
        output = model_call(prompt)
        if case.expected_contains.lower() in output.lower():
            correct += 1
    return correct / len(cases)

def fake_model_call(prompt: str) -> str:
    if "step by step" in prompt.lower():
        return "Step 1: 3 apples. Step 2: 2 more apples. Total: 5 apples."
    return "5"

cases = [EvalCase(input_text="3 apples plus 2 apples", expected_contains="5")]

zero_shot = PromptVariant(name="direct", build_prompt=lambda x: f"What is the total? {x}")
cot = PromptVariant(name="chain-of-thought", build_prompt=lambda x: f"Let's think step by step. What is the total? {x}")

if __name__ == "__main__":
    for variant in (zero_shot, cot):
        acc = score_variant(variant, cases, fake_model_call)
        print(f"{variant.name}: accuracy={acc:.0%}")
