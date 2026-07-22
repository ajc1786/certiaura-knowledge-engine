from __future__ import annotations
import argparse
import ast
import hashlib
import json
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

ALLOWED_ROOTS = {"00_Governance","01_Knowledge_Systems","02_Peptides","03_Biology","04_Conditions","05_Monitoring","06_Evidence","07_Goals","08_Product_Passports","09_Cost_Intelligence","10_Marketplace","11_Academy","12_Reports","13_Project_Genesis","Assets","Database","Documentation","Images","Schemas","Scripts","Standards","Templates"}
TEXT_EXTENSIONS = {".md",".json",".csv",".py",".ps1",".cmd",".txt",".yml",".yaml"}
EXCLUSIONS = {"Documentation/Build_Records/0052/ASSET_INTENT_MANIFEST.json","Documentation/Build_Records/0052/BUILD_MANIFEST.json","Documentation/Build_Records/0052/CHECKSUMS.sha256","Documentation/Build_Records/0052/PACKAGE_INVENTORY.csv","Documentation/Build_Records/0052/PREDECESSOR_CANONICAL_EVIDENCE.json","Documentation/Build_Records/0052/ACCUMULATED_LESSONS_UPDATE_REPORT.json","Documentation/Build_Records/0052/LESSONS_COVERAGE_REPORT.json","Documentation/Build_Records/0052/CANDIDATE_VALIDATION_REPORT.json","Documentation/Build_Records/0052/REAL_WORLD_OPERATOR_WORKFLOW_REGRESSION_REPORT.json"}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def materialise(package: str):
    path = Path(package)
    if path.is_dir():
        return path, None
    temporary = Path(tempfile.mkdtemp(prefix="preflight0052rc6_"))
    with zipfile.ZipFile(path) as archive:
        archive.extractall(temporary)
    return temporary, temporary


def extract_owned(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "OWNED_PATHS" for target in node.targets):
            if isinstance(node.value, ast.Call) and node.value.args:
                return set(ast.literal_eval(node.value.args[0]))
    raise RuntimeError("OWNED_PATHS exact literal missing")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package")
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    root, temporary = materialise(args.package)
    errors = []
    try:
        manifest = json.loads((root / "Documentation/Build_Records/0052/ASSET_INTENT_MANIFEST.json").read_text(encoding="utf-8"))
        entries = manifest.get("files", [])
        paths = [x.get("repository_path") for x in entries]
        actual = sorted(str(x.relative_to(root)).replace("\\", "/") for x in root.rglob("*") if x.is_file())
        if manifest.get("build_number") != "0052" or manifest.get("candidate") != "RC6" or manifest.get("build_provenance") != "CERT-BUILD-0052":
            errors.append("manifest identity invalid")
        if sorted(paths) != actual:
            errors.append("manifest inventory does not equal package inventory")
        if len(paths) != len(set(paths)) or len(paths) != len({x.casefold() for x in paths}):
            errors.append("duplicate or case-only path collision")
        if any(not path or path.split("/")[0] not in ALLOWED_ROOTS for path in paths):
            errors.append("unauthorised root")
        if any("Predecessor_Repository" in path or "predecessor_build_0051_identity" in path for path in paths):
            errors.append("candidate-authored predecessor fixture prohibited")
        if "13_Project_Genesis/Release/derive_build_0051_predecessor_evidence.py" not in paths:
            errors.append("canonical predecessor derivation script missing")
        for entry in entries:
            relative = entry.get("repository_path")
            if entry.get("build_provenance") != "CERT-BUILD-0052" or entry.get("ownership_basis") != "EXACT_ASSET_INTENT_MANIFEST_PATH":
                errors.append("invalid exact ownership metadata: " + str(relative))
            path = root / relative
            if path.suffix.lower() in TEXT_EXTENSIONS:
                raw = path.read_bytes()
                if b"\r" in raw or not raw.endswith(b"\n"):
                    errors.append("LF hygiene failure: " + relative)
                for number, line in enumerate(raw.split(b"\n"), start=1):
                    if line.endswith((b" ", b"\t")):
                        errors.append(f"trailing whitespace: {relative}:{number}")
            if path.suffix.lower() in {".ps1", ".cmd"}:
                try:
                    text = path.read_bytes().decode("ascii")
                except UnicodeDecodeError:
                    errors.append("non-ASCII operator script: " + relative)
                    continue
                if re.search(r"\$(?:Repo|Repository)\b", text):
                    errors.append("stale operator path alias: " + relative)
                if "python -c" in text.lower() or "py -c" in text.lower():
                    errors.append("inline Python -c prohibited: " + relative)
        owned = extract_owned(root / "13_Project_Genesis/Validators/build_0052_asset_ownership.py")
        if owned != set(paths):
            errors.append("ownership set differs from manifest")
        ownership_text = (root / "13_Project_Genesis/Validators/build_0052_asset_ownership.py").read_text(encoding="utf-8")
        if any(token in ownership_text for token in ("glob(", "rglob(", "0052 in", "in path")):
            errors.append("broad ownership scan")
        replacements = [x for x in entries if x.get("approved_replacement") is True]
        if not replacements or any(x.get("predecessor_build") != "0051" for x in replacements):
            errors.append("approved replacements not explicitly bound to Build 0051")
        control = json.loads((root / "00_Governance/CERTIAURA_LOCKED_ACCUMULATED_LESSONS_AND_CONTINUOUS_LEARNING_STANDARD.control.json").read_text(encoding="utf-8"))
        if control.get("version") != "2.7.0" or control.get("current_incident", {}).get("active_candidate") != "RC6":
            errors.append("cumulative lessons source version or incident invalid")
        precursor = json.loads((root / "Documentation/Build_Records/0052/PRE_AUTHORISED_PRECURSOR_STATE.json").read_text(encoding="utf-8"))
        precursor_paths = precursor.get("paths", [])
        if precursor.get("status") != "EXACT_STAGED_GOVERNANCE_PRECURSOR_REQUIRED" or len(precursor_paths) != 6:
            errors.append("pre-authorised precursor state invalid")
        if len({x.get("repository_path") for x in precursor_paths}) != 6 or any(not re.fullmatch(r"[0-9A-F]{64}", str(x.get("sha256", ""))) for x in precursor_paths):
            errors.append("pre-authorised precursor paths or hashes invalid")
        evidence_source = (root / "13_Project_Genesis/Release/derive_build_0051_predecessor_evidence.py").read_text(encoding="utf-8")
        for required_token in ("PATH_KEYS", "normalised_manifest_entries", "PREDECESSOR_MANIFEST_PATH_ALIAS_CONFLICT", "predecessor_manifest_path_schema"):
            if required_token not in evidence_source:
                errors.append("manifest schema compatibility control missing: " + required_token)
        updater_source = (root / "Scripts/update_certiaura_accumulated_lessons.py").read_text(encoding="utf-8")
        for required_token in ("CURRENT_LESSON_REQUIRED_FIELD_MISSING", "LEGACY_LESSON_SUBSTANCE_MISSING", "historical_schema_migrations", "VERSION_AWARE_RECORDED_MIGRATION", "introduces_new_occurrence", "validate_ledger_only_historical_evidence", "HISTORICAL_LEDGER_ONLY_SET_MISMATCH"):
            if required_token not in updater_source:
                errors.append("historical lessons schema control missing: " + required_token)
        regression_ps = (root / "Scripts/Invoke_Certiaura_Build_0052_Windows_PS51_Regression.ps1").read_text(encoding="ascii")
        import_ps = (root / "Scripts/Invoke_Certiaura_Build_0052_Import.ps1").read_text(encoding="ascii")
        for source_name, source_text in (("windows regression", regression_ps), ("canonical import wrapper", import_ps)):
            for required_token in ("Convert-NativeOutputToText", "Assert-NativeOutputContains"):
                if required_token not in source_text:
                    errors.append("scalar native-output assertion control missing from " + source_name + ": " + required_token)
            if re.search(r"\.Output\s+-notmatch", source_text):
                errors.append("collection-valued -notmatch assertion prohibited in " + source_name)
        if "MULTILINE_NATIVE_OUTPUT_MATCH_VALIDATED" not in regression_ps:
            errors.append("multiline native-output positive and negative controls missing")
        importer_source = (root / "13_Project_Genesis/Import/run_build_0052_import.py").read_text(encoding="utf-8")
        for required_token in ("BUILD_0052_TRANSACTION_ROLLED_BACK", "print(failure_message, file=sys.stderr)", 'result["rollback_reason"]'):
            if required_token not in importer_source:
                errors.append("transactional failure visibility control missing: " + required_token)
        pending = ["PREDECESSOR_CANONICAL_EVIDENCE.json","ACCUMULATED_LESSONS_UPDATE_REPORT.json","LESSONS_COVERAGE_REPORT.json","CANDIDATE_VALIDATION_REPORT.json","REAL_WORLD_OPERATOR_WORKFLOW_REGRESSION_REPORT.json"]
        for name in pending:
            data = json.loads((root / "Documentation/Build_Records/0052" / name).read_text(encoding="utf-8"))
            if data.get("status") != "PENDING_RUNTIME_GENERATION" or data.get("static_pass_prohibited") is not True:
                errors.append("runtime report is not an explicit pending placeholder: " + name)
        records = {}
        for line in (root / "Documentation/Build_Records/0052/CHECKSUMS.sha256").read_text(encoding="utf-8").splitlines():
            if line:
                digest, relative = line.split("  ", 1)
                records[relative] = digest.upper()
        expected = sorted(set(paths) - EXCLUSIONS)
        if sorted(records) != expected:
            errors.append("checksum inventory coverage mismatch")
        for relative, digest in records.items():
            if sha(root / relative) != digest:
                errors.append("checksum mismatch: " + relative)
        output = {"valid":not errors,"build_number":"0052","candidate":"RC6","file_count":len(paths),"candidate_authored_predecessor_fixture":"PROHIBITED_AND_ABSENT","text_hygiene":"PASS" if not any("hygiene" in x or "trailing" in x for x in errors) else "FAIL","checksum_validation":"PASS" if not any("checksum" in x for x in errors) else "FAIL","errors":errors}
        report = Path(args.report)
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(json.dumps(output, indent=2))
        return 0 if not errors else 1
    finally:
        if temporary:
            shutil.rmtree(temporary, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
