# Literature search record (re-run of 21 November 2026)

This folder records the literature search behind the 41 security studies of the paper's synthesis (supplement, *Review protocol*).
The 41 studies were selected by the first author for their relevance to GNSS-independent, space-based multilateration surveillance,
from an earlier search that was not logged, together with studies from other conferences and sources and studies reached by snowballing.
The search was therefore re-run on 21 November 2026 and logged here. The re-run checks coverage; it is not the origin of the 41.

| File | Content |
|---|---|
| `search_log.csv` | One row per database and query family: the exact string as run, the fields and limits, the records retrieved and the exported file. Q2 and Q3 were first run on broader strings (rows marked *superseded*, more than 39,000 records) and replaced by the tightened strings. |
| `search_records_unique.csv` | The 2,477 unique records after merging the 12 exports (title, year, DOI, venue, the databases and queries that returned it, number of hits) and the bibliography keys of the retained studies it matches. Abstracts are left out. |
| `retained_studies_coverage.csv` | The 41 studies of `data/atlas/csv/paper_alignment.csv`: retrieved by the re-run or not, and the reason for each study that was not. |
| `build_search_record.py` | Merges the exports, removes duplicates and marks the retained studies. |

## Numbers

3,524 records were retrieved (IEEE Xplore 1,219, ACM Digital Library 234, arXiv 220, Scopus 1,851); removing 1,047 duplicates
(same DOI, otherwise same normalised title with years at most one apart) leaves 2,477 unique records. The re-run retrieves 23 of the 41
studies (24 of the 45 bibliography entries behind them). Of the 18 not retrieved, 3 were published before 2014, 5 are talks, white papers, a thesis or a code
repository that the databases do not index, 7 concern GNSS spoofing, ACARS, CPDLC, LDACS, aeronautical-communication security or ILS and VOR, which the
strings do not name, and 3 were not retrieved by the strings (the reason is not established).

## What is not here

* **The raw exports** (Scopus and IEEE CSV, ACM BibTeX, arXiv Atom XML) are not redistributed, because of the databases' licences. `search_log.csv` gives the strings and dates, so the search can be repeated; the result will differ as the databases grow.
* **Screening counts.** The selection of the 41 was a judgement of relevance by one reviewer (title, abstract, then full text), not a sequence of rule-based exclusions, so no counts of records excluded at each step are reported. This is a limitation of the review.

## Rebuilding

```bash
python data/search/build_search_record.py --raw RAW_DIR --bib mybibliography.bib --out OUT_DIR
```

`RAW_DIR` holds the exports named `scopus_Q1.csv`, `ieee_Q1.csv`, `acm_Q1.bib`, `arxiv_Q1.xml` and so on for Q1 to Q3. Requires pandas.
The script writes `records.csv` (with abstracts: keep it local) and `counts.json`; the columns of `search_records_unique.csv` are a subset of `records.csv`.
