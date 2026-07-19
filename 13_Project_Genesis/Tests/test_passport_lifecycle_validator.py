import importlib.util, json, unittest
from pathlib import Path

HERE=Path(__file__).resolve()
ROOT=HERE.parents[2]
VALIDATOR=ROOT/'13_Project_Genesis'/'Validators'/'validate_passport_lifecycle.py'
EXAMPLES=ROOT/'08_Product_Passports'/'Examples'
spec=importlib.util.spec_from_file_location('validator',VALIDATOR)
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

def load(name): return json.loads((EXAMPLES/name).read_text(encoding='utf-8'))

class TestLifecycleValidator(unittest.TestCase):
    def test_valid_published_passes(self): self.assertEqual([],mod.validate(load('valid_published.example.json')))
    def test_valid_suspended_passes(self): self.assertEqual([],mod.validate(load('valid_suspended.example.json')))
    def test_invalid_fails_many_controls(self): self.assertGreaterEqual(len(mod.validate(load('invalid_active_listing.example.json'))),12)
    def test_unresolved_critical_blocks_published(self):
        d=load('valid_published.example.json'); d['lifecycle_events']=[{'event_id':'PPS-EVT-T-001','event_type':'REPORT_INTEGRITY_DISPUTE','severity':'CRITICAL','detected_at':'2026-07-18T12:00:00Z','source':'Test','description':'Open critical event','required_action':'Suspend','owner':'Test','due_date':'2026-07-18','status':'OPEN','resolved_at':None,'resolution':None,'resulting_passport_state':None,'resulting_marketplace_state':None}]; d['marketplace']['unresolved_high_or_critical_trigger']=True
        self.assertTrue(any('PUBLISHED prohibited' in x for x in mod.validate(d)))
    def test_marketplace_requires_published(self):
        d=load('valid_published.example.json'); d['lifecycle_state']='READY_FOR_PUBLICATION'
        self.assertTrue(any('active marketplace requires PUBLISHED' in x for x in mod.validate(d)))
    def test_public_claim_requires_e4_or_e5(self):
        d=load('valid_published.example.json'); d['public_claims'][0]['evidence_class']='E3'
        self.assertTrue(any('E4 or E5' in x for x in mod.validate(d)))
    def test_suspended_requires_inactive_marketplace(self):
        d=load('valid_suspended.example.json'); d['marketplace']['marketplace_state']='ELIGIBLE'
        self.assertTrue(any('suspended passport' in x for x in mod.validate(d)))
    def test_expiry_cannot_exceed_review(self):
        d=load('valid_published.example.json'); d['publication']['effective_until']='2027-02-18'; d['publication']['next_review_date']='2027-02-18'
        self.assertTrue(any('controlling review effective date' in x for x in mod.validate(d)))
    def test_audit_is_immutable(self):
        d=load('valid_published.example.json'); d['audit']['immutable_record']=False
        self.assertTrue(any('immutable_record' in x for x in mod.validate(d)))
    def test_claim_review_link_must_match(self):
        d=load('valid_published.example.json'); d['public_claims'][0]['source_review_decision_id']='OTHER'
        self.assertTrue(any('must match controlling review' in x for x in mod.validate(d)))

if __name__=='__main__': unittest.main()
