import os, uuid
from app.storage.store import artifact_path
from app.storage.db import add_artifact
from app.retrieval.llm import generate

def context_from_sources(sources):
    return "\n\n".join(f"SOURCE: {s['name']}\n{s.get('content','')}" for s in sources)

def make_artifact(nid,kind,title,sources):
    # Use extracted text persisted in the ingestion layer; sources passed here contain a bounded context.
    ctx="\n\n".join(f"SOURCE {i+1} ({s['name']}):\n{s['text']}" for i,s in enumerate(sources))
    if kind=="report":
        prompt=f"Create a well-structured Markdown research report grounded only in these notebook excerpts. Include title, executive summary, key findings, detailed sections, and conclusion. Mention source names where relevant.\n\n{ctx}"
    else:
        prompt=f"Create a Markdown study quiz with 10 questions based only on these notebook excerpts. Use a mix of conceptual and factual questions. End with a clearly labeled Answer Key.\n\n{ctx}"
    content=generate(prompt)
    path=artifact_path(nid,kind); open(path,"w",encoding="utf-8").write(content)
    aid=uuid.uuid4().hex; add_artifact(aid,nid,kind,title,path)
    return path,content
