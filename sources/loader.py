from pathlib import Path

from sources.manual_json import load_manual_jobs
from sources.discovered_json import load_discovered_jobs
from sources.discovered_jobs import normalize_discovered_job


def normalize_job(job: dict, source_file: str) -> dict:
    normalized = dict(job)
    normalized["source_file"] = source_file
    normalized.setdefault("private_note", "")
    return normalized


def load_jobs_from_json(path: str):
    import json

    file_path = Path(path)

    if not file_path.exists():
        return []

    with file_path.open("r", encoding="utf-8") as f:
        jobs = json.load(f)

    source_file = file_path.name

    return [
        normalize_job(
            normalize_discovered_job(
                url=job["url"],
                source_id=job.get("source_id", source_file.replace(".json", "")),
                source_type=job.get("source_type", "json_input"),
                private_note=job.get("private_note", ""),
                title=job.get("title", ""),
                location=job.get("location", ""),
                company=job.get("company", ""),
            ),
            source_file,
        )
        for job in jobs
    ]


def load_jobs_to_process():
    jobs = []

    manual_jobs = load_manual_jobs()
    discovered_jobs = load_discovered_jobs()

    jobs.extend(
        normalize_job(job, "jobs.json")
        for job in manual_jobs
    )

    jobs.extend(
        normalize_job(job, "discovered_jobs.json")
        for job in discovered_jobs
    )

    return jobs