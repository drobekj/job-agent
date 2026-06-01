from config import DATABASE_PATH
from sources.loader import load_jobs_to_process
from fetcher import fetch_job_text
from evaluator import evaluate_job
from db import init_db, save_evaluation, job_exists
from prompts import build_prompt


prompt = build_prompt()
jobs = load_jobs_to_process()

conn = init_db(DATABASE_PATH)

for job in jobs:
    job_url = job["url"]

    if job_exists(conn, job_url):
        print(f"SKIP (already exists): {job_url}")
        continue

    source_file = job.get("source_file", "unknown")
    private_note = job.get("private_note", "")

    job_text = fetch_job_text(job_url)

    markdown, row = evaluate_job(
        job_url,
        prompt,
        job_text,
        private_note
    )

    is_shortlisted = int(
        row["final_score"] >= 40
        or row["verdict"] == "Apply"
    )

    job_url += row["mock"]

    status = "new"

    save_evaluation(
        conn=conn,
        url=job_url,
        source_file=source_file,
        title=row["title"],
        company=row["company"],
        location=row["location"],
        final_score=row["final_score"],
        verdict=row["verdict"],
        salary_estimate_czk=row["salary_estimate_czk"],
        is_shortlisted=is_shortlisted,
        status=status,
        private_note=private_note,
        markdown_report=markdown
    )

conn.close()

print("\nHotovo.")