import importlib.util
import json
import unittest
from datetime import datetime
from pathlib import Path

HERE=Path(__file__).resolve()
ROOT=HERE.parents[2]
ENGINE=ROOT/'13_Project_Genesis'/'Automation'/'run_passport_monitor.py'
INPUT=ROOT/'08_Product_Passports'/'Examples'/'Input'
spec=importlib.util.spec_from_file_location('engine',ENGINE)
engine=importlib.util.module_from_spec(spec); spec.loader.exec_module(engine)

def load(name): return json.loads((INPUT/name).read_text(encoding='utf-8'))
AS_OF=datetime.fromisoformat('2026-07-18T09:00:00+00:00')

class TestMonitorEngine(unittest.TestCase):
    def run_one(self,name,run_id='PPS-MON-TEST-001'):
        return engine.build_run([load(name)],run_id=run_id,run_type='SCHEDULED',as_of=AS_OF,executed_by='Test')

    def test_current_record_has_no_alerts(self):
        r=self.run_one('current_passport.example.json')
        self.assertEqual(0,r['summary']['alert_count'])
        self.assertEqual('COMPLETED',r['run']['run_status'])

    def test_seven_day_expiry_alert(self):
        r=self.run_one('expiring_passport.example.json')
        codes=r['checks'][0]['finding_codes']
        self.assertIn('PASSPORT_EXPIRY_7D',codes)
        self.assertTrue(r['summary']['alert_count']>=1)

    def test_expired_auto_expires_and_removes_marketplace(self):
        r=self.run_one('expired_passport.example.json')
        c=r['checks'][0]
        self.assertEqual('AUTO_SUSPEND',c['action_instruction'])  # upstream review is also expired and stricter
        self.assertEqual('SUSPENDED',c['proposed_passport_state'])
        self.assertEqual('SUSPENDED',c['proposed_marketplace_state'])
        self.assertIn('PASSPORT_EXPIRED',c['finding_codes'])
        self.assertIn('UPSTREAM_REVIEW_EXPIRED',c['finding_codes'])

    def test_critical_trigger_auto_suspends(self):
        r=self.run_one('critical_trigger_passport.example.json')
        c=r['checks'][0]
        self.assertEqual('AUTO_SUSPEND',c['action_instruction'])
        self.assertEqual('SUSPENDED',c['proposed_passport_state'])
        self.assertTrue(any(x.startswith('OPEN_CRITICAL_TRIGGER') for x in c['finding_codes']))

    def test_deduplication_is_stable(self):
        a=self.run_one('expiring_passport.example.json','PPS-MON-TEST-002')
        b=self.run_one('expiring_passport.example.json','PPS-MON-TEST-003')
        keys_a={x['dedupe_key'] for x in a['alerts']}
        keys_b={x['dedupe_key'] for x in b['alerts']}
        self.assertEqual(keys_a,keys_b)

    def test_engine_is_read_only(self):
        source=load('critical_trigger_passport.example.json')
        before=json.dumps(source,sort_keys=True)
        engine.build_run([source],run_id='PPS-MON-TEST-004',run_type='SCHEDULED',as_of=AS_OF,executed_by='Test')
        self.assertEqual(before,json.dumps(source,sort_keys=True))

if __name__=='__main__': unittest.main()
