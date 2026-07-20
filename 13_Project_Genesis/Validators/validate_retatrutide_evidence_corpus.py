#!/usr/bin/env python3
from __future__ import annotations
import argparse
import csv
import json
import re
import sys
from pathlib import Path

NOTICE = "Retatrutide remains investigational and is not approved for public use."
REQUIRED = {"evidence_id", "title", "source_type", "publication_status", "peer_review_status", "study_design", "primary_identifier", "source_url", "publication_date", "key_results", "safety_findings", "limitations", "claim_support", "evidence_tier", "review_status", "provenance", "investigational_status_notice"}

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def validate(root: Path) -> list[str]:
    errors: list[str] = []
    corpus_dir = root / "06_Evidence/Retatrutide/Corpus"
    index_path = root / "06_Evidence/Retatrutide/RETATRUTIDE_EVIDENCE_CORPUS_INDEX.json"
    graph_path = root / "06_Evidence/Retatrutide/RETATRUTIDE_CITATION_GRAPH.json"
    matrix_path = root / "06_Evidence/Retatrutide/RETATRUTIDE_CLAIM_EVIDENCE_MATRIX.csv"
    review_path = root / "06_Evidence/Retatrutide/RETATRUTIDE_SCIENTIFIC_REVIEW_BASELINE.json"
    watch_path = root / "06_Evidence/Retatrutide/RETATRUTIDE_LIVING_EVIDENCE_WATCH.json"
    for p in (corpus_dir, index_path, graph_path, matrix_path, review_path, watch_path):
        if not p.exists(): errors.append(f"Missing required path: {p.relative_to(root)}")
    if errors: return errors
    records = {}
    identifiers = set()
    for path in sorted(corpus_dir.glob("*.json")):
        try: data = load(path)
        except Exception as exc:
            errors.append(f"Invalid JSON {path.relative_to(root)}: {exc}"); continue
        missing = sorted(REQUIRED - set(data))
        if missing: errors.append(f"{path.name}: missing fields {missing}")
        eid = data.get("evidence_id", "")
        if not re.fullmatch(r"RET-EVD-\d{4}", eid): errors.append(f"{path.name}: invalid evidence_id {eid!r}")
        if eid in records: errors.append(f"Duplicate evidence_id: {eid}")
        records[eid] = data
        pid = data.get("primary_identifier") or {}
        key = (pid.get("type"), pid.get("value"))
        if not all(key): errors.append(f"{path.name}: incomplete primary_identifier")
        elif key in identifiers: errors.append(f"Duplicate primary_identifier: {key}")
        identifiers.add(key)
        if data.get("investigational_status_notice") != NOTICE: errors.append(f"{path.name}: investigational notice missing or changed")
        if data.get("peer_review_status") == "not_peer_reviewed" and "CONDITIONAL" not in data.get("review_status", "") and "STATUS_SOURCE" not in data.get("evidence_tier", ""):
            errors.append(f"{path.name}: non-peer-reviewed source is not conditional/status controlled")
        if data.get("source_type") == "clinical_trial_registry_record" and any("result" in x.lower() and "no final" not in x.lower() for x in data.get("key_results", [])):
            errors.append(f"{path.name}: registry record appears to be represented as results")
    index = load(index_path)
    index_ids = {x.get("evidence_id") for x in index.get("records", [])}
    if index_ids != set(records): errors.append("Corpus index IDs do not exactly match evidence files")
    for item in index.get("records", []):
        p = root / item.get("path", "")
        if not p.is_file(): errors.append(f"Index references missing path: {item.get('path')}")
    graph = load(graph_path)
    node_ids = [n.get("node_id") for n in graph.get("nodes", [])]
    if len(node_ids) != len(set(node_ids)): errors.append("Citation graph contains duplicate node IDs")
    node_set = set(node_ids)
    for edge in graph.get("edges", []):
        if edge.get("source") not in node_set or edge.get("target") not in node_set:
            errors.append(f"Broken graph edge: {edge.get('edge_id')}")
    matrix_claims = {}
    with matrix_path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            cid = row.get("claim_id", "")
            if cid in matrix_claims: errors.append(f"Duplicate claim_id: {cid}")
            matrix_claims[cid] = row
            eids = [x for x in row.get("evidence_ids", "").split("|") if x]
            if not eids: errors.append(f"Claim has no evidence: {cid}")
            for eid in eids:
                if eid not in records: errors.append(f"Claim {cid} references missing evidence {eid}")
            if not row.get("limitations"): errors.append(f"Claim lacks limitations: {cid}")
    graph_claims = {n for n in node_set if n.startswith("RET-CLM-")}
    if graph_claims != set(matrix_claims): errors.append("Graph claim nodes do not exactly match claim matrix")
    review = load(review_path)
    if review.get("review_outcome") != "CONDITIONALLY_ACCEPTED_AS_INVESTIGATIONAL_EVIDENCE_BASELINE": errors.append("Unexpected scientific review outcome")
    if NOTICE not in review.get("mandatory_public_notice", ""): errors.append("Review baseline lacks mandatory investigational notice")
    watch = load(watch_path)
    required_sources = {"PubMed", "ClinicalTrials.gov", "FDA", "MHRA", "EMA"}
    present = {x.get("source") for x in watch.get("sources", [])}
    if not required_sources <= present: errors.append("Living evidence watch omits a mandatory source")
    return errors

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--report")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    errors = validate(root)
    report = {"build_number": "0041", "valid": not errors, "evidence_count": len(list((root / "06_Evidence/Retatrutide/Corpus").glob("*.json"))) if (root / "06_Evidence/Retatrutide/Corpus").exists() else 0, "errors": errors}
    if args.report: Path(args.report).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1
if __name__ == "__main__": raise SystemExit(main())
