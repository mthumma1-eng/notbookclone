import json, os, sqlite3
from datetime import datetime, timezone
from app.config import STORAGE_DIR

DB_PATH = os.path.join(STORAGE_DIR, "notebooks.db")

def now(): return datetime.now(timezone.utc).isoformat()

def conn():
    c = sqlite3.connect(DB_PATH)
    c.execute("PRAGMA foreign_keys=ON")
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with conn() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS notebooks(
            id TEXT PRIMARY KEY, name TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sources(
            id TEXT PRIMARY KEY, notebook_id TEXT NOT NULL, name TEXT NOT NULL, source_type TEXT NOT NULL,
            location TEXT, created_at TEXT NOT NULL, FOREIGN KEY(notebook_id) REFERENCES notebooks(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT, notebook_id TEXT NOT NULL, role TEXT NOT NULL,
            content TEXT NOT NULL, citations TEXT, created_at TEXT NOT NULL,
            FOREIGN KEY(notebook_id) REFERENCES notebooks(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS artifacts(
            id TEXT PRIMARY KEY, notebook_id TEXT NOT NULL, kind TEXT NOT NULL, title TEXT NOT NULL,
            path TEXT NOT NULL, created_at TEXT NOT NULL, FOREIGN KEY(notebook_id) REFERENCES notebooks(id) ON DELETE CASCADE
        );
        ''')

def create_notebook(nid, name):
    with conn() as c: c.execute("INSERT INTO notebooks VALUES(?,?,?,?)", (nid,name,now(),now()))

def list_notebooks():
    with conn() as c: return [dict(r) for r in c.execute("SELECT * FROM notebooks ORDER BY created_at")]

def rename_notebook(nid,name):
    with conn() as c: c.execute("UPDATE notebooks SET name=?,updated_at=? WHERE id=?",(name,now(),nid))

def delete_notebook(nid):
    with conn() as c:
        c.execute("DELETE FROM notebooks WHERE id=?",(nid,))

def add_source(sid,nid,name,source_type,location):
    with conn() as c: c.execute("INSERT INTO sources VALUES(?,?,?,?,?,?)",(sid,nid,name,source_type,location,now()))

def list_sources(nid):
    with conn() as c: return [dict(r) for r in c.execute("SELECT * FROM sources WHERE notebook_id=? ORDER BY created_at",(nid,))]

def add_message(nid,role,content,citations=None):
    with conn() as c: c.execute("INSERT INTO messages(notebook_id,role,content,citations,created_at) VALUES(?,?,?,?,?)",(nid,role,content,json.dumps(citations or []),now()))

def list_messages(nid):
    with conn() as c:
        rows=c.execute("SELECT * FROM messages WHERE notebook_id=? ORDER BY id",(nid,)).fetchall()
        return [(r["role"],r["content"],json.loads(r["citations"] or "[]")) for r in rows]

def add_artifact(aid,nid,kind,title,path):
    with conn() as c: c.execute("INSERT INTO artifacts VALUES(?,?,?,?,?,?)",(aid,nid,kind,title,path,now()))

def list_artifacts(nid):
    with conn() as c: return [dict(r) for r in c.execute("SELECT * FROM artifacts WHERE notebook_id=? ORDER BY created_at DESC",(nid,))]
