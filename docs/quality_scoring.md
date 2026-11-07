# Methodological quality scoring

The project defines **13 evaluation criteria** in four domains. Each criterion is graded 0 (not met/insufficient), 1 (partially met), or 2 (fully met). The maximum **overall raw total is 26**.

| Domain | Criteria | Max score | Source quality file subtotal column |
|---|---:|---:|---|
| Data Quality | 3 | 6 | `Score` |
| Methodological Practices | 2 | 4 | `Score.1` |
| Transparency | 4 | 8 | `Score.2` |
| Research Completeness | 4 | 8 | `Score.3` |

The full human-readable scoring criteria, with definitions, are preserved in `quality_criteria.csv`. Study-level ratings, total scores and verbatim review rationales are in `data/processed/quality_assessment.csv`.

For reporting a normalized score, divide each subtotal by its domain maximum and the total score by 26. The validator checks each row's component scores against source subtotals and totals. Raw scores should not be described as normalized without division. Reviewers should also verify whether all studies met the authors' chosen assessment and consensus protocols.
