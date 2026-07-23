from __future__ import annotations
import py_compile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Tests(unittest.TestCase):
 def test_importer_compiles(self): py_compile.compile(str(ROOT/"13_Project_Genesis/Import/run_build_0059_import.py"),doraise=True)
 def test_importer_has_forced_failure_and_rollback(self):
  t=(ROOT/"13_Project_Genesis/Import/run_build_0059_import.py").read_text(); self.assertIn("FORCED_POST_APPLY_FAILURE",t); self.assertIn("ROLLBACK_STATE_EXACT",t)
 def test_importer_writes_lf(self): self.assertIn('newline="\\n"',(ROOT/"13_Project_Genesis/Import/run_build_0059_import.py").read_text())
