import json
import os

from config import DISCOVERED_JOBS_PATH
from sources.discovered_jobs import normalize_discovered_job


def load_discovered_jobs():

    if not os.path.exists(DISCOVERED_JOBS_PATH):
        return []

    with open(DISCOVERED_JOBS_PATH, "r", encoding="utf-8") as f:
        jobs = json.load(f)

    return [
        normalize_discovered_job(
            url=job["url"],
            source_id=job.get("source_id", "discovered"),
            source_type=job.get("source_type", "unknown"),
            private_note=job.get("private_note", ""),
            title=job.get("title", ""),
            location=job.get("location", ""),
            company=job.get("company", ""),
        )
        for job in jobs
    ]