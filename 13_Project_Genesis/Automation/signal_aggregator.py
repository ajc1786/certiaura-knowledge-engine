from __future__ import annotations
import json, sys, collections
from pathlib import Path
counts=collections.Counter(); cases=[]
for p in Path(sys.argv[1]).glob('*.json'):
    try:d=json.loads(p.read_text(encoding='utf-8'))
    except Exception:continue
    if d.get('record_type')!='surveillance_case':continue
    key=(d.get('traceability',{}).get('product_id') or 'UNKNOWN', d.get('signal',{}).get('term') or d.get('source','UNKNOWN'))
    counts[key]+=1; cases.append(d.get('case_id'))
signals=[{'product_id':k[0],'term':k[1],'case_count':v,'review_recommendation':'OPEN_TREND_REVIEW' if v>=2 else 'CONTINUE_MONITORING'} for k,v in sorted(counts.items())]
out={'case_count':len(cases),'signals':signals,'authority':'AGGREGATE_AND_RECOMMEND_ONLY'}
Path(sys.argv[2]).write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,indent=2))
