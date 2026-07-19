from __future__ import annotations
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]

class ManifestControls(unittest.TestCase):
    def test_manifest_is_complete(self):
        manifest_path = REPO / 'Documentation/Build_Records/0037/ASSET_INTENT_MANIFEST.json'
        data = json.loads(manifest_path.read_text(encoding='utf-8'))
        listed = {x['repository_path'] for x in data['package_files']}
        actual = {p.relative_to(REPO).as_posix() for p in REPO.rglob('*') if p.is_file()}
        self.assertEqual(actual, listed)

    def test_no_wrapper_and_allowed_roots(self):
        allowed = {'00_Governance','01_Knowledge_Systems','02_Peptides','03_Biology','04_Conditions','05_Monitoring','06_Evidence','07_Goals','08_Product_Passports','09_Cost_Intelligence','10_Marketplace','11_Academy','12_Reports','13_Project_Genesis','Assets','Database','Documentation','Images','Schemas','Scripts','Standards','Templates'}
        actual = {p.relative_to(REPO).parts[0] for p in REPO.rglob('*') if p.is_file()}
        self.assertTrue(actual <= allowed)
        self.assertFalse(any(x.lower().startswith(('certiaura_build_0037','build_0037')) for x in actual))

    def test_every_formal_asset_preserves_identity(self):
        data = json.loads((REPO / 'Documentation/Build_Records/0037/ASSET_INTENT_MANIFEST.json').read_text(encoding='utf-8'))
        formal = [x for x in data['package_files'] if x['classification'] == 'FORMAL_ASSET']
        self.assertGreaterEqual(len(formal), 10)
        self.assertTrue(all(x.get('preserve_existing_uai') is True for x in formal))
        self.assertTrue(all(x.get('intended_action') in {'CREATE','UPDATE','SUPERSEDE','RETIRE','NO_CHANGE'} for x in formal))

if __name__ == '__main__':
    unittest.main()
