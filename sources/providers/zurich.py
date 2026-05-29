import html
import re
from urllib.parse import unquote

import requests

from fetcher import fetch_job_text
from sources.discovered_jobs import normalize_discovered_job


ZURICH_URL = "https://www.careers.zurich.com/search/?q=actuarial"

LOCATION_PATTERNS = [
    r"\bBratislava\b",
    r"\bSlovakia\b",
    r"\bSK\s*-",
    r"\bZürich\b",
    r"\bSwitzerland\b",
    r"\bCH\s*-",
    r"\bSwindon\b",
    r"\bUnited Kingdom\b",
    r"\bGB\s*-",
    r"\bVienna\b",
    r"\bAustria\b",
    r"\bAT\s*-",
]

URL_FALLBACK_PATTERNS = [
    r"\bBratislava\b",
    r"\bZürich\b",
    r"\bSwindon\b",
    r"\bVienna\b",
    r"\bLondon\b",
]


def get_job_slug(url):
    decoded_url = html.unescape(unquote(url))
    match = re.search(r"/job/([^/]+)/", decoded_url)
    return match.group(1) if match else ""


def extract_location(text):

    match = re.search(
        r"Location\(s\):\s*(.+)",
        text,
        re.IGNORECASE,
    )

    if match:
        return match.group(1).strip()

    known_locations = [
        "Bratislava",
        "Zürich",
        "Zurich",
        "Swindon",
        "Vienna",
        "London",
        "Toronto",
        "Hong Kong",
        "Kuala Lumpur",
        "Jakarta",
        "Montréal",
        "Schaumburg",
    ]

    for location in known_locations:
        if location.lower() in text.lower():
            return location

    return ""

def extract_title(text):
    lines = text.splitlines()

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if len(line) < 10:
            continue

        return line

    return ""

def matches_any_pattern(value, patterns):
    return any(
        re.search(pattern, value, re.IGNORECASE)
        for pattern in patterns
    )


def is_relevant_job(url):
    text = fetch_job_text(url)

    if not text:
        print(f"[DROP] no text | {url}")
        return False

    location = extract_location(text)

    if location:
        relevant = matches_any_pattern(location, LOCATION_PATTERNS)
        #print(f"[{'KEEP' if relevant else 'DROP'}] location='{location}' | {url}")
        return relevant

    slug = get_job_slug(url)
    relevant = matches_any_pattern(slug, URL_FALLBACK_PATTERNS)

    #print(f"[{'KEEP' if relevant else 'DROP'}] url_fallback_slug='{slug}' | {url}")
    return relevant


def discover():
    response = requests.get(
        ZURICH_URL,
        timeout=20,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    response.raise_for_status()

    urls = sorted(set(
        "https://www.careers.zurich.com" + match
        for match in re.findall(r'href="(/job/[^"]+)"', response.text)
    ))

    filtered_urls = []

    for url in urls:
        if is_relevant_job(url):
            filtered_urls.append(url)

    jobs = []

    for url in filtered_urls:
        text = fetch_job_text(url)
        jobs.append(
            normalize_discovered_job(
                url=url,
                source_id="zurich",
                source_type="company_career",
                private_note="",
                title=extract_title(text) if text else "",
                location=extract_location(text) if text else "",
                company="Zurich",
            )
        )

    return jobs