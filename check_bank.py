import json

PATH = "prompts/prompt_bank.jsonl"
expected_ids = [f"H{i:02d}" for i in range(1, 21)] + [f"B{i:02d}" for i in range(1, 11)]

records = []
with open(PATH, "r", encoding="utf-8") as f:
    for n, line in enumerate(f, start=1):
        line = line.strip()
        if not line:
            print(f"line {n}: empty line (remove it)")
            continue
        try:
            records.append(json.loads(line))   # fails if a line is broken
        except json.JSONDecodeError as e:
            print(f"line {n}: BROKEN JSON: {e}")

ids = [r["prompt_id"] for r in records]
print("records:", len(records))
print("IDs in expected order:", ids == expected_ids)
print("duplicates:", len(ids) - len(set(ids)))
print("harmful:", sum(r["kind"] == "harmful" for r in records),
      "| benign:", sum(r["kind"] == "benign" for r in records))
print("empty texts:", sum(not r["text"].strip() for r in records))

for r in records:
    print(r["prompt_id"], r["kind"], "|", r["text"][:60])