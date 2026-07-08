# Chat App Metrics Dashboard Spec

## Metrics to track
- Time-to-first-token (p50/p95)
- Total completion latency (p50/p95)
- Input/output token usage & cost per conversation
- Safety-system trigger rate (per 1000 turns)
- User satisfaction signals: thumbs up/down rate, session length, drop-off turn

## Panels
1. Latency over time (line chart)
2. Token cost per day (bar chart)
3. Safety triggers by category (table)
4. Satisfaction rate trend (line chart)

Reusable component: code/chat_session_from_scratch.py::ChatSession
