import importlib.util, json, unittest
from datetime import datetime
from pathlib import Path
HERE=Path(__file__).resolve(); ROOT=HERE.parents[2]; EX=ROOT/'10_Marketplace'/'Examples'
def module(name,rel):
 p=ROOT/rel; s=importlib.util.spec_from_file_location(name,p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
analytics=module('analytics','13_Project_Genesis/Automation/portfolio_analytics.py')
ranker=module('ranker','13_Project_Genesis/Automation/rank_sourcing_options.py')
monitor=module('monitor','13_Project_Genesis/Automation/monitor_service_levels.py')
def load(n): return json.loads((EX/n).read_text(encoding='utf-8'))
class Test0035JAnalytics(unittest.TestCase):
 def test_diversified_metrics(self): self.assertEqual({'hhi':2160,'max_supplier_percent':28.0,'top_three_percent':72.0,'critical_single_source_count':0},analytics.calculate_metrics(load('valid_diversified_portfolio.example.json')))
 def test_concentrated_metrics(self): self.assertEqual(4150,analytics.calculate_metrics(load('valid_concentrated_mitigated_portfolio.example.json'))['hhi'])
 def test_diversified_rating_amber_due_actions(self): self.assertEqual('AMBER',analytics.resilience_rating(load('valid_diversified_portfolio.example.json')))
 def test_recommendation_only(self): self.assertTrue(ranker.rank(load('valid_sourcing_decision.example.json'))['recommendation_only'])
 def test_recommended_supplier(self): self.assertEqual('SUP-000002',ranker.rank(load('valid_sourcing_decision.example.json'))['recommended_supplier_id'])
 def test_suspended_candidate_ineligible(self): self.assertIsNone(ranker.rank(load('invalid_automatic_sole_source_award.example.json'))['recommended_supplier_id'])
 def test_clean_service_alerts(self): self.assertEqual([],monitor.alerts_for(load('valid_diversified_portfolio.example.json'),datetime.fromisoformat('2026-07-19T12:00:00+00:00')))
 def test_breach_alert(self):
  d=load('valid_diversified_portfolio.example.json'); d['suppliers'][0]['sla']['on_time_in_full_percent']=80; a=monitor.alerts_for(d,datetime.fromisoformat('2026-07-19T12:00:00+00:00')); self.assertEqual('CRITICAL',a[0]['severity'])
 def test_alert_never_positive(self):
  d=load('valid_diversified_portfolio.example.json'); d['suppliers'][0]['sla']['on_time_in_full_percent']=80; self.assertTrue(all(x['automatic_positive_action'] is False for x in monitor.alerts_for(d,datetime.fromisoformat('2026-07-19T12:00:00+00:00'))))
if __name__=='__main__': unittest.main()
