from dataclasses import dataclass, field

@dataclass
class PromptTemplate:
    instruction: str
    output_indicator: str = ""
    examples: list = field(default_factory=list)

    def render(self, input_data: str) -> str:
        parts = [self.instruction.strip()]
        if self.examples:
            parts.append("\nExamples:")
            for i, (ex_in, ex_out) in enumerate(self.examples, start=1):
                parts.append(f"Input {i}: {ex_in}\nOutput {i}: {ex_out}")
        parts.append(f"\nInput: {input_data}")
        if self.output_indicator:
            parts.append(self.output_indicator)
        return "\n".join(parts)

if __name__ == "__main__":
    template = PromptTemplate(
        instruction="Classify the sentiment of the input as Positive, Negative, or Neutral.",
        output_indicator="Output:",
        examples=[
            ("I love this product!", "Positive"),
            ("This is the worst experience I've had.", "Negative"),
            ("The package arrived on Tuesday.", "Neutral"),
        ],
    )
    prompt = template.render("The support team never responded to my emails.")
    print(prompt)
