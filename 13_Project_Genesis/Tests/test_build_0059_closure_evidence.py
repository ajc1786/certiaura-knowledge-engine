from __future__ import annotations
import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; REC=ROOT/"Documentation/Build_Records/0059"; CLOSE=ROOT/"Scripts/Close_Certiaura_Build_0059.ps1"
class Tests(unittest.TestCase):
 def test_schema_fields(self):
  s=json.loads((ROOT/"Schemas/certiaura_build_0059_closure_evidence.schema.json").read_text()); self.assertIn("run_id",s["required"]); self.assertIn("actions_url",s["required"]); self.assertIn("founder_ready_status",s["required"])
 def test_close_script_has_delimiters(self):
  t=CLOSE.read_text(); self.assertIn("CERTIAURA_BUILD_0059_CLOSURE_EVIDENCE_BEGIN",t); self.assertIn("CERTIAURA_BUILD_0059_CLOSURE_EVIDENCE_END",t)
 def test_close_script_prints_all_fields(self):
  t=CLOSE.read_text();
  for x in ["Build number:","Candidate:","Build title:","Canonical commit:","Commit subject:","GitHub Actions run ID:","Workflow:","Run attempt:","Branch:","Event:","Status:","Conclusion:","Created:","Updated:","Actions URL:","Local and origin/main aligned:","Repository clean:","Git non-interactive guard:"]: self.assertIn(x,t)
 def test_close_script_writes_external_json(self): self.assertIn('Join-Path $ReportRoot "BUILD_0059_CLOSURE_EVIDENCE.json"',CLOSE.read_text())
 def test_close_script_writes_canonical_local_json(self): self.assertIn("Documentation\\Build_Records\\0059\\Closure_Evidence",CLOSE.read_text())
 def test_local_json_ignored_by_git(self): self.assertIn("*.json",(REC/"Closure_Evidence/.gitignore").read_text())
 def test_founder_ready_line(self): self.assertIn("FOUNDER_CONFIRMATION_READY: Reply with exact phrase GREEN",CLOSE.read_text())
 def test_guard_endpoints(self):
  t=CLOSE.read_text(); self.assertIn("BUILD_0059_GIT_NONINTERACTIVE_GUARD_VALIDATED",t); self.assertIn("NO_MANUAL_GIT_OBJECT_CLEANUP_PROMPTS",t)
