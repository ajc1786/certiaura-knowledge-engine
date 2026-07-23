from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def git_bytes(repo: Path, spec: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), "show", spec],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository")
    parser.add_argument("manifest")
    parser.add_argument("--report")
    args = parser.parse_args()
    repo = Path(args.repository).resolve()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    paths = sorted(
        {
            str(item["repository_path"]).replace("\\", "/")
            for item in manifest.get("files", []) + manifest.get("generated_files", [])
        }
    )
    errors: list[str] = []
    for rel in paths:
        working_path = repo / rel
        if not working_path.is_file():
            errors.append(f"working-tree path missing: {rel}")
            continue
        try:
            index_bytes = git_bytes(repo, f":{rel}")
        except Exception as exc:
            errors.append(f"index path unreadable {rel}: {exc}")
            continue
        if working_path.read_bytes() != index_bytes:
            errors.append(f"raw working-tree/index byte mismatch: {rel}")
    result = {
        "build_number": str(manifest.get("build_number", "")),
        "path_count": len(paths),
        "valid": not errors,
        "errors": errors,
        "result": "STAGED_BYTE_EQUALITY_VALIDATED" if not errors else "FAIL",
    }
    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(
            json.dumps(result, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
