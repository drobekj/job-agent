import json

import requests
import trafilatura
from bs4 import BeautifulSoup


def fetch_job_page(url: str) -> dict:
    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0",
            },
            timeout=20,
        )

        response.raise_for_status()

        html = response.text

        soup = BeautifulSoup(html, "html.parser")

        page_title = ""
        og_title = ""
        json_ld = []

        if soup.title and soup.title.string:
            page_title = soup.title.string.strip()

        og_tag = soup.find(
            "meta",
            property="og:title",
        )

        if og_tag:
            og_title = og_tag.get("content", "").strip()

        for tag in soup.find_all(
            "script",
            type="application/ld+json",
        ):
            try:
                data = json.loads(tag.string)
                json_ld.append(data)
            except Exception:
                pass

        text = trafilatura.extract(html) or ""

        return {
            "text": text,
            "page_title": page_title,
            "og_title": og_title,
            "json_ld": json_ld,
        }

    except Exception as e:
        print(f"Fetch error for {url}: {e}")

        return {
            "text": "",
            "page_title": "",
            "og_title": "",
            "json_ld": [],
        }


def fetch_job_text(url: str) -> str:
    page = fetch_job_page(url)
    return page["text"]