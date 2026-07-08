# Lesson 08 — Building Image Generation Applications

> One-line motto — A great image prompt is a great text prompt with a camera lens attached.

## The Problem

Image generation models (DALL·E, Stable Diffusion, and similar diffusion-based models) turn a text prompt into a raster image, but naive prompts ("a dog") produce generic, low-quality results. Building a real image-generation feature also means handling variations, editing, safety filtering, and cost — all different from text generation.

## The Concept

### How image generation models work (conceptually)

Most modern image generators are **diffusion models**: they start from random noise and iteratively "denoise" it, guided at each step by the text prompt (via a text encoder), until a coherent image emerges. You don't need to implement diffusion to use these models effectively, but knowing the mechanism explains *why* prompt wording ("style," "lighting," "composition") has such a strong effect — it's steering the denoising process at every step.

### Anatomy of a strong image prompt

1. **Subject** — what is depicted ("a golden retriever puppy").
2. **Style/medium** — ("digital painting," "photorealistic," "watercolor," "3D render").
3. **Composition/framing** — ("close-up," "wide shot," "rule of thirds").
4. **Lighting and mood** — ("soft morning light," "dramatic backlighting").
5. **Technical qualifiers** — ("4k," "highly detailed," "shallow depth of field") — useful for some models, ignored by others, so test per-model.

### Core image API capabilities

- **Generation** — text-to-image from a prompt.
- **Variation** — generate alternate versions of an existing image while preserving its general composition.
- **Editing/inpainting** — modify a specific masked region of an existing image while leaving the rest untouched (e.g., "replace the sky with a sunset").
- **Size/resolution and quantity parameters** — most APIs let you request multiple images per call and choose output resolution, both of which affect cost.

### Responsible image generation

Image generation carries specific risks beyond text: generating photorealistic depictions of real people, deepfakes, or copyrighted characters/art styles. Most providers apply content filters on both the prompt and the resulting image, and application-level policies should add their own review layer for user-facing generation features (consistent with the mitigation layers from Lesson 02).

### Cost and latency considerations

Image generation is typically slower and more expensive per request than text generation. Practical patterns:

- Cache generated images keyed by prompt (and parameters) to avoid regenerating identical requests.
- Generate at lower resolution for previews, then generate a final high-resolution version only on explicit user confirmation.
- Queue/async generation with a loading state, since generation can take several seconds.

## Build It

Since real diffusion models require GPUs and large weights, build a small "prompt compiler" from scratch that assembles a well-structured image prompt from separate subject/style/lighting/composition fields — the discipline that makes image prompts consistently good, independent of which model executes them.

```python
# code/image_prompt_builder_from_scratch.py
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
```

## Use It

Send the compiled prompt to a real image generation API, then request a variation of the result.

```python
# code/image_generation_app.py
# pip install openai requests --break-system-packages
from openai import OpenAI
import requests

client = OpenAI()

def generate_image(prompt: str, size: str = "1024x1024") -> str:
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        n=1,
    )
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
```

## Ship It

**Artifact produced by this lesson:** `outputs/image-prompt-style-guide.md` — a reusable style-guide table (subject/style/composition/lighting/qualifiers) plus the `ImagePromptSpec` builder from Build It, so non-technical teammates can produce consistent prompts without memorizing syntax.

## Exercises

1. Generate the same subject with three different `style` values (e.g., "photorealistic," "watercolor," "3D render") and compare the results.
2. Add a `negative_qualifiers` field to `ImagePromptSpec` (things to avoid, where the target model/API supports negative prompts) and demonstrate its effect.
3. **Challenge:** Build a simple image-prompt cache (keyed by the compiled prompt string + size) that avoids re-generating and re-downloading an image for an identical request, and write a test proving the second identical call doesn't hit the network.
