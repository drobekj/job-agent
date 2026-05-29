import json
from config import JOBS_JSON_PATH
from sources.discovered_jobs import normalize_discovered_job


def load_manual_jobs():
    with open(JOBS_JSON_PATH, "r", encoding="utf-8") as f:
        jobs = json.load(f)

    return [
        normalize_discovered_job(
            url=job["url"],
            source_id=job.get("source_id", "manual"),
            source_type=job.get("source_type", "manual_input"),
            private_note=job.get("private_note", ""),
        )
        for job in jobs
    ]