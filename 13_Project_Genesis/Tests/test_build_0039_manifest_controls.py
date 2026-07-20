from __future__ import annotations
import csv, json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BUILD_RECORD=ROOT/"Documentation/Build_Records/0039"
class ManifestControls(unittest.TestCase):
    def test_manifest_covers_package(self):
        manifest=json.loads((BUILD_RECORD/"ASSET_INTENT_MANIFEST.json").read_text(encoding="utf-8"))
        declared={f["repository_path"] for f in manifest["files"]}
        with (BUILD_RECORD/"FILE_INVENTORY.csv").open("r",encoding="utf-8-sig",newline="") as handle:
            inventory={row["repository_path"] for row in csv.DictReader(handle)}
        self.assertEqual(declared,inventory)
        missing=sorted(path for path in declared if not (ROOT/Path(*path.split("/"))).is_file())
        self.assertEqual([],missing)
        with (BUILD_RECORD/"PACKAGE_CONTENT_SHA256.csv").open("r",encoding="utf-8-sig",newline="") as handle:
            hashed={row["repository_path"] for row in csv.DictReader(handle)}
        self_referential={
            "Documentation/Build_Records/0039/FILE_INVENTORY.csv",
            "Documentation/Build_Records/0039/PACKAGE_CONTENT_SHA256.csv",
        }
        self.assertEqual(declared-self_referential,hashed)
    def test_package_version(self):
        manifest=json.loads((BUILD_RECORD/"BUILD_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["package_version"],"1.3.2")
if __name__=="__main__": unittest.main()
