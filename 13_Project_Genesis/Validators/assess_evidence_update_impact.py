from evidence_control_common import *
def validate(data):
    e=[]; w=[]
    require(data,["record_type","impact_id","source_event_id","impact_level","affected_assets","required_actions","reviewer"],e)
    if data.get("record_type")!="evidence_update_impact": e.append("record_type must be evidence_update_impact")
    require_enum(data,"impact_level",{"NONE","MINOR","MATERIAL","URGENT_SAFETY"},e)
    require_human(data.get("reviewer"),e)
    if data.get("impact_level") in {"MATERIAL","URGENT_SAFETY"}:
        require_nonempty_list(data,"affected_assets",e); require_nonempty_list(data,"required_actions",e)
    return ValidationResult(not e,e,w)
if __name__=="__main__": cli(validate)
