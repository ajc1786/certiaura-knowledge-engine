from __future__ import annotations
import ast,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Tests(unittest.TestCase):
 def test_importer_compiles(self): ast.parse((ROOT/"13_Project_Genesis/Import/run_build_0058_import.py").read_text())
 def test_importer_has_forced_failure_and_rollback(self):
  t=(ROOT/"13_Project_Genesis/Import/run_build_0058_import.py").read_text(); self.assertIn("force_failure_after_apply",t); self.assertIn("ROLLBACK_STATE_EXACT",t)
 def test_importer_writes_lf(self): self.assertIn('newline="\\n"',(ROOT/"13_Project_Genesis/Import/run_build_0058_import.py").read_text())
if __name__=="__main__": unittest.main()
