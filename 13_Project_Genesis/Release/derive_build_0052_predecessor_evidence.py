from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXPECTED_COMMIT = "890df218b4f4dea92f4ccfa36b8106de59eca1b1"
EXPECTED_BUILD = "0052"
EXPECTED_CANDIDATE = "RC6"
EXPECTED_PATH_COUNT = 59
MANIFEST_PATH = "Documentation/Build_Records/0052/ASSET_INTENT_MANIFEST.json"
DELIVERY_PATH = "Documentation/Build_Records/0052/CANDIDATE_DELIVERY.json"


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result


def git_bytes(repo: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        error = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {error}")
    return result.stdout


def derive(
    repository: str | Path,
    current_manifest: str | Path,
    report: str | Path | None = None,
    expected_commit: str = EXPECTED_COMMIT,
    expected_count: int = EXPECTED_PATH_COUNT,
) -> dict[str, Any]:
    repo = Path(repository).resolve()
    manifest_file = Path(current_manifest).resolve()
    if not (repo / ".git").exists():
        raise RuntimeError("repository is not a Git working tree")

    git(repo, "cat-file", "-e", f"{expected_commit}^{{commit}}")
    manifest_raw = git_bytes(repo, "show", f"{expected_commit}:{MANIFEST_PATH}")
    predecessor = json.loads(manifest_raw.decode("utf-8"))

    if str(predecessor.get("build_number")) != EXPECTED_BUILD:
        raise RuntimeError("predecessor manifest build_number is not 0052")
    if str(predecessor.get("candidate")) != EXPECTED_CANDIDATE:
        raise RuntimeError("predecessor candidate is not RC6")

    predecessor_paths = sorted(
        {
            str(item["repository_path"]).replace("\\", "/")
            for item in predecessor.get("files", [])
        }
    )
    if len(predecessor_paths) != expected_count:
        raise RuntimeError(
            f"expected {expected_count} predecessor paths but found {len(predecessor_paths)}"
        )

    blobs: list[dict[str, Any]] = []
    for path in predecessor_paths:
        data = git_bytes(repo, "show", f"{expected_commit}:{path}")
        blob = git(repo, "rev-parse", f"{expected_commit}:{path}").stdout.strip()
        blobs.append(
            {
                "repository_path": path,
                "git_blob": blob,
                "sha256": hashlib.sha256(data).hexdigest(),
                "size_bytes": len(data),
            }
        )

    current = json.loads(manifest_file.read_text(encoding="utf-8"))
    current_items = list(current.get("files", [])) + list(
        current.get("generated_files", [])
    )
    current_paths = {
        str(item["repository_path"]).replace("\\", "/") for item in current_items
    }
    allowed = {
        str(item["repository_path"]).replace("\\", "/")
        for item in current_items
        if item.get("approved_predecessor_overlap") is True
    }
    intersection = sorted(set(predecessor_paths) & current_paths)
    prohibited = sorted(set(intersection) - allowed)
    if prohibited:
        raise RuntimeError(
            "unapproved predecessor/current-build path intersection: "
            + ", ".join(prohibited)
        )

    delivery_result = git(
        repo, "cat-file", "-e", f"{expected_commit}:{DELIVERY_PATH}", check=False
    )
    if delivery_result.returncode == 0:
        delivery = json.loads(
            git_bytes(repo, "show", f"{expected_commit}:{DELIVERY_PATH}").decode(
                "utf-8"
            )
        )
        observed_candidate = str(
            delivery.get("candidate") or delivery.get("successful_candidate") or ""
        )
        if observed_candidate and observed_candidate != EXPECTED_CANDIDATE:
            raise RuntimeError("Build 0052 delivery evidence does not identify RC6")

    result = {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "CANONICAL_GIT_OBJECTS",
        "predecessor_build": "0052",
        "predecessor_candidate": "RC6",
        "predecessor_commit": expected_commit,
        "manifest_path": MANIFEST_PATH,
        "predecessor_path_count": len(predecessor_paths),
        "current_build": str(current.get("build_number")),
        "intersection": intersection,
        "approved_intersection": sorted(set(intersection) & allowed),
        "prohibited_intersection": prohibited,
        "withdrawn_candidates": ["RC1", "RC2", "RC3", "RC4", "RC5"],
        "blobs": blobs,
        "result": "PREDECESSOR_CANONICAL_SOURCE_VERIFIED",
    }
    if report:
        path = Path(report)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(result, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository")
    parser.add_argument("current_manifest")
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    try:
        result = derive(args.repository, args.current_manifest, args.report)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:
        failure = {"result": "FAIL", "error": str(exc)}
        path = Path(args.report)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(failure, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(json.dumps(failure, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
