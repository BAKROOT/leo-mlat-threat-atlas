"""Stratified random sample of 20 threats for the independent expert validation.
Constraints (fixed in advance): >= 4 threats per layer; every STRIDE-tau primary category, every evidence level
(E0-E3 and postulated) and every adversary class (AC1-AC7) occurs at least once; enablers are included only if drawn
by chance. Rejection sampling with a fixed seed; the first accepted draw is written to validation/sample.csv.
Usage: python validation/sample_threats.py [catalogue.xlsx] [seed]"""
import sys, csv, random, openpyxl
XLSX = sys.argv[1] if len(sys.argv) > 1 else 'data/catalogue/LEO_MLAT_Threat_Catalogue.xlsx'
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 20261112
N = 20
wb = openpyxl.load_workbook(XLSX, data_only=True)
ws = wb['Catalogue']
rows = list(ws.iter_rows(min_row=4, values_only=True))
hdr = rows[0]; ix = {h: i for i, h in enumerate(hdr) if h}
need = ['ID', 'Layer', 'STRIDE-tau primary', 'Adversary class', 'Evidence', 'Role']
th = []
for r in rows[1:]:
    if r[0] and str(r[0]).startswith('T'):
        d = {k: r[ix[k]] for k in need}
        d['Evidence'] = d['Evidence'] or 'P'
        th.append(d)
assert len(th) == 55, len(th)
cats = {k: {t[k] for t in th} for k in ('STRIDE-tau primary', 'Adversary class', 'Evidence')}
rnd = random.Random(SEED)
def ok(s):
    if any(sum(t['Layer'] == l for t in s) < 4 for l in ('L1', 'L2', 'L3', 'L4')): return False
    return all({t[k] for t in s} >= cats[k] for k in cats)
for attempt in range(1, 200001):
    s = rnd.sample(th, N)
    if ok(s): break
else:
    raise SystemExit('no admissible sample found: relax the constraints')
s.sort(key=lambda t: t['ID'])
with open('validation/sample.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['ID'] + need[1:])
    for t in s: w.writerow([t[k] for k in need])
print('seed', SEED, 'attempts', attempt, 'sample', [t['ID'] for t in s])
