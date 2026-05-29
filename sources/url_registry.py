import json
import os

from config import JOBS_JSON_PATH
from config import DISCOVERED_JOBS_PATH


def get_known_urls():

    urls = set()

    for path in [JOBS_JSON_PATH, DISCOVERED_JOBS_PATH]:

        if not os.path.exists(path):
            continue

        with open(path, "r", encoding="utf-8") as f:
            jobs = json.load(f)

        for job in jobs:
            urls.add(job["url"])

    return urls