#!/usr/bin/env python3
"""Create deterministic descriptive summary tables from the frozen source records."""
import csv
from collections import Counter,defaultdict
from pathlib import Path
from statistics import mean
from validate_data import validate, read, score, SCORE_FIELDS, ROOT, DATA, DOMAINS

def write_csv(name,header,rows):
    p=ROOT/'results'/'tables'/name;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(header);w.writerows(rows)
    print('Wrote',p.relative_to(ROOT))

def main():
    errors,warnings,stats=validate()
    if errors:raise SystemExit('Cannot regenerate: data validation errors: '+'; '.join(errors))
    included=read(DATA/'included_studies.csv')
    extraction=read(DATA/'study_extraction.csv')
    quality=read(DATA/'quality_assessment.csv')
    # A study may have multiple extraction rows. Do not imply these are independent studies.
    by_id=defaultdict(list)
    for row in extraction:by_id[row['id']].append(row)
    for field,name in [('Taxa Order','taxa_by_study.csv'),('ML Algorithm Category','method_category_by_study.csv'),('Evaluation Method','evaluation_method_by_study.csv')]:
        counts=Counter()
        for ident,rows in by_id.items():
            labels={val.strip() for row in rows for val in row.get(field,'').replace(',',';').split(';') if val.strip()}
            for label in labels:counts[label]+=1
        write_csv(name,['category','unique_studies'],sorted(counts.items(),key=lambda z:(-z[1],z[0])))
    max_score=2*len(SCORE_FIELDS)
    q_totals=[sum(score(r[f]) for f in SCORE_FIELDS) for r in quality]
    domain_rows=[]
    for fields,col in DOMAINS:
        denom=2*len(fields)
        normalized=[sum(score(r[x]) for x in fields)/denom for r in quality]
        domain_rows.append([col,len(fields),denom,round(mean(normalized),6)])
    domain_rows.append(['Overall',13,max_score,round(mean(s/max_score for s in q_totals),6)])
    write_csv('quality_domain_means.csv',['domain_code','n_criteria','max_raw_score','mean_normalized_score'],domain_rows)
    write_csv('dataset_counts.csv',['metric','count'],[['included_studies',len(included)],['extraction_rows',len(extraction)],['quality_assessments',len(quality)]])
    print('Completed deterministic descriptive summaries. NOTE: these are not all figures in the original paper.')
if __name__=='__main__':main()
