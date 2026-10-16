import csv
from collections import Counter, defaultdict

ORDER = ["R", "P", "C", "CO", "E", "X"]

with open("labeling/labels.csv", encoding="utf-8", newline="") as f:
    labels = {r["blind_id"]: r["label"].strip().upper() for r in csv.DictReader(f)}
with open("labeling/blind_key.csv", encoding="utf-8", newline="") as f:
    key = {r["blind_id"]: r for r in csv.DictReader(f)}

assert len(labels) == 420, f"labels: {len(labels)}"
assert set(labels) == set(key), "label IDs and key IDs do not match"
assert all(l in ORDER for l in labels.values()), "unknown label found"


def build(group_fn):
    cells = defaultdict(Counter)
    for bid, lab in labels.items():
        k = key[bid]
        prompt_id = k["run_key"].split("|")[1]          # e.g. H05
        kind = "harmful" if prompt_id.startswith("H") else "benign"
        model = k["model"].split("/")[-1]
        cells[group_fn(model, kind, k["temperature"])][lab] += 1
    return cells


def show(title, cells):
    print("\n" + title)
    print("group".ljust(40) + "n".rjust(5) + "".join(l.rjust(12) for l in ORDER))
    for group in sorted(cells):
        c = cells[group]
        n = sum(c.values())
        row = "".join(f"{c[l]} ({100 * c[l] / n:.0f}%)".rjust(12) for l in ORDER)
        print(" | ".join(group).ljust(40) + str(n).rjust(5) + row)


show("BY MODEL AND PROMPT KIND", build(lambda m, kd, t: (m, kd)))
show("BY MODEL, KIND AND TEMPERATURE", build(lambda m, kd, t: (m, kd, t)))