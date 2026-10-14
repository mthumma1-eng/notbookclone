# RAG Evaluation

## Methods

### Method 1 — Vector Similarity
Direct top-k semantic retrieval using normalized Sentence Transformers embeddings and Chroma distance search.

### Method 2 — MMR / Diversity Retrieval
Retrieve a larger candidate set, then select chunks using a relevance/diversity objective. This reduces redundant chunks and can improve coverage.

## Test protocol

Use the same notebook and questions for both methods. Run `evaluation/evaluate.py` and record:

| Question | Method | Retrieved Chunks | Response Time | Answer Quality |
|---|---|---:|---:|---|
| Q1 | Vector Similarity | 4 | measured | human rating |
| Q1 | MMR | 4 | measured | human rating |
| Q2 | Vector Similarity | 4 | measured | human rating |
| Q2 | MMR | 4 | measured | human rating |

The generated CSV contains the actual retrieved text snippets and measured retrieval times. Human answer-quality ratings should be completed after running the same questions through the deployed application.

## Tradeoff discussion template

Vector similarity is simpler and normally has lower retrieval overhead. MMR adds candidate processing but can return more diverse evidence. Select the method that gives better grounded answers for the project's representative questions while considering latency.
