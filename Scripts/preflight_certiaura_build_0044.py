from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path, PurePosixPath

ALLOWED_ROOTS = {
    "00_Governance", "01_Knowledge_Systems", "02_Peptides", "03_Biology",
    "04_Conditions", "05_Monitoring", "06_Evidence", "07_Goals",
    "08_Product_Passports", "09_Cost_Intelligence", "10_Marketplace",
    "11_Academy", "12_Reports", "13_Project_Genesis", "Assets", "Database",
    "Documentation", "Images", "Schemas", "Scripts", "Standards", "Templates"
}
TEXT_SUFFIXES = {
    ".md", ".json", ".csv", ".py", ".ps1", ".cmd", ".bat", ".txt",
    ".html", ".css", ".js", ".yml", ".yaml", ".xml"
}
REQUIRED = {
    "Documentation/Build_Records/0044/BUILD_MANIFEST.json",
    "Documentation/Build_Records/0044/ASSET_INTENT_MANIFEST.json",
    "Documentation/Build_Records/0044/PACKAGE_CONTENT_SHA256.json",
    "Documentation/Build_Records/0044/PACKAGE_INVENTORY.json",
    "Scripts/Invoke_Certiaura_Build_0044_Windows_PS51_Regression.ps1",
    "Scripts/Run_Certiaura_Build_0044.ps1"
}

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def text_hygiene(name: str, data: bytes, errors: list[str]) -> None:
    suffix = PurePosixPath(name).suffix.lower()
    if suffix not in TEXT_SUFFIXES:
        return
    if data.startswith(b"\xef\xbb\xbf"):
        errors.append(f"UTF-8 BOM is not permitted: {name}")
    if b"\r" in data:
        errors.append(f"Repository text must use LF line endings: {name}")
    if not data.endswith(b"\n"):
        errors.append(f"Repository text must end with one newline: {name}")
    for number, line in enumerate(data.splitlines(), 1):
        if line.endswith((b" ", b"\t")):
            errors.append(f"Trailing whitespace at {name}:{number}")
    if suffix == ".ps1" and any(byte > 127 for byte in data):
        errors.append(f"Non-ASCII byte in Windows PowerShell 5.1 script: {name}")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package")
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    errors: list[str] = []
    package = Path(args.package)

    if not package.is_file():
        errors.append(f"Package not found: {package}")
        names: list[str] = []
        roots: set[str] = set()
    else:
        with zipfile.ZipFile(package) as archive:
            names = [name for name in archive.namelist() if not name.endswith("/")]
            roots = {PurePosixPath(name).parts[0] for name in names}
            if roots - ALLOWED_ROOTS:
                errors.append("Unauthorised root routes: " + ", ".join(sorted(roots - ALLOWED_ROOTS)))
            if len(roots) == 1 and next(iter(roots)).lower().startswith("certiaura_build_"):
                errors.append("Build-named wrapper folder detected")
            lower_paths: dict[str, str] = {}
            for name in names:
                lowered = name.lower()
                if lowered in lower_paths and lower_paths[lowered] != name:
                    errors.append(f"Case-only path collision: {lower_paths[lowered]} / {name}")
                lower_paths[lowered] = name
                text_hygiene(name, archive.read(name), errors)
            for required in sorted(REQUIRED):
                if required not in names:
                    errors.append("Missing required package file: " + required)

            if not errors:
                intent = json.loads(archive.read(
                    "Documentation/Build_Records/0044/ASSET_INTENT_MANIFEST.json"
                ))
                classifications = [item["path"] for item in intent.get("file_classifications", [])]
                missing = sorted(set(names) - set(classifications))
                extra = sorted(set(classifications) - set(names))
                if missing:
                    errors.append("Unclassified package files: " + ", ".join(missing))
                if extra:
                    errors.append("Classified paths absent from package: " + ", ".join(extra))
                if len(classifications) != len(set(classifications)):
                    errors.append("Duplicate file classifications detected")

                checks = json.loads(archive.read(
                    "Documentation/Build_Records/0044/PACKAGE_CONTENT_SHA256.json"
                ))
                checksum_paths = [item["path"] for item in checks.get("files", [])]
                expected_checksum_paths = sorted(
                    name for name in names
                    if name != "Documentation/Build_Records/0044/PACKAGE_CONTENT_SHA256.json"
                )
                if sorted(checksum_paths) != expected_checksum_paths:
                    errors.append("Checksum inventory does not exactly match package contents")
                for item in checks.get("files", []):
                    if item["path"] in names and digest(archive.read(item["path"])) != item["sha256"]:
                        errors.append("Checksum mismatch: " + item["path"])

                for name in names:
                    if PurePosixPath(name).suffix.lower() == ".json":
                        try:
                            json.loads(archive.read(name).decode("utf-8"))
                        except Exception as exc:
                            errors.append(f"Invalid JSON {name}: {exc}")

    result = {
        "valid": not errors,
        "build_number": "0044",
        "package_file_count": len(names),
        "roots": sorted(roots),
        "ascii_only_powershell": not any("Non-ASCII byte" in error for error in errors),
        "repository_text_hygiene": not any(
            marker in error
            for error in errors
            for marker in ["line endings", "newline", "Trailing whitespace", "BOM"]
        ),
        "errors": errors
    }
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
