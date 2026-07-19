from __future__ import annotations

import csv
import importlib.util
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve()
IMPORT_DIR = HERE.parents[1] / 'Import'
sys.path.insert(0, str(IMPORT_DIR))
from asset_register_reconciler import load_register, plan_reconciliation, resolve_register, RegisterError
from transactional_build_import import validate_member

FIELDS = ["Universal Asset Identifier", "Asset Title", "Knowledge System", "Repository Path", "Version", "Status", "Owner"]

class AssetRegisterTests(unittest.TestCase):
    def write_register(self, root: Path, rows):
        path = root / 'Database' / 'MASTER_ASSET_REGISTER.csv'
        path.parent.mkdir(parents=True)
        with path.open('w', encoding='utf-8', newline='') as fh:
            writer = csv.DictWriter(fh, fieldnames=FIELDS)
            writer.writeheader(); writer.writerows(rows)
        return path

    def asset(self, path='08_Product_Passports/Standards/TEST.md', title='Test', system='PPS'):
        return {"repository_path": path, "asset_title": title, "knowledge_system": system, "intended_action": "UPDATE", "allow_create_if_missing": True, "proposed_version": "1.0.0", "proposed_status": "ACTIVE"}

    def test_resolve_unique_register(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); expected = self.write_register(root, [])
            self.assertEqual(resolve_register(root), expected.resolve())

    def test_missing_register_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(RegisterError): resolve_register(Path(td))

    def test_ambiguous_register_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); self.write_register(root, [])
            other = root / 'Documentation' / 'MASTER_ASSET_REGISTER.csv'; other.parent.mkdir(); other.write_text(','.join(FIELDS)+'\n')
            with self.assertRaises(RegisterError): resolve_register(root)

    def test_preserves_existing_uai_by_path(self):
        rows = [{"Universal Asset Identifier": "CERT-PPS-000007", "Asset Title": "Old", "Knowledge System": "PPS", "Repository Path": "08_Product_Passports/Standards/TEST.md"}]
        result = plan_reconciliation(rows, [self.asset()], '0038')
        self.assertTrue(result['valid'])
        self.assertEqual(result['changes'][0]['uai'], 'CERT-PPS-000007')
        self.assertEqual(result['changes'][0]['action'], 'UPDATE')

    def test_allocates_next_uai_for_genuine_new_asset(self):
        rows = [{"Universal Asset Identifier": "CERT-PPS-000007", "Asset Title": "Existing", "Knowledge System": "PPS", "Repository Path": "08_Product_Passports/Standards/EXISTING.md"}]
        result = plan_reconciliation(rows, [self.asset()], '0038')
        self.assertTrue(result['valid'])
        self.assertEqual(result['changes'][0]['uai'], 'CERT-PPS-000008')
        self.assertEqual(result['changes'][0]['action'], 'CREATE')

    def test_incoming_explicit_identifiers_are_reserved_before_allocation(self):
        rows = []
        unnumbered = self.asset(
            path="08_Product_Passports/Standards/UNNUMBERED.md",
            title="Unnumbered",
            system="PPS",
        )
        explicit = self.asset(
            path="08_Product_Passports/Standards/EXPLICIT.md",
            title="Explicit",
            system="PPS",
        )
        explicit["existing_uai"] = "CERT-PPS-000001"
        result = plan_reconciliation(rows, [unnumbered, explicit], "0038")
        self.assertTrue(result["valid"], result["conflicts"])
        changes = {x["path"]: x["uai"] for x in result["changes"]}
        self.assertEqual(changes["08_Product_Passports/Standards/EXPLICIT.md"], "CERT-PPS-000001")
        self.assertEqual(changes["08_Product_Passports/Standards/UNNUMBERED.md"], "CERT-PPS-000002")

    def test_duplicate_uai_blocks(self):
        rows = [
            {"Universal Asset Identifier": "CERT-PPS-000007", "Asset Title": "A", "Knowledge System": "PPS", "Repository Path": "a"},
            {"Universal Asset Identifier": "CERT-PPS-000007", "Asset Title": "B", "Knowledge System": "PPS", "Repository Path": "b"},
        ]
        result = plan_reconciliation(rows, [], '0038')
        self.assertFalse(result['valid'])
        self.assertTrue(any(x['code'] == 'DUPLICATE_UAI' for x in result['conflicts']))

    def test_path_traversal_rejected(self):
        self.assertIn('UNSAFE_PATH', validate_member('../evil.txt'))

    def test_wrapper_root_rejected_as_unauthorised(self):
        self.assertIn('UNAUTHORISED_ROOT', validate_member('Certiaura_Build_0038/file.txt'))

if __name__ == '__main__':
    unittest.main()
