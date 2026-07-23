from __future__ import annotations
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.text=(ROOT/"Scripts/Close_Certiaura_Build_0058.ps1").read_text(encoding="utf-8")
 def test_close_script_uses_guard(self): self.assertIn("Invoke-CertiauraGitNonInteractiveGuard",self.text)
 def test_close_script_requires_no_prompt_endpoint(self): self.assertIn("NO_MANUAL_GIT_OBJECT_CLEANUP_PROMPTS",self.text)
 def test_close_script_emits_guard_validation(self): self.assertIn("BUILD_0058_GIT_NONINTERACTIVE_GUARD_VALIDATED",self.text)
 def test_close_script_requires_exact_actions(self):
  for token in ["Certiaura Repository Validation","completed","success","head_sha","head_branch","event"]: self.assertIn(token,self.text)
if __name__=="__main__": unittest.main()
