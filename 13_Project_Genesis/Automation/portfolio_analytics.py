from datetime import datetime

def _num(v):
    return float(v) if isinstance(v,(int,float)) else 0.0

def calculate_metrics(data):
    suppliers=data.get('suppliers',[]) if isinstance(data,dict) else []
    pcts=[_num(x.get('spend_percent')) for x in suppliers if isinstance(x,dict)]
    pcts=sorted(pcts, reverse=True)
    hhi=round(sum(x*x for x in pcts))
    max_pct=round(max(pcts),2) if pcts else 0
    top3=round(sum(pcts[:3]),2)
    critical_single=0
    for c in data.get('categories',[]):
        if not isinstance(c,dict) or not c.get('critical'): continue
        active=c.get('active_alternatives') if isinstance(c.get('active_alternatives'),list) else []
        mit=c.get('mitigation') if isinstance(c.get('mitigation'),dict) else {}
        approved_mitigation=mit.get('status')=='APPROVED' and mit.get('owner_id') and mit.get('due_at') and mit.get('approved_by')
        if not active and not approved_mitigation: critical_single += 1
    return {'hhi':hhi,'max_supplier_percent':max_pct,'top_three_percent':top3,'critical_single_source_count':critical_single}

def resilience_rating(data):
    m=calculate_metrics(data)
    if m['critical_single_source_count']>0 or m['max_supplier_percent']>60 or m['hhi']>2500 or m['top_three_percent']>90:
        return 'RED'
    if m['max_supplier_percent']>40 or m['hhi']>1800 or m['top_three_percent']>75 or data.get('resilience',{}).get('open_actions'):
        return 'AMBER'
    return 'GREEN'

def calculate(data):
    metrics=calculate_metrics(data)
    rating=resilience_rating(data)
    alerts=[]
    if metrics['critical_single_source_count']:
        alerts.append('UNMITIGATED_CRITICAL_SINGLE_SOURCE')
    if metrics['max_supplier_percent']>60: alerts.append('MAX_SUPPLIER_RED')
    elif metrics['max_supplier_percent']>40: alerts.append('MAX_SUPPLIER_AMBER')
    if metrics['hhi']>2500: alerts.append('HHI_RED')
    elif metrics['hhi']>1800: alerts.append('HHI_AMBER')
    if metrics['top_three_percent']>90: alerts.append('TOP_THREE_RED')
    elif metrics['top_three_percent']>75: alerts.append('TOP_THREE_AMBER')
    return {'metrics':metrics,'recommended_resilience_rating':rating,'alerts':alerts,'automatic_award_prohibited':True,'human_decision_required':True}
