"""Run a small reproducible retrieval comparison.
Usage: python -m evaluation.evaluate <notebook_id> "question 1" "question 2"
"""
import csv,sys,time
from app.retrieval.vector import query_basic,query_mmr

def run(nid,questions):
    rows=[]
    for q in questions:
        for name,fn in [("Vector Similarity",query_basic),("MMR / Diversity",query_mmr)]:
            t=time.perf_counter(); chunks=fn(nid,q,4); elapsed=time.perf_counter()-t
            rows.append({"question":q,"method":name,"retrieved_chunks":len(chunks),"response_time_sec":round(elapsed,4),"chunks":" || ".join(x['text'][:350].replace('\n',' ') for x in chunks),"answer_quality":"Fill after human review (Poor/Fair/Good/Excellent)"})
    with open("evaluation/results.csv","w",newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    print("Wrote evaluation/results.csv")

if __name__=="__main__":
    if len(sys.argv)<3: raise SystemExit('Usage: python -m evaluation.evaluate NOTEBOOK_ID "Question 1" "Question 2"')
    run(sys.argv[1],sys.argv[2:])
