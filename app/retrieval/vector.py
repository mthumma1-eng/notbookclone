import chromadb
from sentence_transformers import SentenceTransformer
from app.config import CHROMA_DIR, EMBEDDING_MODEL

_client=chromadb.PersistentClient(path=CHROMA_DIR)
_model=None

def model():
    global _model
    if _model is None: _model=SentenceTransformer(EMBEDDING_MODEL)
    return _model

def collection(nid): return _client.get_or_create_collection(name="nb_"+nid.replace("-","_"))

def add_chunks(nid,chunks,metadatas):
    c=collection(nid); ids=[f"{nid}_{i}_{abs(hash(ch))}" for i,ch in enumerate(chunks)]
    emb=model().encode(chunks,normalize_embeddings=True).tolist()
    c.add(ids=ids,documents=chunks,metadatas=metadatas,embeddings=emb)

def query_basic(nid,q,k=4):
    c=collection(nid); emb=model().encode([q],normalize_embeddings=True).tolist()
    if c.count()==0:return []
    r=c.query(query_embeddings=emb,n_results=min(k,c.count()),include=["documents","metadatas","distances"])
    return [{"text":d,"metadata":m,"distance":dist} for d,m,dist in zip(r["documents"][0],r["metadatas"][0],r["distances"][0])]

def query_mmr(nid,q,k=4,fetch=12,lambda_mult=.65):
    c=collection(nid); emb=model().encode([q],normalize_embeddings=True).tolist()
    if c.count()==0:return []
    r=c.query(query_embeddings=emb,n_results=min(fetch,c.count()),include=["documents","metadatas","embeddings","distances"])
    docs=r["documents"][0]; metas=r["metadatas"][0]; embs=r["embeddings"][0]
    import numpy as np
    E=np.array(embs); qv=np.array(emb[0]); sims=E@qv
    selected=[]; remaining=list(range(len(docs)))
    while remaining and len(selected)<min(k,len(docs)):
        if not selected: idx=max(remaining,key=lambda i:sims[i])
        else:
            idx=max(remaining,key=lambda i:lambda_mult*sims[i]-(1-lambda_mult)*max(float(E[i]@E[j]) for j in selected))
        selected.append(idx); remaining.remove(idx)
    return [{"text":docs[i],"metadata":metas[i],"distance":float(1-sims[i])} for i in selected]
