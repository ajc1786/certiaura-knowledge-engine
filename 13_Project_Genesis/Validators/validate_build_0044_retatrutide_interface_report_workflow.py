from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

BUILD = "0044"
BUILD_PROVENANCE = "CERT-BUILD-0044"
ASSET_INTENT_PATH = "Documentation/Build_Records/0044/ASSET_INTENT_MANIFEST.json"
REGISTER_PATH = "Documentation/Master_Asset_Register.csv"
REQUIRED_PATHS = [
    "Standards/RETATRUTIDE_PATIENT_FACING_INTERFACE_STANDARD.md",
    "Standards/RETATRUTIDE_BRANDED_REPORT_RENDERING_STANDARD.md",
    "Standards/RETATRUTIDE_CONTROLLED_CONVERSATION_STANDARD.md",
    "Schemas/retatrutide_controlled_conversation_request.schema.json",
    "Schemas/retatrutide_controlled_conversation_response.schema.json",
    "Schemas/retatrutide_branded_report_manifest.schema.json",
    "Templates/retatrutide_report_brand_tokens.json",
    "Templates/retatrutide_patient_report_branded.template.html",
    "Scripts/render_retatrutide_branded_report.py",
    "Scripts/run_retatrutide_controlled_conversation.py",
    "Scripts/serve_retatrutide_patient_interface.py",
    "Scripts/Convert_Certiaura_Build_0044_Report_To_Pdf.ps1",
    "Scripts/Start_Certiaura_Retatrutide_Patient_Interface.ps1",
    "Scripts/Invoke_Certiaura_Build_0044_Preflight.ps1",
    "Scripts/Invoke_Certiaura_Build_0044_Import.ps1",
    "Scripts/Invoke_Certiaura_Build_0044_Windows_PS51_Regression.ps1",
    "Scripts/Run_Certiaura_Build_0044.ps1",
    "13_Project_Genesis/UI/Retatrutide_Patient_Interface/index.html",
    "13_Project_Genesis/UI/Retatrutide_Patient_Interface/styles.css",
    "13_Project_Genesis/UI/Retatrutide_Patient_Interface/app.js",
    "13_Project_Genesis/UI/Retatrutide_Patient_Interface/README.md",
    "13_Project_Genesis/AI/retatrutide_controlled_conversation_policy.json",
    "Documentation/Build_Records/0044/BUILD_MANIFEST.json",
    ASSET_INTENT_PATH,
    "Documentation/Build_Records/0044/EXAMPLE_BRANDED_PATIENT_REPORT.html",
    "Documentation/Build_Records/0044/EXAMPLE_BRANDED_PATIENT_REPORT.pdf",
    "Documentation/Build_Records/0044/EXAMPLE_BRANDED_PATIENT_REPORT_MANIFEST.json",
]
BUILD_0043_DEPENDENCIES = [
    "Scripts/generate_retatrutide_patient_journey_report.py",
    "Scripts/query_retatrutide_knowledge.py",
    "13_Project_Genesis/AI/retatrutide_ai_query_policy.json",
    "Schemas/retatrutide_patient_journey_report.schema.json",
]
TEXT_SUFFIXES = {
    ".md", ".json", ".csv", ".py", ".ps1", ".cmd", ".bat", ".txt",
    ".html", ".css", ".js", ".yml", ".yaml"
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_register_rows(repository: Path) -> list[dict[str, str]]:
    register = repository / REGISTER_PATH
    if not register.is_file():
        return []
    with register.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def build_owned_text_paths(
    repository: Path,
    register_rows: list[dict[str, str]] | None = None,
) -> list[str]:
    """Return exact Build 0044-owned text paths.

    Ownership is derived from the package Asset Intent Manifest and canonical
    Build Provenance. Numeric substring matching is deliberately prohibited
    because UAI serials such as CERT-BKS-000044 are unrelated to Build 0044.
    """
    intent_path = repository / ASSET_INTENT_PATH
    if not intent_path.is_file():
        return []
    intent = json.loads(intent_path.read_text(encoding="utf-8"))
    owned: set[str] = set()
    for item in intent.get("file_classifications", []):
        relative = str(item.get("path") or "").replace("\\", "/")
        if not relative:
            continue
        if item.get("classification") == "FORMAL_ASSET":
            continue
        if Path(relative).suffix.lower() in TEXT_SUFFIXES:
            owned.add(relative)

    rows = register_rows if register_rows is not None else read_register_rows(repository)
    for row in rows:
        if (row.get("Build Provenance") or "").strip() != BUILD_PROVENANCE:
            continue
        relative = (row.get("Repository Path") or "").strip().replace("\\", "/")
        if relative and Path(relative).suffix.lower() in TEXT_SUFFIXES:
            owned.add(relative)
    return sorted(owned)


def check_text_hygiene(repository: Path, relative: str) -> list[str]:
    path = repository / Path(relative)
    if not path.is_file():
        return ["Build 0044-owned text file missing: " + relative]
    errors: list[str] = []
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        errors.append("UTF-8 BOM detected: " + relative)
    if b"\r" in data:
        errors.append("Non-LF line ending detected: " + relative)
    if not data.endswith(b"\n"):
        errors.append("Final newline missing: " + relative)
    for number, line in enumerate(data.splitlines(), 1):
        if line.endswith((b" ", b"\t")):
            errors.append(f"Trailing whitespace: {relative}:{number}")
    if path.suffix.lower() == ".ps1" and any(byte > 127 for byte in data):
        errors.append("Non-ASCII PowerShell script: " + relative)
    return errors


def check_pdf(path: Path) -> list[str]:
    errors = []
    if not path.is_file():
        return [f"Missing PDF: {path}"]
    data = path.read_bytes()
    if len(data) < 1024:
        errors.append("Example PDF is unexpectedly small")
    if not data.startswith(b"%PDF-"):
        errors.append("Example PDF header is invalid")
    if b"%%EOF" not in data[-4096:]:
        errors.append("Example PDF end marker is missing")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository")
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    repository = Path(args.repository).resolve()
    errors: list[str] = []

    for relative in REQUIRED_PATHS + BUILD_0043_DEPENDENCIES:
        if not (repository / relative).is_file():
            errors.append("Missing required file: " + relative)

    register_rows = read_register_rows(repository)
    owned_text_paths = build_owned_text_paths(repository, register_rows)
    if not owned_text_paths:
        errors.append("No exact Build 0044-owned text paths were resolved")
    for relative in owned_text_paths:
        errors.extend(check_text_hygiene(repository, relative))

    ui_root = repository / "13_Project_Genesis/UI/Retatrutide_Patient_Interface"
    ui_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(ui_root.glob("*"))
        if path.suffix.lower() in {".html", ".css", ".js", ".md"}
    ) if ui_root.is_dir() else ""
    for forbidden in [
        "innerHTML", "outerHTML", "document.write", "localStorage",
        "sessionStorage", "indexedDB", "http://", "https://"
    ]:
        if forbidden in ui_text:
            errors.append("Forbidden UI construct or remote dependency: " + forbidden)

    server_path = repository / "Scripts/serve_retatrutide_patient_interface.py"
    if server_path.is_file():
        server_text = server_path.read_text(encoding="utf-8")
        if 'default="127.0.0.1"' not in server_text:
            errors.append("Interface server does not default to loopback")
        if '"0.0.0.0"' in server_text:
            errors.append("Interface server contains an unrestricted bind address")

    manifest_path = repository / "Documentation/Build_Records/0044/BUILD_MANIFEST.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("build_number") != BUILD:
            errors.append("Build manifest number mismatch")
        if manifest.get("dependencies", [{}])[-1].get("build") != "0043":
            errors.append("Build 0043 dependency is not recorded")

    formal_rows: list[dict[str, str]] = []
    if register_rows:
        identifiers: dict[str, int] = {}
        paths: dict[str, int] = {}
        for row in register_rows:
            uai = (row.get("Universal Asset Identifier") or "").strip()
            path = (row.get("Repository Path") or "").strip().replace("\\", "/")
            if uai:
                identifiers[uai] = identifiers.get(uai, 0) + 1
            if path:
                paths[path.lower()] = paths.get(path.lower(), 0) + 1
            if BUILD in (row.get("Source Builds") or "").split("; "):
                formal_rows.append(row)
        for uai, count in identifiers.items():
            if count > 1:
                errors.append("Duplicate UAI in Master Asset Register: " + uai)
        for path, count in paths.items():
            if count > 1:
                errors.append("Duplicate repository path in Master Asset Register: " + path)

        build_rows = [
            row for row in register_rows
            if (row.get("Build Provenance") or "").strip() == BUILD_PROVENANCE
        ]
        if len(build_rows) != 2:
            errors.append(f"Expected 2 Build 0044 formal asset rows; found {len(build_rows)}")
        for row in build_rows:
            relative = (row.get("Repository Path") or "").replace("\\", "/")
            asset_path = repository / Path(relative)
            if not asset_path.is_file():
                errors.append("Registered Build 0044 asset missing: " + relative)
                continue
            if (row.get("File SHA256") or "").strip().lower() != sha256_file(asset_path):
                errors.append("Build 0044 asset hash mismatch: " + relative)
            filename_uai = re.search(r"CERT-[A-Z]{3}-\d{6}", asset_path.name)
            if not filename_uai or filename_uai.group(0) != row.get("Universal Asset Identifier"):
                errors.append("Build 0044 asset filename/UAI mismatch: " + relative)
    else:
        errors.append("Canonical Master Asset Register missing")

    for path in repository.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(repository).as_posix()
        if "__UAI__" in path.name:
            errors.append("Unresolved formal-asset filename placeholder: " + relative)
        if (
            path.suffix.lower() == ".md"
            and (
                relative.startswith("12_Reports/Retatrutide/Patient_Interface/")
                or relative.startswith("13_Project_Genesis/AI/")
            )
            and b"UAI_ALLOCATION_REQUIRED" in path.read_bytes()
        ):
            errors.append("Unresolved formal-asset content placeholder: " + relative)

    errors.extend(check_pdf(
        repository / "Documentation/Build_Records/0044/EXAMPLE_BRANDED_PATIENT_REPORT.pdf"
    ))

    build_row_count = len([
        row for row in formal_rows
        if (row.get("Build Provenance") or "") == BUILD_PROVENANCE
    ])
    result = {
        "valid": not errors,
        "build_number": BUILD,
        "required_file_count": len(REQUIRED_PATHS),
        "build_0043_dependency_count": len(BUILD_0043_DEPENDENCIES),
        "formal_asset_rows": build_row_count,
        "owned_text_file_count": len(owned_text_paths),
        "validator_scope": "EXACT_ASSET_INTENT_AND_BUILD_PROVENANCE",
        "ui_security_baseline": not any("UI" in error or "bind" in error for error in errors),
        "errors": errors,
    }
    output = Path(args.report)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
