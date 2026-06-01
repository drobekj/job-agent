from sources.manual_json import load_manual_jobs
from sources.discovered_json import load_discovered_jobs


def normalize_job(job: dict, source_file: str) -> dict:
    normalized = dict(job)

    normalized["source_file"] = source_file
    normalized.setdefault("private_note", "")

    return normalized


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