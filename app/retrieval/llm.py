from openai import OpenAI
from app.config import LLM_API_KEY,LLM_BASE_URL,LLM_MODEL


def answer(question,chunks):
    if not LLM_API_KEY: raise RuntimeError("LLM_API_KEY is not configured. Add it to your environment/secrets.")
    client=OpenAI(api_key=LLM_API_KEY,base_url=LLM_BASE_URL)
    context="\n\n".join(f"SOURCE {i+1}: {x['text']}" for i,x in enumerate(chunks))
    prompt=f'''You are a grounded research assistant. Answer ONLY from the provided source excerpts. If the sources do not contain the answer, say that the notebook sources do not provide enough information. Be concise but useful. Cite supporting sources inline as [Source 1], [Source 2], etc.\n\nSOURCES:\n{context}\n\nQUESTION:\n{question}'''
    r=client.chat.completions.create(model=LLM_MODEL,messages=[{"role":"system","content":"You answer questions using only supplied evidence."},{"role":"user","content":prompt}],temperature=.2)
    return r.choices[0].message.content

def generate(prompt):
    if not LLM_API_KEY: raise RuntimeError("LLM_API_KEY is not configured.")
    client=OpenAI(api_key=LLM_API_KEY,base_url=LLM_BASE_URL)
    r=client.chat.completions.create(model=LLM_MODEL,messages=[{"role":"user","content":prompt}],temperature=.25)
    return r.choices[0].message.content
