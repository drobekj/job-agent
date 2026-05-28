from config import (INPUT_FILE, OUTPUT_DIR, DATABASE_PATH)
from fetcher import fetch_job_text
from evaluator import evaluate_job
from db import init_db, save_evaluation
from prompts import build_prompt
import json

prompt = build_prompt()

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    jobs = json.load(f)

conn = init_db(DATABASE_PATH)
all_markdown = ""

for job in jobs:
    job_url = job["url"]
    private_note = job.get("private_note", "")
    job_text = fetch_job_text(job_url)
    #markdown, row = evaluate_job(job_url, prompt, job_text, private_note)
    markdown="tady je markdown"
    title="model dev"#row["title"],
    company="baic"#row["company"],
    location="braslav"#row["location"],
    
    verdict="take it"#row["verdict"]
    final_score=44#row["final_score"]
    is_shortlisted = int(
        final_score >= 50
        or verdict == "Apply"
    )
    save_evaluation(
        conn=conn,
        url="hh",#job_url,
        title=title,#row["title"],
        company=company,#row["company"],
        location=location,#row["location"],
        final_score=final_score,#row["final_score"],
        verdict=verdict,#row["verdict"],
        salary_estimate_czk=79999,#row["salary_estimate_czk"],
        is_shortlisted=is_shortlisted,
        markdown_report=markdown
    )
conn.close()

print("\nHotovo.")