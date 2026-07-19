import argparse, json
from pathlib import Path

REQUIRED={'assurance','quality','delivery','resilience','total_cost','service'}

def score_candidate(candidate, weights):
    scores=candidate.get('scores',{})
    return round(sum(float(scores.get(k,0))*float(weights.get(k,0))/100 for k in REQUIRED),2)

def rank(data):
    weights=data.get('criteria_weights',{})
    ranked=[]
    for c in data.get('candidates',[]):
        row=dict(c)
        row['calculated_weighted_score']=score_candidate(c,weights)
        eligible=c.get('assurance_status') in {'QUALIFIED','CONDITIONAL'} and c.get('scope_current') is True and not c.get('blocking_flags')
        row['eligible']=eligible
        ranked.append(row)
    ranked.sort(key=lambda x:(x['eligible'],x['calculated_weighted_score']), reverse=True)
    winner=next((x for x in ranked if x['eligible']),None)
    return {'ranked_candidates':ranked,'recommended_supplier_id':winner.get('supplier_id') if winner else None,'recommended_score':winner.get('calculated_weighted_score') if winner else None,'recommendation_only':True,'automatic_award_prohibited':True}

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument('input'); p.add_argument('output',nargs='?')
    a=p.parse_args(argv); data=json.loads(Path(a.input).read_text(encoding='utf-8')); out=rank(data); text=json.dumps(out,indent=2)
    if a.output: Path(a.output).write_text(text+'\n',encoding='utf-8')
    else: print(text)
    return 0
if __name__=='__main__': raise SystemExit(main())
