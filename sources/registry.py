import json
from config import SOURCES_JSON_PATH


def load_sources():
    with open(SOURCES_JSON_PATH, "r", encoding="utf-8") as f:
        sources = json.load(f)

    return [
        source
        for source in sources
        if source.get("enabled", True)
    ]