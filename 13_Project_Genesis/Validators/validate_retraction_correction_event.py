from evidence_control_common import *
def validate(data):
    e=[]; w=[]
    require(data,["record_type","event_id","citation_id","event_type","detected_at","authority","action_plan"],e)
    if data.get("record_type")!="retraction_correction_event": e.append("record_type must be retraction_correction_event")
    require_enum(data,"event_type",{"RETRACTION","CORRECTION","EXPRESSION_OF_CONCERN","WITHDRAWAL"},e)
    require_nonempty_list(data,"action_plan",e)
    return ValidationResult(not e,e,w)
if __name__=="__main__": cli(validate)
