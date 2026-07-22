from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

BUILD_NUMBER = "0051"
BUILD_PROVENANCE = "CERT-BUILD-0051"
EXPECTED_SUBJECT = "Add Certiaura Build 0051 retatrutide post-closure surveillance, governed case reopening, periodic review and recurrence analytics baseline"
MANIFEST_PATH = "Documentation/Build_Records/0051/ASSET_INTENT_MANIFEST.json"


def git(repo: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    result = subprocess.run(["git", "-C", str(repo), *args], input=input_bytes, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError("GIT_COMMAND_FAILED: " + " ".join(args) + ": " + result.stderr.decode("utf-8", "replace").strip())
    return result.stdout


def object_bytes(repo: Path, commit: str, path: str) -> bytes:
    return git(repo, "show", f"{commit}:{path}")


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


PATH_KEYS = ("repository_path", "repository_relative_path", "relative_path", "file_path", "path")


def normalise_repository_path(value: str) -> str:
    if not isinstance(value, str):
        raise RuntimeError("PREDECESSOR_MANIFEST_PATH_NOT_STRING")
    path = value.strip().replace("\\", "/")
    while path.startswith("./"):
        path = path[2:]
    if not path or path.startswith("/") or re.match(r"^[A-Za-z]:/", path) or "\x00" in path:
        raise RuntimeError("PREDECESSOR_MANIFEST_PATH_INVALID")
    parts = path.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise RuntimeError("PREDECESSOR_MANIFEST_PATH_INVALID")
    return "/".join(parts)


def normalised_manifest_entries(manifest: dict) -> tuple[list[tuple[str, dict]], dict]:
    raw_entries = manifest.get("files")
    if isinstance(raw_entries, dict):
        items = []
        for raw_path, metadata in raw_entries.items():
            if metadata is None:
                metadata = {}
            if not isinstance(metadata, dict):
                raise RuntimeError("PREDECESSOR_MANIFEST_FILE_MAP_METADATA_INVALID")
            items.append((normalise_repository_path(raw_path), metadata))
        schema = {"container": "OBJECT_MAP", "path_fields": ["OBJECT_KEY"]}
    elif isinstance(raw_entries, list) and raw_entries:
        items = []
        detected = []
        for index, entry in enumerate(raw_entries):
            if isinstance(entry, str):
                items.append((normalise_repository_path(entry), {}))
                detected.append("STRING_ENTRY")
                continue
            if not isinstance(entry, dict):
                raise RuntimeError(f"PREDECESSOR_MANIFEST_ENTRY_INVALID:{index}")
            candidates = []
            for key in PATH_KEYS:
                value = entry.get(key)
                if isinstance(value, str) and value.strip():
                    candidates.append((key, normalise_repository_path(value)))
            if not candidates:
                keys = ",".join(sorted(str(key) for key in entry.keys()))
                raise RuntimeError(f"PREDECESSOR_MANIFEST_PATH_INVALID:{index}:KEYS={keys}")
            values = {value for _, value in candidates}
            if len(values) != 1:
                raise RuntimeError(f"PREDECESSOR_MANIFEST_PATH_ALIAS_CONFLICT:{index}")
            items.append((next(iter(values)), entry))
            detected.extend(key for key, _ in candidates)
        schema = {"container": "ARRAY", "path_fields": sorted(set(detected))}
    else:
        raise RuntimeError("PREDECESSOR_MANIFEST_FILE_LIST_EMPTY")
    paths = [path for path, _ in items]
    if len(paths) != len(set(paths)):
        raise RuntimeError("PREDECESSOR_MANIFEST_DUPLICATE_PATH")
    if len(paths) != len({path.casefold() for path in paths}):
        raise RuntimeError("PREDECESSOR_MANIFEST_CASE_COLLISION")
    return sorted(items, key=lambda item: item[0]), schema


def paths_from_manifest(manifest: dict) -> list[str]:
    entries, _ = normalised_manifest_entries(manifest)
    return [path for path, _ in entries]


def manifest_path_schema(manifest: dict) -> dict:
    _, schema = normalised_manifest_entries(manifest)
    return schema


def uais_from_manifest(manifest: dict) -> list[str]:
    values = []
    entries, _ = normalised_manifest_entries(manifest)
    for _, entry in entries:
        for key in ("existing_uai", "uai", "universal_asset_identifier", "universal_asset_id"):
            value = entry.get(key)
            if isinstance(value, str) and value.strip():
                values.append(value.strip())
    return sorted(set(values))

def validate_evidence(evidence: dict, fixture_root: Path, current_manifest: dict, expected_package_sha256: str) -> list[str]:
    errors = []
    if evidence.get("build_number") != BUILD_NUMBER:
        errors.append("WRONG_BUILD_NUMBER")
    if evidence.get("build_provenance") != BUILD_PROVENANCE:
        errors.append("WRONG_PROVENANCE")
    if evidence.get("import_commit_subject") != EXPECTED_SUBJECT:
        errors.append("WRONG_COMMIT_SUBJECT")
    for key in ("import_commit_sha", "closed_snapshot_sha", "predecessor_manifest_sha256"):
        value = evidence.get(key)
        if not isinstance(value, str) or not value:
            errors.append("MISSING_" + key.upper())
    if evidence.get("package_sha256") != expected_package_sha256:
        errors.append("PACKAGE_SHA_MISMATCH")
    paths = evidence.get("repository_paths")
    hashes = evidence.get("path_sha256")
    if not isinstance(paths, list) or not paths:
        errors.append("EMPTY_PATH_LIST")
        paths = []
    if len(paths) != len(set(paths)):
        errors.append("DUPLICATE_PATH")
    if not isinstance(hashes, dict) or sorted(hashes) != sorted(paths):
        errors.append("HASH_PATH_SET_MISMATCH")
        hashes = {}
    predecessor_manifest_file = fixture_root / MANIFEST_PATH
    if not predecessor_manifest_file.is_file():
        errors.append("PREDECESSOR_MANIFEST_FIXTURE_MISSING")
    else:
        try:
            predecessor_manifest_bytes = predecessor_manifest_file.read_bytes()
            predecessor_manifest = json.loads(predecessor_manifest_bytes.decode("utf-8"))
            if sha_bytes(predecessor_manifest_bytes) != evidence.get("predecessor_manifest_sha256"):
                errors.append("PREDECESSOR_MANIFEST_SHA_MISMATCH")
            if predecessor_manifest.get("build_number") != BUILD_NUMBER:
                errors.append("PREDECESSOR_MANIFEST_BUILD_MISMATCH")
            if predecessor_manifest.get("build_provenance") not in (None, BUILD_PROVENANCE):
                errors.append("PREDECESSOR_MANIFEST_PROVENANCE_MISMATCH")
            if predecessor_manifest.get("commit_subject") not in (None, EXPECTED_SUBJECT):
                errors.append("PREDECESSOR_MANIFEST_SUBJECT_MISMATCH")
            if manifest_path_schema(predecessor_manifest) != evidence.get("predecessor_manifest_path_schema"):
                errors.append("PREDECESSOR_MANIFEST_SCHEMA_MISMATCH")
            if paths_from_manifest(predecessor_manifest) != sorted(paths):
                errors.append("PREDECESSOR_MANIFEST_EVIDENCE_PATH_MISMATCH")
            if uais_from_manifest(predecessor_manifest) != sorted(evidence.get("universal_asset_identifiers", [])):
                errors.append("PREDECESSOR_UAI_SET_MISMATCH")
        except Exception as exc:
            errors.append("PREDECESSOR_MANIFEST_FIXTURE_INVALID:" + str(exc))
    current_entries = current_manifest.get("files", [])
    current_paths = {x.get("repository_path") for x in current_entries}
    approved = {x.get("repository_path") for x in current_entries if x.get("approved_replacement") is True and x.get("predecessor_build") == BUILD_NUMBER}
    raw_intersection = set(paths) & current_paths
    unauthorised = raw_intersection - approved
    if unauthorised:
        errors.append("UNAUTHORISED_MANIFEST_INTERSECTION")
    recorded_approved = set(evidence.get("approved_replacement_intersection", []))
    if raw_intersection != recorded_approved:
        errors.append("APPROVED_INTERSECTION_MISMATCH")
    for path in paths:
        fixture = fixture_root / path
        if not fixture.is_file():
            errors.append("FIXTURE_PATH_MISSING:" + path)
            continue
        if hashes.get(path) != sha_bytes(fixture.read_bytes()):
            errors.append("FIXTURE_HASH_MISMATCH:" + path)
    return errors


def mutation_tests(base: dict, fixture_root: Path, current_manifest: dict, package_sha: str) -> list[dict]:
    tests = []
    def expect(name, mutate_evidence=None, mutate_manifest=None, mutate_fixture=None):
        evidence = json.loads(json.dumps(base))
        manifest = json.loads(json.dumps(current_manifest))
        temporary = fixture_root
        cleanup = None
        if mutate_evidence:
            mutate_evidence(evidence)
        if mutate_manifest:
            mutate_manifest(manifest)
        if mutate_fixture:
            temporary, cleanup = mutate_fixture(fixture_root, evidence)
        errors = validate_evidence(evidence, temporary, manifest, package_sha)
        if cleanup:
            cleanup()
        tests.append({"name": name, "result": "PASS" if errors else "FAIL", "blocking_errors": errors})
    expect("wrong_build_number", lambda e: e.__setitem__("build_number", "0052"))
    expect("wrong_provenance", lambda e: e.__setitem__("build_provenance", "CERT-BUILD-0052"))
    expect("wrong_commit_subject", lambda e: e.__setitem__("import_commit_subject", "wrong"))
    expect("missing_import_sha", lambda e: e.__setitem__("import_commit_sha", ""))
    expect("missing_closed_sha", lambda e: e.__setitem__("closed_snapshot_sha", ""))
    expect("wrong_manifest_sha", lambda e: e.__setitem__("predecessor_manifest_sha256", ""))
    expect("wrong_package_sha", lambda e: e.__setitem__("package_sha256", "0" * 64))
    expect("empty_paths", lambda e: e.__setitem__("repository_paths", []))
    expect("duplicate_path", lambda e: e["repository_paths"].append(e["repository_paths"][0]))
    expect("invented_path", lambda e: (e["repository_paths"].append("INVENTED.txt"), e["path_sha256"].__setitem__("INVENTED.txt", "0" * 64)))
    expect("missing_hash", lambda e: e["path_sha256"].pop(e["repository_paths"][0]))
    expect("uai_set_tamper", lambda e: e.__setitem__("universal_asset_identifiers", ["CERT-FAKE-000001"]))
    def add_intersection(m):
        current_paths = {x.get("repository_path") for x in m.get("files", [])}
        candidate = next(path for path in base["repository_paths"] if path not in current_paths)
        m["files"].append({"repository_path": candidate, "approved_replacement": False})
    expect("unauthorised_intersection", mutate_manifest=add_intersection)
    expect("approved_intersection_record_mismatch", lambda e: e.__setitem__("approved_replacement_intersection", ["INVENTED.txt"]))
    def missing_fixture(root, evidence):
        import shutil, tempfile
        temporary = Path(tempfile.mkdtemp(prefix="pred_negative_"))
        shutil.copytree(root, temporary / "fixture")
        fixture = temporary / "fixture"
        target = fixture / evidence["repository_paths"][0]
        target.unlink()
        return fixture, lambda: shutil.rmtree(temporary)
    expect("missing_fixture_file", mutate_fixture=missing_fixture)
    return tests


def derive(repo: Path, current_manifest_path: Path, output_root: Path, package_sha: str) -> dict:
    if not (repo / ".git").is_dir():
        raise RuntimeError("PREDECESSOR_REPOSITORY_INVALID")
    current_manifest = json.loads(current_manifest_path.read_text(encoding="utf-8"))
    log = git(repo, "log", "--all", "--format=%H%x00%s").decode("utf-8", "replace").splitlines()
    matches = []
    for line in log:
        if "\x00" not in line:
            continue
        commit, subject = line.split("\x00", 1)
        if subject == EXPECTED_SUBJECT:
            matches.append(commit)
    if len(matches) != 1:
        raise RuntimeError(f"PREDECESSOR_IMPORT_COMMIT_MATCH_COUNT:{len(matches)}")
    import_commit = matches[0]
    closed_snapshot = git(repo, "rev-parse", "HEAD").decode().strip()
    ancestor = subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", import_commit, closed_snapshot])
    if ancestor.returncode != 0:
        raise RuntimeError("PREDECESSOR_IMPORT_NOT_ANCESTOR_OF_CLOSED_SNAPSHOT")
    manifest_import_bytes = object_bytes(repo, import_commit, MANIFEST_PATH)
    manifest_closed_bytes = object_bytes(repo, closed_snapshot, MANIFEST_PATH)
    manifest_import = json.loads(manifest_import_bytes.decode("utf-8"))
    manifest_closed = json.loads(manifest_closed_bytes.decode("utf-8"))
    if manifest_import.get("build_number") != BUILD_NUMBER or manifest_closed.get("build_number") != BUILD_NUMBER:
        raise RuntimeError("PREDECESSOR_MANIFEST_BUILD_NUMBER_MISMATCH")
    for manifest in (manifest_import, manifest_closed):
        if manifest.get("build_provenance") not in (None, BUILD_PROVENANCE):
            raise RuntimeError("PREDECESSOR_MANIFEST_PROVENANCE_MISMATCH")
        if manifest.get("commit_subject") not in (None, EXPECTED_SUBJECT):
            raise RuntimeError("PREDECESSOR_MANIFEST_COMMIT_SUBJECT_MISMATCH")
    import_paths = paths_from_manifest(manifest_import)
    closed_paths = paths_from_manifest(manifest_closed)
    import_schema = manifest_path_schema(manifest_import)
    closed_schema = manifest_path_schema(manifest_closed)
    if import_schema != closed_schema:
        raise RuntimeError("PREDECESSOR_IMPORT_CLOSED_MANIFEST_SCHEMA_MISMATCH")
    if import_paths != closed_paths:
        raise RuntimeError("PREDECESSOR_IMPORT_CLOSED_PATH_SET_MISMATCH")
    import_uais = uais_from_manifest(manifest_import)
    closed_uais = uais_from_manifest(manifest_closed)
    if import_uais != closed_uais:
        raise RuntimeError("PREDECESSOR_IMPORT_CLOSED_UAI_SET_MISMATCH")
    fixture_root = output_root / "Predecessor_Repository"
    fixture_root.mkdir(parents=True, exist_ok=False)
    manifest_fixture = fixture_root / MANIFEST_PATH
    manifest_fixture.parent.mkdir(parents=True, exist_ok=True)
    manifest_fixture.write_bytes(manifest_closed_bytes)
    path_hashes = {}
    for path in closed_paths:
        data = object_bytes(repo, closed_snapshot, path)
        target = fixture_root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        path_hashes[path] = sha_bytes(data)
    current_entries = current_manifest.get("files", [])
    current_paths = {x.get("repository_path") for x in current_entries}
    approved = {x.get("repository_path") for x in current_entries if x.get("approved_replacement") is True and x.get("predecessor_build") == BUILD_NUMBER}
    raw_intersection = sorted(set(closed_paths) & current_paths)
    unauthorised = sorted(set(raw_intersection) - approved)
    if unauthorised:
        raise RuntimeError("PREDECESSOR_CURRENT_UNAUTHORISED_INTERSECTION:" + ",".join(unauthorised))
    evidence = {
        "result": "PREDECESSOR_CANONICAL_EVIDENCE_VALIDATED",
        "source": "CANONICAL_GIT_OBJECT_DATABASE",
        "build_number": BUILD_NUMBER,
        "build_provenance": BUILD_PROVENANCE,
        "import_commit_subject": EXPECTED_SUBJECT,
        "import_commit_sha": import_commit,
        "closed_snapshot_sha": closed_snapshot,
        "predecessor_manifest_path": MANIFEST_PATH,
        "predecessor_manifest_sha256": sha_bytes(manifest_closed_bytes),
        "predecessor_manifest_path_schema": closed_schema,
        "import_closed_manifest_byte_equality": manifest_import_bytes == manifest_closed_bytes,
        "repository_paths": closed_paths,
        "path_count": len(closed_paths),
        "path_sha256": path_hashes,
        "universal_asset_identifiers": closed_uais,
        "raw_manifest_intersection": raw_intersection,
        "approved_replacement_intersection": raw_intersection,
        "unauthorised_manifest_intersection": [],
        "package_sha256": package_sha,
    }
    errors = validate_evidence(evidence, fixture_root, current_manifest, package_sha)
    if errors:
        raise RuntimeError("PREDECESSOR_EVIDENCE_VALIDATION_FAILED:" + ",".join(errors))
    negatives = mutation_tests(evidence, fixture_root, current_manifest, package_sha)
    if len(negatives) != 15 or any(x["result"] != "PASS" for x in negatives):
        raise RuntimeError("PREDECESSOR_NEGATIVE_TESTS_FAILED")
    evidence["negative_tests"] = negatives
    evidence["negative_test_count"] = len(negatives)
    evidence["negative_tests_result"] = "PASS"
    (output_root / "PREDECESSOR_CANONICAL_EVIDENCE.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8", newline="\n")
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", required=True)
    parser.add_argument("--current-manifest", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--package-sha256", required=True)
    args = parser.parse_args()
    output = Path(args.output_root).resolve()
    if output.exists():
        raise RuntimeError("PREDECESSOR_OUTPUT_ALREADY_EXISTS")
    output.mkdir(parents=True)
    evidence = derive(Path(args.repository).resolve(), Path(args.current_manifest).resolve(), output, args.package_sha256.upper())
    print(json.dumps({"result": evidence["result"], "path_count": evidence["path_count"], "negative_tests": evidence["negative_test_count"]}, indent=2))
    print("PREDECESSOR_CANONICAL_EVIDENCE_VALIDATED")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
