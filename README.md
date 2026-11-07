# Towards ML-based bioacoustics-based surveillance of mammal zoonotic reservoirs

**Public reproducibility release manuscript under revision**

This repository contains the **study data**, **quality assessments**, **Python notebooks** and **analysis scripts** used to explore and summarize machine-learning approaches for terrestrial mammal bioacoustics. It contains **no original audio recordings**, and it is not a repository of trained machine-learning models.

The [systematic-review protocol is registered on OSF](https://doi.org/10.17605/OSF.IO/CSFQT); the full protocol is not duplicated here. Search methods and eligibility criteria are described in the manuscript and its supplementary material.

**Live interactive dashboard:** https://review-paper-dashboard.onrender.com/ (the hosted dashboard is separate from the notebook code; its deployment/source code is not part of this repository).

## Reproduce the results

**Requirements:** Python 3.10+; internet access for the initial notebook dependency installation. No API key is required for the standard offline analysis.

From a checkout of this repository:

### 1. Validate the extracted data and rebuild summary tables

```bash
bash run_analysis.sh
```

This runs `scripts/validate_data.py` and `scripts/generate_summary.py`. It checks the extracted-study and quality-score tables, then regenerates five descriptive CSV tables under `results/tables/`:

| Table | What it shows |
| --- | --- |
| `dataset_counts.csv` | Numbers of studies, extraction rows and quality assessments |
| `taxa_by_study.csv` | Taxonomic orders represented, counted by unique study |
| `method_category_by_study.csv` | Machine-learning categories counted by unique study |
| `evaluation_method_by_study.csv` | Evaluation approaches reported by unique study |
| `quality_domain_means.csv` | Mean normalized quality scores by domain and overall |

These outputs are derived directly from the frozen CSV inputs. **24 unique studies contribute 25 extraction rows** because one study has two species-specific entries; study-level counts use distinct IDs. The 13 methodological quality criteria have a maximum raw total of 26 points.

### 2. Reproduce the notebook plots

The repository includes three notebooks:

| Notebook | Outputs |
| --- | --- |
| `notebooks/01_data_exploration.ipynb` | Descriptive extraction-data visualizations |
| `notebooks/02_quality_assessment.ipynb` | Quality-assessment visualizations |
| `notebooks/03_results_and_figures.ipynb` | Results figures, Sankey diagrams and related visualizations |

**Recommended (works on Arch Linux/Omarchy without changing system Python):**

```bash
bash scripts/run_figures.sh
```

This creates an isolated `.venv/`, installs `requirements-notebooks.txt`, runs the three notebooks, and exports their displayed Matplotlib/Plotly figures into `results/figures/`. The generated PNG/HTML figures and notebook-cell manifests are **local outputs** and are intentionally excluded from Git so anyone can regenerate them.

For manual execution:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-notebooks.txt
python scripts/export_notebook_figures.py
```

For a single notebook:

```bash
.venv/bin/python scripts/export_notebook_figures.py \
  --notebook 03_results_and_figures.ipynb
```

The notebook exporter captures plots displayed by notebook cells. The number of files is **not** necessarily the number of final manuscript figures: exploratory and duplicate plots can be present, and some defined plots are not displayed. Use each notebook's `manifest.json` to locate the originating cells and compare the generated outputs to the manuscript.

### 3. Optional IUCN conservation-status plots

The default exporter runs **offline** and intentionally skips 21 code cells in the results notebook: one Colab-specific package installation and 20 IUCN-dependent cells (API requests, processing and plots). These are **not 21 missing plots**. To run the IUCN section, you need your own valid IUCN Red List API **v4** token:

```bash
cp .env.example .env
# Edit .env to set IUCN_REDLIST_API_TOKEN=YOUR_FRESH_TOKEN

.venv/bin/python scripts/check_iucn_connection.py
.venv/bin/python scripts/export_notebook_figures.py \
  --notebook 03_results_and_figures.ipynb --with-iucn
```

Get a token from https://api.iucnredlist.org/. **Never commit `.env` or a credential**. The live API may change over time, so IUCN-generated conservation plots are not frozen, time-independent outputs. The previously embedded notebook token must be revoked/rotated if still active.

## Repository structure

```text
data/
  processed/            # Study extraction, 24-study lookup, QA and reference data
  derived/              # Numeric quality-score export
  SHA256SUMS            # Checksums of frozen source CSVs and definitions
notebooks/              # 3 reproducible analysis notebooks
scripts/                # Validation, table generation, figure export and IUCN test
results/tables/          # 5 committed reproducible descriptive tables
docs/                   # Data provenance, extraction codebook and quality rubric
```

The underlying data files are never overwritten by the reproducibility scripts. You can verify the frozen input snapshots using:

```bash
sha256sum -c data/SHA256SUMS
```

Source definitions: [extraction codebook](docs/extraction_codebook_complete.csv), [quality assessment rubric](docs/quality_scoring.md), [criteria details](docs/quality_criteria.csv) and [data provenance](docs/data_provenance.md).

## Data and code availability

This public repository provides the versioned **v1.0.0** source snapshot of curated data, analysis notebooks and scripts for reproducing the review's descriptive results. The manuscript is under revision; journal citation details will be updated after acceptance. The protocol is registered separately on OSF. The repository contains no original audio data and requires no external archive service.

Licenses selected by the authors: **MIT** for software and notebook code ([LICENSE](LICENSE)); **CC BY 4.0** for the authors' original curated review data and documentation ([LICENSE-DATA.md](LICENSE-DATA.md)), subject to the third-party rights exceptions in the license notice.

**Citation:** [CITATION.cff](CITATION.cff) contains the working author information; manuscript publication metadata will be updated after acceptance.

**Security:** This public repository was created from a clean exported source snapshot with a **new Git history**, without inheriting the earlier private research commits or unpublished screening materials. Do not commit credentials or the local `.env` file.
