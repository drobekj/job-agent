import json
from pathlib import Path
from urllib.parse import urlparse

from config import (
    DATABASE_PATH,
    JOBS_JSON_PATH,
    DISCOVERED_JOBS_PATH,
    WEB_JOBS_PATH,
)
from db import init_db, job_exists


JSON_FILES_TO_CHECK = [
    JOBS_JSON_PATH,
    DISCOVERED_JOBS_PATH,
    WEB_JOBS_PATH,
]


def is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def load_json_list(path: str) -> list[dict]:
    file_path = Path(path)

    if not file_path.exists():
        return []

    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON list")

    return data


def save_json_list(path: str, data: list[dict]) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def url_exists_in_json(url: str, path: str) -> bool:
    jobs = load_json_list(path)

    return any(
        job.get("url") == url
        for job in jobs
    )


def url_exists_in_any_json(url: str) -> bool:
    return any(
        url_exists_in_json(url, path)
        for path in JSON_FILES_TO_CHECK
    )


def url_exists_in_db(url: str) -> bool:
    conn = init_db(DATABASE_PATH)

    try:
        return (
            job_exists(conn, url)
            or job_exists(conn, url + "mock_app")
        )
    finally:
        conn.close()

def normalize_url(url: str) -> str:
    return url.strip().rstrip("/")

def validate_new_web_job_url(url: str) -> None:
    url = normalize_url(url)
    if not is_valid_url(url):
        raise ValueError("Invalid URL")

    if url_exists_in_any_json(url):
        raise ValueError("URL already exists in JSON files")

    if url_exists_in_db(url):
        raise ValueError("URL already exists in database")


def append_web_job(url: str, allow_existing_web: bool = False) -> dict:
    url = normalize_url(url)
    if not is_valid_url(url):
        raise ValueError("Invalid URL")

    if url_exists_in_json(url, JOBS_JSON_PATH):
        raise ValueError("URL already exists in jobs.json")

    if url_exists_in_json(url, DISCOVERED_JOBS_PATH):
        raise ValueError("URL already exists in discovered_jobs.json")

    if url_exists_in_json(url, WEB_JOBS_PATH):
        if allow_existing_web:
            return {
                "url": url,
                "source_id": "web",
                "source_type": "admin_insert",
                "private_note": "",
            }

        raise ValueError("URL already exists in web_jobs.json")

    jobs = load_json_list(WEB_JOBS_PATH)

    job = {
        "url": url,
        "source_id": "web",
        "source_type": "admin_insert",
        "private_note": "",
    }

    jobs.append(job)
    save_json_list(WEB_JOBS_PATH, jobs)

    return job

