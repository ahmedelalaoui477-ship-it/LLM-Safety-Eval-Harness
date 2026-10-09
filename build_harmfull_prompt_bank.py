import csv
import json
import random

SEED = 42
PER_CATEGORY = 4
CATEGORIES = [
    "Harassment/Discrimination",
    "Economic harm",
    "Disinformation",
    "Privacy",
    "Expert advice",
]
EXCLUDE = {
    "Blackmail": "threat content, consistent with Extortion",
    "Holocaust glorification": "atrocity glorification",
    "Enslavement": "atrocity glorification",
    "Holocaust denial": "atrocity denial",
    "Identity theft": "high real-world misuse value",
    "Steal debit cards": "high real-world misuse value",
    "Steal government information": "high real-world misuse value",
    "Counterfeiting": "high real-world misuse value",
    "Extortion": "threat content, keep phase 1 milder",
    "Black market organs": "high real-world misuse value",
}

with open("data/jbb_harmful.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

rng = random.Random(SEED)
chosen = []
for category in CATEGORIES:
    candidates = [r for r in rows
                  if r["Category"] == category and r["Behavior"] not in EXCLUDE]
    chosen.extend(rng.sample(candidates, PER_CATEGORY))

with open("prompts/bank_v1.jsonl", "w", encoding="utf-8") as out:
    for i, r in enumerate(chosen, start=1):
        record = {
            "prompt_id": f"H{i:02d}",
            "source": "JBB-harmful",
            "source_ref": f"{r['Behavior']} (Index {r['Index']}, from {r['Source']})",
            "category": r["Category"],
            "kind": "harmful",
            "text": r["Goal"],
        }
        out.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(record["prompt_id"], "|", r["Category"], "|", r["Behavior"], "|", r["Source"])