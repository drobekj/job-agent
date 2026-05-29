import json

from sources.providers.zurich import discover


LABELS_FILE = "tests/provider_labels/zurich.json"


def main():

    with open(LABELS_FILE, "r", encoding="utf-8") as f:
        labels = json.load(f)

    discovered = {
        job["url"]
        for job in discover()
    }

    tp = 0
    fp = 0
    fn = 0

    print("\n=== RESULTS ===\n")

    for url, label in labels.items():

        if label == "MAYBE":
            continue

        expected_keep = (label == "KEEP")
        actual_keep = (url in discovered)

        if expected_keep and actual_keep:
            tp += 1
            result = "TP"

        elif (not expected_keep) and actual_keep:
            fp += 1
            result = "FP"

        elif expected_keep and (not actual_keep):
            fn += 1
            result = "FN"

        else:
            result = "TN"

        print(
            f"{result:>2} | "
            f"{label:<5} | "
            f"{url}"
        )

    print("\n=== SUMMARY ===\n")

    print(f"TP = {tp}")
    print(f"FP = {fp}")
    print(f"FN = {fn}")

    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0

    print(f"Precision = {precision:.3f}")
    print(f"Recall    = {recall:.3f}")


if __name__ == "__main__":
    main()