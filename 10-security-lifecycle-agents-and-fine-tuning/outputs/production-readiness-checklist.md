# Production Readiness Checklist

## Security
- [ ] Prompt injection mitigations in place (delimiters, input/output filtering)
- [ ] Least-privilege scoping on any function-calling capability
- [ ] Output validated before use in downstream systems
- [ ] Prompts/completions logged for audit (with PII handling policy)
- [ ] Periodic red-teaming scheduled

## LLMOps / Lifecycle
- [ ] Prompts & RAG configs versioned in source control
- [ ] Evaluation dataset exists and runs on every change
- [ ] Staged rollout plan for new prompt/model versions
- [ ] Production monitoring dashboard (quality, cost, latency)

## Agents
- [ ] Guardrails on max steps / max calls per tool
- [ ] Human-in-the-loop approval for high-privilege actions
- [ ] Clear fallback when the agent can't complete the goal

## Fine-tuning vs. RAG vs. Prompting decision
- Knowledge gap (facts) -> RAG
- Format/tone/style consistency at scale -> Fine-tuning
- Everything else -> Prompt engineering first
