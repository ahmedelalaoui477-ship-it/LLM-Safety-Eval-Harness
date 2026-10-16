import csv
from collections import Counter

HUMAN = "labeling/labels.csv"
JUDGE = "labeling/LLM-labels.csv"   
VALID = ["R", "P", "C", "X"]


def read_labels(path):
    with open(path, encoding="utf-8", newline="") as f:
        return {r["blind_id"]: r["label"].strip().upper() for r in csv.DictReader(f)}


human = read_labels(HUMAN)
judge = read_labels(JUDGE)

# only items that both of you labeled with R, P, C or X
ids = sorted(i for i in human if i in judge
             and human[i] in VALID and judge[i] in VALID)
print("human labels:", len(human), "| judge labels:", len(judge),
      "| compared:", len(ids))

n = len(ids)
agree = sum(human[i] == judge[i] for i in ids)
po = agree / n   # observed agreement

h_counts = Counter(human[i] for i in ids)
j_counts = Counter(judge[i] for i in ids)
pe = sum((h_counts[l] / n) * (j_counts[l] / n) for l in VALID)   
kappa = (po - pe) / (1 - pe) if pe < 1 else float("nan")

print(f"raw agreement: {po:.3f} ({agree}/{n})")
print(f"Cohen's kappa: {kappa:.3f}")

print("\nconfusion matrix (rows = human, columns = judge)")
print("      " + "".join(f"{l:>5}" for l in VALID))
for h in VALID:
    row = "".join(f"{sum(1 for i in ids if human[i] == h and judge[i] == j):>5}"
                  for j in VALID)
    print(f"{h:>5} " + row)

print("\ndisagreements (blind_id: human -> judge):")
for i in ids:
    if human[i] != judge[i]:
        print(f"{i}: {human[i]} -> {judge[i]}")