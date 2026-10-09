import json
import pandas as pd

df = pd.read_csv("data/xstest_prompts.csv", sep=None, engine="python")
safe = df[df["label"] == "safe"]

chosen_types = [
    "homonyms",
    "figurative_language",
    "safe_contexts",
    "historical_events",
    "privacy_public",
]

records = []
for i, t in enumerate(chosen_types, start=6):          # IDs start at B06
    group = safe[safe["type"] == t]
    row = group.sample(n=1, random_state=42).iloc[0]   # same draw as before
    records.append({
        "prompt_id": f"B{i:02d}",                      # B06, B07, ...
        "source": "XSTest",
        "source_ref": f"{row['type']} (XSTest id {int(row['id'])})",
        "category": row["type"],
        "kind": "benign",
        "text": row["prompt"],
    })

assert len(records) == 5, "expected 5 prompts"
assert len({r["prompt_id"] for r in records}) == 5, "duplicate IDs"

with open("prompts/looks-scary.jsonl", "w", encoding="utf-8") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

for r in records:
    print(r["prompt_id"], "|", r["source_ref"], "|", r["text"])