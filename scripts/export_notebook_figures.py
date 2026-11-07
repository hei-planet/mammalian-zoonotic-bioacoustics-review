#!/usr/bin/env python3
"""Execute plotting notebooks and export Matplotlib and Plotly outputs offline.

This is a reproducibility aid, not a guarantee that the figures match
the accepted manuscript. Live IUCN-dependent cells are skipped.
"""
import argparse
import os
import base64
import json
import re
import shutil
import tempfile
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
NAMES = (
    "01_data_exploration.ipynb",
    "02_quality_assessment.ipynb",
    "03_results_and_figures.ipynb",
)


def render(name: str, target: Path, with_iucn: bool = False) -> dict:
    notebook = nbformat.read(ROOT / "notebooks" / name, as_version=4)
    skipped = []
    if name.startswith("03_"):
        for index, cell in enumerate(notebook.cells):
            if cell.cell_type != "code":
                continue
            if index == 1 or (not with_iucn and 122 <= index <= 141):
                # Skip Colab pip installation; skip IUCN calls unless opted in.
                cell.source = "# Skipped during offline reproduction."
                skipped.append(index)
            else:
                # Lower saved-PNG resolution only; analysis is unchanged.
                cell.source = cell.source.replace("dpi=700", "dpi=180")
    target.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="review-figures-") as tmp:
        workspace = Path(tmp)
        (workspace / "data").symlink_to(ROOT / "data", target_is_directory=True)
        notebook = NotebookClient(
            notebook, timeout=180, kernel_name="python3", allow_errors=True,
            resources={"metadata": {"path": str(workspace)}},
        ).execute()
        for generated in workspace.iterdir():
            if generated.is_file() and generated.suffix.lower() in (".png", ".svg", ".json"):
                shutil.copy2(generated, target / generated.name)

    import plotly.io as pio
    from plotly.offline import get_plotlyjs

    errors, plots = [], []
    heading = "Introduction"
    plotly_bundle = target.parent / "plotly.min.js"
    written_html = False
    for i, cell in enumerate(notebook.cells):
        if cell.cell_type == "markdown":
            matches = re.findall(r"^#{1,4}\s+(.+)$", cell.source, flags=re.MULTILINE)
            if matches:
                heading = matches[-1].strip()
        for j, output in enumerate(cell.get("outputs", [])):
            if output.output_type == "error":
                errors.append({"cell": i, "type": output.ename, "message": output.evalue})
                continue
            if output.output_type not in ("display_data", "execute_result"):
                continue
            data = output.get("data", {})
            stem = f"cell_{i:03d}_{j:02d}"
            if "application/vnd.plotly.v1+json" in data:
                raw = data["application/vnd.plotly.v1+json"]
                fig = pio.from_json(json.dumps({
                    k: raw[k] for k in ("data", "layout", "frames") if k in raw
                }))
                html = pio.to_html(fig, include_plotlyjs=False, full_html=False)
                (target / f"{stem}.html").write_text(
                    '<!doctype html><meta charset="utf-8">'
                    '<script src="../plotly.min.js"></script>\n' + html,
                    encoding="utf-8",
                )
                plots.append({"cell": i, "section": heading,
                              "file": f"{stem}.html", "format": "interactive HTML"})
                written_html = True
            elif "image/png" in data:
                (target / f"{stem}.png").write_bytes(base64.b64decode(data["image/png"]))
                plots.append({"cell": i, "section": heading,
                              "file": f"{stem}.png", "format": "PNG"})
    if written_html and not plotly_bundle.exists():
        plotly_bundle.write_text(get_plotlyjs(), encoding="utf-8")
    report = {
        "notebook": name, "plots": plots, "errors": errors,
        "skipped_code_cells": skipped,
        "status": "PASS" if not errors else "FAIL",
        "notes": ("Unreviewed exports. Live IUCN data enabled; validate these outputs."
                  if with_iucn and name.startswith("03_")
                  else "Unreviewed exports. IUCN-dependent figures omitted in offline mode."),
    }
    (target / "manifest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"{name}: {len(plots)} exported, {len(errors)} errors, "
          f"{len(skipped)} skipped cells", flush=True)
    if errors:
        for err in errors:
            print(f"  cell {err['cell']}: {err['type']}: {err['message']}", flush=True)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--notebook", choices=NAMES, action="append",
                        help="Choose one notebook; default runs all plotting notebooks.")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "figures")
    parser.add_argument(
        "--with-iucn", action="store_true",
        help="Opt in to live IUCN Red List API requests and conservation-status plots."
    )
    args = parser.parse_args()
    # Read optional local, gitignored credentials without overriding shell variables.
    load_dotenv(ROOT / ".env", override=False)
    if args.with_iucn and not os.environ.get("IUCN_REDLIST_API_TOKEN", "").strip():
        parser.error("Missing IUCN_REDLIST_API_TOKEN. Copy .env.example to .env "
                     "and insert a fresh IUCN v4 API token (do not commit it).")
    summary = []
    for name in args.notebook or NAMES:
        summary.append(render(name, args.output / Path(name).stem, with_iucn=args.with_iucn))
    (args.output / "execution_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return 1 if any(item["errors"] for item in summary) else 0


if __name__ == "__main__":
    raise SystemExit(main())
