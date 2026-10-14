import os, gradio as gr
from app import service

service.ensure_default()

CSS='''
#title { text-align:center; }
.small { font-size: 0.9rem; opacity: .8; }
''' 

def nb_choices(): return [(n['name'],n['id']) for n in service.notebooks()]
def selected_sources(nid): return service.sources_md(nid)
def selected_history(nid): return service.history(nid)

def create_nb(name):
    nid=service.create(name); return gr.update(choices=nb_choices(),value=nid), "Created notebook."
def rename_nb(nid,name):
    if not nid: return gr.update(choices=nb_choices()), "Select a notebook."
    service.rename(nid,name); return gr.update(choices=nb_choices(),value=nid), "Renamed notebook."
def delete_nb(nid):
    if not nid:return gr.update(choices=nb_choices()),"Select a notebook."
    service.delete(nid); choices=nb_choices(); return gr.update(choices=choices,value=(choices[0][1] if choices else None)),"Notebook deleted."

def upload(nid,file):
    try:return service.ingest_file(nid,file),service.sources_md(nid)
    except Exception as e:return f"❌ {e}",service.sources_md(nid)
def add_url(nid,url):
    try:return service.ingest_web(nid,url),service.sources_md(nid)
    except Exception as e:return f"❌ {e}",service.sources_md(nid)

def ask(nid,q,method,chat):
    try:
        ans,cits,elapsed=service.chat(nid,q,method); new=service.history(nid)
        citation_md="\n".join(f"- {x}" for x in cits)
        return new,"**Citations**\n"+citation_md+f"\n\n*Retrieval time: {elapsed:.3f}s*",""
    except Exception as e:return chat,f"❌ {e}",q

def make_art(nid,kind):
    try:
        path,content=service.artifact(nid,kind); return content,path
    except Exception as e:return f"❌ {e}",None

with gr.Blocks(title="NotebookLM Clone",css=CSS,theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 📚 NotebookLM / Gemini Notebook Clone",elem_id="title")
    gr.Markdown("Create notebooks, ground answers in your sources, and generate study artifacts.",elem_classes="small")
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Notebooks")
            _initial_choices=nb_choices()
            nb=gr.Dropdown(choices=_initial_choices,value=(_initial_choices[0][1] if _initial_choices else None),label="Current notebook",interactive=True)
            new_name=gr.Textbox(label="New notebook name",placeholder="e.g. Machine Learning")
            with gr.Row():
                create=gr.Button("＋ Create")
                rename=gr.Button("Rename")
                delete=gr.Button("Delete",variant="stop")
            status=gr.Markdown()
            gr.Markdown("### Sources")
            file=gr.File(label="Upload PDF / PPTX / TXT",file_types=[".pdf",".pptx",".txt"],type="filepath")
            upload_btn=gr.Button("Index File",variant="primary")
            url=gr.Textbox(label="Web URL",placeholder="https://example.com/article")
            url_btn=gr.Button("Index URL")
            sources=gr.Markdown()
            gr.Markdown("### Artifacts")
            report_btn=gr.Button("Generate Report")
            quiz_btn=gr.Button("Generate Quiz + Answer Key")
            artifact_preview=gr.Markdown()
            artifact_file=gr.File(label="Download artifact")
        with gr.Column(scale=2):
            gr.Markdown("### RAG Chat")
            method=gr.Radio(["Vector Similarity","MMR / Diversity Retrieval"],value="Vector Similarity",label="Retrieval approach")
            chat=gr.Chatbot(type="messages",label="Notebook conversation",height=470)
            with gr.Row():
                question=gr.Textbox(label="Question",placeholder="Ask something about your sources...",scale=5)
                ask_btn=gr.Button("Ask",variant="primary",scale=1)
            citations=gr.Markdown("Add a source and ask a question to see citations.")
            gr.Markdown("**Evaluation note:** MMR is implemented as the second retrieval approach; the evaluation script records retrieval time and retrieved chunks for representative questions.")

    nb.change(selected_sources,nb,sources)
    nb.change(selected_history,nb,chat)
    create.click(create_nb,new_name,[nb,status]).then(selected_sources,nb,sources)
    rename.click(rename_nb,[nb,new_name],[nb,status])
    delete.click(delete_nb,nb,[nb,status]).then(selected_sources,nb,sources).then(selected_history,nb,chat)
    upload_btn.click(upload,[nb,file],[status,sources])
    url_btn.click(add_url,[nb,url],[status,sources])
    ask_btn.click(ask,[nb,question,method,chat],[chat,citations,question])
    question.submit(ask,[nb,question,method,chat],[chat,citations,question])
    report_btn.click(lambda n:make_art(n,"report"),nb,[artifact_preview,artifact_file])
    quiz_btn.click(lambda n:make_art(n,"quiz"),nb,[artifact_preview,artifact_file])
    demo.load(selected_sources,nb,sources)

if __name__ == "__main__": demo.launch(server_name="0.0.0.0",server_port=int(os.getenv("PORT","7860")))
