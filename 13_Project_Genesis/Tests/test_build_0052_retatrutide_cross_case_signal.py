from __future__ import annotations
import importlib.util
import json
import unittest
from pathlib import Path

GENESIS = Path(__file__).resolve().parents[1]
PACKAGE = Path(__file__).resolve().parents[2]
VALIDATOR = GENESIS / "Validators" / "validate_retatrutide_cross_case_signal.py"
spec = importlib.util.spec_from_file_location("signal_validator", VALIDATOR)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SignalTests(unittest.TestCase):
    def load(self, name):
        return json.loads((PACKAGE / "05_Monitoring/Examples/Retatrutide" / name).read_text(encoding="utf-8"))

    def test_valid(self):
        self.assertEqual([], module.validate(self.load("valid_cross_case_watch_signal.example.json")))

    def test_conditional(self):
        self.assertEqual([], module.validate(self.load("conditional_insufficient_cohort.example.json")))

    def test_invalid(self):
        self.assertTrue(module.validate(self.load("invalid_autonomous_cross_case_action.example.json")))


if __name__ == "__main__":
    unittest.main()
