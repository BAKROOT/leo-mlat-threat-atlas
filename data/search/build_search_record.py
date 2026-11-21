"""Merge the database exports of the literature search, remove duplicates and mark the studies of data/atlas/csv/paper_alignment.csv.

Usage: python build_search_record.py --raw RAW_DIR --bib mybibliography.bib [--out OUT_DIR]
RAW_DIR holds the exports, named {scopus,ieee,acm,arxiv}_Q{1,2,3}.{csv,csv,bib,xml} (not redistributed here: database licences).
Writes records.csv (one row per unique record, with abstracts: keep it local) and counts.json.
Duplicates: same DOI (case-insensitive), else same normalised title with years at most one apart."""
import argparse, csv, json, re, glob, os, unicodedata
import xml.etree.ElementTree as ET
import pandas as pd

csv.field_size_limit(10**8)
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument('--raw', required=True); ap.add_argument('--bib', required=True); ap.add_argument('--out', default='.')
ARGS = ap.parse_args()
RAW = ARGS.raw; OUT = ARGS.out
ALIGN = os.path.join(HERE, '..', 'atlas', 'csv', 'paper_alignment.csv')

def norm(t):
    t = unicodedata.normalize('NFKD', str(t or '')).encode('ascii', 'ignore').decode().lower()
    t = re.sub(r'<[^>]+>|\{|\}|\\[a-z]+', ' ', t)
    return re.sub(r'[^a-z0-9]+', ' ', t).strip()

def doi_of(x):
    x = str(x or '').strip().lower()
    m = re.search(r'10\.\d{4,9}/\S+', x)
    return m.group(0).rstrip('.') if m else ''

def rec(db, q, title, year, doi, venue, authors, abstract, kw, typ=''):
    try: year = int(str(year)[:4])
    except Exception: year = None
    return dict(db=db, query=q, title=re.sub(r'\s+', ' ', str(title or '')).strip(), year=year, doi=doi_of(doi),
                venue=str(venue or '').strip(), authors=str(authors or '').strip(), abstract=re.sub(r'\s+', ' ', str(abstract or '')).strip(),
                keywords=str(kw or '').strip(), doctype=str(typ or '').strip())

def read_scopus(path, q):
    d = pd.read_csv(path, dtype=str).fillna('')
    return [rec('Scopus', q, r['Title'], r['Year'], r['DOI'], r['Source title'], r['Authors'], r['Abstract'],
                '; '.join(x for x in (r.get('Author Keywords', ''), r.get('Index Keywords', '')) if x), r.get('Document Type', ''))
            for _, r in d.iterrows()]

def read_ieee(path, q):
    d = pd.read_csv(path, dtype=str).fillna('')
    return [rec('IEEE Xplore', q, r.get('Document Title', ''), r.get('Publication Year', ''), r.get('DOI', ''),
                r.get('Publication Title', ''), r.get('Authors', ''), r.get('Abstract', ''),
                '; '.join(x for x in (r.get('Author Keywords', ''), r.get('IEEE Terms', '')) if x), r.get('Document Identifier', ''))
            for _, r in d.iterrows()]

def read_bib(path, q):
    s = open(path, encoding='utf-8', errors='replace').read()
    out = []
    for m in re.finditer(r'@(\w+)\s*\{', s):
        start = m.end(); depth = 1; i = start
        while i < len(s) and depth:
            depth += {'{': 1, '}': -1}.get(s[i], 0); i += 1
        body = s[start:i - 1]
        def f(k):
            mm = re.search(r'(?<![a-z])' + k + r'\s*=\s*\{', body, re.I)
            if not mm: return ''
            j = mm.end(); dep = 1; k0 = j
            while j < len(body) and dep:
                dep += {'{': 1, '}': -1}.get(body[j], 0); j += 1
            return body[k0:j - 1]
        out.append(rec('ACM DL', q, f('title'), f('year'), f('doi'), f('booktitle') or f('journal'), f('author'), f('abstract'), f('keywords'), m.group(1)))
    return out

def read_arxiv(path, q):
    ns = {'a': 'http://www.w3.org/2005/Atom', 'x': 'http://arxiv.org/schemas/atom'}
    root = ET.parse(path).getroot(); out = []
    for e in root.findall('a:entry', ns):
        doi = e.findtext('x:doi', '', ns)
        out.append(rec('arXiv', q, e.findtext('a:title', '', ns), e.findtext('a:published', '', ns), doi,
                       (e.findtext('x:journal_ref', '', ns) or 'arXiv ' + e.findtext('a:id', '', ns).split('/abs/')[-1]),
                       '; '.join(a.findtext('a:name', '', ns) for a in e.findall('a:author', ns)),
                       e.findtext('a:summary', '', ns), e.findtext('x:primary_category', '', ns) or '', 'preprint'))
        out[-1]['arxiv_id'] = e.findtext('a:id', '', ns).split('/abs/')[-1]
    return out

READ = {'scopus': read_scopus, 'ieee': read_ieee, 'acm': read_bib, 'arxiv': read_arxiv}
rows, counts = [], {}
for p in sorted(glob.glob(os.path.join(RAW, '*_Q?.*'))):
    db, q = os.path.basename(p).split('.')[0].split('_')
    r = READ[db](p, q); rows += r; counts[f'{db}_{q}'] = len(r)

# duplicate removal
order = {'Scopus': 0, 'IEEE Xplore': 1, 'ACM DL': 2, 'arXiv': 3}
rows.sort(key=lambda r: (order[r['db']], r['query']))
groups, by_doi, by_title = [], {}, {}
for r in rows:
    nt = norm(r['title']); g = None
    if r['doi'] and r['doi'] in by_doi: g = by_doi[r['doi']]
    elif nt and nt in by_title:
        for gi in by_title[nt]:
            ys = [x['year'] for x in groups[gi] if x['year']]
            if not ys or not r['year'] or min(abs(r['year'] - y) for y in ys) <= 1: g = gi; break
    if g is None:
        g = len(groups); groups.append([])
        by_title.setdefault(nt, []).append(g)
    groups[g].append(r)
    if r['doi']: by_doi.setdefault(r['doi'], g)

# the 41 retained studies (bib keys from the paper) matched by DOI or normalised title
bib = open(ARGS.bib, encoding='utf-8').read()
def bibfield(body, k):
    m = re.search(k + r'\s*=\s*[{"](.*?)[}"]\s*,?\s*\n', body, re.S | re.I)
    return re.sub(r'[{}\s]+', ' ', m.group(1)).strip() if m else ''
ents = {m.group(2).strip(): m.group(3) for m in re.finditer(r'@(\w+)\{([^,]+),(.*?)\n\}', bib, re.S)}
retained = []
for r in csv.DictReader(open(ALIGN)):
    for k in r['BibTeX Key(s)'].split(';'):
        k = k.strip(); b = ents.get(k, '')
        retained.append(dict(row=r['#'], key=k, title=bibfield(b, 'title'), doi=doi_of(bibfield(b, 'doi')), year=bibfield(b, 'year')))
# match on DOI, exact normalised title, or the first 60 characters of the normalised title (subtitles differ)
key_of = {}
for i, g in enumerate(groups):
    dois = {x['doi'] for x in g if x['doi']}; nts = {norm(x['title']) for x in g}
    for s in retained:
        nt = norm(s['title'])
        if (s['doi'] and s['doi'] in dois) or (nt and (nt in nts or any(len(nt) > 25 and (n.startswith(nt[:60]) or nt.startswith(n[:60])) and len(n) > 25 for n in nts))):
            key_of.setdefault(i, []).append(s['key'])

out = []
for i, g in enumerate(groups):
    best = max(g, key=lambda x: (len(x['abstract']), order[x['db']] == 0))
    out.append(dict(rec_id=f'R{i+1:04d}', title=best['title'], year=min((x['year'] for x in g if x['year']), default=''),
                     doi=next((x['doi'] for x in g if x['doi']), ''), venue=best['venue'], authors=best['authors'][:300],
                     doctype=best['doctype'], abstract=best['abstract'], keywords=best['keywords'][:500],
                     found_in='; '.join(sorted({f"{x['db']} {x['query']}" for x in g})), n_hits=len(g),
                     retained_key='; '.join(key_of.get(i, []))))
pd.DataFrame(out).to_csv(os.path.join(OUT, 'records.csv'), index=False)
found = {k for v in key_of.values() for k in v}
res = dict(per_file=counts, records_identified=len(rows), unique_after_dedup=len(groups), duplicates_removed=len(rows) - len(groups),
           retained_found=sorted(found), retained_not_found=[s['key'] for s in retained if s['key'] not in found])
json.dump(res, open(os.path.join(OUT, 'counts.json'), 'w'), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != 'retained_found'}, indent=1)); print('found', len(found), 'of', len(retained))
