from evidence_control_common import *
def validate(data):
    e=[]; w=[]
    require(data,["record_type","ingestion_id","citation_id","state","rights_check","deduplication","ingested_at"],e)
    if data.get("record_type")!="evidence_ingestion": e.append("record_type must be evidence_ingestion")
    require_enum(data,"state",{"DISCOVERED","RIGHTS_CHECKED","NORMALISED","DEDUPLICATED","INGESTED","TRIAGED","IN_REVIEW","APPROVED","CONDITIONAL","REJECTED","QUARANTINED","SUPERSEDED","RETRACTED"},e)
    rights=data.get("rights_check")
    if not isinstance(rights,dict): e.append("rights_check must be an object")
    elif rights.get("full_text_stored") is True and rights.get("status")!="PASS": e.append("Full text cannot be stored without a passing rights check")
    dedupe=data.get("deduplication")
    if not isinstance(dedupe,dict) or dedupe.get("status") not in {"UNIQUE","DUPLICATE","POSSIBLE_DUPLICATE"}: e.append("A valid deduplication status is required")
    return ValidationResult(not e,e,w)
if __name__=="__main__": cli(validate)
