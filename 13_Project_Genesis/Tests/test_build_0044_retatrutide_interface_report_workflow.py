from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[2]
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

def load_module(name: str, relative: str):
    path = REPOSITORY / relative
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module

renderer = load_module("build0044_renderer", "Scripts/render_retatrutide_branded_report.py")
conversation = load_module("build0044_conversation", "Scripts/run_retatrutide_controlled_conversation.py")
server = load_module("build0044_server", "Scripts/serve_retatrutide_patient_interface.py")
validator = load_module("build0044_validator", "13_Project_Genesis/Validators/validate_build_0044_retatrutide_interface_report_workflow.py")

class Build0044Tests(unittest.TestCase):
    def load(self, relative: str):
        return json.loads((REPOSITORY / relative).read_text(encoding="utf-8"))

    def run_conversation(self, example: str):
        policy = self.load("13_Project_Genesis/AI/retatrutide_controlled_conversation_policy.json")
        request = self.load("13_Project_Genesis/AI/Examples/" + example)
        return conversation.run_session(request, REPOSITORY, policy)

    def test_01_json_assets_parse(self):
        for relative in validator.build_owned_text_paths(REPOSITORY):
            path = REPOSITORY / relative
            if path.suffix.lower() == ".json":
                json.loads(path.read_text(encoding="utf-8"))

    def test_02_renderer_is_deterministic_and_escapes_input(self):
        report = self.load("12_Reports/Retatrutide/Examples/branded_patient_report_input.example.json")
        tokens = self.load("Templates/retatrutide_report_brand_tokens.json")
        report["patient_reference"] = "<script>alert(1)</script>"
        first_html, first_manifest = renderer.render(report, tokens)
        second_html, second_manifest = renderer.render(report, tokens)
        self.assertEqual(first_html, second_html)
        self.assertEqual(first_manifest, second_manifest)
        self.assertNotIn("<script>alert(1)</script>", first_html)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", first_html)
        self.assertFalse(first_manifest["remote_dependencies"])

    def test_03_grounded_conversation(self):
        result = self.run_conversation("controlled_conversation_valid.example.json")
        self.assertEqual(result["turn_count"], 2)
        self.assertIn(result["session_state"], {"ACTIVE_GROUNDED", "ACTIVE_WITH_ABSTENTION"})
        self.assertTrue(all(exchange["response_state"] in {
            "ANSWERED_GROUNDED", "ABSTAINED_INSUFFICIENT_EVIDENCE"
        } for exchange in result["exchanges"]))

    def test_04_personal_dosing_is_refused(self):
        result = self.run_conversation("controlled_conversation_personal_dosing.example.json")
        self.assertEqual(result["exchanges"][0]["response_state"], "REFUSED_SAFETY_BOUNDARY")
        self.assertEqual(result["session_state"], "SAFETY_BOUNDARY_ENFORCED")

    def test_05_urgent_state_locks_following_turn(self):
        result = self.run_conversation("controlled_conversation_urgent.example.json")
        self.assertTrue(result["urgent_lock"])
        self.assertEqual(result["session_state"], "LOCKED_URGENT_ROUTING")
        self.assertEqual(result["exchanges"][0]["response_state"], "URGENT_CLINICAL_ROUTING")
        self.assertEqual(result["exchanges"][1]["response_state"], "URGENT_CLINICAL_ROUTING")

    def test_06_direct_identifier_is_rejected(self):
        result = self.run_conversation("controlled_conversation_identifiable_input.example.json")
        self.assertEqual(result["exchanges"][0]["response_state"], "REFUSED_IDENTIFIABLE_INPUT")
        self.assertEqual(result["session_state"], "IDENTIFIABLE_INPUT_REJECTED")

    def test_07_turn_limit_is_enforced(self):
        request = self.load("13_Project_Genesis/AI/Examples/controlled_conversation_valid.example.json")
        request["turns"] = [request["turns"][0]] * 13
        policy = self.load("13_Project_Genesis/AI/retatrutide_controlled_conversation_policy.json")
        with self.assertRaisesRegex(ValueError, "Turn limit exceeded"):
            conversation.run_session(request, REPOSITORY, policy)

    def test_08_server_rejects_non_loopback_binding(self):
        with self.assertRaisesRegex(ValueError, "loopback"):
            server.validate_bind_host("0.0.0.0")

    def test_09_ui_has_no_unsafe_dom_or_persistent_storage(self):
        ui_root = REPOSITORY / "13_Project_Genesis/UI/Retatrutide_Patient_Interface"
        text = "\n".join(path.read_text(encoding="utf-8") for path in ui_root.iterdir() if path.is_file())
        for forbidden in [
            "innerHTML", "outerHTML", "document.write", "localStorage",
            "sessionStorage", "indexedDB", "http://", "https://"
        ]:
            self.assertNotIn(forbidden, text)

    def test_10_example_pdf_has_structural_markers(self):
        path = REPOSITORY / "Documentation/Build_Records/0044/EXAMPLE_BRANDED_PATIENT_REPORT.pdf"
        data = path.read_bytes()
        self.assertGreater(len(data), 1024)
        self.assertTrue(data.startswith(b"%PDF-"))
        self.assertIn(b"%%EOF", data[-4096:])

    def test_11_powershell_is_ascii_lf_and_parser_safe_source(self):
        for path in REPOSITORY.glob("Scripts/*0044*.ps1"):
            data = path.read_bytes()
            self.assertFalse(any(byte > 127 for byte in data), path.name)
            self.assertNotIn(b"\r", data, path.name)
            self.assertTrue(data.endswith(b"\n"), path.name)

    def test_12_build_text_has_no_trailing_whitespace(self):
        for relative in validator.build_owned_text_paths(REPOSITORY):
            path = REPOSITORY / relative
            data = path.read_bytes()
            self.assertNotIn(b"\r", data, path.as_posix())
            self.assertTrue(data.endswith(b"\n"), path.as_posix())
            for line in data.splitlines():
                self.assertFalse(line.endswith((b" ", b"\t")), path.as_posix())

    def test_13_validator_scope_uses_exact_ownership_not_numeric_substrings(self):
        owned = set(validator.build_owned_text_paths(REPOSITORY))
        self.assertNotIn("03_Biology/CERT-BKS-000044_Amylin.md", owned)
        self.assertNotIn("04_Conditions/CERT-CKS-000044_Condition.md", owned)
        self.assertTrue(any(path.startswith("Documentation/Build_Records/0044/") for path in owned))
        self.assertTrue(any(path.startswith("12_Reports/Retatrutide/Patient_Interface/CERT-RKS-") for path in owned))

if __name__ == "__main__":
    unittest.main()
