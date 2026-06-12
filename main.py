import argparse

from config import DATABASE_PATH
from sources.loader import (
    load_jobs_to_process,
    load_jobs_from_json,
)
from fetcher import fetch_job_page
from evaluator import evaluate_job
from db import (
    init_db,
    save_evaluation,
    job_exists,
    has_ai_evaluation,
    mark_job_as_repeated,
)
from prompts import build_prompt
from web_jobs import normalize_url


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--source",
        help="Path to json file with jobs",
    )

    parser.add_argument(
        "--mode",
        choices=["prepare", "evaluate"],
        default="evaluate",
    )

    return parser.parse_args()


def db_url_for_mode(job_url: str, mode: str) -> str:
    if mode == "prepare":
        return job_url + "mock_app"

    return job_url


def main():
    args = parse_args()

    use_real_api = args.mode == "evaluate"

    if args.source:
        jobs = load_jobs_from_json(args.source)
    else:
        jobs = load_jobs_to_process()

    prompt = build_prompt()

    conn = init_db(DATABASE_PATH)

    for job in jobs:
        job_url = normalize_url(job["url"])
        expected_db_url = db_url_for_mode(job_url, args.mode)
        if args.mode == "evaluate" and job_exists(conn, job_url):
            if has_ai_evaluation(conn, job_url):
                mark_job_as_repeated(conn, job_url)
                print(f"SKIP (AI evaluation already exists, marked renew): {job_url}")
                continue
        if args.mode == "prepare" and job_exists(conn, expected_db_url):
            print(f"SKIP (already exists): {expected_db_url}")
            continue

        source_file = job.get("source_file", "unknown")
        private_note = job.get("private_note", "")

        try:
            page = fetch_job_page(job_url)

            job_text = page["text"]
            page_title = page["page_title"]
            og_title = page["og_title"]
            json_ld = page["json_ld"]
            
            markdown, row = evaluate_job(
                url=job_url,
                prompt=prompt,
                job_text=job_text,
                private_note=private_note,
                use_real_api=use_real_api,
                page_title=page_title,
                og_title=og_title,
                json_ld=json_ld,
            )

            db_url = job_url + row["mock"]

            save_evaluation(
                conn=conn,
                url=db_url,
                source_file=source_file,
                title=row["title"],
                company=row["company"],
                location=row["location"],
                final_score=row["final_score"],
                verdict=row["verdict"],
                salary_estimate_czk=row["salary_estimate_czk"],
                status="new",
                private_note=private_note,
                markdown_report=markdown,
            )

            print(f"OK: {job_url}")

        except Exception as e:
            print(f"ERROR: {job_url}")
            print(e)

    conn.close()

    print("\nHotovo.")


if __name__ == "__main__":
    main()