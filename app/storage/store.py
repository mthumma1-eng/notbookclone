import os, shutil, uuid
from app.config import DATA_DIR, STORAGE_DIR
from app.storage import db

def notebook_dir(nid):
    p=os.path.join(DATA_DIR,nid); os.makedirs(os.path.join(p,"sources"),exist_ok=True); os.makedirs(os.path.join(p,"artifacts"),exist_ok=True); return p

def save_uploaded(nid, path, original_name):
    ext=os.path.splitext(original_name)[1].lower(); out=os.path.join(notebook_dir(nid),"sources",f"{uuid.uuid4().hex}{ext}")
    shutil.copy2(path,out); return out

def artifact_path(nid, kind):
    return os.path.join(notebook_dir(nid),"artifacts",f"{kind}_{uuid.uuid4().hex[:10]}.md")
