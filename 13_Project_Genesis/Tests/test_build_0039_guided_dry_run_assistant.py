from __future__ import annotations
import importlib.util, unittest
from pathlib import Path, PurePosixPath
class GuidedAssistant(unittest.TestCase):
    def test_core_has_run_importer(self):
        p=Path(__file__).resolve().parents[1]/"Tools/project_genesis_dry_run_core.py"; text=p.read_text(encoding="utf-8"); self.assertIn("def run_importer",text); self.assertIn("transactional_build_import.py",text)
if __name__=="__main__": unittest.main()
