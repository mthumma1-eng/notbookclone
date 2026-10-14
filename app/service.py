import os, time, uuid, shutil
from app.storage import db
from app.storage.store import save_uploaded
from app.ingestion.loaders import load_file, load_url
from app.ingestion.chunker import chunk_text
from app.retrieval.vector import add_chunks, query_basic, query_mmr, collection, _client
from app.retrieval.llm import answer
from app.artifacts.generator import make_artifact
from app.config import CHUNK_SIZE,CHUNK_OVERLAP

def setup(): db.init_db()

def ensure_default():
    setup()
    if not db.list_notebooks(): db.create_notebook(uuid.uuid4().hex[:12],"My First Notebook")

def notebooks(): return db.list_notebooks()

def create(name):
    name=(name or "Untitled Notebook").strip(); nid=uuid.uuid4().hex[:12]; db.create_notebook(nid,name); return nid

def rename(nid,name): db.rename_notebook(nid,(name or "Untitled Notebook").strip())
def delete(nid):
    db.delete_notebook(nid)
    try: _client.delete_collection("nb_"+nid.replace("-","_"))
    except Exception: pass
    shutil.rmtree(os.path.join("data",nid), ignore_errors=True)

def ingest_file(nid,path):
    if not nid or not path: raise ValueError("Select a notebook and a file.")
    text,meta=load_file(path); chunks=chunk_text(text,CHUNK_SIZE,CHUNK_OVERLAP)
    sid=uuid.uuid4().hex[:12]; stored=save_uploaded(nid,path,os.path.basename(path))
    metadata=[{"source_id":sid,"source_name":os.path.basename(path),"source_type":os.path.splitext(path)[1].lower().replace(".",""),"location":stored,"chunk_index":i} for i in range(len(chunks))]
    add_chunks(nid,chunks,metadata); db.add_source(sid,nid,os.path.basename(path),os.path.splitext(path)[1].lower().replace('.',''),stored)
    return f"Added **{os.path.basename(path)}**: {len(chunks)} chunks indexed."

def ingest_web(nid,url):
    if not nid or not url: raise ValueError("Select a notebook and enter a URL.")
    text,meta=load_url(url); chunks=chunk_text(text,CHUNK_SIZE,CHUNK_OVERLAP)
    sid=uuid.uuid4().hex[:12]; name=meta.get("title") or url
    metadata=[{"source_id":sid,"source_name":name,"source_type":"url","location":url,"chunk_index":i} for i in range(len(chunks))]
    add_chunks(nid,chunks,metadata); db.add_source(sid,nid,name,"url",url)
    return f"Added **{name}**: {len(chunks)} chunks indexed."

def sources_md(nid):
    src=db.list_sources(nid)
    if not src:return "*No sources yet.*"
    return "\n".join(f"- **{s['name']}** · `{s['source_type']}`" for s in src)

def chat(nid,question,method="Vector Similarity"):
    if not question.strip(): return "",[] ,0
    start=time.perf_counter(); chunks=query_basic(nid,question) if method.startswith("Vector") else query_mmr(nid,question); elapsed=time.perf_counter()-start
    if not chunks: raise ValueError("This notebook has no indexed sources yet.")
    text=answer(question,chunks)
    citations=[f"[{i+1}] {c['metadata'].get('source_name','source')} — chunk {c['metadata'].get('chunk_index','?')}" for i,c in enumerate(chunks)]
    db.add_message(nid,"user",question,[]); db.add_message(nid,"assistant",text,citations)
    return text,citations,elapsed

def history(nid):
    out=[]
    for role,content,cits in db.list_messages(nid):
        if role=="user": out.append({"role":"user","content":content})
        else: out.append({"role":"assistant","content":content + ("\n\n**Sources:**\n"+"\n".join(cits) if cits else "")})
    return out

def artifact(nid,kind):
    # Retrieve a representative, broad context from the notebook vector store.
    c=collection(nid)
    if c.count()==0: raise ValueError("Add sources before generating artifacts.")
    r=c.get(include=["documents","metadatas"])
    pairs=[]
    seen=set()
    for doc,meta in zip(r["documents"],r["metadatas"]):
        name=meta.get("source_name","source")
        if name not in seen:
            seen.add(name)
        pairs.append({"name":name,"text":doc})
    # Limit context while preserving multiple sources.
    pairs=pairs[:30]
    return make_artifact(nid,kind,"Notebook Report" if kind=="report" else "Notebook Quiz",pairs)
