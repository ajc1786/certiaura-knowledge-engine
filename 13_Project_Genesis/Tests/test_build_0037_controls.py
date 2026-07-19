from __future__ import annotations
import importlib.util
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
FIX = HERE / 'Fixtures' / 'Build_0037'
VAL = REPO / '13_Project_Genesis' / 'Validators'


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

claim = module('claim_validator', VAL / 'validate_scientific_claim.py')
comms = module('comms_validator', VAL / 'validate_communication_approval.py')
ai = module('ai_validator', VAL / 'validate_ai_recommendation_output.py')


def load(name):
    return json.loads((FIX / name).read_text(encoding='utf-8'))

class Build0037ControlTests(unittest.TestCase):
    def test_valid_scientific_claim(self):
        self.assertEqual([], claim.validate(load('valid_scientific_claim.example.json')))

    def test_conditional_commercial_claim(self):
        self.assertEqual([], claim.validate(load('conditional_commercial_claim.example.json')))

    def test_invalid_medicinal_claim(self):
        errors = claim.validate(load('invalid_medicinal_claim.example.json'))
        self.assertGreaterEqual(len(errors), 5)

    def test_valid_communication(self):
        self.assertEqual([], comms.validate(load('valid_communication_approval.example.json')))

    def test_invalid_public_pom_communication(self):
        errors = comms.validate(load('invalid_public_pom_communication.example.json'))
        self.assertTrue(any('prescription-only' in e for e in errors))
        self.assertTrue(any('disclosure' in e for e in errors))

    def test_valid_ai_educational_output(self):
        self.assertEqual([], ai.validate(load('valid_ai_educational_output.example.json')))

    def test_invalid_ai_dose_output(self):
        errors = ai.validate(load('invalid_ai_dose_output.example.json'))
        self.assertGreaterEqual(len(errors), 6)

    def test_all_schemas_parse(self):
        for schema in (REPO / 'Schemas').glob('*.schema.json'):
            json.loads(schema.read_text(encoding='utf-8'))

if __name__ == '__main__':
    unittest.main()
