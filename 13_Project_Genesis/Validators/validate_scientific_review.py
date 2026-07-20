from evidence_control_common import *
def validate(data):
    e=[]; w=[]
    require(data,["record_type","review_id","citation_id","reviewer","decision","certainty","limitations","reviewed_at"],e)
    if data.get("record_type")!="scientific_review": e.append("record_type must be scientific_review")
    require_human(data.get("reviewer"),e)
    require_enum(data,"decision",{"APPROVED","CONDITIONAL","REJECTED","ESCALATED","SUPERSEDED"},e)
    require_enum(data,"certainty",{"HIGH","MODERATE","LOW","VERY_LOW","INSUFFICIENT","NOT_APPLICABLE"},e)
    ai=data.get("ai_assistance",{})
    if isinstance(ai,dict) and ai.get("final_authority")=="ai": e.append("Artificial intelligence cannot be the final scientific authority")
    if data.get("decision")=="CONDITIONAL" and not data.get("limitations"): e.append("Conditional approval requires limitations")
    return ValidationResult(not e,e,w)
if __name__=="__main__": cli(validate)
