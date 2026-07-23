import py_compile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; I=ROOT/"13_Project_Genesis/Import/run_build_0060_import.py"; V=ROOT/"13_Project_Genesis/Validators/validate_build_0060_repository.py"
class Tests(unittest.TestCase):
 def test_importer_compiles(self): py_compile.compile(str(I),doraise=True)
 def test_repository_validator_compiles(self): py_compile.compile(str(V),doraise=True)
 def test_importer_has_forced_failure_and_rollback(self):
  t=I.read_text(); self.assertIn("FORCED_POST_APPLY_FAILURE",t); self.assertIn("ROLLBACK_STATE_EXACT",t); self.assertIn("CLEAN_REAPPLY_VALIDATED",t)
 def test_importer_writes_lf(self): self.assertNotIn(b"\r\n",I.read_bytes())
 def test_windows_report_path_self_exclusion_carried_forward(self): self.assertIn('replace("\\\\","/")',V.read_text())
if __name__=="__main__": unittest.main()
