from sources.manual_json import load_manual_jobs
from sources.discovered_json import load_discovered_jobs


def load_jobs_to_process():
    jobs = []

    jobs.extend(load_manual_jobs())
    jobs.extend(load_discovered_jobs())

    return jobs