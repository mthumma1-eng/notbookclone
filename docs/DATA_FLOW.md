# Data Flow

1. Notebook is created with a unique 12-character ID.
2. Uploaded source is copied to `data/<notebook_id>/sources/`.
3. Extracted text is split into overlapping chunks.
4. Every chunk receives metadata: source ID, source name, type, location, and chunk index.
5. Embeddings are stored in the Chroma collection for that notebook.
6. Questions are embedded and compared with the notebook collection only.
7. Retrieved chunks are passed to the LLM as evidence.
8. The answer and citations are stored in SQLite.
9. Artifact requests retrieve notebook chunks and generate Markdown files in the notebook's artifact folder.
