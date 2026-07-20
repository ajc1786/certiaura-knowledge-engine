from evidence_control_common import *
def validate(data):
    e=[]; w=[]
    require(data,["record_type","citation_id","title","source_type","identifiers","retrieved_at","rights","review_status","content_hash"],e)
    if data.get("record_type")!="citation_provenance": e.append("record_type must be citation_provenance")
    require_enum(data,"review_status",{"unreviewed","human_verified","rejected","quarantined"},e)
    require_sha256(data.get("content_hash"),"content_hash",e)
    rights=data.get("rights")
    if not isinstance(rights,dict) or not rights.get("basis"): e.append("rights.basis is required")
    if data.get("approved_for_claim_use") is True and data.get("review_status")!="human_verified": e.append("Claim use requires human_verified review status")
    return ValidationResult(not e,e,w)
if __name__=="__main__": cli(validate)
