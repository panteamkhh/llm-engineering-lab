# Model & Deployment Strategy Selection Checklist

## 1. Open source vs. proprietary
- [ ] Do you need to self-host for compliance/data residency? -> lean open source
- [ ] Do you need fastest time-to-market with minimal ops? -> lean proprietary API
- [ ] Do you need to fine-tune weights freely, including architecture-level changes? -> open source

## 2. Prompt Engineering vs. RAG vs. Fine-tuning vs. Train-from-scratch
- [ ] Is the task general-purpose language understanding the base model already handles well? -> Prompt engineering (zero/one/few-shot)
- [ ] Do you need access to private, proprietary, or frequently changing data? -> RAG
- [ ] Do you need a specific output format/style/tone at low latency, and have quality labeled data? -> Fine-tuning
- [ ] Is your domain so specialized that no foundation model transfers well, and do you have massive domain data + compute? -> Train from scratch (rare)

## 3. Cost & maintenance tradeoffs
| Factor | Prompt Eng. | RAG | Fine-tuning | From scratch |
|---|---|---|---|---|
| Setup cost | Low | Medium | Medium-High | Very High |
| Ongoing cost | API usage | API + vector DB | API + retraining | Full infra |
| Data needed | None-few examples | Document corpus | Labeled examples | Massive corpus |
| Time to first result | Minutes | Days | Weeks | Months+ |

Remember: these approaches are complementary. Many production systems combine two or more.
