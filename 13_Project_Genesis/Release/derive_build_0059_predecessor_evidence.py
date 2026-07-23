from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXPECTED_COMMIT = "594152fcfba3b1612b71d7b6e5c23759c906e464"
EXPECTED_BUILD = "0059"
EXPECTED_CANDIDATE = "RC1"
EXPECTED_PATH_COUNT = 97
MANIFEST_PATH = "Documentation/Build_Records/0059/ASSET_INTENT_MANIFEST.json"
DELIVERY_PATH = "Documentation/Build_Records/0059/CANDIDATE_DELIVERY.json"
MAR_PATH = "Documentation/Master_Asset_Register.csv"
EXPECTED_SUBJECT = "Add Certiaura Build 0059 tesamorelin governed review-board approvals, evidence-pack version control, challenge and appeal resolution, suspension recovery, periodic reassessment and reusable peptide-review operating model baseline"
EXPECTED_FORMAL_UAIS = {
    "Standards/CERTIAURA_POWERSHELL_CLOSURE_EVIDENCE_OUTPUT_STANDARD.md": "CERT-SYS-000871",
    "Standards/REUSABLE_PEPTIDE_REVIEW_OPERATING_MODEL_STANDARD.md": "CERT-SYS-000872",
    "Standards/TESAMORELIN_CHALLENGE_AND_APPEAL_MATRIX.json": "CERT-PKS-000439",
    "Standards/TESAMORELIN_EVIDENCE_PACK_VERSION_CONTROL_STANDARD.md": "CERT-EKS-000790",
    "Standards/TESAMORELIN_PERIODIC_REASSESSMENT_MODEL.json": "CERT-MKS-000221",
    "Standards/TESAMORELIN_REVIEW_BOARD_GOVERNANCE_STANDARD.md": "CERT-SYS-000873",
    "Standards/TESAMORELIN_SUSPENSION_RECOVERY_AND_REENTRY_MATRIX.json": "CERT-PKS-000440",
}


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
    subject = git(repo, "log", "-1", "--format=%s", expected_commit).stdout.strip()
    if subject != EXPECTED_SUBJECT:
        raise RuntimeError("predecessor commit subject does not match closed Build 0059 RC2")
    manifest_raw = git_bytes(repo, "show", f"{expected_commit}:{MANIFEST_PATH}")
    predecessor = json.loads(manifest_raw.decode("utf-8"))

    if str(predecessor.get("build_number")) != EXPECTED_BUILD:
        raise RuntimeError("predecessor manifest build_number is not 0059")
    if str(predecessor.get("candidate")) != EXPECTED_CANDIDATE:
        raise RuntimeError("predecessor candidate is not RC2")

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
            raise RuntimeError("Build 0059 delivery evidence does not identify RC1")

    formal_paths = {
        str(item["repository_path"]).replace("\\\\", "/")
        for item in predecessor.get("files", [])
        if item.get("classification") == "FORMAL_ASSET"
    }
    if formal_paths != set(EXPECTED_FORMAL_UAIS):
        raise RuntimeError("Build 0059 formal-asset path set does not match the locked predecessor fixture")

    mar_text = git_bytes(repo, "show", f"{expected_commit}:{MAR_PATH}").decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(mar_text))
    headers = list(reader.fieldnames or [])
    header_lookup = {header.strip().lower(): header for header in headers}
    uai_col = header_lookup.get("universal asset identifier") or header_lookup.get("uai")
    path_col = header_lookup.get("repository path") or header_lookup.get("canonical path")
    if not uai_col or not path_col:
        raise RuntimeError("predecessor Master Asset Register UAI/path columns cannot be resolved")
    mar_by_path = {
        str(row.get(path_col, "")).strip().replace("\\\\", "/"): str(row.get(uai_col, "")).strip()
        for row in reader
        if str(row.get(path_col, "")).strip()
    }
    observed_formal_uais = {path: mar_by_path.get(path, "") for path in sorted(EXPECTED_FORMAL_UAIS)}
    if observed_formal_uais != EXPECTED_FORMAL_UAIS:
        raise RuntimeError("Build 0059 formal-asset UAI fixture does not match canonical Git history")

    result = {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "CANONICAL_GIT_OBJECTS",
        "predecessor_build": "0059",
        "predecessor_candidate": "RC1",
        "predecessor_commit": expected_commit,
        "predecessor_commit_subject": subject,
        "predecessor_formal_asset_uais": observed_formal_uais,
        "manifest_path": MANIFEST_PATH,
        "predecessor_path_count": len(predecessor_paths),
        "current_build": str(current.get("build_number")),
        "intersection": intersection,
        "approved_intersection": sorted(set(intersection) & allowed),
        "prohibited_intersection": prohibited,
        "withdrawn_candidates": [],
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
