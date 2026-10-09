import json

rows = [json.loads(l) for l in open("logs/raw_calls.jsonl", encoding="utf-8") if l.strip()]

print("lines:", len(rows))
print("unique run_keys:", len({r["run_key"] for r in rows}))

for r in rows:
    print(r["run_key"], r["finish_reason"], r["completion_tokens"],
          r["model_returned"], "reasoning:", bool(r["reasoning_text"]))

from collections import defaultdict

groups = defaultdict(list)
for r in rows:
    if r["temperature"] == 0.0:
        groups[(r["model_requested"], r["prompt_id"])].append(r["content"])

for (model, pid), contents in groups.items():
    print(model, pid, "identical:", len(set(contents)) == 1, "| n =", len(contents))