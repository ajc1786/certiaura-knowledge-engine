from __future__ import annotations

import csv
import json
import re
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REGISTER_NAME_RE = re.compile(r"master[^a-z0-9]*asset[^a-z0-9]*register", re.I)
UAI_RE = re.compile(r"^CERT-([A-Z]+)-(\d{6})$")

CANONICAL_FIELDS = [
    "Universal Asset Identifier", "Asset Title", "Asset Type", "Knowledge System", "Repository Path",
    "Version", "Status", "Owner", "Completion Percentage", "Parent Assets", "Child Assets",
    "Relationship List", "Evidence Links", "Report Links", "Marketplace Links", "Last Review",
    "Next Review", "Change History", "Build Provenance", "Source Builds", "Registration Basis",
    "File SHA256", "Last Updated"
]

ALIASES = {
    "uai": ["Universal Asset Identifier", "UAI", "Asset ID", "Asset_ID", "asset_id", "id"],
    "title": ["Asset Title", "Title", "Name", "asset_title", "title"],
    "asset_type": ["Asset Type", "Type", "asset_type", "type"],
    "system": ["Knowledge System", "System", "knowledge_system", "system"],
    "path": ["Repository Path", "Canonical Path", "Path", "repository_path", "canonical_path", "path"],
    "version": ["Version", "version"],
    "status": ["Status", "status"],
    "owner": ["Owner", "owner"],
    "completion": ["Completion Percentage", "Completion", "completion_percentage"],
    "parents": ["Parent Assets", "Parents", "parent_assets"],
    "children": ["Child Assets", "Children", "child_assets"],
    "relationships": ["Relationship List", "Relationships", "relationship_list", "relationships"],
    "evidence": ["Evidence Links", "evidence_links"],
    "reports": ["Report Links", "report_links"],
    "marketplace": ["Marketplace Links", "marketplace_links"],
    "last_review": ["Last Review", "last_review"],
    "next_review": ["Next Review", "next_review"],
    "history": ["Change History", "change_history"],
    "provenance": ["Build Provenance", "build_provenance"],
    "source_builds": ["Source Builds", "source_builds"],
    "registration_basis": ["Registration Basis", "registration_basis"],
    "file_sha256": ["File SHA256", "SHA256", "sha256", "file_sha256"],
    "updated": ["Last Updated", "last_updated"]
}

SYSTEM_ROOTS = {
    "00_Governance": "SYS", "01_Knowledge_Systems": "SYS", "02_Peptides": "PKS",
    "03_Biology": "BKS", "04_Conditions": "CKS", "05_Monitoring": "MKS",
    "06_Evidence": "EKS", "07_Goals": "GKS", "08_Product_Passports": "PPS",
    "09_Cost_Intelligence": "CIS", "10_Marketplace": "MPS", "11_Academy": "AKS",
    "12_Reports": "RKS", "13_Project_Genesis": "SYS", "Assets": "SYS",
    "Database": "SYS", "Documentation": "SYS", "Images": "SYS", "Schemas": "SYS",
    "Scripts": "SYS", "Standards": "SYS", "Templates": "SYS"
}

class RegisterError(RuntimeError):
    pass


def norm_path(value: str | None) -> str:
    return (value or "").replace("\\", "/").strip("/").lower()


def norm_text(value: str | None) -> str:
    return re.sub(r"\s+", " ", (value or "").strip()).lower()


def _candidate_registers(repo: Path) -> list[Path]:
    exact = [
        repo / "Database" / "MASTER_ASSET_REGISTER.csv",
        repo / "Database" / "MASTER_ASSET_REGISTER.json",
        repo / "Database" / "Master_Asset_Register.csv",
        repo / "Documentation" / "MASTER_ASSET_REGISTER.csv",
        repo / "00_Governance" / "MASTER_ASSET_REGISTER.csv",
        repo / "Assets" / "MASTER_ASSET_REGISTER.csv",
    ]
    candidates = [p for p in exact if p.is_file()]
    excluded = {".git", ".certiaura_backups", "Build_Records", "__pycache__"}
    for p in repo.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in {".csv", ".json"}:
            continue
        if any(part in excluded for part in p.parts):
            continue
        stem = re.sub(r"[_\- ]+", " ", p.stem)
        if REGISTER_NAME_RE.search(stem):
            candidates.append(p)
    unique: dict[str, Path] = {}
    for p in candidates:
        unique[str(p.resolve()).lower()] = p.resolve()
    return sorted(unique.values(), key=lambda p: str(p).lower())


def resolve_register(repo: Path, explicit: Path | None = None) -> Path:
    if explicit is not None:
        p = explicit if explicit.is_absolute() else repo / explicit
        if not p.is_file():
            raise RegisterError(f"MASTER_ASSET_REGISTER_NOT_FOUND: {p}")
        return p.resolve()
    candidates = _candidate_registers(repo)
    if not candidates:
        raise RegisterError("MASTER_ASSET_REGISTER_NOT_FOUND")
    if len(candidates) > 1:
        raise RegisterError("MASTER_ASSET_REGISTER_AMBIGUOUS: " + "; ".join(str(x) for x in candidates))
    return candidates[0]


def _alias_value(row: dict[str, Any], key: str) -> str:
    for name in ALIASES[key]:
        if name in row and row[name] not in (None, ""):
            value = row[name]
            if isinstance(value, (dict, list)):
                return json.dumps(value, ensure_ascii=False)
            return str(value)
    return ""


def _canonicalise(row: dict[str, Any]) -> dict[str, str]:
    out = {str(k): "" if v is None else (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v)) for k, v in row.items()}
    mapping = {
        "Universal Asset Identifier": "uai", "Asset Title": "title", "Asset Type": "asset_type", "Knowledge System": "system",
        "Repository Path": "path", "Version": "version", "Status": "status", "Owner": "owner",
        "Completion Percentage": "completion", "Parent Assets": "parents", "Child Assets": "children",
        "Relationship List": "relationships", "Evidence Links": "evidence", "Report Links": "reports",
        "Marketplace Links": "marketplace", "Last Review": "last_review", "Next Review": "next_review",
        "Change History": "history", "Build Provenance": "provenance", "Source Builds": "source_builds",
        "Registration Basis": "registration_basis", "File SHA256": "file_sha256", "Last Updated": "updated"
    }
    for canonical, alias_key in mapping.items():
        if not out.get(canonical):
            out[canonical] = _alias_value(row, alias_key)
    return out


def load_register(path: Path) -> tuple[list[dict[str, str]], dict[str, Any]]:
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            if not reader.fieldnames:
                raise RegisterError("MASTER_ASSET_REGISTER_INVALID_CSV_HEADER")
            rows = [_canonicalise(dict(row)) for row in reader]
            return rows, {"format": "csv", "fieldnames": list(reader.fieldnames)}
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        raw = data
        shape = "list"
    elif isinstance(data, dict) and isinstance(data.get("assets"), list):
        raw = data["assets"]
        shape = "assets_object"
    else:
        raise RegisterError("MASTER_ASSET_REGISTER_INVALID_JSON_SHAPE")
    return [_canonicalise(dict(x)) for x in raw], {"format": "json", "shape": shape, "original": data}


def _write_register(path: Path, rows: list[dict[str, str]], meta: dict[str, Any]) -> None:
    if meta["format"] == "csv":
        original = [x for x in meta.get("fieldnames", []) if x]
        fields = original + [x for x in CANONICAL_FIELDS if x not in original]
        with path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                writer.writerow({k: row.get(k, "") for k in fields})
        return
    original = deepcopy(meta.get("original"))
    if meta.get("shape") == "list":
        payload: Any = rows
    else:
        payload = original if isinstance(original, dict) else {}
        payload["assets"] = rows
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _assert_unique(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    conflicts: list[dict[str, str]] = []
    by_id: dict[str, int] = {}
    by_path: dict[str, int] = {}
    for idx, row in enumerate(rows):
        uai = row.get("Universal Asset Identifier", "").strip()
        path = norm_path(row.get("Repository Path"))
        if uai:
            if uai in by_id:
                conflicts.append({"code": "DUPLICATE_UAI", "value": uai, "rows": f"{by_id[uai]},{idx}"})
            by_id[uai] = idx
        if path:
            if path in by_path:
                conflicts.append({"code": "DUPLICATE_CANONICAL_PATH", "value": path, "rows": f"{by_path[path]},{idx}"})
            by_path[path] = idx
    return conflicts


def _next_numbers(rows: list[dict[str, str]]) -> dict[str, int]:
    maxima: dict[str, int] = {}
    for row in rows:
        match = UAI_RE.match(row.get("Universal Asset Identifier", "").strip())
        if match:
            system, number = match.group(1), int(match.group(2))
            maxima[system] = max(maxima.get(system, 0), number)
    return maxima


def _allocate(system: str, maxima: dict[str, int]) -> str:
    system = re.sub(r"[^A-Z]", "", system.upper()) or "SYS"
    maxima[system] = maxima.get(system, 0) + 1
    return f"CERT-{system}-{maxima[system]:06d}"


def infer_system(path: str) -> str:
    root = path.replace("\\", "/").split("/", 1)[0]
    return SYSTEM_ROOTS.get(root, "SYS")


def plan_reconciliation(rows: list[dict[str, str]], formal_assets: list[dict[str, Any]], build_number: str) -> dict[str, Any]:
    working = deepcopy(rows)
    conflicts = _assert_unique(working)
    changes: list[dict[str, Any]] = []
    maxima = _next_numbers(working)
    now = datetime.now(timezone.utc).isoformat()

    incoming_uai_paths: dict[str, set[str]] = {}
    for incoming_asset in formal_assets:
        incoming_uai = (incoming_asset.get("existing_uai") or "").strip()
        if incoming_uai:
            incoming_uai_paths.setdefault(incoming_uai, set()).add(norm_path(incoming_asset.get("repository_path")))
    for incoming_uai, paths in incoming_uai_paths.items():
        if len(paths) > 1:
            conflicts.append({"code": "DUPLICATE_INCOMING_UAI", "value": incoming_uai, "paths": sorted(paths)})

    for asset in formal_assets:
        path = asset["repository_path"].replace("\\", "/").strip("/")
        title = asset["asset_title"].strip()
        system = asset.get("knowledge_system") or infer_system(path)
        supplied_uai = (asset.get("existing_uai") or "").strip()

        matches: list[int] = []
        if supplied_uai:
            matches = [i for i, row in enumerate(working) if row.get("Universal Asset Identifier", "").strip() == supplied_uai]
        if not matches:
            matches = [i for i, row in enumerate(working) if norm_path(row.get("Repository Path")) == norm_path(path)]
        if not matches and asset.get("allow_title_match", False):
            matches = [i for i, row in enumerate(working) if norm_text(row.get("Asset Title")) == norm_text(title) and norm_text(row.get("Knowledge System")) == norm_text(system)]

        if len(matches) > 1:
            conflicts.append({"code": "AMBIGUOUS_ASSET_MATCH", "path": path, "title": title, "matches": matches})
            continue

        if matches:
            idx = matches[0]
            row = working[idx]
            preserved = row.get("Universal Asset Identifier", "").strip()
            if not preserved:
                preserved = _allocate(system, maxima)
            old_path = row.get("Repository Path", "")
            row.update({
                "Universal Asset Identifier": preserved,
                "Asset Title": title,
                "Asset Type": asset.get("asset_type") or row.get("Asset Type") or "Knowledge Asset",
                "Knowledge System": system,
                "Repository Path": path,
                "Version": asset.get("proposed_version") or row.get("Version") or "1.0.0",
                "Status": asset.get("proposed_status") or row.get("Status") or "ACTIVE",
                "Owner": asset.get("owner") or row.get("Owner") or "Certiaura",
                "Parent Assets": _serialise(asset.get("parent_assets"), row.get("Parent Assets", "")),
                "Child Assets": _serialise(asset.get("child_assets"), row.get("Child Assets", "")),
                "Relationship List": _serialise(asset.get("relationships"), row.get("Relationship List", "")),
                "Evidence Links": _serialise(asset.get("evidence_links"), row.get("Evidence Links", "")),
                "Report Links": _serialise(asset.get("report_links"), row.get("Report Links", "")),
                "Marketplace Links": _serialise(asset.get("marketplace_links"), row.get("Marketplace Links", "")),
                "Build Provenance": _merge_list_history(row.get("Build Provenance", ""), asset.get("build_provenance") or [f"CERT-BUILD-{build_number}"]),
                "Source Builds": _merge_list_history(row.get("Source Builds", ""), asset.get("source_builds") or []),
                "Registration Basis": asset.get("registration_basis") or row.get("Registration Basis") or "BUILD_MANIFEST",
                "File SHA256": asset.get("file_sha256") or row.get("File SHA256") or "",
                "Change History": _append_history(row.get("Change History", ""), f"{now}: restored/reconciled by Build {build_number}"),
                "Last Updated": now,
            })
            changes.append({"action": "UPDATE", "uai": preserved, "path": path, "previous_path": old_path})
        else:
            if not asset.get("allow_create_if_missing", False):
                conflicts.append({"code": "ASSET_NOT_FOUND_CREATE_NOT_ALLOWED", "path": path, "title": title})
                continue
            uai = supplied_uai or _allocate(system, maxima)
            new_row = {field: "" for field in CANONICAL_FIELDS}
            new_row.update({
                "Universal Asset Identifier": uai,
                "Asset Title": title,
                "Asset Type": asset.get("asset_type") or "Knowledge Asset",
                "Knowledge System": system,
                "Repository Path": path,
                "Version": asset.get("proposed_version") or "1.0.0",
                "Status": asset.get("proposed_status") or "ACTIVE",
                "Owner": asset.get("owner") or "Certiaura",
                "Completion Percentage": str(asset.get("completion_percentage", "100")),
                "Parent Assets": _serialise(asset.get("parent_assets"), ""),
                "Child Assets": _serialise(asset.get("child_assets"), ""),
                "Relationship List": _serialise(asset.get("relationships"), ""),
                "Evidence Links": _serialise(asset.get("evidence_links"), ""),
                "Report Links": _serialise(asset.get("report_links"), ""),
                "Marketplace Links": _serialise(asset.get("marketplace_links"), ""),
                "Last Review": asset.get("last_review") or "",
                "Next Review": asset.get("next_review") or "",
                "Change History": f"{now}: created/restored by Build {build_number}",
                "Build Provenance": _merge_list_history("", asset.get("build_provenance") or [f"CERT-BUILD-{build_number}"]),
                "Source Builds": _merge_list_history("", asset.get("source_builds") or []),
                "Registration Basis": asset.get("registration_basis") or "BUILD_MANIFEST",
                "File SHA256": asset.get("file_sha256") or "",
                "Last Updated": now,
            })
            working.append(new_row)
            changes.append({"action": "CREATE", "uai": uai, "path": path})

    conflicts.extend(_assert_unique(working))
    unique_conflicts = []
    seen = set()
    for c in conflicts:
        key = json.dumps(c, sort_keys=True)
        if key not in seen:
            unique_conflicts.append(c); seen.add(key)
    summary = {
        "existing_assets": len(rows),
        "formal_assets_in_manifest": len(formal_assets),
        "creates": sum(1 for x in changes if x["action"] == "CREATE"),
        "updates": sum(1 for x in changes if x["action"] == "UPDATE"),
        "expected_assets_after_import": len(working),
        "conflicts": len(unique_conflicts),
    }
    return {"valid": not unique_conflicts, "summary": summary, "changes": changes, "conflicts": unique_conflicts, "rows": working}


def _serialise(value: Any, existing: str) -> str:
    if value in (None, [], {}, ""):
        return existing
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)



def _merge_list_history(existing: str, values: Any) -> str:
    current = [x.strip() for x in re.split(r"[|,;]", existing or "") if x.strip()]
    if isinstance(values, str):
        incoming = [x.strip() for x in re.split(r"[|,;]", values) if x.strip()]
    else:
        incoming = [str(x).strip() for x in (values or []) if str(x).strip()]
    merged: list[str] = []
    for item in current + incoming:
        if item not in merged:
            merged.append(item)
    return " | ".join(merged)

def _append_history(existing: str, item: str) -> str:
    existing = (existing or "").strip()
    return f"{existing} | {item}" if existing else item


def reconcile(repo: Path, manifest_path: Path, explicit_register: Path | None = None, apply: bool = False, report_path: Path | None = None) -> dict[str, Any]:
    register = resolve_register(repo, explicit_register)
    rows, meta = load_register(register)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    result = plan_reconciliation(rows, manifest.get("formal_assets", []), manifest["build_number"])
    result["register_path"] = str(register.relative_to(repo))
    if apply and result["valid"]:
        _write_register(register, result.pop("rows"), meta)
        result["applied"] = True
    else:
        result.pop("rows", None)
        result["applied"] = False
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result
