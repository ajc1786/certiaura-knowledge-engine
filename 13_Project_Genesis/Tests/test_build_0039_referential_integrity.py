from __future__ import annotations
import json, unittest
from pathlib import Path, PurePosixPath
ROOT=Path(__file__).resolve().parents[2]
class ReferentialIntegrity(unittest.TestCase):
    def test_fixture_references(self):
        f=ROOT/"13_Project_Genesis/Tests/Fixtures/Build_0039"
        cit=json.loads((f/"valid_citation.example.json").read_text()); cid=cit["citation_id"]
        for name in ["valid_evidence_ingestion.example.json","valid_retraction_event.example.json","valid_scientific_review.example.json"]:
            self.assertEqual(json.loads((f/name).read_text())["citation_id"],cid)
    def test_surveillance_event_query(self):
        f=ROOT/"13_Project_Genesis/Tests/Fixtures/Build_0039"
        q=json.loads((f/"valid_surveillance_query.example.json").read_text()); e=json.loads((f/"valid_surveillance_event.example.json").read_text()); self.assertEqual(e["query_id"],q["query_id"])
if __name__=="__main__": unittest.main()
