from __future__ import annotations

import argparse
import hashlib
import json
import py_compile
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


def run(command, cwd=None, expected=0):
    result = subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != expected:
        raise RuntimeError(
            f"command failed ({result.returncode}, expected {expected}): {' '.join(map(str, command))}\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package")
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    package = Path(args.package).resolve()
    report = Path(args.report).resolve()
    errors = []
    checks = {}
    try:
        checks["zip_sha256"] = hashlib.sha256(package.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "payload"
            with zipfile.ZipFile(package) as zf:
                zf.extractall(root)
            manifest = json.loads((root / "Documentation/Build_Records/0058/ASSET_INTENT_MANIFEST.json").read_text(encoding="utf-8"))
            names = sorted(str(path.relative_to(root)).replace("\\", "/") for path in root.rglob("*") if path.is_file())
            declared = sorted(str(item["repository_path"]).replace("\\", "/") for item in manifest["files"])
            if names != declared:
                errors.append("extracted package paths do not equal Asset Intent Manifest files")
            checks["package_path_count"] = len(names)
            for path in root.rglob("*.json"):
                json.loads(path.read_text(encoding="utf-8"))
            checks["json_parse"] = "PASS"
            for path in root.rglob("*.py"):
                py_compile.compile(str(path), doraise=True)
            for cache in root.rglob("__pycache__"):
                shutil.rmtree(cache)
            checks["python_compile"] = "PASS"

            example_items = [item for item in manifest["files"] if item.get("classification") == "EXAMPLE"]
            validator = root / "13_Project_Genesis/Validators/validate_tesamorelin_longitudinal_review.py"
            for item in example_items:
                path = root / item["repository_path"]
                expected = 1 if path.name.startswith("invalid_") else 0
                run([sys.executable, "-B", str(validator), str(path)], expected=expected)
            checks["example_contracts"] = "PASS"

            tests = run([sys.executable, "-B", "-m", "unittest", "discover", "-s", "13_Project_Genesis/Tests", "-p", "test_build_0058_*.py", "-v"], cwd=root)
            checks["automated_tests"] = "PASS"
            checks["test_output"] = tests.stdout[-8000:]
    except Exception as exc:
        errors.append(str(exc))
    result = {
        "build_number": "0058",
        "candidate": "RC2",
        "valid": not errors,
        "checks": checks,
        "errors": errors,
        "result": "CANDIDATE_RELEASE_VALIDATED" if not errors else "FAIL",
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
