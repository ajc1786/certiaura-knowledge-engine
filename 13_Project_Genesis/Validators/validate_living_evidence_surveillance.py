from evidence_control_common import *
def validate(data):
    e=[]; w=[]
    rt=data.get("record_type")
    if rt=="living_evidence_surveillance_query":
        require(data,["query_id","question","search_expression","sources","cadence","owner","status"],e)
        if not str(data.get("search_expression","")).strip(): e.append("search_expression must not be blank")
        require_nonempty_list(data,"sources",e)
        require_enum(data,"cadence",{"DAILY","WEEKLY","MONTHLY","QUARTERLY","ON_DEMAND"},e)
        require_enum(data,"status",{"ACTIVE","PAUSED","RETIRED"},e)
    elif rt=="living_evidence_surveillance_event":
        require(data,["event_id","query_id","detected_at","classification","result_ids","triage"],e)
        require_enum(data,"classification",{"NO_CHANGE","POTENTIAL_UPDATE","URGENT_SAFETY","RETRACTION_OR_CORRECTION","METHOD_ONLY"},e)
        if data.get("classification") in {"URGENT_SAFETY","RETRACTION_OR_CORRECTION"} and not isinstance(data.get("triage"),dict): e.append("High-risk events require triage")
    else: e.append("Unsupported surveillance record_type")
    return ValidationResult(not e,e,w)
if __name__=="__main__": cli(validate)
