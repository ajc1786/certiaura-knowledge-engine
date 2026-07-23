import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; CLOSE=ROOT/"Scripts/Close_Certiaura_Build_0060.ps1"; SCHEMA=ROOT/"Schemas/certiaura_build_0060_closure_evidence.schema.json"
class Tests(unittest.TestCase):
 def text(self): return CLOSE.read_text()
 def test_delimiters(self): self.assertIn("CERTIAURA_BUILD_0060_CLOSURE_EVIDENCE_BEGIN",self.text()); self.assertIn("CERTIAURA_BUILD_0060_CLOSURE_EVIDENCE_END",self.text())
 def test_fields(self):
  for x in ["Build number:","Candidate:","Build title:","Canonical commit:","Commit subject:","GitHub Actions run ID:","Workflow:","Run attempt:","Branch:","Event:","Status:","Conclusion:","Created:","Updated:","Actions URL:","Local and origin/main aligned:","Repository clean:"]: self.assertIn(x,self.text())
 def test_persistence(self): self.assertIn("ExternalEvidence",self.text()); self.assertIn("LocalEvidence",self.text()); self.assertIn("BUILD_0060_CLOSURE_EVIDENCE.json",self.text())
 def test_founder_ready(self): self.assertIn("FOUNDER_CONFIRMATION_READY: Reply with exact phrase GREEN",self.text())
 def test_schema_fields(self): self.assertGreaterEqual(len(json.loads(SCHEMA.read_text())["required"]),20)
 def test_guard_endpoints(self): self.assertIn("NO_MANUAL_GIT_OBJECT_CLEANUP_PROMPTS",self.text())
if __name__=="__main__": unittest.main()
