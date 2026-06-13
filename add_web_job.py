import argparse
import json
import subprocess
import sys
from pathlib import Path

from config import DATABASE_PATH
from db import (
    get_job_by_url,
    has_ai_evaluation,
    init_db,
)
from web_jobs import append_web_job, normalize_url


SINGLE_WEB_JOB_PATH = "inputs/_single_web_job.json"


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "mode",
        choices=["prepare", "evaluate"],
        help="Processing mode",
    )

    parser.add_argument(
        "url",
        help="Job URL to add into inputs/web_jobs.json",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force evaluation even if already evaluated",
    )

    return parser.parse_args()

def save_single_job_file(job: dict) -> None:
    file_path = Path(SINGLE_WEB_JOB_PATH)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as f:
        json.dump([job], f, ensure_ascii=False, indent=2)


def get_existing_state(url: str) -> str:
    conn = init_db(DATABASE_PATH)

    try:
        job = get_job_by_url(conn, url)

        if job is None:
            return "missing"

        if has_ai_evaluation(conn, url):
            return "evaluated"

        return "prepared"

    finally:
        conn.close()


def main():
    args = parse_args()

    normalized_url = normalize_url(args.url)
    existing_state = get_existing_state(normalized_url)

    if existing_state == "prepared" and args.mode == "prepare":
        print("already prepared")
        return

    if existing_state == "evaluated":
        if not (args.mode == "evaluate" and args.force):
            print("already evaluated")
            return
        
    job = append_web_job(
        normalized_url,
        allow_existing_web=args.mode == "evaluate",
    )

    save_single_job_file(job)

    command = [
        sys.executable,
        "main.py",
        "--source",
        SINGLE_WEB_JOB_PATH,
        "--mode",
        args.mode,
    ]

    if args.force:
        command.append("--force")

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(result.stderr or result.stdout)
        raise SystemExit(result.returncode)

    if existing_state == "prepared" and args.mode == "evaluate":
        print("prepared to evaluated")
    elif args.mode == "prepare":
        print("prepared")
    else:
        print("evaluated")


if __name__ == "__main__":
    main()