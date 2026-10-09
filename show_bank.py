import json

for line in open("prompts/bank_v1.jsonl", encoding="utf-8"):
    p = json.loads(line)
    print(p["prompt_id"], "|", p["text"])
    print()