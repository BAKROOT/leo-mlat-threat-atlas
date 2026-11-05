#!/usr/bin/env python3
"""
Export the data sheets of the workbook to plain CSV (UTF-8), so that they can be read, diffed and
version-controlled without Excel. Values are the cached values stored in the workbook (formulas already
evaluated). The workbook stays the master copy; the CSV files are a snapshot.

Usage (from the repository root):   python scripts/export_csv.py
Writes data/catalogue/csv/*.csv (catalogue sheets) and data/atlas/csv/*.csv (atlas sheets of the same workbook)
"""
import csv, os, sys
import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKBOOK = "data/catalogue/LEO_MLAT_Threat_Catalogue.xlsx"
JOBS = [
    # (output folder, [(sheet, header row (1-based) or None for a raw dump, output name)])
    ("data/catalogue/csv", [
        ("Catalogue", 4, "catalogue_55_threats"), ("Binding", 4, "threat_x_atlas_source_binding"),
        ("Assets", 4, "asset_register_27"), ("SATERA", 4, "satera_17_entries"),
        ("Checks", 4, "paper_statistics_checks"), ("CVE Register", 4, "cve_register_57"),
        ("Worked", 4, "worked_example"), ("Review", 4, "review_of_earlier_workbook"),
        ("Rubric", None, "rubric_raw"),
        ("Threat Propagation", 4, "threat_propagation_65"), ("Asset-Threat Matrix", 4, "asset_threat_matrix"),
        ("Asset Connections", 4, "asset_connections_27"), ("Multi-step Attacks", 4, "multistep_attacks"),
        ("Mitigations", 4, "mitigations_25"),
    ]),
    # the atlas sheets; the atlas CVE Register and Mitigations are the catalogue sheets of the same name
    ("data/atlas/csv", [
        ("Threat Atlas", 5, "atlas_78_sources"), ("Asset Evidence", 5, "asset_evidence_27"),
        ("Paper Alignment", 4, "paper_alignment"),
        ("Gap Matrix", None, "gap_matrix_raw"), ("Excluded Entries", None, "excluded_entries_raw"),
        ("Classification Key", None, "classification_key_raw"), ("Atlas Overview", None, "overview_raw"),
    ]),
]

def clean(v):
    if v is None: return ""
    if isinstance(v, float) and v.is_integer(): return str(int(v))
    return str(v).replace("\r", "").strip()

def main():
    wb = openpyxl.load_workbook(os.path.join(ROOT, WORKBOOK), data_only=True)
    for folder, jobs in JOBS:
        outdir = os.path.join(ROOT, folder); os.makedirs(outdir, exist_ok=True)
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
            print(f"{folder.split('/')[1]:9s} {sheet:20s} -> csv/{name}.csv  ({len(rows) - (1 if hdr else 0)} rows)")

if __name__ == "__main__":
    main()
