from __future__ import annotations
import unittest
from pathlib import Path, PurePosixPath
class RepositoryValidatorAssets(unittest.TestCase):
    def test_required_recovery_assets_present(self):
        root=Path(__file__).resolve().parents[2]
        self.assertTrue((root/"13_Project_Genesis/Import/recover_failed_build_import.py").is_file())
        self.assertTrue((root/"Documentation/Build_Records/0039/RECOVERY_UTILITY_SAFETY_STANDARD.md").is_file())
if __name__=="__main__": unittest.main()
