import json

from config import DISCOVERED_JOBS_PATH
from sources.providers.zurich import discover as discover_zurich
from sources.providers.generali import discover as discover_generali
from sources.providers.swissre import discover as discover_swissre


def main():
    discovered_jobs = []

    discovered_jobs.extend(discover_zurich())
    discovered_jobs.extend(discover_generali())
    discovered_jobs.extend(discover_swissre())

    with open(DISCOVERED_JOBS_PATH, "w", encoding="utf-8") as f:
        json.dump(discovered_jobs, f, ensure_ascii=False, indent=2)

    print(f"Hotovo. Uloženo {len(discovered_jobs)} pozic do {DISCOVERED_JOBS_PATH}.")


if __name__ == "__main__":
    main()