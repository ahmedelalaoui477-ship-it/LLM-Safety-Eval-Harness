import csv
import json
import os
from datetime import datetime, timezone

ITEMS = "logs/blind_items.jsonl"
LABELS = "labeling/labels.csv"
VALID = ["R", "P", "C", "CO", "E", "ERR", "X"]
FIELDS = ["blind_id", "label", "note", "timestamp_utc"]


def load_items():
    items = []
    with open(ITEMS, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def load_labels():
    if not os.path.exists(LABELS):
        return []
    with open(LABELS, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def save_labels(rows):
    with open(LABELS, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main():
    os.makedirs("labeling", exist_ok=True)
    items = load_items()
    rows = load_labels()
    total = len(items)

    while True:
        done = {r["blind_id"] for r in rows}
        todo = [it for it in items if it["blind_id"] not in done]
        if not todo:
            print("All items labeled.")
            break

        it = todo[0]
        os.system("clear")
        print(f"[{len(done) + 1}/{total}] {it['blind_id']} | "
              f"prompt {it['prompt_id']} | finish_reason = {it['finish_reason']}")
        print("\n=== PROMPT ===")
        print(it["prompt_text"])
        print("\n=== RESPONSE ===")
        print(it["content"] if it["content"].strip() else "[EMPTY CONTENT]")
        print("\n" + "-" * 60)

        cmd = input("Label (R P C CO E ERR X) | u = undo | q = quit: ").strip().upper()

        if cmd == "Q":
            break
        if cmd == "U":
            if rows:
                removed = rows.pop()
                save_labels(rows)
                print("Removed label of", removed["blind_id"])
                input("Press Enter...")
            continue
        if cmd not in VALID:
            input("Not a valid label. Press Enter...")
            continue

        note = input("Note (optional; no harmful text): ").strip()
        rows.append({
            "blind_id": it["blind_id"],
            "label": cmd,
            "note": note,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        })
        save_labels(rows)

    print(f"Labeled so far: {len(rows)} / {total}")


if __name__ == "__main__":
    main()