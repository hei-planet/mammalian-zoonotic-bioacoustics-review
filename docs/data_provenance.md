# Source data and provenance

The review tables were exported from the authors' **Research Protocol / Paper 1** Google Drive workspace on **2026-11-07** and retained as fixed CSV input snapshots. The original working files are held separately in Google Drive.

| File | Source |
| --- | --- |
| `data/processed/study_extraction.csv` | Data Extraction Table / Included-papers tab (25 species-/experiment-specific records) |
| `data/processed/included_studies.csv` | Derived unique-study lookup of 24 IDs |
| `data/processed/quality_assessment.csv` | Quality Assessment Table / Evaluation tab (24 study-level records, with justifications) |
| `data/processed/multiple_species_details.csv` | Data Extraction Table / Details-on-Multiple-Species tab |
| `data/processed/zoonotic_reservoirs.csv` | Bioacoustics-reservoirs-ALL reference sheet |
| `data/derived/papers_with_normalized_scores.csv` | Secondary numeric quality-score export |
| `docs/extraction_codebook_complete.csv` | Original source definitions supplemented with derived column descriptions; check `Definition provenance` for inferred fields |
| `docs/quality_criteria.csv` | Original quality-scoring criteria and guidelines |

There are 24 distinct studies and 25 extraction rows, since one study has two distinct species-specific records.

**Review protocol:** https://doi.org/10.17605/OSF.IO/CSFQT. Search strings, screening and study selection are described in the review protocol, manuscript and supplementary materials, which are separate from this code/data reproducibility package.

The data here do not contain original audio, full-text PDFs, commercial database RIS exports or named reviewer screening archives. Citations and third-party rights are retained as described in `LICENSE-DATA.md`.
