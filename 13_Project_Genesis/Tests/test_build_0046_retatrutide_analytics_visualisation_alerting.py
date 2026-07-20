from __future__ import annotations
import importlib.util,json,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,ROOT/path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
analytics=load("analytics",Path("Scripts/analyze_retatrutide_longitudinal_outcomes.py"))
sys.modules["analyze_retatrutide_longitudinal_outcomes"]=analytics
render=load("render",Path("Scripts/render_retatrutide_outcome_trends.py"))
alerts=load("alerts",Path("Scripts/evaluate_retatrutide_controlled_alerts.py"))
class Build0046Tests(unittest.TestCase):
 def setUp(self):
  self.journey=json.loads((ROOT/"05_Monitoring/Retatrutide/Analytics/Examples/analytics_journey.example.json").read_text())
  self.low=json.loads((ROOT/"05_Monitoring/Retatrutide/Analytics/Examples/analytics_insufficient.example.json").read_text())
  self.policy=json.loads((ROOT/"13_Project_Genesis/AI/retatrutide_controlled_alerting_policy.json").read_text())
  self.schedule=json.loads((ROOT/"05_Monitoring/Retatrutide/Analytics/Examples/review_schedule.example.json").read_text())
 def test_analytics_ready(self):self.assertEqual(analytics.analyze(self.journey,self.policy)["analytics_state"],"READY_FOR_REVIEW")
 def test_analytics_deterministic(self):self.assertEqual(analytics.analyze(self.journey,self.policy)["analytics_id"],analytics.analyze(self.journey,self.policy)["analytics_id"])
 def test_weight_trend(self):
  result=analytics.analyze(self.journey,self.policy);metric=next(x for x in result["metrics"] if x["metric"]=="weight_kg");self.assertEqual(metric["direction"],"DECREASE");self.assertEqual(metric["observation_count"],3)
 def test_source_event_ids_preserved(self):self.assertEqual(len(analytics.analyze(self.journey,self.policy)["metrics"][0]["source_event_ids"]),3)
 def test_evidence_refs_preserved(self):self.assertIn("CERT-PKS-000001",analytics.analyze(self.journey,self.policy)["metrics"][0]["evidence_refs"])
 def test_insufficient_data(self):self.assertEqual(analytics.analyze(self.low,self.policy)["analytics_state"],"INSUFFICIENT_DATA")
 def test_identifier_key_rejected(self):
  bad=json.loads((ROOT/"05_Monitoring/Retatrutide/Analytics/Examples/analytics_identifiable.example.json").read_text())
  with self.assertRaisesRegex(ValueError,"IDENTIFIABLE_INPUT_REJECTED"):analytics.analyze(bad,self.policy)
 def test_identifier_pattern_rejected(self):
  bad=json.loads(json.dumps(self.journey));bad["events"][0]["payload"]["notes"]="email person@example.com"
  with self.assertRaises(ValueError):analytics.analyze(bad,self.policy)
 def test_urgent_propagates(self):
  urgent=json.loads(json.dumps(self.journey));urgent["journey_state"]="LOCKED_URGENT_ROUTING";self.assertEqual(analytics.analyze(urgent,self.policy)["analytics_state"],"LOCKED_URGENT_ROUTING")
 def test_render_deterministic(self):
  a=analytics.analyze(self.journey,self.policy);m1,s1=render.render(a);m2,s2=render.render(a);self.assertEqual(m1,m2);self.assertEqual(s1,s2)
 def test_svg_has_no_script_or_external_url(self):
  _,svg=render.render(analytics.analyze(self.journey,self.policy));low=svg.lower();self.assertNotIn("<script",low);self.assertNotIn("href=\"http",low);self.assertNotIn("src=\"http",low)
 def test_alert_no_alert(self):self.assertEqual(alerts.evaluate(self.journey,analytics.analyze(self.journey,self.policy),self.schedule,self.policy)["alert_state"],"NO_ALERT")
 def test_alert_review_state(self):
  sched={**self.schedule,"schedule_state":"CLINICIAN_DISCUSSION_REQUIRED"};self.assertEqual(alerts.evaluate(self.journey,analytics.analyze(self.journey,self.policy),sched,self.policy)["alert_state"],"CLINICIAN_DISCUSSION_REQUIRED")
 def test_alert_insufficient(self):self.assertEqual(alerts.evaluate(self.low,analytics.analyze(self.low,self.policy),self.schedule,self.policy)["alert_state"],"INSUFFICIENT_DATA")
 def test_alert_urgent_precedence(self):
  urgent=json.loads(json.dumps(self.journey));urgent["journey_state"]="LOCKED_URGENT_ROUTING";self.assertEqual(alerts.evaluate(urgent,analytics.analyze(urgent,self.policy),self.schedule,self.policy)["alert_state"],"LOCKED_URGENT_ROUTING")
 def test_threshold_alert(self):
  changed=json.loads(json.dumps(self.journey));changed["events"][-1]["payload"]["weight_kg"]=90.0;result=analytics.analyze(changed,self.policy);self.assertEqual(alerts.evaluate(changed,result,self.schedule,self.policy)["alert_state"],"CLINICIAN_DISCUSSION_REQUIRED")
 def test_no_personalised_dosing_output(self):
  text=json.dumps(alerts.evaluate(self.journey,analytics.analyze(self.journey,self.policy),self.schedule,self.policy)).lower();self.assertNotIn("take ",text);self.assertIn("does not diagnose",text)
 def test_cli_pipeline(self):
  with tempfile.TemporaryDirectory() as td:
   td=Path(td);a=td/"analytics.json";m=td/"trend.json";s=td/"trend.svg";c=td/"alert.json"
   commands=[
    [sys.executable,"-B",str(ROOT/"Scripts/analyze_retatrutide_longitudinal_outcomes.py"),str(ROOT/"05_Monitoring/Retatrutide/Analytics/Examples/analytics_journey.example.json"),"--policy",str(ROOT/"13_Project_Genesis/AI/retatrutide_controlled_alerting_policy.json"),"--output",str(a)],
    [sys.executable,"-B",str(ROOT/"Scripts/render_retatrutide_outcome_trends.py"),str(a),"--output-json",str(m),"--output-svg",str(s)],
    [sys.executable,"-B",str(ROOT/"Scripts/evaluate_retatrutide_controlled_alerts.py"),str(ROOT/"05_Monitoring/Retatrutide/Analytics/Examples/analytics_journey.example.json"),str(a),str(ROOT/"05_Monitoring/Retatrutide/Analytics/Examples/review_schedule.example.json"),"--policy",str(ROOT/"13_Project_Genesis/AI/retatrutide_controlled_alerting_policy.json"),"--output",str(c)]]
   for command in commands:
    done=subprocess.run(command,capture_output=True,text=True,check=False);self.assertEqual(done.returncode,0,done.stderr)
   self.assertTrue(a.is_file() and m.is_file() and s.is_file() and c.is_file())
 def test_ui_memory_only(self):
  text=(ROOT/"13_Project_Genesis/UI/Retatrutide_Outcome_Analytics/app.js").read_text();self.assertNotIn("localStorage",text);self.assertNotIn("sessionStorage",text);self.assertNotIn("innerHTML",text)
 def test_lessons_include_build_0045_defects(self):
  text=(ROOT/"Documentation/Build_Records/0046/LESSONS_LEARNED_BASELINE.md").read_text().lower();self.assertIn("nativecommanderror",text);self.assertIn("external",text);self.assertIn("exact asset",text)
 def test_ps51_expected_negative_fixture_control(self):
  text=(ROOT/"Scripts/Invoke_Certiaura_Build_0046_Windows_PS51_Regression.ps1").read_text(encoding="ascii");self.assertIn('$SavedErrorActionPreference=$ErrorActionPreference',text);self.assertIn('$IdentifierExit=$LASTEXITCODE',text);self.assertIn('Rejected identifier input created output.',text)
if __name__=="__main__":unittest.main()
