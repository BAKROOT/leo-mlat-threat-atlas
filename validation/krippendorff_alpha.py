"""Krippendorff's alpha (nominal or ordinal) with a bootstrap confidence interval over units (threats).
Input CSV (long format): unit,rater,value   (missing values left empty). Usage:
  python validation/krippendorff_alpha.py ratings.csv nominal|ordinal [n_boot=2000] [seed=1]
Interpretation limits fixed in advance: alpha >= 0.800 reliable, 0.667 <= alpha < 0.800 tentative, below: not reliable."""
import sys, csv, collections, random
import numpy as np

def alpha(units, level):
    """units: list of lists of values (one list per unit, missing values removed)."""
    units = [u for u in units if len(u) >= 2]
    vals = sorted({v for u in units for v in u})
    if len(vals) < 2: return float('nan')
    k = {v: i for i, v in enumerate(vals)}
    n = np.zeros((len(vals), len(vals)))
    for u in units:
        m = len(u); c = collections.Counter(u)
        for a in c:
            for b in c:
                n[k[a], k[b]] += (c[a] * (c[b] - (1 if a == b else 0))) / (m - 1)
    nc = n.sum(1); N = nc.sum()
    if level == 'nominal':
        d = 1 - np.eye(len(vals))
    else:  # ordinal metric
        cum = np.cumsum(nc)
        d = np.zeros_like(n)
        for i in range(len(vals)):
            for j in range(len(vals)):
                if i != j:
                    lo, hi = min(i, j), max(i, j)
                    d[i, j] = (cum[hi] - nc[hi] / 2 - cum[lo] + nc[lo] / 2) ** 2
    Do = (n * d).sum() / N
    De = (np.outer(nc, nc) * d).sum() / (N * (N - 1))
    return 1 - Do / De if De > 0 else float('nan')

def load(path):
    U = collections.defaultdict(list)
    with open(path) as f:
        for r in csv.DictReader(f):
            if r['value'] != '':
                v = r['value']
                try: v = float(v)
                except ValueError: pass
                U[r['unit']].append(v)
    return list(U.values())

if __name__ == '__main__':
    path, level = sys.argv[1], sys.argv[2]
    nb = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
    rng = random.Random(int(sys.argv[4]) if len(sys.argv) > 4 else 1)
    units = load(path)
    a = alpha(units, level)
    bs = []
    for _ in range(nb):
        s = [units[rng.randrange(len(units))] for _ in units]
        x = alpha(s, level)
        if x == x: bs.append(x)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    print(f'alpha = {a:.3f}  95% bootstrap CI [{lo:.3f}, {hi:.3f}]  units = {len(units)}  level = {level}')
