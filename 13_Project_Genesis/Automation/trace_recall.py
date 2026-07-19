from __future__ import annotations
import json,sys
from pathlib import Path
d=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8')); scope=d.get('affected_scope') or {}
trace={'incident_id':d.get('incident_id'),'recall_id':d.get('recall_id'),'products':scope.get('products',[]),'batches':scope.get('batches',[]),'orders':scope.get('orders',[]),'recipients':scope.get('recipients',[]),'population':scope.get('population',0),'traceability':d.get('traceability',{}),'automation_authority':'IDENTIFY_AND_DRAFT_ONLY'}
Path(sys.argv[2]).write_text(json.dumps(trace,indent=2)+'\n',encoding='utf-8'); print('TRACE GENERATED')
