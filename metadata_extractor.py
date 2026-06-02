import re


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def find_jobposting(data):
    if isinstance(data, dict):

        if data.get("@type") == "JobPosting":
            return data

        for value in data.values():
            result = find_jobposting(value)

            if result:
                return result

    elif isinstance(data, list):

        for item in data:
            result = find_jobposting(item)

            if result:
                return result

    return None


def extract_from_jobposting(jobposting: dict) -> dict:

    title = clean_text(
        jobposting.get("title", "")
    )

    company = ""

    org = jobposting.get(
        "hiringOrganization",
        {}
    )

    if isinstance(org, dict):
        company = clean_text(
            org.get("name", "")
        )

    location = ""

    job_location = jobposting.get(
        "jobLocation",
        {}
    )

    if isinstance(job_location, list):
        job_location = (
            job_location[0]
            if job_location
            else {}
        )

    if isinstance(job_location, dict):

        address = job_location.get(
            "address",
            {}
        )

        if isinstance(address, dict):

            parts = [
                address.get(
                    "addressLocality",
                    "",
                ),
                address.get(
                    "addressRegion",
                    "",
                ),
                address.get(
                    "addressCountry",
                    "",
                ),
            ]

            location = ", ".join(
                clean_text(x)
                for x in parts
                if clean_text(x)
            )

    return {
        "title": title,
        "company": company,
        "location": location,
    }


def split_title_company(
    page_title: str,
) -> tuple[str, str]:

    page_title = clean_text(page_title)

    if not page_title:
        return "", ""

    separators = [
        " | ",
        " - ",
        " – ",
        " — ",
        " at ",
        " @ ",
    ]

    for separator in separators:
        if separator in page_title:
            left, right = page_title.split(
                separator,
                1,
            )

            return (
                clean_text(left),
                clean_text(right),
            )

    return page_title, ""


def extract_location_from_text(
    job_text: str,
) -> str:

    lines = [
        clean_text(line)
        for line in job_text.splitlines()
        if clean_text(line)
    ]

    location_keywords = [
        "Prague",
        "Praha",
        "Bratislava",
        "Vienna",
        "Wien",
        "Ostrava",
        "Brno",
        "Remote",
        "Hybrid",
    ]

    for line in lines[:40]:

        for keyword in location_keywords:

            if keyword.lower() in line.lower():
                return line[:200]

    return ""


def extract_job_metadata(
    url: str,
    page_title: str,
    og_title: str,
    json_ld: list,
    job_text: str,
) -> dict:

    for item in json_ld:

        jobposting = find_jobposting(item)

        if jobposting:

            metadata = extract_from_jobposting(
                jobposting
            )

            if metadata["title"]:
                return metadata

    linkedin_match = re.search(
        r"^(.*?) hiring (.*?) in (.*?) \| LinkedIn$",
        page_title,
        flags=re.IGNORECASE,
    )

    if linkedin_match:

        return {
            "company": clean_text(
                linkedin_match.group(1)
            ),
            "title": clean_text(
                linkedin_match.group(2)
            ),
            "location": clean_text(
                linkedin_match.group(3)
            ),
        }

    title, company = split_title_company(
        og_title or page_title
    )

    if not title:

        lines = [
            clean_text(line)
            for line in job_text.splitlines()
            if clean_text(line)
        ]

        if lines:
            title = lines[0][:200]

    location = extract_location_from_text(
        job_text
    )

    return {
        "title": title,
        "company": company,
        "location": location,
    }