import re

def chunk_text(text,size=900,overlap=150):
    text=re.sub(r"\n{3,}","\n\n",text).strip()
    chunks=[]; start=0
    while start < len(text):
        end=min(len(text),start+size)
        if end < len(text):
            boundary=max(text.rfind("\n\n",start,end),text.rfind(". ",start,end),text.rfind(" ",start,end))
            if boundary>start+size//2: end=boundary+1
        chunk=text[start:end].strip()
        if chunk: chunks.append(chunk)
        if end>=len(text): break
        start=max(end-overlap,start+1)
    return chunks
