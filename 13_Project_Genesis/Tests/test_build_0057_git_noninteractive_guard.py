from __future__ import annotations
import subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Tests(unittest.TestCase):
 def test_guard_contract(self):
  t=(ROOT/"Scripts/Invoke_Certiaura_Git_NonInteractive_Guard.ps1").read_text(encoding="utf-8");
  for x in ["gc.auto","maintenance.auto","gc.autoDetach","GIT_TERMINAL_PROMPT","finally","Restore-CertiauraGitLocalConfigState"]: self.assertIn(x,t)
 def test_close_uses_guard(self):
  t=(ROOT/"Scripts/Close_Certiaura_Build_0057.ps1").read_text(encoding="utf-8"); self.assertIn("Invoke-CertiauraGitNonInteractiveGuard",t); self.assertIn("BUILD_0057_COMMITTED_PUSHED",t); self.assertIn("BUILD_0057_GITHUB_ACTIONS_GREEN",t)
 def test_git_config_restore_model(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d); subprocess.run(["git","init",str(p)],check=True,stdout=subprocess.PIPE); subprocess.run(["git","-C",str(p),"config","gc.auto","7"],check=True); before=subprocess.check_output(["git","-C",str(p),"config","--get","gc.auto"],text=True).strip(); subprocess.run(["git","-C",str(p),"config","gc.auto","0"],check=True); subprocess.run(["git","-C",str(p),"config","gc.auto",before],check=True); after=subprocess.check_output(["git","-C",str(p),"config","--get","gc.auto"],text=True).strip(); self.assertEqual(before,after)
if __name__=="__main__": unittest.main()
