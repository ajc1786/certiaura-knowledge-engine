from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SHA_RE = re.compile(r"^[0-9a-f]{40}$")
EXACT_ADD_RE = re.compile(r"^Add Certiaura Build\s+0*([0-9]{1,4})([A-Za-z]?)\b", re.I)
CERTIAURA_BUILD_RE = re.compile(r"\bCertiaura Build\s+0*([0-9]{1,4})([A-Za-z]?)\b", re.I)
PREFERRED_WORKFLOW = "Certiaura Repository Validation"
ALLOWED_RESOLVED_CLASSIFICATIONS = {
    "RUN_ID_VERIFIED",
    "NO_WORKFLOW_AT_COMMIT",
    "NO_RUN_FOUND",
    "RUN_FOUND_NOT_SUCCESS",
    "BUILD_COMMIT_NOT_FOUND",
}


@dataclass(frozen=True)
class CommitRecord:
    sha: str
    subject: str
    position: int
    exact_add: bool
    build_label: str


def run_git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed ({result.returncode}): {result.stderr.strip()}"
        )
    return result.stdout


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def parse_build_subject(subject: str) -> tuple[int, str, bool] | None:
    exact = EXACT_ADD_RE.search(subject)
    if exact:
        number = int(exact.group(1))
        suffix = exact.group(2).upper()
        return number, f"{number:04d}{suffix}", True
    fallback = CERTIAURA_BUILD_RE.search(subject)
    if fallback:
        number = int(fallback.group(1))
        suffix = fallback.group(2).upper()
        return number, f"{number:04d}{suffix}", False
    return None


def first_parent_commits(repo: Path) -> list[tuple[str, str]]:
    raw = run_git(repo, "log", "--first-parent", "--reverse", "--format=%H%x00%s")
    commits: list[tuple[str, str]] = []
    for line in raw.splitlines():
        if "\x00" not in line:
            continue
        sha, subject = line.split("\x00", 1)
        if SHA_RE.match(sha):
            commits.append((sha, subject))
    return commits


def candidate_commits(repo: Path, start: int, end: int) -> dict[int, list[CommitRecord]]:
    result: dict[int, list[CommitRecord]] = {number: [] for number in range(start, end + 1)}
    for position, (sha, subject) in enumerate(first_parent_commits(repo)):
        parsed = parse_build_subject(subject)
        if not parsed:
            continue
        number, label, exact_add = parsed
        if start <= number <= end:
            result[number].append(
                CommitRecord(
                    sha=sha,
                    subject=subject,
                    position=position,
                    exact_add=exact_add,
                    build_label=label,
                )
            )
    return result


def choose_canonical(candidates: list[CommitRecord]) -> tuple[CommitRecord | None, str]:
    exact = [item for item in candidates if item.exact_add]
    if exact:
        return exact[-1], "LATEST_EXACT_ADD_SUBJECT_ON_FIRST_PARENT_MAIN"
    if candidates:
        return candidates[-1], "LATEST_CERTIAURA_BUILD_SUBJECT_FALLBACK"
    return None, "NO_MATCHING_BUILD_COMMIT"


def github_headers(token: str | None) -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Certiaura-Historical-Actions-Audit",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def fetch_all_runs(owner: str, repository: str, token: str | None) -> list[dict[str, Any]]:
    runs: list[dict[str, Any]] = []
    page = 1
    headers = github_headers(token)
    while page <= 100:
        query = urllib.parse.urlencode({"per_page": 100, "page": page})
        url = f"https://api.github.com/repos/{owner}/{repository}/actions/runs?{query}"
        request = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"GitHub API HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"GitHub API connection failed: {exc}") from exc
        page_runs = list(payload.get("workflow_runs", []))
        runs.extend(page_runs)
        if len(page_runs) < 100:
            break
        page += 1
    return runs


def runs_by_sha(runs: Iterable[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for run in runs:
        sha = str(run.get("head_sha", "")).lower()
        if SHA_RE.match(sha):
            result.setdefault(sha, []).append(run)
    for values in result.values():
        values.sort(key=lambda item: str(item.get("created_at", "")))
    return result


def workflow_present(repo: Path, commit: str) -> bool:
    output = run_git(
        repo,
        "ls-tree",
        "-r",
        "--name-only",
        commit,
        "--",
        ".github/workflows",
        check=False,
    )
    return any(line.strip().endswith((".yml", ".yaml")) for line in output.splitlines())


def select_run(values: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, list[str]]:
    relevant = [
        item
        for item in values
        if str(item.get("event", "")) == "push"
        and str(item.get("head_branch", "")) == "main"
    ]
    preferred = [item for item in relevant if str(item.get("name", "")) == PREFERRED_WORKFLOW]
    pool = preferred or relevant or values
    successful = [
        item
        for item in pool
        if str(item.get("status", "")) == "completed"
        and str(item.get("conclusion", "")) == "success"
    ]
    chosen_pool = successful or pool
    if not chosen_pool:
        return None, []
    chosen = sorted(
        chosen_pool,
        key=lambda item: (
            str(item.get("created_at", "")),
            int(item.get("run_attempt") or 0),
            int(item.get("id") or 0),
        ),
    )[-1]
    return chosen, [str(item.get("id")) for item in pool if item.get("id")]


def commit_contains(repo: Path, commit: str, needle: str) -> bool:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "grep",
            "-F",
            "--quiet",
            needle,
            commit,
            "--",
            "Documentation",
            "00_Governance",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def capture_status(
    repo: Path,
    first_parent: list[tuple[str, str]],
    selected: CommitRecord,
    next_position: int | None,
    run_id: str,
) -> tuple[str, str | None]:
    upper = next_position if next_position is not None else len(first_parent)
    for sha, _subject in first_parent[selected.position + 1 : upper]:
        if commit_contains(repo, sha, run_id):
            return "CONTEMPORANEOUS_HISTORY_CONFIRMED", sha
    if commit_contains(repo, "HEAD", run_id):
        return "CURRENT_REPOSITORY_RECORD_ONLY", None
    return "BACKFILLED_BY_BUILD_0055", None


def make_record(
    build_number: int,
    candidates: list[CommitRecord],
    selected: CommitRecord | None,
    selection_basis: str,
    run_index: dict[str, list[dict[str, Any]]],
    repo: Path,
    first_parent: list[tuple[str, str]],
    next_position: int | None,
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "build_number": f"{build_number:04d}",
        "candidate_commit_count": len(candidates),
        "candidate_commits": [
            {
                "commit": item.sha,
                "subject": item.subject,
                "build_label": item.build_label,
                "exact_add_subject": item.exact_add,
            }
            for item in candidates
        ],
        "selection_basis": selection_basis,
        "canonical_commit": selected.sha if selected else None,
        "canonical_subject": selected.subject if selected else None,
        "workflow_present_at_commit": False,
        "classification": "BUILD_COMMIT_NOT_FOUND",
        "run_id": None,
        "workflow_name": None,
        "run_attempt": None,
        "status": None,
        "conclusion": None,
        "branch": None,
        "event": None,
        "created_at": None,
        "updated_at": None,
        "actions_url": None,
        "all_candidate_run_ids": [],
        "capture_status": "NOT_APPLICABLE",
        "capture_commit": None,
        "accounted": False,
    }
    if selected is None:
        base["accounted"] = True
        base["capture_status"] = "RESOLVED_EXCEPTION"
        return base
    base["workflow_present_at_commit"] = workflow_present(repo, selected.sha)
    values = run_index.get(selected.sha.lower(), [])
    chosen, all_ids = select_run(values)
    base["all_candidate_run_ids"] = all_ids
    if chosen is None:
        base["classification"] = (
            "NO_WORKFLOW_AT_COMMIT"
            if not base["workflow_present_at_commit"]
            else "NO_RUN_FOUND"
        )
        base["accounted"] = True
        base["capture_status"] = "RESOLVED_EXCEPTION"
        return base
    base.update(
        {
            "run_id": str(chosen.get("id")) if chosen.get("id") else None,
            "workflow_name": chosen.get("name"),
            "run_attempt": chosen.get("run_attempt"),
            "status": chosen.get("status"),
            "conclusion": chosen.get("conclusion"),
            "branch": chosen.get("head_branch"),
            "event": chosen.get("event"),
            "created_at": chosen.get("created_at"),
            "updated_at": chosen.get("updated_at"),
            "actions_url": chosen.get("html_url"),
        }
    )
    success = (
        base["run_id"] is not None
        and base["status"] == "completed"
        and base["conclusion"] == "success"
        and str(chosen.get("head_sha", "")).lower() == selected.sha.lower()
    )
    base["classification"] = "RUN_ID_VERIFIED" if success else "RUN_FOUND_NOT_SUCCESS"
    base["accounted"] = True
    if base["run_id"]:
        status, commit = capture_status(
            repo,
            first_parent,
            selected,
            next_position,
            str(base["run_id"]),
        )
        base["capture_status"] = status
        base["capture_commit"] = commit
    return base


def write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    fields = [
        "build_number",
        "canonical_commit",
        "canonical_subject",
        "classification",
        "run_id",
        "workflow_name",
        "run_attempt",
        "status",
        "conclusion",
        "branch",
        "event",
        "created_at",
        "updated_at",
        "capture_status",
        "capture_commit",
        "workflow_present_at_commit",
        "candidate_commit_count",
        "selection_basis",
        "accounted",
        "actions_url",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for record in records:
            writer.writerow({field: record.get(field) for field in fields})


def audit(
    repository: Path,
    owner: str,
    repository_name: str,
    output_directory: Path,
    start_build: int,
    end_build: int,
    token: str | None,
) -> dict[str, Any]:
    if not (repository / ".git").exists():
        raise RuntimeError(f"not a Git repository: {repository}")
    first_parent = first_parent_commits(repository)
    candidates = candidate_commits(repository, start_build, end_build)
    runs = fetch_all_runs(owner, repository_name, token)
    run_index = runs_by_sha(runs)
    selected_map: dict[int, CommitRecord | None] = {}
    basis_map: dict[int, str] = {}
    for number in range(start_build, end_build + 1):
        selected, basis = choose_canonical(candidates[number])
        selected_map[number] = selected
        basis_map[number] = basis
    records: list[dict[str, Any]] = []
    for number in range(start_build, end_build + 1):
        next_position = None
        for future in range(number + 1, end_build + 1):
            future_commit = selected_map.get(future)
            if future_commit is not None:
                next_position = future_commit.position
                break
        records.append(
            make_record(
                number,
                candidates[number],
                selected_map[number],
                basis_map[number],
                run_index,
                repository,
                first_parent,
                next_position,
            )
        )
    unresolved = [record for record in records if not record["accounted"]]
    exceptions = [
        record
        for record in records
        if record["classification"] != "RUN_ID_VERIFIED"
    ]
    verified = [record for record in records if record["classification"] == "RUN_ID_VERIFIED"]
    contemporaneous = [
        record
        for record in verified
        if record["capture_status"] == "CONTEMPORANEOUS_HISTORY_CONFIRMED"
    ]
    backfilled = [
        record
        for record in verified
        if record["capture_status"] != "CONTEMPORANEOUS_HISTORY_CONFIRMED"
    ]
    all_accounted = len(records) == end_build - start_build + 1 and not unresolved
    summary = {
        "schema_version": "1.0.0",
        "audit_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "repository": f"{owner}/{repository_name}",
        "repository_head": run_git(repository, "rev-parse", "HEAD").strip(),
        "build_range": {"start": f"{start_build:04d}", "end": f"{end_build:04d}"},
        "expected_build_count": end_build - start_build + 1,
        "record_count": len(records),
        "accounted_count": sum(1 for record in records if record["accounted"]),
        "verified_run_id_count": len(verified),
        "contemporaneous_capture_count": len(contemporaneous),
        "backfilled_or_current_record_count": len(backfilled),
        "exception_count": len(exceptions),
        "unresolved_count": len(unresolved),
        "all_builds_accounted": all_accounted,
        "all_exact_run_ids_captured": len(verified) == len(records),
        "result": (
            "HISTORICAL_ACTIONS_AUDIT_COMPLETE"
            if all_accounted
            else "HISTORICAL_ACTIONS_AUDIT_INCOMPLETE"
        ),
    }
    evidence = {
        "schema_version": "1.0.0",
        "summary": summary,
        "records": records,
    }
    output_directory.mkdir(parents=True, exist_ok=True)
    write_json(output_directory / "HISTORICAL_GITHUB_ACTIONS_EVIDENCE.json", evidence)
    write_csv(output_directory / "HISTORICAL_GITHUB_ACTIONS_EVIDENCE_REGISTER.csv", records)
    write_json(
        output_directory / "HISTORICAL_GITHUB_ACTIONS_EXCEPTIONS.json",
        {
            "schema_version": "1.0.0",
            "exception_count": len(exceptions),
            "exceptions": exceptions,
        },
    )
    write_json(
        output_directory / "HISTORICAL_GITHUB_ACTIONS_AUDIT_SUMMARY.json",
        summary,
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository")
    parser.add_argument("--owner", default="ajc1786")
    parser.add_argument("--repository-name", default="certiaura-knowledge-engine")
    parser.add_argument("--output-directory", required=True)
    parser.add_argument("--start-build", type=int, default=1)
    parser.add_argument("--end-build", type=int, default=54)
    parser.add_argument("--token")
    args = parser.parse_args()
    token = args.token or os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    try:
        summary = audit(
            Path(args.repository).resolve(),
            args.owner,
            args.repository_name,
            Path(args.output_directory).resolve(),
            args.start_build,
            args.end_build,
            token,
        )
    except Exception as exc:
        print(json.dumps({"result": "HISTORICAL_ACTIONS_AUDIT_FAILED", "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(summary, indent=2))
    return 0 if summary["result"] == "HISTORICAL_ACTIONS_AUDIT_COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
