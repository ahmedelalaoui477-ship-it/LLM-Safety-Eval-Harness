import csv
import json
import random

SEED = 42
CATEGORIES = [
    "Harassment/Discrimination",
    "Economic harm",
    "Disinformation",
    "Privacy",
    "Expert advice",
]
EXCLUDE = {}   # same idea as before: Behavior title -> written reason

with open("data/jbb_benign.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

rng = random.Random(SEED)
chosen = []
for category in CATEGORIES:
    candidates = [r for r in rows
                  if r["Category"] == category and r["Behavior"] not in EXCLUDE]
    chosen.append(rng.choice(candidates))

with open("prompts/bank_v1_benign_jbb.jsonl", "w", encoding="utf-8") as out:
    for i, r in enumerate(chosen, start=1):
        record = {
            "prompt_id": f"B{i:02d}",
            "source": "JBB-benign",
            "source_ref": f"{r['Behavior']} (Index {r['Index']}, from {r['Source']})",
            "category": r["Category"],
            "kind": "benign",
            "text": r["Goal"],
        }
        out.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(record["prompt_id"], "|", r["Category"], "|", r["Behavior"], "|", r["Source"])