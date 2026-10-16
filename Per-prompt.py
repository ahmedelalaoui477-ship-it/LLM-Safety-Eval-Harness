import csv
from collections import Counter, defaultdict

with open("labeling/labels.csv", encoding="utf-8", newline="") as f:
    labels = {r["blind_id"]: r["label"].strip().upper() for r in csv.DictReader(f)}
with open("labeling/blind_key.csv", encoding="utf-8", newline="") as f:
    key = {r["blind_id"]: r for r in csv.DictReader(f)}

cells = defaultdict(Counter)
for bid, lab in labels.items():
    k = key[bid]
    prompt_id = k["run_key"].split("|")[1]                     # e.g. H05
    model = "small" if "gpt-oss" in k["model"] else "large"
    cells[(prompt_id, model)][lab] += 1


def fmt(c):
    return " ".join(f"{l}{c[l]}" for l in ["R", "P", "C", "CO", "E", "X"] if c[l])


print("prompt".ljust(8) + "small (gpt-oss)".ljust(22) + "large (nemotron)")
for pid in sorted({p for p, _ in cells}):
    print(pid.ljust(8)
          + fmt(cells[(pid, "small")]).ljust(22)
          + fmt(cells[(pid, "large")]))