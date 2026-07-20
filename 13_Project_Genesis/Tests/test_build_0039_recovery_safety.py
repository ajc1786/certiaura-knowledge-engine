from __future__ import annotations
import importlib.util, tempfile, unittest
from pathlib import Path, PurePosixPath
MODULE=Path(__file__).resolve().parents[1]/"Import"/"transactional_build_import.py"
spec=importlib.util.spec_from_file_location("tbi",MODULE); tbi=importlib.util.module_from_spec(spec); spec.loader.exec_module(tbi)
class RecoverySafety(unittest.TestCase):
    def test_preexisting_sibling_file_and_folder_survive(self):
        with tempfile.TemporaryDirectory() as td:
            repo=Path(td)/"repo"; target=repo/"06_Evidence/Standards"; target.mkdir(parents=True)
            sibling=target/"pre_existing_sibling.md"; sibling.write_text("keep",encoding="utf-8")
            nested=target/"Existing_Subfolder"; nested.mkdir(); nested_file=nested/"keep.txt"; nested_file.write_text("keep nested",encoding="utf-8")
            created=target/"transaction_created"; created.mkdir(); generated=created/"generated.txt"; generated.write_text("generated",encoding="utf-8")
            journal={"backup_root":str(Path(td)/"backup"),"created_files":[{"path":generated.relative_to(repo).as_posix(),"applied_sha256":tbi.sha256_file(generated)}],"replaced_files":[],"created_directories":[created.relative_to(repo).as_posix()]}
            result=tbi.recover_transaction(repo,journal,apply=True)
            self.assertFalse(generated.exists()); self.assertFalse(created.exists())
            self.assertEqual(sibling.read_text(),"keep"); self.assertEqual(nested_file.read_text(),"keep nested"); self.assertTrue(target.exists())
            self.assertFalse(result["recursive_directory_deletion_used"])
    def test_nonempty_transaction_directory_is_preserved(self):
        with tempfile.TemporaryDirectory() as td:
            repo=Path(td)/"repo"; created=repo/"Documentation/New"; created.mkdir(parents=True); (created/"unexpected_sibling.txt").write_text("preserve")
            journal={"backup_root":str(Path(td)/"backup"),"created_files":[],"replaced_files":[],"created_directories":[created.relative_to(repo).as_posix()]}
            result=tbi.recover_transaction(repo,journal,apply=True)
            self.assertTrue(created.exists()); self.assertTrue((created/"unexpected_sibling.txt").exists())
            self.assertTrue(any(a["action"]=="PRESERVE_NONEMPTY_DIRECTORY" for a in result["actions"]))
    def test_changed_created_file_is_not_deleted(self):
        with tempfile.TemporaryDirectory() as td:
            repo=Path(td)/"repo"; repo.mkdir(); f=repo/"new.txt"; f.write_text("original"); expected=tbi.sha256_file(f); f.write_text("user changed")
            journal={"backup_root":str(Path(td)/"backup"),"created_files":[{"path":"new.txt","applied_sha256":expected}],"replaced_files":[],"created_directories":[]}
            result=tbi.recover_transaction(repo,journal,apply=True); self.assertTrue(f.exists()); self.assertEqual(f.read_text(),"user changed")
            self.assertTrue(any(a["action"]=="PRESERVE_CHANGED_CREATED_FILE" for a in result["actions"]))
if __name__=="__main__": unittest.main()
