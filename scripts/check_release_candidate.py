#!/usr/bin/env python3
"""Check release-candidate file selection without changing source data."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md", "CITATION.cff", "LICENSE", "LICENSE-DATA.md", "VERSION",
    "data/processed/study_extraction.csv", "data/processed/quality_assessment.csv",
    "notebooks/01_data_exploration.ipynb",
    "notebooks/02_quality_assessment.ipynb",
    "notebooks/03_results_and_figures.ipynb",
    "scripts/export_notebook_figures.py",
    "docs/extraction_codebook_complete.csv", "data/SHA256SUMS",
]
FORBIDDEN = [
    "audit", "protocol", ".env", "LICENSE_AND_CITATION_PENDING.md",
    "notebooks/04_screening_agreement_ARCHIVAL.ipynb",
    "notebooks/05_screening_metadata_ARCHIVAL.ipynb",
]
problems = []
for p in REQUIRED:
    if not (ROOT / p).is_file():
        problems.append(f"Missing required file: {p}")
for p in FORBIDDEN:
    if (ROOT / p).exists():
        problems.append(f"Private-only or obsolete path present: {p}")
for p in ROOT.rglob("*"):
    if p.is_file() and p.name.endswith((".asreview", ".ris")):
        problems.append(f"Forbidden screening export: {p.relative_to(ROOT)}")
for notebook in (ROOT / "notebooks").glob("*.ipynb"):
    obj = json.loads(notebook.read_text(encoding="utf-8"))
    for n, cell in enumerate(obj.get("cells", [])):
        source = cell.get("source", "")
        source = "".join(source) if isinstance(source, list) else source
        if "BEARER_TOKEN = " in source and 'os.environ.get' not in source:
            problems.append(f"Potential literal credential in {notebook.name}, cell {n}")
print("Clean candidate selection: " + ("PASS" if not problems else "FAIL"))
for issue in problems:
    print("ERROR:", issue)
raise SystemExit(bool(problems))
