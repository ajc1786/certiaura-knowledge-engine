from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import zipfile
from pathlib import PurePosixPath

BUILD_ID = "CERT-BUILD-0047"
MANIFEST = "Documentation/Build_Records/0047/ASSET_INTENT_MANIFEST.json"
INVENTORY = "Documentation/Build_Records/0047/PACKAGE_INVENTORY.csv"
CHECKSUMS = "Documentation/Build_Records/0047/CHECKSUMS.sha256"
ALLOWED_ROOTS = {
    "00_Governance", "01_Knowledge_Systems", "02_Peptides", "03_Biology", "04_Conditions",
    "05_Monitoring", "06_Evidence", "07_Goals", "08_Product_Passports", "09_Cost_Intelligence",
    "10_Marketplace", "11_Academy", "12_Reports", "13_Project_Genesis", "Assets", "Database",
    "Documentation", "Images", "Schemas", "Scripts", "Standards", "Templates",
}
TEXT_EXTENSIONS = {".md", ".json", ".csv", ".py", ".ps1", ".cmd", ".txt", ".sha256"}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package")
    args = parser.parse_args()
    errors: list[str] = []
    with zipfile.ZipFile(args.package) as zf:
        names = sorted(i.filename.replace("\\", "/") for i in zf.infolist() if not i.is_dir())
        lowered: set[str] = set()
        for name in names:
            p = PurePosixPath(name)
            if p.is_absolute() or ".." in p.parts or p.parts[0] not in ALLOWED_ROOTS:
                errors.append(f"unsafe or unauthorised path: {name}")
            if name.lower() in lowered:
                errors.append(f"duplicate or case-only collision: {name}")
            lowered.add(name.lower())
            if "__pycache__" in p.parts or p.suffix.lower() in {".pyc", ".pyo"}:
                errors.append(f"runtime artefact: {name}")
        for required in (MANIFEST, INVENTORY, CHECKSUMS):
            if required not in names:
                errors.append(f"missing required package record: {required}")
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2))
            return 1

        manifest = json.loads(zf.read(MANIFEST).decode("utf-8"))
        if manifest.get("build_id") != BUILD_ID:
            errors.append("manifest build_id mismatch")
        declared = sorted(item.get("path") for item in manifest.get("files", []))
        if declared != names:
            errors.append(f"manifest/archive mismatch missing={sorted(set(names)-set(declared))} extra={sorted(set(declared)-set(names))}")
        for item in manifest.get("files", []):
            if item.get("build_provenance") != BUILD_ID:
                errors.append(f"manifest provenance mismatch: {item.get('path')}")

        inventory_rows = list(csv.DictReader(io.StringIO(zf.read(INVENTORY).decode("utf-8"))))
        inventory_paths = sorted(row["path"] for row in inventory_rows)
        if inventory_paths != names:
            errors.append("inventory/archive mismatch")

        checksum_lines = zf.read(CHECKSUMS).decode("ascii").splitlines()
        expected = {}
        for line in checksum_lines:
            if not line.strip():
                continue
            value, path = line.split("  ", 1)
            expected[path] = value.upper()
        check_targets = [n for n in names if n != CHECKSUMS]
        if sorted(expected) != sorted(check_targets):
            errors.append("checksum target set mismatch")
        for name in check_targets:
            actual = digest(zf.read(name))
            if expected.get(name) != actual:
                errors.append(f"checksum mismatch: {name}")

        for name in names:
            p = PurePosixPath(name)
            if p.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            data = zf.read(name)
            if b"\r" in data:
                errors.append(f"non-LF line ending: {name}")
            if not data.endswith(b"\n"):
                errors.append(f"missing final newline: {name}")
            for number, line in enumerate(data.split(b"\n"), 1):
                if line.endswith(b" ") or line.endswith(b"\t"):
                    errors.append(f"trailing whitespace: {name}:{number}")
            if p.suffix.lower() in {".ps1", ".cmd"} and any(byte > 127 for byte in data):
                errors.append(f"non-ASCII PowerShell/CMD file: {name}")
            if p.suffix.lower() == ".json":
                try:
                    json.loads(data.decode("utf-8"))
                except Exception as exc:
                    errors.append(f"invalid JSON {name}: {exc}")
    result = {"valid": not errors, "errors": errors, "package_file_count": len(names), "build_id": BUILD_ID}
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
