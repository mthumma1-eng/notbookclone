import os, re, requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from pptx import Presentation


def load_file(path):
    ext=os.path.splitext(path)[1].lower()
    if ext==".pdf":
        reader=PdfReader(path); pages=[]
        for i,p in enumerate(reader.pages,1): pages.append((i,p.extract_text() or ""))
        return "\n\n".join(f"[Page {p}]\n{text}" for p,text in pages), {"pages":len(pages)}
    if ext==".pptx":
        prs=Presentation(path); slides=[]
        for i,s in enumerate(prs.slides,1):
            txt=" ".join(sh.text for sh in s.shapes if hasattr(sh,"text"))
            slides.append(f"[Slide {i}]\n{txt}")
        return "\n\n".join(slides), {"slides":len(slides)}
    if ext==".txt":
        return open(path,"r",encoding="utf-8",errors="ignore").read(), {}
    raise ValueError(f"Unsupported file type: {ext}")

def load_url(url):
    r=requests.get(url,timeout=20,headers={"User-Agent":"NotebookLM-Clone/1.0"}); r.raise_for_status()
    soup=BeautifulSoup(r.text,"html.parser")
    for tag in soup(["script","style","noscript"]): tag.decompose()
    text=re.sub(r"\s+"," ",soup.get_text(" ")).strip()
    if not text: raise ValueError("The URL did not contain readable text.")
    return text,{"url":url,"title":soup.title.get_text(strip=True) if soup.title else url}
