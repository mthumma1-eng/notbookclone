
import os
import numpy as np
import chromadb
from huggingface_hub import InferenceClient
from app.config import CHROMA_DIR

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "BAAI/bge-small-en-v1.5"
)
HF_TOKEN = os.getenv("HF_TOKEN", "")

_client = chromadb.PersistentClient(path=CHROMA_DIR)
_hf_client = None


def hf_client():
    global _hf_client
    if not HF_TOKEN:
        raise RuntimeError(
            "HF_TOKEN is missing. Add a Hugging Face token "
            "to your environment variables."
        )
    if _hf_client is None:
        _hf_client = InferenceClient(token=HF_TOKEN)
    return _hf_client


def embed_texts(texts):
    result = hf_client().feature_extraction(
        texts,
        model=EMBEDDING_MODEL
    )
    vectors = np.asarray(result, dtype=np.float32)

    # Ensure one vector per input text.
    if vectors.ndim == 1:
        vectors = vectors.reshape(1, -1)

    # Normalize vectors for cosine-style similarity.
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    vectors = vectors / np.maximum(norms, 1e-12)
    return vectors.tolist()


def collection(nid):
    return _client.get_or_create_collection(
        name="nb_" + nid.replace("-", "_")
    )


def add_chunks(nid, chunks, metadatas):
    if not chunks:
        return

    c = collection(nid)
    ids = [
        f"{nid}_{i}_{abs(hash(ch))}"
        for i, ch in enumerate(chunks)
    ]
    embeddings = embed_texts(chunks)

    c.add(
        ids=ids,
        documents=chunks,
        metadatas=metadatas,
        embeddings=embeddings
    )


def query_basic(nid, q, k=4):
    c = collection(nid)
    if c.count() == 0:
        return []

    emb = embed_texts([q])
    r = c.query(
        query_embeddings=emb,
        n_results=min(k, c.count()),
        include=["documents", "metadatas", "distances"]
    )

    return [
        {"text": d, "metadata": m, "distance": dist}
        for d, m, dist in zip(
            r["documents"][0],
            r["metadatas"][0],
            r["distances"][0]
        )
    ]


def query_mmr(nid, q, k=4, fetch=12, lambda_mult=0.65):
    c = collection(nid)
    if c.count() == 0:
        return []

    emb = embed_texts([q])
    r = c.query(
        query_embeddings=emb,
        n_results=min(fetch, c.count()),
        include=["documents", "metadatas", "embeddings"]
    )

    docs = r["documents"][0]
    metas = r["metadatas"][0]
    vectors = np.asarray(r["embeddings"][0], dtype=np.float32)

    if not docs:
        return []

    qv = np.asarray(emb[0], dtype=np.float32)
    similarities = vectors @ qv

    selected = []
    remaining = list(range(len(docs)))

    while remaining and len(selected) < min(k, len(docs)):
        if not selected:
            idx = max(remaining, key=lambda i: similarities[i])
        else:
            idx = max(
                remaining,
                key=lambda i: lambda_mult * similarities[i]
                - (1 - lambda_mult) * max(
                    float(vectors[i] @ vectors[j])
                    for j in selected
                )
            )

        selected.append(idx)
        remaining.remove(idx)

    return [
        {
            "text": docs[i],
            "metadata": metas[i],
            "distance": float(1 - similarities[i])
        }
        for i in selected
    ]
