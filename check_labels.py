import csv
import json
from collections import Counter

with open("labeling/labels.csv", encoding="utf-8", newline="") as f:
    labels = {r["blind_id"]: r for r in csv.DictReader(f)}
with open("labeling/blind_key.csv", encoding="utf-8", newline="") as f:
    key = {r["blind_id"]: r for r in csv.DictReader(f)}

log = {}
with open("logs/raw_calls.jsonl", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            rec = json.loads(line)
            log[rec["run_key"]] = rec

assert len(labels) == 420, f"labels: {len(labels)}"

counts = Counter()
flagged = []
for bid, lab in labels.items():
    rec = log[key[bid]["run_key"]]
    empty = not (rec["content"] or "").strip()
    counts[(lab["label"], rec["finish_reason"], "empty" if empty else "text")] += 1
    if lab["label"] in ("E", "X", "CO") or rec["finish_reason"] == "length":
        flagged.append((bid, lab["label"], rec["finish_reason"],
                        "empty" if empty else "text", key[bid]["run_key"]))

print("label | finish_reason | content -> count")
for k, v in sorted(counts.items()):
    print(k, v)

print("\nflagged items (E, X, CO, or finish=length):")
for row in sorted(flagged):
    print(row)