# NotebookLM / Gemini Notebook Clone

A full-stack AI research and study assistant for creating multiple notebooks, ingesting PDF/PPTX/TXT/URL sources, asking grounded RAG questions with citations, and generating Markdown reports and quizzes with answer keys.

## Features

- Create, rename, delete, and switch between notebooks
- Notebook-isolated source files, vector collections, chat history, and artifacts
- PDF, PPTX, TXT, and single-page URL ingestion
- Text extraction → chunking → embeddings → ChromaDB
- RAG chat with source citations
- Persistent SQLite chat/source/notebook metadata
- Two retrieval approaches: vector similarity and MMR/diversity retrieval
- Markdown report generation
- Markdown quiz + answer key generation
- Downloadable artifacts
- Environment-variable based API keys
- Docker deployment
- GitHub Actions CI/CD deployment to Hugging Face Spaces

## Architecture

```text
User
  |
  v
Gradio UI
  |
  v
Application Service Layer
  |-------------------|---------------------|
  v                   v                     v
Ingestion          SQLite               Artifact Generator
  |                   |                     |
PDF/PPTX/TXT/URL     |                     v
  |             notebooks/sources/      Markdown
  v             messages/artifacts      report/quiz
Chunking
  |
Embeddings
  |
ChromaDB
  |
Vector / MMR Retriever
  |
OpenAI-compatible LLM API
  |
Answer + citations
```

## Local setup

Python 3.11 is recommended.

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux
python -m app.main
```

Open `http://localhost:7860`.

### Environment variables

- `LLM_API_KEY` – API key for your LLM provider
- `LLM_BASE_URL` – OpenAI-compatible endpoint, default is Groq
- `LLM_MODEL` – model name supported by your provider
- `EMBEDDING_MODEL` – Sentence Transformers embedding model
- `TOP_K` – number of chunks retrieved
- `CHUNK_SIZE` – target chunk size
- `CHUNK_OVERLAP` – overlap between chunks

Do not commit `.env` or API keys.

## Storage design

Each notebook has a unique ID. Files are stored under `data/<notebook_id>/sources/`, generated artifacts under `data/<notebook_id>/artifacts/`, metadata and conversations in `storage/notebooks.db`, and embeddings in the Chroma persistent directory.

This design intentionally uses local persistent storage. On hosting platforms where the filesystem is ephemeral, data can disappear after a rebuild/restart unless persistent storage is enabled. For the assignment, this limitation is documented rather than hidden.

## RAG pipeline

1. User selects a notebook.
2. Source is extracted.
3. Text is split into overlapping chunks.
4. `all-MiniLM-L6-v2` generates normalized embeddings.
5. Chunks and citation metadata are stored in a notebook-specific Chroma collection.
6. A question is embedded and relevant chunks are retrieved.
7. The LLM receives only the retrieved source excerpts.
8. The answer includes `[Source N]` references and the UI displays the retrieved source/chunk metadata.

### Retrieval comparison

**Vector Similarity** selects the highest semantic-similarity chunks. It is simple and fast but can return several highly similar chunks from the same passage.

**MMR / Diversity Retrieval** first fetches a larger candidate set and then balances query relevance with diversity. It can improve coverage across different parts of a source at the cost of additional retrieval computation.

Run:

```bash
python -m evaluation.evaluate NOTEBOOK_ID "What is the main idea?" "What evidence supports the conclusion?"
```

Then manually rate answer quality and discuss response-time/coverage tradeoffs in `evaluation/RAG_EVALUATION.md`.

## CI/CD

The GitHub Actions workflow:

```text
Push to main
    ↓
GitHub Actions
    ↓
Install dependencies
    ↓
Compile/check Python
    ↓
Upload project to Hugging Face Space
```

Create these GitHub repository secrets:

- `HF_TOKEN` – Hugging Face write token
- `HF_SPACE` – Space repo ID, e.g. `username/notebooklm-clone`

For the deployed Space, add the runtime secret `LLM_API_KEY` and any optional LLM configuration variables in the Space settings. Never put them in the repository.

## Deployment demonstration

Record 1–2 minutes showing:

1. Live application
2. Notebook creation/selection
3. Source ingestion
4. RAG question
5. Citation
6. Report or quiz generation/download
7. GitHub Actions successful deployment

## Submission checklist

- [x] Multiple notebooks
- [x] Rename/delete/switch
- [x] PDF/PPTX/TXT/URL ingestion
- [x] Chunking and embeddings
- [x] Chroma vector database
- [x] RAG chat
- [x] Citations
- [x] Persistent chat metadata
- [x] Report artifact
- [x] Quiz + answer key
- [x] Artifact download
- [x] Error handling
- [x] Two retrieval approaches
- [x] Evaluation script
- [x] Architecture documentation
- [x] Dockerfile
- [x] GitHub Actions workflow
- [x] Secrets via environment variables

Before submission, add the live deployment URL and GitHub repository URL to the final submission document.
