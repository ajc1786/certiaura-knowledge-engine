import importlib.util
import json
import unittest
from pathlib import Path

HERE=Path(__file__).resolve()
ROOT=HERE.parents[2]
VALIDATOR=ROOT/'13_Project_Genesis'/'Validators'/'validate_passport_monitoring_run.py'
OUTPUT=ROOT/'08_Product_Passports'/'Examples'/'Output'
spec=importlib.util.spec_from_file_location('validator',VALIDATOR)
validator=importlib.util.module_from_spec(spec); spec.loader.exec_module(validator)

def load(name): return json.loads((OUTPUT/name).read_text(encoding='utf-8'))

class TestMonitoringValidator(unittest.TestCase):
    def test_valid_no_action_passes(self):
        self.assertEqual([],validator.validate(load('valid_no_action_run.example.json')))

    def test_valid_alert_run_passes(self):
        self.assertEqual([],validator.validate(load('valid_alert_run.example.json')))

    def test_invalid_positive_action_fails_many_controls(self):
        errors=validator.validate(load('invalid_auto_reinstatement_run.example.json'))
        self.assertGreaterEqual(len(errors),6)
        self.assertTrue(any('positive' in x.lower() for x in errors))

    def test_expired_requires_restrictive_action(self):
        d=load('valid_alert_run.example.json')
        target=next(x for x in d['checks'] if 'PASSPORT_EXPIRED' in x['finding_codes'])
        target['action_instruction']='QUEUE_REVIEW'
        self.assertTrue(any('PASSPORT_EXPIRED requires' in x for x in validator.validate(d)))

    def test_critical_requires_p0(self):
        d=load('valid_alert_run.example.json')
        alert=next(x for x in d['alerts'] if x['severity']=='CRITICAL')
        alert['priority']='P3'
        self.assertTrue(any('CRITICAL requires P0' in x for x in validator.validate(d)))

    def test_summary_must_reconcile(self):
        d=load('valid_alert_run.example.json'); d['summary']['alert_count']+=1
        self.assertTrue(any('summary.alert_count' in x for x in validator.validate(d)))

    def test_source_hash_required(self):
        d=load('valid_no_action_run.example.json'); d['checks'][0]['source_sha256']='bad'
        self.assertTrue(any('source_sha256' in x for x in validator.validate(d)))

    def test_immutable_audit_required(self):
        d=load('valid_no_action_run.example.json'); d['audit']['immutable_record']=False
        self.assertTrue(any('immutable_record' in x for x in validator.validate(d)))

if __name__=='__main__': unittest.main()
