#!/usr/bin/env python3
"""Validate the supplied review tables without modifying source CSVs."""
import csv
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'/'processed'
SCORE_FIELDS=['Data volume','Data balance','Data quality control',
              'Model selection','Model validation',
              'Method description','Code availability','Data availability','Technical specifications',
              'Comparative analysis','Performance evaluation','Ecological relevance','Future directions']
DOMAINS=[(['Data volume','Data balance','Data quality control'],'Score'),
         (['Model selection','Model validation'],'Score.1'),
         (['Method description','Code availability','Data availability','Technical specifications'],'Score.2'),
         (['Comparative analysis','Performance evaluation','Ecological relevance','Future directions'],'Score.3')]

def read(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def score(cell):
    cell=str(cell).strip()
    if cell in ('0','1','2'):return int(cell)
    if len(cell)>1 and cell[0] in '012' and cell[1]==':':return int(cell[0])
    raise ValueError('Unknown score: '+repr(cell[:50]))

def validate():
    errors=[]; warnings=[]
    studies=read(DATA/'included_studies.csv')
    extracted=read(DATA/'study_extraction.csv')
    quality=read(DATA/'quality_assessment.csv')
    idlist=[r['id'].strip() for r in extracted]
    studies_ids=[r['id'].strip() for r in studies]
    q_ids=[r['id'].strip() for r in quality]
    if len(studies)!=24:errors.append(f'Expected 24 unique studies, found {len(studies)}')
    if len(set(studies_ids))!=len(studies_ids):errors.append('Repeated IDs in unique-studies table')
    if set(studies_ids)!=set(idlist):errors.append('Study IDs differ between extraction and unique bibliography')
    if set(studies_ids)!=set(q_ids):errors.append('Study IDs differ between extraction and quality assessment')
    if len(q_ids)!=len(set(q_ids)):errors.append('Quality assessment has duplicate IDs')
    repeats={k:v for k,v in Counter(idlist).items() if v>1}
    if repeats: warnings.append('Extraction has multiple rows per study: '+str(repeats)+'; preserve for experiment-level analyses')
    quality_scores={}
    for r in quality:
        try:
            vals={c:score(r[c]) for c in SCORE_FIELDS}
            subtotal=[sum(vals[f] for f in domain) for domain,_ in DOMAINS]
            stated=[int(float(r[field])) for _,field in DOMAINS]
            stated_total=int(float(r['Total Score']))
            total=sum(vals.values())
            if subtotal!=stated:errors.append(f"Study {r['id']} domain subtotals differ: {subtotal} vs {stated}")
            if total!=stated_total:errors.append(f"Study {r['id']} total differs: {total} vs {stated_total}")
            if total>26:errors.append(f"Study {r['id']} total exceeds 26")
            quality_scores[r['id']]=total
        except (ValueError, KeyError, TypeError) as exc:errors.append(f"Study {r['id']} scoring: {exc}")
    # Check the separate numeric-derived score export, not a new source of truth.
    derived=read(ROOT/'data'/'derived'/'papers_with_normalized_scores.csv')
    if len(derived)!=24: warnings.append(f'Derived-score table has {len(derived)} rows instead of 24')
    for row in derived:
        study_id=row.get('id','').strip()
        if study_id in quality_scores:
            try:
                stated=int(float(row['Total Score']))
                if stated!=quality_scores[study_id]:warnings.append(f'Derived score mismatch at study {study_id}: {stated} vs {quality_scores[study_id]}')
            except (ValueError,TypeError): warnings.append(f'Non-numeric score in derived table: {study_id}')
    # Confirm that every extracted column is described in the curated codebook.
    variables=read(ROOT/'docs'/'extraction_codebook_complete.csv')
    defined={r['Column'].strip() for r in variables if r.get('Column')}
    missing=[h for h in extracted[0] if h not in defined]
    if missing:errors.append('Missing columns from extraction codebook: '+', '.join(missing))
    # PRISMA accounting is documented in the manuscript/protocol, not in this
    # analysis package. We intentionally do not embed unverified draft counts.
    # No public database dumps, linked full texts or ASReview archives are distributed.
    return errors,warnings,{'included_studies':len(studies),'extraction_rows':len(extracted),'quality_rows':len(quality),'score_max':26}

if __name__=='__main__':
    errors,warnings,stats=validate()
    print('Review dataset validation')
    print('Counts:',stats)
    print('Errors:',len(errors))
    for msg in errors:print('  ERROR',msg)
    print('Warnings / manual verification:',len(warnings))
    for msg in warnings:print('  REVIEW',msg)
    raise SystemExit(1 if errors else 0)
