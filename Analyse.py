import csv, json, os
from collections import Counter, defaultdict

# 1. human labels (keep last row per blind_id)
labels, dup = {}, 0
for row in csv.DictReader(open("labeling/labels.csv", encoding="utf-8")):
    if row["blind_id"] in labels:
        dup += 1
    labels[row["blind_id"]] = row["label"].strip()

# 2. blind key: blind_id -> run_key, model
key = {r["blind_id"]: r for r in csv.DictReader(open("labeling/blind_key.csv", encoding="utf-8"))}

# 3. prompt_id from the log, by run_key (metadata only, no response text)
prompt_of = {}
for line in open("logs/raw_calls.jsonl", encoding="utf-8"):
    if line.strip():
        r = json.loads(line)
        prompt_of[r["run_key"]] = r["prompt_id"]

# 4. join and count
overall = Counter()
by_group = defaultdict(Counter)    # (model, "harmful"/"benign") -> label counts
by_prompt = defaultdict(Counter)   # (model, prompt_id) -> label counts
missing = 0
for bid, lab in labels.items():
    k = key.get(bid)
    if k is None or k["run_key"] not in prompt_of:
        missing += 1
        continue
    pid = prompt_of[k["run_key"]]
    kind = "harmful" if pid.startswith("H") else "benign"
    overall[lab] += 1
    by_group[(k["model"], kind)][lab] += 1
    by_prompt[(k["model"], pid)][lab] += 1

print("labels rows:", len(labels), "| duplicate blind_ids:", dup, "| unmatched:", missing)
print("overall:", dict(overall))

out = {}
for (model, kind), c in sorted(by_group.items()):
    n = sum(c.values())
    out[f"{model} | {kind}"] = {"n": n, "counts": dict(c), "R+P": c["R"] + c["P"]}
    print(model, kind, "n =", n, dict(c), "R+P =", c["R"] + c["P"])

os.makedirs("results", exist_ok=True)
json.dump(out, open("results/phase1_rates.json", "w"), indent=2)

labs = ["R", "P", "C", "CO", "E", "ERR", "X"]
with open("results/phase1_per_prompt.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["model", "prompt_id"] + labs)
    for (model, pid), c in sorted(by_prompt.items()):
        w.writerow([model, pid] + [c[l] for l in labs])