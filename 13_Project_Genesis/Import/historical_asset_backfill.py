from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from asset_register_reconciler import (
    _write_register,
    infer_system,
    load_register,
    norm_path,
    plan_reconciliation,
    resolve_register,
)

UAI_RE = re.compile(r"\bCERT-[A-Z]+-\d{6}\b")
STRONG_UAI_RE = re.compile(
    r"(?:Universal\s+Asset\s+Identifier|UAI|Asset\s+ID|Document\s+ID)\s*\*{0,2}\s*[:|]\s*\*{0,2}\s*`?(CERT-[A-Z]+-\d{6})`?",
    re.I,
)
VERSION_RE = re.compile(r"(?:^|\n)\s*(?:\*\*)?Version(?:\*\*)?\s*[:|]\s*`?([0-9]+(?:\.[0-9A-Za-z_-]+){1,3})`?", re.I)
STATUS_RE = re.compile(r"(?:^|\n)\s*(?:\*\*)?Status(?:\*\*)?\s*[:|]\s*`?([^\n`]+)", re.I)
OWNER_RE = re.compile(r"(?:^|\n)\s*(?:\*\*)?Owner(?:\*\*)?\s*[:|]\s*`?([^\n`]+)", re.I)
TITLE_RE = re.compile(r"(?:^|\n)\s*#\s+([^\n]+)")

DEFAULT_POLICY: dict[str, Any] = {
    "policy_version": "1.0.0",
    "canonical_roots": [
        "00_Governance", "01_Knowledge_Systems", "02_Peptides", "03_Biology",
        "04_Conditions", "05_Monitoring", "06_Evidence", "07_Goals",
        "08_Product_Passports", "09_Cost_Intelligence", "10_Marketplace",
        "11_Academy", "12_Reports", "13_Project_Genesis", "Assets", "Database",
        "Documentation", "Images", "Schemas", "Scripts", "Standards", "Templates"
    ],
    "excluded_directory_names": [
        ".git", ".github", ".certiaura_backups", "__pycache__", "node_modules",
        ".venv", "venv", "Build_Records", "Tests", "Examples", "Fixtures"
    ],
    "excluded_filename_patterns": [
        "*.pyc", "*.pyo", "*.tmp", "*.temp", "*.bak", "*.log", "*.sha256",
        "PACKAGE_CONTENT_SHA256.csv", "FILE_INVENTORY.csv", "BUILD_MANIFEST.json",
        "CHANGE_LOG_PROPOSED.csv", "COMMIT_MESSAGE.txt", "TEST_REPORT.txt",
        "*.example.*", "*.generated.*"
    ],
    "excluded_exact_paths": [],
    "registerable_extensions": [
        ".md", ".json", ".yaml", ".yml", ".csv", ".py", ".ps1", ".sql",
        ".html", ".htm", ".xml", ".txt", ".pdf", ".docx", ".xlsx", ".pptx",
        ".png", ".jpg", ".jpeg", ".svg", ".webp"
    ],
    "include_readme_files": True,
    "include_registers": True,
    "include_schemas": True,
    "include_templates": True,
    "include_scripts": True,
    "include_dashboards": True,
    "include_media": True,
    "default_status": "ACTIVE",
    "default_owner": "Certiaura",
    "default_version": "1.0.0",
    "allowed_missing_register_statuses": [
        "RETIRED", "SUPERSEDED", "ARCHIVED", "DEPRECATED", "APPROVED_EXCEPTION"
    ]
}

TEXT_EXTENSIONS = {".md", ".json", ".yaml", ".yml", ".csv", ".py", ".ps1", ".sql", ".html", ".htm", ".xml", ".txt"}


def load_policy(path: Path | None) -> dict[str, Any]:
    policy = deepcopy(DEFAULT_POLICY)
    if path and path.is_file():
        supplied = json.loads(path.read_text(encoding="utf-8"))
        policy.update(supplied)
    return policy


def _matches_glob(filename: str, patterns: Iterable[str]) -> bool:
    p = PurePosixPath(filename)
    return any(p.match(pattern) for pattern in patterns)


def _is_excluded(rel: str, policy: dict[str, Any], register_rel: str | None) -> tuple[bool, str]:
    p = PurePosixPath(rel)
    if not p.parts:
        return True, "EMPTY_PATH"
    if p.parts[0] not in set(policy["canonical_roots"]):
        return True, "UNAUTHORISED_ROOT"
    if any(part in set(policy["excluded_directory_names"]) for part in p.parts):
        return True, "EXCLUDED_DIRECTORY"
    if register_rel and norm_path(rel) == norm_path(register_rel):
        return True, "CANONICAL_REGISTER_SELF_EXCLUSION"
    if norm_path(rel) in {norm_path(x) for x in policy.get("excluded_exact_paths", [])}:
        return True, "EXCLUDED_EXACT_PATH"
    if _matches_glob(p.name, policy.get("excluded_filename_patterns", [])):
        return True, "EXCLUDED_FILENAME_PATTERN"
    if p.suffix.lower() not in set(policy["registerable_extensions"]):
        return True, "NON_REGISTERABLE_EXTENSION"
    if not policy.get("include_readme_files", True) and p.name.lower().startswith("readme"):
        return True, "README_EXCLUDED"
    return False, ""


def _asset_type(rel: str) -> str:
    parts = PurePosixPath(rel).parts
    lowered = {x.lower() for x in parts}
    name = PurePosixPath(rel).name.lower()
    if parts and parts[0] == "00_Governance":
        return "Governance Control"
    mapping = [
        ("standards", "Standard"), ("schemas", "Schema"), ("templates", "Template"),
        ("registers", "Register"), ("validators", "Validator"), ("automation", "Automation"),
        ("dashboards", "Dashboard"), ("reports", "Report"), ("calculators", "Calculator"),
        ("scripts", "Script"), ("images", "Media Asset"), ("assets", "Media Asset"),
    ]
    for key, value in mapping:
        if key in lowered:
            return value
    if name.endswith(".schema.json"):
        return "Schema"
    if name.endswith(".template.json"):
        return "Template"
    if name.endswith("_register.csv") or name.endswith("_matrix.csv"):
        return "Register"
    if parts and parts[0] == "Documentation":
        return "Documentation Asset"
    if parts and parts[0] == "13_Project_Genesis":
        return "Platform Component"
    return "Knowledge Asset"


def _safe_text(data: bytes, suffix: str) -> str:
    if suffix not in TEXT_EXTENSIONS:
        return ""
    if len(data) > 2_000_000:
        data = data[:2_000_000]
    return data.decode("utf-8-sig", errors="replace")


def _json_metadata(text: str) -> dict[str, Any]:
    try:
        obj = json.loads(text)
    except Exception:
        return {}
    if not isinstance(obj, dict):
        return {}
    result: dict[str, Any] = {}
    for source, target in [
        ("title", "title"), ("asset_title", "title"), ("name", "title"),
        ("version", "version"), ("status", "status"), ("owner", "owner"),
        ("uai", "uai"), ("universal_asset_identifier", "uai"), ("asset_id", "uai")
    ]:
        value = obj.get(source)
        if value not in (None, "") and target not in result:
            result[target] = str(value)
    return result


def _metadata(rel: str, data: bytes, policy: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    suffix = PurePosixPath(rel).suffix.lower()
    text = _safe_text(data, suffix)
    jmeta = _json_metadata(text) if suffix == ".json" and text else {}
    conflicts: list[dict[str, Any]] = []

    strong = sorted(set(STRONG_UAI_RE.findall(text))) if text else []
    broad = sorted(set(UAI_RE.findall(text))) if text else []
    explicit = jmeta.get("uai")
    if explicit and UAI_RE.fullmatch(explicit):
        strong = sorted(set(strong + [explicit]))
    if len(strong) > 1:
        conflicts.append({"code": "MULTIPLE_STRONG_UAI_VALUES", "path": rel, "values": strong})
    existing_uai = strong[0] if len(strong) == 1 else None

    title = jmeta.get("title")
    if not title and text:
        match = TITLE_RE.search(text)
        if match:
            title = match.group(1).strip().strip("#").strip()
    if not title:
        title = re.sub(r"[_\-]+", " ", PurePosixPath(rel).stem).strip().upper()

    version = jmeta.get("version")
    if not version and text:
        match = VERSION_RE.search(text)
        version = match.group(1).strip() if match else None
    status = jmeta.get("status")
    if not status and text:
        match = STATUS_RE.search(text)
        status = match.group(1).strip().strip("*") if match else None
    owner = jmeta.get("owner")
    if not owner and text:
        match = OWNER_RE.search(text)
        owner = match.group(1).strip().strip("*") if match else None

    return {
        "asset_title": title,
        "asset_type": _asset_type(rel),
        "knowledge_system": infer_system(rel),
        "existing_uai": existing_uai,
        "proposed_version": version or policy["default_version"],
        "proposed_status": status or policy["default_status"],
        "owner": owner or policy["default_owner"],
        "file_sha256": hashlib.sha256(data).hexdigest(),
    }, conflicts


def _inventory_provenance(repo: Path, additional_files: dict[str, bytes]) -> dict[str, set[str]]:
    mapping: dict[str, set[str]] = defaultdict(set)

    def consume_csv(build_number: str, raw: str) -> None:
        try:
            rows = csv.DictReader(raw.splitlines())
            for row in rows:
                path = row.get("canonical_path") or row.get("repository_path") or row.get("path") or row.get("Path")
                source = row.get("source_build") or row.get("build_number") or build_number
                if path:
                    mapping[norm_path(path)].add(str(source).strip())
        except Exception:
            return

    records = repo / "Documentation" / "Build_Records"
    if records.is_dir():
        for inventory in records.glob("*/FILE_INVENTORY.csv"):
            consume_csv(inventory.parent.name, inventory.read_text(encoding="utf-8-sig", errors="replace"))

    for rel, data in additional_files.items():
        p = PurePosixPath(rel)
        if len(p.parts) >= 4 and p.parts[0:2] == ("Documentation", "Build_Records") and p.name == "FILE_INVENTORY.csv":
            consume_csv(p.parts[2], data.decode("utf-8-sig", errors="replace"))
    return mapping


def _iter_repository_files(repo: Path, additional_files: dict[str, bytes], canonical_roots: list[str]) -> dict[str, bytes]:
    combined: dict[str, bytes] = {}
    for root in canonical_roots:
        base = repo / root
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if path.is_file():
                rel = path.relative_to(repo).as_posix()
                try:
                    combined[rel] = path.read_bytes()
                except OSError:
                    continue
    combined.update({PurePosixPath(k).as_posix(): v for k, v in additional_files.items()})
    return combined


def discover_historical_assets(
    repo: Path,
    policy: dict[str, Any],
    additional_files: dict[str, bytes] | None = None,
    register_path: Path | None = None,
) -> dict[str, Any]:
    additional_files = additional_files or {}
    register_rel = register_path.relative_to(repo).as_posix() if register_path else None
    provenance = _inventory_provenance(repo, additional_files)
    files = _iter_repository_files(repo, additional_files, policy["canonical_roots"])
    candidates: list[dict[str, Any]] = []
    exclusions: list[dict[str, str]] = []
    conflicts: list[dict[str, Any]] = []

    for rel in sorted(files, key=str.lower):
        excluded, reason = _is_excluded(rel, policy, register_rel)
        if excluded:
            exclusions.append({"path": rel, "reason": reason})
            continue
        meta, meta_conflicts = _metadata(rel, files[rel], policy)
        conflicts.extend(meta_conflicts)
        source_builds = sorted(provenance.get(norm_path(rel), set()))
        candidate = {
            "repository_path": rel,
            **meta,
            "intended_action": "UPDATE_OR_CREATE",
            "reconciliation_mode": "FULL_HISTORICAL_BACKFILL_PRESERVE_IDENTITY",
            "allow_create_if_missing": True,
            "completion_percentage": 100,
            "parent_assets": [],
            "child_assets": [],
            "relationships": [],
            "evidence_links": [],
            "report_links": [],
            "marketplace_links": [],
            "last_review": "",
            "next_review": "",
            "build_provenance": [f"CERT-BUILD-{x}" for x in source_builds] or ["CERT-BUILD-0038"],
            "source_builds": source_builds,
            "registration_basis": "HISTORICAL_REPOSITORY_CENSUS",
        }
        candidates.append(candidate)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy_version": policy.get("policy_version"),
        "registerable_assets": candidates,
        "excluded_files": exclusions,
        "conflicts": conflicts,
        "summary": {
            "repository_files_considered": len(files),
            "registerable_assets": len(candidates),
            "excluded_files": len(exclusions),
            "conflicts": len(conflicts),
            "by_system": dict(Counter(x["knowledge_system"] for x in candidates)),
            "by_asset_type": dict(Counter(x["asset_type"] for x in candidates)),
            "with_source_build": sum(1 for x in candidates if x["source_builds"]),
            "without_source_build": sum(1 for x in candidates if not x["source_builds"]),
        },
    }


def _merge_explicit_assets(discovered: list[dict[str, Any]], explicit: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged = {norm_path(x["repository_path"]): x for x in discovered}
    for asset in explicit:
        key = norm_path(asset["repository_path"])
        if key in merged:
            base = merged[key]
            combined = {**base, **asset}
            combined["allow_create_if_missing"] = asset.get("allow_create_if_missing", True)
            combined["source_builds"] = sorted(set(base.get("source_builds", [])) | set(asset.get("source_builds", [])))
            merged[key] = combined
        else:
            merged[key] = asset
    return [merged[k] for k in sorted(merged)]


def _validate_register_coverage(repo: Path, rows: list[dict[str, str]], candidates: list[dict[str, Any]], policy: dict[str, Any], additional_paths: set[str] | None = None) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    additional_paths = {norm_path(x) for x in (additional_paths or set())}
    by_path = {norm_path(row.get("Repository Path")): row for row in rows if norm_path(row.get("Repository Path"))}
    for asset in candidates:
        if norm_path(asset["repository_path"]) not in by_path:
            errors.append({"code": "UNREGISTERED_HISTORICAL_ASSET", "path": asset["repository_path"]})
    allowed = {str(x).upper() for x in policy.get("allowed_missing_register_statuses", [])}
    for row in rows:
        path = row.get("Repository Path", "").strip()
        if not path:
            continue
        target = repo.joinpath(*PurePosixPath(path).parts)
        status = row.get("Status", "").strip().upper()
        if not target.is_file() and norm_path(path) not in additional_paths and status not in allowed:
            errors.append({
                "code": "ORPHAN_MASTER_ASSET_REGISTER_ENTRY",
                "uai": row.get("Universal Asset Identifier", ""),
                "path": path,
                "status": status,
            })
    return errors


def plan_full_historical_reconciliation(
    repo: Path,
    base_manifest: dict[str, Any],
    policy_path: Path | None = None,
    explicit_register: Path | None = None,
    additional_files: dict[str, bytes] | None = None,
) -> dict[str, Any]:
    policy = load_policy(policy_path)
    register = resolve_register(repo, explicit_register)
    rows, _ = load_register(register)
    census = discover_historical_assets(repo, policy, additional_files, register)
    merged_assets = _merge_explicit_assets(census["registerable_assets"], base_manifest.get("formal_assets", []))
    plan = plan_reconciliation(rows, merged_assets, base_manifest.get("build_number", "0038"))
    coverage_errors = _validate_register_coverage(
        repo,
        plan.get("rows", []),
        census["registerable_assets"],
        policy,
        set((additional_files or {}).keys()),
    )
    conflicts = list(census["conflicts"]) + list(plan["conflicts"]) + coverage_errors
    summary = {
        **census["summary"],
        **{f"register_{k}": v for k, v in plan["summary"].items()},
        "total_conflicts": len(conflicts),
    }
    return {
        "valid": not conflicts,
        "register_path": register.relative_to(repo).as_posix(),
        "census": census,
        "merged_formal_assets": merged_assets,
        "changes": plan["changes"],
        "conflicts": conflicts,
        "summary": summary,
        "planned_rows": plan.get("rows", []),
    }


def reconcile_full_historical_repository(
    repo: Path,
    base_manifest_path: Path,
    policy_path: Path | None = None,
    explicit_register: Path | None = None,
    additional_files: dict[str, bytes] | None = None,
    apply: bool = False,
    report_path: Path | None = None,
    census_report_path: Path | None = None,
) -> dict[str, Any]:
    manifest = json.loads(base_manifest_path.read_text(encoding="utf-8"))
    register = resolve_register(repo, explicit_register)
    rows, meta = load_register(register)
    result = plan_full_historical_reconciliation(
        repo, manifest, policy_path, explicit_register, additional_files
    )
    planned_rows = result.pop("planned_rows", [])
    if apply and result["valid"]:
        _write_register(register, planned_rows, meta)
        coverage_errors = _validate_register_coverage(
            repo, planned_rows, result["census"]["registerable_assets"], load_policy(policy_path), set()
        )
        if coverage_errors:
            result["valid"] = False
            result["coverage_errors"] = coverage_errors
            result["applied"] = False
        else:
            result["applied"] = True
    else:
        result["applied"] = False

    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if census_report_path:
        census_report_path.parent.mkdir(parents=True, exist_ok=True)
        census_report_path.write_text(json.dumps(result["census"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result
