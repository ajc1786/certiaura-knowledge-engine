from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

BUILD = "0040"
RELEASE_GATE = "1.1.0"
REQUIRED = [
    "Standards/BUILD_PACKAGE_AUTOMATED_PREFLIGHT_AND_SYNTHETIC_IMPORT_STANDARD.md",
    "13_Project_Genesis/Release/build_package_preflight.py",
    "13_Project_Genesis/Import/transactional_build_import.py",
    "13_Project_Genesis/Import/run_build_0040_import.py",
    "13_Project_Genesis/Validators/validate_build_0040_repository.py",
    "13_Project_Genesis/Tests/test_build_0040_preflight.py",
    "13_Project_Genesis/Tests/test_build_0040_transactional_importer_compatibility.py",
    "Scripts/Invoke_Certiaura_Build_Preflight.ps1",
    "Scripts/Invoke_Certiaura_Build_0040_Import.ps1",
    "Schemas/build_package_preflight_report.schema.json",
    "Templates/build_package_preflight_config.template.json",
    "Documentation/Build_Records/0040/BUILD_MANIFEST.json",
    "Documentation/Build_Records/0040/PACKAGE_INVENTORY.csv",
    "Documentation/Build_Records/0040/CHECKSUMS.sha256",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    repo = Path(args[0]).resolve() if args else Path.cwd().resolve()
    errors: list[str] = []

    for rel in REQUIRED:
        if not (repo / rel).is_file():
            errors.append(f"Missing required file: {rel}")

    record = repo / "Documentation" / "Build_Records" / BUILD
    manifest_path = record / "BUILD_MANIFEST.json"
    inventory_path = record / "PACKAGE_INVENTORY.csv"
    checksum_path = record / "CHECKSUMS.sha256"

    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("build_number") != BUILD:
            errors.append("Build manifest number mismatch")
        if manifest.get("release_gate_version") != RELEASE_GATE:
            errors.append("Release gate version mismatch")
        if manifest.get("corrected_reissue") is not True:
            errors.append("Corrected reissue flag missing")

    importer_path = repo / "13_Project_Genesis/Import/transactional_build_import.py"
    if importer_path.is_file():
        source = importer_path.read_text(encoding="utf-8")
        prohibited = [
            r'BUILD_RECORD\s*=\s*["\']Documentation/Build_Records/0039',
            r'"build_number"\s*:\s*"0039"',
            r'"package_version"\s*:\s*"1\.3\.2"',
        ]
        for pattern in prohibited:
            if re.search(pattern, source):
                errors.append(f"Prior-build hard-coded importer residue detected: {pattern}")
        for required_text in ("discover_build_metadata", "allocated_identifiers", "transaction_status"):
            if required_text not in source:
                errors.append(f"Build-neutral importer capability missing: {required_text}")

    if inventory_path.is_file():
        with inventory_path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        for row in rows:
            rel = row["path"]
            path = repo / rel
            if not path.is_file():
                errors.append(f"Inventory target missing from repository: {rel}")
                continue
            expected = row["sha256"].strip().lower()
            if expected and sha256(path) != expected:
                errors.append(f"Inventory hash mismatch after import: {rel}")

    if checksum_path.is_file():
        for line in checksum_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            digest, rel = line.split("  ", 1)
            path = repo / rel
            if not path.is_file() or sha256(path) != digest.lower():
                errors.append(f"Checksum mismatch after import: {rel}")

    runtime = []
    for path in repo.rglob("*"):
        if ".git" in path.parts:
            continue
        if "__pycache__" in path.parts or path.suffix.lower() in {".pyc", ".pyo"}:
            runtime.append(path.relative_to(repo).as_posix())
    if runtime:
        errors.append(f"Runtime artefacts detected: {runtime[:20]}")

    if errors:
        print(json.dumps({"valid": False, "errors": errors}, indent=2))
        return 1
    print(json.dumps({
        "valid": True,
        "build": BUILD,
        "release_gate_version": RELEASE_GATE,
        "required_files": len(REQUIRED),
        "build_neutral_importer": True,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
