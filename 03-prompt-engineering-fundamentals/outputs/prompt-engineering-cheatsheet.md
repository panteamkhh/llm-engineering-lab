# Prompt Engineering Cheatsheet

## Anatomy
Instruction + Context + Input data + Output indicator

## 5 reusable skeletons

### Classification
"Classify the input as one of: {labels}. Reply with only the label.\nInput: {input}"

### Summarization
"Summarize the following text in {n} sentences, focusing on {focus}.\nText: {input}"

### Extraction
"Extract the following fields as JSON: {fields}.\nText: {input}\nJSON:"

### Rewriting
"Rewrite the following text in a {tone} tone, keeping the same meaning.\nText: {input}"

### Q&A grounded in context
"Using only the context below, answer the question. If the answer isn't in the context, say 'I don't know'.\nContext: {context}\nQuestion: {question}"
