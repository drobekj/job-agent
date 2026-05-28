import requests
import trafilatura


def fetch_job_text(url: str) -> str:
    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
            timeout=20
        )

        response.raise_for_status()

        text = trafilatura.extract(response.text)

        if text:
            return text

        return ""

    except Exception as e:
        print(f"Fetch error for {url}: {e}")
        return ""
