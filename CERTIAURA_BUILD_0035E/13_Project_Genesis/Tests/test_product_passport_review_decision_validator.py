import copy
import importlib.util
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[1]
VALIDATOR_PATH = ROOT / "Validators" / "validate_product_passport_review_decision.py"
EXAMPLES = ROOT.parent / "08_Product_Passports" / "Examples"

spec = importlib.util.spec_from_file_location("validator_0035e", VALIDATOR_PATH)
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validator)


def load(name):
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


class ReviewDecisionValidatorTests(unittest.TestCase):
    def test_valid_verified_passes(self):
        self.assertEqual([], validator.validate_review(load("valid_verified_review.example.json")))

    def test_valid_conditional_passes(self):
        self.assertEqual([], validator.validate_review(load("valid_conditional_review.example.json")))

    def test_invalid_verified_fails(self):
        self.assertGreaterEqual(len(validator.validate_review(load("invalid_verified_review.example.json"))), 10)

    def test_four_eyes_rule(self):
        data = load("valid_verified_review.example.json")
        data["review_team"]["final_approver"]["name"] = data["review_team"]["lead_reviewer"]["name"]
        self.assertTrue(any("four-eyes" in e for e in validator.validate_review(data)))

    def test_public_display_requires_verified_claim(self):
        data = load("valid_conditional_review.example.json")
        data["claim_reviews"][0]["public_display_approved"] = True
        self.assertTrue(any("public display" in e for e in validator.validate_review(data)))

    def test_verified_claim_requires_e4_or_e5(self):
        data = load("valid_verified_review.example.json")
        data["claim_reviews"][0]["evidence_class_awarded"] = "E3"
        self.assertTrue(any("E4 or E5" in e for e in validator.validate_review(data)))

    def test_marketplace_eligible_requires_verified(self):
        data = load("valid_conditional_review.example.json")
        data["decision"]["marketplace_eligibility"] = "ELIGIBLE"
        self.assertTrue(any("marketplace_eligibility" in e for e in validator.validate_review(data)))

    def test_invalid_transition(self):
        data = load("valid_verified_review.example.json")
        data["source_submission_status"] = "REJECTED"
        self.assertTrue(any("state transition" in e for e in validator.validate_review(data)))


if __name__ == "__main__":
    unittest.main()
