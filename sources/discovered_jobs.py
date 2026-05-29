def normalize_discovered_job(
    url,
    source_id,
    source_type,
    private_note="",
    title="",
    location="",
    company="",
):
    return {
        "url": url,
        "source_id": source_id,
        "source_type": source_type,
        "private_note": private_note,
        "title": title,
        "location": location,
        "company": company,
    }