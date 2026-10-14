
import os
import numpy as np
import chromadb
from fastembed import TextEmbedding
from app.config import CHROMA_DIR

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "BAAI/bge-small-en-v1.5",
)

_client = chromadb.PersistentClient(path=CHROMA_DIR)
_embedding_model = None


def get_embedding_model():
    global _embedding_model

    if _embedding_model is None:
        _embedding_model = TextEmbedding(
            model_name=EMBEDDING_MODEL,
            threads=1,
        )

    return _embedding_model


def embed_texts(texts):
    if not texts:
        return []

    model = get_embedding_model()
    vectors = list(model.embed(texts, batch_size=8))

    return [vector.tolist() for vector in vectors]


def collection(nid):
    return _client.get_or_create_collection(
        name="nb_" + nid.replace("-", "_")
    )


def add_chunks(nid, chunks, metadatas):
    if not chunks:
        return

    c = collection(nid)

    # Process small batches to limit memory usage.
    for start in range(0, len(chunks), 8):
        batch_chunks = chunks[start:start + 8]
        batch_metadata = metadatas[start:start + 8]

        ids = [
            f"{nid}_{i}_{abs(hash(chunk))}"
            for i, chunk in enumerate(
                batch_chunks, start=start
            )
        ]

        embeddings = embed_texts(batch_chunks)

        c.upsert(
            ids=ids,
            documents=batch_chunks,
            metadatas=batch_metadata,
            embeddings=embeddings,
        )


def query_basic(nid, q, k=4):
    c = collection(nid)

    if c.count() == 0:
        return []

    embeddings = embed_texts([q])

    result = c.query(
        query_embeddings=embeddings,
        n_results=min(k, c.count()),
        include=["documents", "metadatas", "distances"],
    )

    return [
        {"text": doc, "metadata": meta, "distance": distance}
        for doc, meta, distance in zip(
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
        )
    ]


def query_mmr(nid, q, k=4, fetch=12, lambda_mult=0.65):
    c = collection(nid)

    if c.count() == 0:
        return []

    embeddings = embed_texts([q])

    result = c.query(
        query_embeddings=embeddings,
        n_results=min(fetch, c.count()),
        include=["documents", "metadatas", "embeddings"],
    )

    docs = result["documents"][0]
    metas = result["metadatas"][0]

    if not docs:
        return []

    vectors = np.asarray(
        result["embeddings"][0], dtype=np.float32
    )
    query_vector = np.asarray(embeddings[0], dtype=np.float32)

    similarities = vectors @ query_vector
    selected = []
    remaining = list(range(len(docs)))

    while remaining and len(selected) < min(k, len(docs)):
        if not selected:
            chosen = max(
                remaining, key=lambda i: similarities[i]
            )
        else:
            chosen = max(
                remaining,
                key=lambda i: (
                    lambda_mult * similarities[i]
                    - (1 - lambda_mult) * max(
                        float(vectors[i] @ vectors[j])
                        for j in selected
                    )
                ),
            )

        selected.append(chosen)
        remaining.remove(chosen)

    return [
        {
            "text": docs[i],
            "metadata": metas[i],
            "distance": float(1 - similarities[i]),
        }
        for i in selected
    ]
