# RAG Architecture & Chunking Checklist

```mermaid
flowchart LR
    Docs[Documents] --> Chunk --> Embed --> VectorDB[(Vector DB)]
    Query[User Query] --> EmbedQ[Embed] --> Search --> VectorDB
    Search --> Context[Retrieved Chunks]
    Context --> Prompt --> LLM --> Answer
```

## Chunking decision checklist
- [ ] Chunk size fits comfortably under the embedding model's input limit
- [ ] Chunk boundaries respect semantic units (paragraph/section, not mid-sentence)
- [ ] Overlap (10-20%) added to avoid losing boundary context
- [ ] Metadata (source, date, section) stored alongside each chunk
- [ ] Re-indexing plan exists for when source documents change
