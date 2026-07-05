# Generative AI Engineering — From Scratch Notes

Study notes and runnable examples derived from a 4h20m "Generative AI for Beginners" video course, restructured into 10 practical, GitHub-ready lessons. Every lesson follows a **Build It / Use It** split: implement the core idea from scratch first (no SDK), then do the same thing with a real production API — so the framework never feels like a black box.

## Repo structure

```
.
├── README.md                                  # this file — lesson index + pattern
└── phases/
    └── 01-generative-ai-for-beginners/         # phase folder
        ├── 01-foundations-of-generative-ai-and-llms/
        │   ├── docs/en.md                      # lesson narrative (required)
        │   ├── code/                           # runnable implementations
        │   └── outputs/                        # reusable artifact this lesson produces
        ├── 02-responsible-generative-ai/
        ├── 03-prompt-engineering-fundamentals/
        ├── 04-advanced-prompt-engineering/
        ├── 05-building-text-generation-apps/
        ├── 06-building-chat-applications/
        ├── 07-search-apps-and-vector-databases/
        ├── 08-building-image-generation-apps/
        ├── 09-low-code-function-calling-and-ux/
        └── 10-security-lifecycle-agents-and-fine-tuning/
```

Each lesson directory follows the same six-beat template in `docs/en.md`:

```markdown
# Lesson Title
> One-line motto — the core idea in one sentence.

## The Problem       — why this matters, what you can't do without it
## The Concept        — the ideas, explained with intuition, before any code
## Build It            — step-by-step implementation from scratch
## Use It               — the same idea via a real framework/library/API
## Ship It              — the artifact (prompt/skill/checklist/tool) this lesson produces
## Exercises           — practice + a challenge exercise
```

## Lesson index

| # | Lesson | Covers |
|---|---|---|
| 01 | [Foundations of Generative AI and LLMs](phases/01-generative-ai-for-beginners/01-foundations-of-generative-ai-and-llms/docs/en.md) | Transformers, tokenization, foundation models, open source vs. proprietary, choosing a strategy |
| 02 | [Using Generative AI Responsibly](phases/01-generative-ai-for-beginners/02-responsible-generative-ai/docs/en.md) | Identify/measure/mitigate/operate, responsible AI principles |
| 03 | [Prompt Engineering Fundamentals](phases/01-generative-ai-for-beginners/03-prompt-engineering-fundamentals/docs/en.md) | Zero/one/few-shot, prompt anatomy, prompt templates |
| 04 | [Advanced Prompt Engineering](phases/01-generative-ai-for-beginners/04-advanced-prompt-engineering/docs/en.md) | Personas, chain-of-thought, structured output, prompt injection |
| 05 | [Building Text Generation Applications](phases/01-generative-ai-for-beginners/05-building-text-generation-apps/docs/en.md) | Generation parameters, retries, streaming |
| 06 | [Building Chat Applications](phases/01-generative-ai-for-beginners/06-building-chat-applications/docs/en.md) | Conversation state, history management, chat metrics |
| 07 | [Search Apps, Vector Databases & RAG](phases/01-generative-ai-for-beginners/07-search-apps-and-vector-databases/docs/en.md) | Embeddings, vector stores, chunking, full RAG pipeline |
| 08 | [Building Image Generation Applications](phases/01-generative-ai-for-beginners/08-building-image-generation-apps/docs/en.md) | Diffusion models (conceptually), image prompt design, editing/variations |
| 09 | [Low-Code AI, Function Calling & UX](phases/01-generative-ai-for-beginners/09-low-code-function-calling-and-ux/docs/en.md) | Low-code platforms, function/tool calling, AI application UX design |
| 10 | [Security, Lifecycle, Agents & Fine-Tuning](phases/01-generative-ai-for-beginners/10-security-lifecycle-agents-and-fine-tuning/docs/en.md) | AI-specific security risks, LLMOps, agent loops, fine-tuning workflow |

## Content rules (borrowed from the reference repo's contribution guide)

- **Build from scratch first**, then show the framework/library version — always in that order.
- **No filler.** Every section should teach something usable, not restate the obvious.
- **Original code only** — every code sample here is written for this repo, runnable standalone with the listed `pip install` line.
- **One topic, one lesson.** If a lesson is trying to teach two unrelated things, split it.
- **Numbering is sequential and permanent** — once a lesson number ships, don't renumber it; add new lessons at the next free number.

## Suggested next steps for turning this into content

- Each `docs/en.md` file can be published as-is as a blog post, dev.to article, or repo page.
- Each `code/` file is a standalone script — good material for short video walkthroughs or code-along threads.
- Each `outputs/` file is a lead-magnet-style downloadable checklist/cheat-sheet, useful for newsletter or social content.
