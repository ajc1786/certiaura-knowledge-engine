from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "05_Monitoring/Examples/Tesamorelin"


class Tests(unittest.TestCase):
    def test_accepted_pilot_states_are_coherent(self):
        acceptance = json.loads((EXAMPLES / "valid_pilot_acceptance_decision.example.json").read_text(encoding="utf-8"))
        evidence = json.loads((EXAMPLES / "valid_evidence_corpus_map.example.json").read_text(encoding="utf-8"))
        biological = json.loads((EXAMPLES / "valid_biological_boundary.example.json").read_text(encoding="utf-8"))
        safety = json.loads((EXAMPLES / "valid_safety_boundary.example.json").read_text(encoding="utf-8"))
        monitoring = json.loads((EXAMPLES / "valid_monitoring_model.example.json").read_text(encoding="utf-8"))
        self.assertEqual("BASELINE_MAPPED", acceptance["evidence_corpus_state"])
        self.assertEqual(evidence["coverage_state"], acceptance["evidence_corpus_state"])
        self.assertEqual(biological["boundary_state"], acceptance["biological_boundary_state"])
        self.assertEqual(safety["boundary_state"], acceptance["safety_boundary_state"])
        self.assertEqual(monitoring["model_state"], acceptance["monitoring_model_state"])
        self.assertEqual([], acceptance["open_critical_gaps"])

    def test_no_cross_peptide_equivalence(self):
        for path in EXAMPLES.glob("*.json"):
            record = json.loads(path.read_text(encoding="utf-8"))
            self.assertIs(False, record["clinical_equivalence_claimed"], path.name)
            self.assertIs(False, record["clinical_decision_support_authorised"], path.name)


if __name__ == "__main__":
    unittest.main()
