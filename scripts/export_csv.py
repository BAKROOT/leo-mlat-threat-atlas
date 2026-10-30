#!/usr/bin/env python3
"""
Export the data sheets of the two workbooks to plain CSV (UTF-8), so that they can be read, diffed and
version-controlled without Excel. Values are the cached values stored in the workbooks (formulas already
evaluated). The workbooks stay the master copy; the CSV files are a snapshot.

Usage (from the repository root):   python scripts/export_csv.py
Writes data/catalogue/csv/*.csv and data/atlas/csv/*.csv
"""
import csv, os, sys
import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBS = {
    "data/catalogue/SATERA_Extended_Threat_Catalogue.xlsx": [
        # (sheet, header row (1-based) or None for a raw dump, output name)
        ("Catalogue", 4, "catalogue_55_threats"), ("Binding", 4, "threat_x_atlas_source_binding"),
        ("Assets", 4, "asset_register_27"), ("SATERA", 4, "satera_17_entries"),
        ("Checks", 4, "paper_statistics_checks"), ("CVE Register", 4, "cve_register_57"),
        ("Worked", 4, "worked_example"), ("Review", 4, "review_of_earlier_workbook"),
        ("Rubric", None, "rubric_raw"),
    ],
    "data/atlas/PRISM-LEO_Threat_Exploit_Atlas.xlsx": [
        ("Threat Atlas", 5, "atlas_78_sources"), ("Asset Register", 5, "asset_register_27"),
        ("CVE Register", 5, "cve_register_57"), ("Mitigations", 5, "mitigations_25"),
        ("Paper Alignment", 4, "paper_alignment"),
        ("Gap Matrix", None, "gap_matrix_raw"), ("Excluded Entries", None, "excluded_entries_raw"),
        ("Classification Key", None, "classification_key_raw"), ("Overview", None, "overview_raw"),
    ],
}

def clean(v):
    if v is None: return ""
    if isinstance(v, float) and v.is_integer(): return str(int(v))
    return str(v).replace("\r", "").strip()

def main():
    for rel, jobs in JOBS.items():
        wb = openpyxl.load_workbook(os.path.join(ROOT, rel), data_only=True)
        outdir = os.path.join(ROOT, os.path.dirname(rel), "csv"); os.makedirs(outdir, exist_ok=True)
        for sheet, hdr, name in jobs:
            ws = wb[sheet]
            rows = [[clean(c) for c in r] for r in ws.iter_rows(values_only=True)]
            if hdr is not None:
                head = rows[hdr - 1]
                width = max(i for i, h in enumerate(head) if h) + 1
                body = []
                for r in rows[hdr:]:
                    if not r[0]: break          # tables end at the first row with an empty first cell
                    body.append(r[:width])
                rows = [head[:width]] + body
            else:
                rows = [r for r in rows if any(r)]
                width = max(max((i for i, c in enumerate(r) if c), default=0) for r in rows) + 1
                rows = [r[:width] for r in rows]
            with open(os.path.join(outdir, name + ".csv"), "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerows(rows)
            print(f"{rel.split('/')[1]:9s} {sheet:20s} -> csv/{name}.csv  ({len(rows) - (1 if hdr else 0)} rows)")

if __name__ == "__main__":
    main()
