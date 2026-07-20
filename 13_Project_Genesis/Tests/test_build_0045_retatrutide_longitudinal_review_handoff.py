from __future__ import annotations
import importlib.util, json, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

record = load("record", Path("Scripts/record_retatrutide_longitudinal_event.py"))
schedule = load("schedule", Path("Scripts/generate_retatrutide_review_schedule.py"))
handoff = load("handoff", Path("Scripts/generate_retatrutide_clinician_handoff.py"))

class Build0045Tests(unittest.TestCase):
    def setUp(self):
        self.base = {
            "journey_id": "RJ-TEST0045",
            "version": "1.0.0",
            "journey_state": "ACTIVE",
            "events": [],
            "chain_head": "0" * 64,
        }
        self.event = {
            "journey_id": "RJ-TEST0045",
            "observed_at": "2026-07-01T09:00:00Z",
            "event_type": "BASELINE",
            "payload": {"weight_kg": 106.0},
            "source_refs": ["CERT-PKS-000001"],
        }
        self.policy = json.loads(
            (ROOT / "13_Project_Genesis/AI/retatrutide_review_scheduling_policy.json").read_text()
        )

    def test_append_event(self):
        self.assertEqual(len(record.append_event(self.base, self.event)["events"]), 1)

    def test_deterministic_event_id(self):
        first = record.append_event(self.base, self.event)["events"][0]["event_id"]
        second = record.append_event(self.base, self.event)["events"][0]["event_id"]
        self.assertEqual(first, second)

    def test_hash_chain_changes(self):
        one = record.append_event(self.base, self.event)
        two = record.append_event(one, {**self.event, "observed_at": "2026-07-02T09:00:00Z", "event_type": "MEASUREMENT"})
        self.assertNotEqual(one["chain_head"], two["chain_head"])

    def test_identifier_rejected(self):
        bad = {**self.event, "payload": {"question": "email me at person@example.com"}}
        with self.assertRaisesRegex(ValueError, "IDENTIFIABLE_INPUT_REJECTED"):
            record.append_event(self.base, bad)

    def test_phone_rejected(self):
        bad = {**self.event, "payload": {"question": "call 07123 456789"}}
        with self.assertRaises(ValueError):
            record.append_event(self.base, bad)

    def test_urgent_locks_journey(self):
        urgent = {**self.event, "event_type": "SYMPTOM", "payload": {"symptom": "severe abdominal pain"}}
        self.assertEqual(record.append_event(self.base, urgent)["journey_state"], "LOCKED_URGENT_ROUTING")

    def test_cli_appends_to_packaged_raw_seed(self):
        script = ROOT / "Scripts/record_retatrutide_longitudinal_event.py"
        seed = ROOT / "05_Monitoring/Retatrutide/Examples/longitudinal_journey_seed.example.json"
        urgent = ROOT / "05_Monitoring/Retatrutide/Examples/longitudinal_event_urgent.example.json"
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "urgent_journey.json"
            completed = subprocess.run(
                [sys.executable, "-B", str(script), str(urgent), "--journey", str(seed), "--output", str(output)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            result = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(result["journey_state"], "LOCKED_URGENT_ROUTING")
            self.assertEqual(len(result["events"]), 5)
            self.assertTrue(all(item.get("event_id") for item in result["events"]))
            self.assertTrue(all(item.get("event_hash") for item in result["events"]))

    def test_routine_schedule(self):
        journey = record.append_event(self.base, self.event)
        result = schedule.generate(journey, self.policy, "2026-07-02T00:00:00Z")
        self.assertEqual(result["schedule_state"], "ROUTINE")

    def test_overdue_schedule(self):
        journey = record.append_event(self.base, self.event)
        result = schedule.generate(journey, self.policy, "2026-08-02T00:00:00Z")
        self.assertEqual(result["schedule_state"], "CLINICIAN_DISCUSSION_REQUIRED")

    def test_urgent_schedule(self):
        urgent = {**self.event, "event_type": "SYMPTOM", "payload": {"symptom": "chest pain"}}
        journey = record.append_event(self.base, urgent)
        result = schedule.generate(journey, self.policy, "2026-07-01T10:00:00Z")
        self.assertEqual(result["schedule_state"], "LOCKED_URGENT_ROUTING")

    def test_handoff_ready(self):
        journey = record.append_event(self.base, self.event)
        sched = schedule.generate(journey, self.policy, "2026-07-02T00:00:00Z")
        self.assertEqual(handoff.generate(journey, sched)["handoff_state"], "READY_FOR_CLINICIAN_DISCUSSION")

    def test_handoff_urgent(self):
        urgent = {**self.event, "event_type": "SYMPTOM", "payload": {"symptom": "difficulty breathing"}}
        journey = record.append_event(self.base, urgent)
        sched = schedule.generate(journey, self.policy, "2026-07-01T10:00:00Z")
        self.assertEqual(handoff.generate(journey, sched)["handoff_state"], "URGENT_CLINICAL_ROUTING")

    def test_handoff_provenance(self):
        journey = record.append_event(self.base, self.event)
        sched = schedule.generate(journey, self.policy, "2026-07-02T00:00:00Z")
        self.assertIn("CERT-PKS-000001", handoff.generate(journey, sched)["provenance"]["source_refs"])

    def test_no_personalised_dosing_language(self):
        journey = record.append_event(self.base, self.event)
        sched = schedule.generate(journey, self.policy, "2026-07-02T00:00:00Z")
        text = json.dumps(handoff.generate(journey, sched)).lower()
        self.assertIn("does not diagnose", text)

    def test_ui_has_no_persistent_storage(self):
        text = (ROOT / "13_Project_Genesis/UI/Retatrutide_Longitudinal_Journey/app.js").read_text()
        self.assertNotIn("localStorage", text)
        self.assertNotIn("innerHTML", text)

    def test_internal_backup_control_documented(self):
        text = (ROOT / "Documentation/Build_Records/0045/LESSONS_LEARNED_BASELINE.md").read_text().lower()
        self.assertIn("outside", text)

    def test_ps51_expected_failure_is_captured_without_terminating_harness(self):
        text = (ROOT / "Scripts/Invoke_Certiaura_Build_0045_Windows_PS51_Regression.ps1").read_text(encoding="ascii")
        self.assertIn('$SavedErrorActionPreference=$ErrorActionPreference', text)
        self.assertIn('$ErrorActionPreference="Continue"', text)
        self.assertIn('$IdentifiableExit=$LASTEXITCODE', text)
        self.assertIn('if($IdentifiableExit -eq 0)', text)
        self.assertIn('Rejected identifiable input created an output file.', text)

if __name__ == "__main__":
    unittest.main()
