# Text Generation Parameter Guide

| Use case | temperature | max_tokens | penalties |
|---|---|---|---|
| Code generation | 0-0.2 | task-dependent | none |
| Creative writing | 0.7-1.0 | large | presence_penalty ~0.3 |
| Structured extraction | 0 | tight | none |
| Chat | 0.3-0.7 | moderate | frequency_penalty light |
| Brainstorm lists | 0.8-1.0 | moderate | presence_penalty higher |

Reusable retry helper: code/generation_loop_from_scratch.py::call_model_with_retry
