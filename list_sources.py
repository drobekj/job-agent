from sources.registry import load_sources


sources = load_sources()

for source in sources:
    print(
        f"[{source['priority']}] "
        f"{source['id']} | "
        f"{source['type']} | "
        f"{source['url']}"
    )