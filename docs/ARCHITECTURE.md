# Architecture Documentation

## Components

### UI
Gradio provides notebook management, source upload/URL ingestion, chat, citation display, artifact generation, and artifact download.

### Service layer
`app/service.py` coordinates notebook operations, ingestion, retrieval, chat persistence, and artifact generation.

### Ingestion
- `loaders.py`: PDF, PPTX, TXT, and web-page extraction.
- `chunker.py`: overlapping text chunks.

### Retrieval
- `vector.py`: notebook-specific Chroma collections and Sentence Transformers embeddings.
- Vector Similarity: direct semantic top-k retrieval.
- MMR: candidate retrieval followed by relevance/diversity selection.

### Storage
SQLite stores notebooks, source metadata, conversations, and artifact metadata. Source files and artifacts are organized below the notebook ID. Chroma persists vector embeddings.

### LLM
The application uses an OpenAI-compatible client, so the endpoint/model can be changed without changing application code. The default configuration targets Groq.

## Data flow

`source → extractor → chunker → embedding model → Chroma → retriever → grounded prompt → LLM → cited answer`

Chat messages are saved after every question/answer. Artifacts are saved as Markdown files under the selected notebook.

## Deployment

The Dockerfile exposes port 7860. GitHub Actions installs dependencies, compiles the project, and uploads the repository to a Docker-based Hugging Face Space. Runtime API keys are configured as platform secrets.
