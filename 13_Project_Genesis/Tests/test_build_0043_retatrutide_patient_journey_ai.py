from __future__ import annotations
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Build0043Tests(unittest.TestCase):
 def run_py(self,*args):
  return subprocess.run([sys.executable,"-B",*map(str,args)],text=True,capture_output=True)
 def test_valid_report_and_deterministic_id(self):
  with tempfile.TemporaryDirectory() as td:
   td=Path(td); o1=td/"r1.json"; m1=td/"r1.md"; o2=td/"r2.json"; m2=td/"r2.md"
   script=ROOT/"Scripts/generate_retatrutide_patient_journey_report.py"; profile=ROOT/"12_Reports/Retatrutide/Examples/valid_patient_profile.example.json"
   a=self.run_py(script,profile,"--repository",ROOT,"--output-json",o1,"--output-md",m1); self.assertEqual(a.returncode,0,a.stderr)
   b=self.run_py(script,profile,"--repository",ROOT,"--output-json",o2,"--output-md",m2); self.assertEqual(b.returncode,0,b.stderr)
   r1=json.loads(o1.read_text()); r2=json.loads(o2.read_text()); self.assertEqual(r1["report_id"],r2["report_id"]); self.assertEqual(r1["report_state"],"READY_FOR_CLINICIAN_DISCUSSION")
 def test_conditional_and_urgent_states(self):
  with tempfile.TemporaryDirectory() as td:
   td=Path(td); script=ROOT/"Scripts/generate_retatrutide_patient_journey_report.py"
   for name,state in [("conditional_patient_profile.example.json","CONDITIONAL_MISSING_DATA"),("urgent_patient_profile.example.json","URGENT_CLINICAL_ROUTING")]:
    out=td/(name+".json"); md=td/(name+".md"); p=ROOT/"12_Reports/Retatrutide/Examples"/name
    r=self.run_py(script,p,"--repository",ROOT,"--output-json",out,"--output-md",md); self.assertEqual(r.returncode,0,r.stderr); self.assertEqual(json.loads(out.read_text())["report_state"],state)
 def test_identifiable_input_fails(self):
  with tempfile.TemporaryDirectory() as td:
   r=self.run_py(ROOT/"Scripts/generate_retatrutide_patient_journey_report.py",ROOT/"12_Reports/Retatrutide/Examples/invalid_identifiable_patient_profile.example.json","--repository",ROOT,"--output-json",Path(td)/"x.json","--output-md",Path(td)/"x.md")
   self.assertNotEqual(r.returncode,0)
 def test_ai_grounded_refusal_and_urgent(self):
  with tempfile.TemporaryDirectory() as td:
   td=Path(td); script=ROOT/"Scripts/query_retatrutide_knowledge.py"
   cases=[("valid_evidence_query.example.json",{"ANSWERED_GROUNDED","ABSTAINED_INSUFFICIENT_EVIDENCE"}),("refused_dosing_query.example.json",{"REFUSED_SAFETY_BOUNDARY"}),("urgent_symptom_query.example.json",{"URGENT_CLINICAL_ROUTING"})]
   for name,states in cases:
    out=td/name; r=self.run_py(script,ROOT/"13_Project_Genesis/AI/Examples"/name,"--repository",ROOT,"--policy",ROOT/"13_Project_Genesis/AI/retatrutide_ai_query_policy.json","--output",out); self.assertEqual(r.returncode,0,r.stderr); self.assertIn(json.loads(out.read_text())["response_state"],states)
 def test_powershell_scripts_are_ascii_only(self):
  for p in (ROOT/"Scripts").glob("*.ps1"):
   self.assertTrue(all(b<128 for b in p.read_bytes()),f"Non-ASCII byte in {p.name}")
 def test_no_external_network_code(self):
  for p in [ROOT/"Scripts/generate_retatrutide_patient_journey_report.py",ROOT/"Scripts/query_retatrutide_knowledge.py"]:
   t=p.read_text().lower(); self.assertNotIn("requests.",t); self.assertNotIn("urllib.request",t); self.assertNotIn("openai",t)
if __name__=="__main__": unittest.main()
