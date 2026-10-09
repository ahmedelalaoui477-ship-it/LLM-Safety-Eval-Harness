import json
import sys

rows = [json.loads(l) for l in open("logs/raw_calls.jsonl", encoding="utf-8") if l.strip()]

for r in rows:
    if r["run_key"] in sys.argv[1:]:
        print("RUN KEY:", r["run_key"])
        print("finish:", r["finish_reason"], "| completion tokens:", r["completion_tokens"],
              "| reasoning tokens:", r["reasoning_tokens"])
        print("content length:", len(r["content"] or ""))
        print("reasoning length:", len(r["reasoning_text"] or ""))
        print("CONTENT:", (r["content"] or "")[:400])
        print("REASONING:", (r["reasoning_text"] or "")[:400])
        print("REASONING END:", (r["reasoning_text"] or "")[-400:])
        print("-" * 40)