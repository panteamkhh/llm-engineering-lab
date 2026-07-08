from dataclasses import dataclass

@dataclass
class ImagePromptSpec:
    subject: str
    style: str = "photorealistic"
    composition: str = "medium shot"
    lighting: str = "soft natural light"
    qualifiers: list = None

    def compile(self) -> str:
        parts = [self.subject, self.style, self.composition, self.lighting]
        if self.qualifiers:
            parts.extend(self.qualifiers)
        return ", ".join(p for p in parts if p)

if __name__ == "__main__":
    spec = ImagePromptSpec(
        subject="a golden retriever puppy sitting in a meadow",
        style="digital painting",
        composition="close-up, rule of thirds",
        lighting="soft morning light",
        qualifiers=["highly detailed", "4k"],
    )
    print(spec.compile())
