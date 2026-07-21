from __future__ import annotations
import argparse, hashlib, json, shutil
from datetime import datetime, timezone
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec
ROOT=Path(__file__).resolve().parents[2]
VP=ROOT/'13_Project_Genesis/Validators/validate_retatrutide_case_closure_quality_assurance.py'
spec=spec_from_file_location('v',VP); mod=module_from_spec(spec); spec.loader.exec_module(mod)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def main():
 ap=argparse.ArgumentParser();
 for n in ['closure','action','reconciliation','qa']: ap.add_argument(n,type=Path)
 ap.add_argument('--output-dir',required=True,type=Path); ap.add_argument('--now'); a=ap.parse_args()
 objs=[json.loads(getattr(a,n).read_text(encoding='utf-8')) for n in ['closure','action','reconciliation','qa']]
 blob=json.dumps(objs)
 if mod.DIRECT.search(blob) or mod.TREATMENT.search(blob): raise SystemExit('prohibited content')
 closure,action,rec,qa=objs
 if closure.get('closure_state')=='CLOSURE_APPROVED' and (closure.get('open_action_count')!=0 or closure.get('urgent_routing_active')): raise SystemExit('closure prerequisites not met')
 if qa.get('generator_actor_role')==qa.get('reviewer_actor_role'): raise SystemExit('reviewer separation required')
 out=a.output_dir; out.mkdir(parents=True,exist_ok=True)
 names=['case_closure.json','unresolved_action.json','outcome_reconciliation.json','quality_assurance_review.json']
 for src,name in zip([a.closure,a.action,a.reconciliation,a.qa],names): shutil.copyfile(src,out/name)
 manifest={'build_provenance':'CERT-BUILD-0050','generated_at':a.now or now(),'components':[]}
 for name in names:
  p=out/name; manifest['components'].append({'path':name,'sha256':sha(p),'bytes':p.stat().st_size})
 (out/'bundle_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
 summary=f"# Retatrutide Case Closure and Quality Assurance Summary\n\nClosure state: {closure.get('closure_state')}\n\nQA decision: {qa.get('decision')}\n\nOpen action status: {action.get('status')}\n\nOutcome status: {rec.get('outcome_status')}\n"
 (out/'closure_summary.md').write_text(summary,encoding='utf-8',newline='\n'); return 0
if __name__=='__main__': raise SystemExit(main())
