#!/usr/bin/env python3
"""Transactionally merge Certiaura lesson matrices into the cumulative source."""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

REQUIRED = [
    "lesson_id",
    "origin_builds",
    "control_family",
    "defect_or_risk",
    "root_cause",
    "preventive_control",
    "regression_control",
    "release_gate",
    "status",
]
BEGIN = "<!-- BEGIN AUTO-GENERATED LESSON LEDGER -->"
END = "<!-- END AUTO-GENERATED LESSON LEDGER -->"
ALIASES = {
    "lesson_id": ("lesson_id", "control_id", "lesson_identifier", "id"),
    "origin_builds": ("origin_builds", "origin_build", "builds", "source_builds"),
    "control_family": ("control_family", "category", "control_area", "family", "control_category"),
    "defect_or_risk": (
        "defect_or_risk",
        "defect",
        "risk",
        "issue",
        "problem",
        "finding",
        "lesson",
        "description",
    ),
    "root_cause": ("root_cause", "cause", "root_cause_analysis", "why"),
    "preventive_control": (
        "preventive_control",
        "prevention",
        "preventive_action",
        "corrective_action",
        "control",
        "locked_control",
        "mitigation",
        "action_taken",
    ),
    "regression_control": (
        "regression_control",
        "regression_test",
        "test",
        "validation",
        "verification",
        "test_evidence",
    ),
    "release_gate": (
        "release_gate",
        "release_gate_amendment",
        "gate",
        "validation_gate",
        "closure_gate",
    ),
    "status": ("status", "state"),
}
LEGACY_DEFAULTS = {
    "root_cause": "Not recorded in the legacy matrix; preserved through controlled historical schema migration.",
    "preventive_control": "Retain this historical lesson in the cumulative source and require an equivalent or stronger control in current builds.",
    "regression_control": "Validate that the migrated historical lesson remains present, traceable to its source matrix and is not silently dropped.",
    "release_gate": "HISTORICAL_LESSON_SCHEMA_MIGRATED",
    "status": "LOCKED_ACTIVE_HISTORICAL_MIGRATION",
}


def fail(code: str, message: str) -> None:
    raise RuntimeError(f"{code}: {message}")


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail("LESSONS_JSON_INVALID", f"{path}: {exc}")


def first_present(item: dict, candidates: tuple[str, ...]):
    for candidate in candidates:
        value = item.get(candidate)
        if value not in (None, "", [], {}):
            return candidate, value
    return None, None


def humanise_token(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9]+", " ", value).strip()
    text = re.sub(r"\s+", " ", text)
    return text.title() if text else "Historical legacy control"


def infer_control_family(item: dict, build_number: str) -> tuple[str, str]:
    for key in ("release_gate", "lesson_id", "defect_or_risk"):
        value = item.get(key)
        if value not in (None, ""):
            if key == "lesson_id":
                match = re.search(r"CERT-LESSON-([A-Z0-9]+)", str(value).upper())
                if match:
                    return f"Historical {humanise_token(match.group(1))} control", "INFERRED_FROM_LESSON_ID"
            if key == "release_gate":
                token = re.sub(r"_(?:VALIDATED|COMPLETE|PASS|UPDATED|CURRENT)$", "", str(value).upper())
                return humanise_token(token), "INFERRED_FROM_RELEASE_GATE"
            return humanise_token(str(value)[:80]), "INFERRED_FROM_DEFECT_OR_RISK"
    return f"Historical Build {build_number} control", "INFERRED_FROM_BUILD_NUMBER"


def deterministic_lesson_id(build_number: str, item: dict, index: int) -> str:
    seed = "|".join(
        [
            build_number,
            str(item.get("control_family", "UNCLASSIFIED")),
            str(item.get("defect_or_risk", "")),
            str(index),
        ]
    )
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12].upper()
    return f"CERT-LESSON-BACKFILL-{build_number}-{digest}"


def normalise_matrix(data, build_number: str, source: Path, current_build: str):
    items = None
    container = None
    if isinstance(data, dict):
        for key in ("lessons", "controls", "entries", "control_matrix"):
            if isinstance(data.get(key), list):
                items = data[key]
                container = key
                break
    elif isinstance(data, list):
        items = data
        container = "ROOT_ARRAY"
    if not isinstance(items, list):
        fail("LESSONS_MATRIX_SHAPE_INVALID", str(source))

    strict_current = build_number == current_build
    output = []
    migrations = []

    for index, raw in enumerate(items, start=1):
        if not isinstance(raw, dict):
            fail("LESSON_RECORD_INVALID", f"{source}: record {index}")
        if not raw:
            fail("LEGACY_LESSON_SUBSTANCE_MISSING", f"{source}: record {index}")

        item = copy.deepcopy(raw)
        record_migrations = []

        for canonical, candidates in ALIASES.items():
            if item.get(canonical) not in (None, "", [], {}):
                continue
            alias, value = first_present(item, candidates)
            if alias is not None:
                item[canonical] = copy.deepcopy(value)
                if alias != canonical:
                    record_migrations.append(
                        {
                            "field": canonical,
                            "action": "ALIASED",
                            "basis": alias,
                        }
                    )

        if strict_current:
            for key in REQUIRED:
                if key not in item or item[key] in (None, "", [], {}):
                    fail("CURRENT_LESSON_REQUIRED_FIELD_MISSING", f"{source}: record {index}: {key}")
        else:
            substantive_values = [
                item.get("defect_or_risk"),
                item.get("root_cause"),
                item.get("preventive_control"),
                item.get("regression_control"),
                item.get("release_gate"),
            ]
            if not any(value not in (None, "", [], {}) for value in substantive_values):
                fail("LEGACY_LESSON_SUBSTANCE_MISSING", f"{source}: record {index}")

            if item.get("control_family") in (None, ""):
                value, basis = infer_control_family(item, build_number)
                item["control_family"] = value
                record_migrations.append(
                    {
                        "field": "control_family",
                        "action": "BACKFILLED",
                        "basis": basis,
                    }
                )

            if item.get("defect_or_risk") in (None, ""):
                source_key, source_value = first_present(
                    item,
                    (
                        "corrective_action",
                        "control",
                        "preventive_control",
                        "regression_control",
                    ),
                )
                if source_key is None:
                    fail("LEGACY_LESSON_SUBSTANCE_MISSING", f"{source}: record {index}")
                item["defect_or_risk"] = f"Legacy lesson retained from {source_key}: {source_value}"
                record_migrations.append(
                    {
                        "field": "defect_or_risk",
                        "action": "BACKFILLED",
                        "basis": source_key,
                    }
                )

            for key, default in LEGACY_DEFAULTS.items():
                if item.get(key) in (None, ""):
                    item[key] = default
                    record_migrations.append(
                        {
                            "field": key,
                            "action": "BACKFILLED",
                            "basis": "CONTROLLED_LEGACY_DEFAULT",
                        }
                    )

            if item.get("lesson_id") in (None, ""):
                item["lesson_id"] = deterministic_lesson_id(build_number, item, index)
                item["identifier_basis"] = "DETERMINISTIC_HISTORICAL_BACKFILL"
                record_migrations.append(
                    {
                        "field": "lesson_id",
                        "action": "BACKFILLED",
                        "basis": "DETERMINISTIC_HISTORICAL_BACKFILL",
                    }
                )

            if item.get("origin_builds") in (None, "", [], {}):
                item["origin_builds"] = [build_number]
                record_migrations.append(
                    {
                        "field": "origin_builds",
                        "action": "BACKFILLED",
                        "basis": "SOURCE_BUILD_DIRECTORY",
                    }
                )

        for key in REQUIRED:
            if key not in item or item[key] in (None, "", [], {}):
                fail("LESSON_REQUIRED_FIELD_MISSING", f"{source}: record {index}: {key}")

        if not isinstance(item["origin_builds"], list):
            item["origin_builds"] = [str(item["origin_builds"])]
            record_migrations.append(
                {
                    "field": "origin_builds",
                    "action": "NORMALISED",
                    "basis": "SCALAR_TO_ARRAY",
                }
            )

        item["origin_builds"] = sorted(
            set(str(value) for value in item["origin_builds"] + [build_number])
        )
        item.setdefault("occurrence_count", len(item["origin_builds"]))
        item.setdefault("evidence_paths", [source.as_posix()])
        item.setdefault("repeat_defect", False)

        if record_migrations:
            migration_record = {
                "source": source.as_posix(),
                "build_number": build_number,
                "record_index": index,
                "lesson_id": item["lesson_id"],
                "matrix_container": container,
                "migrations": record_migrations,
            }
            migrations.append(migration_record)
            item["historical_schema_migration"] = {
                "source": source.as_posix(),
                "record_index": index,
                "migrations": record_migrations,
            }

        output.append(item)

    return output, migrations


def stronger(old: dict, new: dict) -> bool:
    old_text = (old.get("preventive_control", "") + "\n" + old.get("regression_control", "")).strip()
    new_text = (new.get("preventive_control", "") + "\n" + new.get("regression_control", "")).strip()
    return new_text != old_text and len(new_text) >= len(old_text)


def merge(existing: list[dict], incoming: list[dict]):
    by_id = {item["lesson_id"]: copy.deepcopy(item) for item in existing}
    changes = []
    for item in incoming:
        lesson_id = item["lesson_id"]
        if lesson_id not in by_id:
            by_id[lesson_id] = item
            changes.append({"lesson_id": lesson_id, "action": "ADDED"})
            continue
        old = by_id[lesson_id]
        old_origins = {str(value) for value in old.get("origin_builds", [])}
        incoming_origins = {str(value) for value in item.get("origin_builds", [])}
        introduces_new_occurrence = bool(incoming_origins - old_origins)
        if (
            item.get("repeat_defect") is True
            and introduces_new_occurrence
            and old.get("root_cause") == item.get("root_cause")
            and not stronger(old, item)
        ):
            fail("REPEATED_DEFECT_CONTROL_NOT_STRENGTHENED", lesson_id)
        merged = copy.deepcopy(old)
        for key, value in item.items():
            if key != "origin_builds" and value not in (None, "", [], {}):
                merged[key] = value
        merged["origin_builds"] = sorted(
            set(old.get("origin_builds", []) + item.get("origin_builds", []))
        )
        merged["occurrence_count"] = max(
            int(old.get("occurrence_count", 1)), len(merged["origin_builds"])
        )
        by_id[lesson_id] = merged
        changes.append({"lesson_id": lesson_id, "action": "UPDATED"})
    return sorted(by_id.values(), key=lambda item: item["lesson_id"]), changes



def lesson_ids_for_build(lessons: list[dict], build_number: str) -> list[str]:
    return sorted(
        item["lesson_id"]
        for item in lessons
        if build_number in {str(value) for value in item.get("origin_builds", [])}
    )


def lesson_id_set_sha256(lesson_ids: list[str]) -> str:
    payload = ("\n".join(lesson_ids) + "\n").encode("ascii")
    return hashlib.sha256(payload).hexdigest().upper()


def validate_ledger_only_historical_evidence(
    master: dict,
    missing_matrix_builds: list[str],
) -> list[dict]:
    coverage = master.get("coverage", {})
    declared = coverage.get("ledger_only_historical_evidence")
    if not isinstance(declared, dict):
        fail("HISTORICAL_LEDGER_ONLY_EVIDENCE_MISSING", ",".join(missing_matrix_builds))

    lessons = master.get("lessons", [])
    by_id = {item.get("lesson_id"): item for item in lessons if isinstance(item, dict)}
    validated = []

    for build_number in missing_matrix_builds:
        record = declared.get(build_number)
        if not isinstance(record, dict):
            fail("HISTORICAL_LEDGER_ONLY_BUILD_UNDECLARED", build_number)
        if record.get("matrix_status") != "LEGACY_MATRIX_NOT_PRESENT_CANONICALLY":
            fail("HISTORICAL_LEDGER_ONLY_STATUS_INVALID", build_number)
        if record.get("evidence_mode") != "AUTHORITATIVE_CUMULATIVE_LEDGER_EXACT_LESSON_SET":
            fail("HISTORICAL_LEDGER_ONLY_MODE_INVALID", build_number)

        declared_ids = record.get("lesson_ids")
        if (
            not isinstance(declared_ids, list)
            or not declared_ids
            or any(not isinstance(value, str) or not value for value in declared_ids)
            or len(declared_ids) != len(set(declared_ids))
        ):
            fail("HISTORICAL_LEDGER_ONLY_IDS_INVALID", build_number)
        declared_ids = sorted(declared_ids)

        actual_ids = lesson_ids_for_build(lessons, build_number)
        if declared_ids != actual_ids:
            missing_ids = sorted(set(declared_ids) - set(actual_ids))
            unexpected_ids = sorted(set(actual_ids) - set(declared_ids))
            fail(
                "HISTORICAL_LEDGER_ONLY_SET_MISMATCH",
                f"{build_number}:missing={missing_ids}:unexpected={unexpected_ids}",
            )

        for lesson_id in declared_ids:
            lesson = by_id.get(lesson_id)
            if not isinstance(lesson, dict):
                fail("HISTORICAL_LEDGER_ONLY_LESSON_MISSING", f"{build_number}:{lesson_id}")
            if build_number not in {str(value) for value in lesson.get("origin_builds", [])}:
                fail("HISTORICAL_LEDGER_ONLY_ORIGIN_MISMATCH", f"{build_number}:{lesson_id}")
            for key in REQUIRED:
                if lesson.get(key) in (None, "", [], {}):
                    fail("HISTORICAL_LEDGER_ONLY_LESSON_INVALID", f"{build_number}:{lesson_id}:{key}")

        actual_digest = lesson_id_set_sha256(declared_ids)
        if record.get("lesson_id_set_sha256") != actual_digest:
            fail("HISTORICAL_LEDGER_ONLY_HASH_MISMATCH", build_number)

        validated.append(
            {
                "build_number": build_number,
                "matrix_status": record["matrix_status"],
                "evidence_mode": record["evidence_mode"],
                "lesson_count": len(declared_ids),
                "lesson_ids": declared_ids,
                "lesson_id_set_sha256": actual_digest,
                "provenance": record.get("provenance"),
            }
        )

    return validated

def render_ledger(lessons: list[dict]) -> str:
    lines = [BEGIN, ""]
    for lesson in lessons:
        lines.extend(
            [
                f"### {lesson['lesson_id']} - {lesson['control_family']}",
                "",
                f"**Origin builds:** {', '.join(lesson['origin_builds'])}",
                f"**Status:** {lesson['status']}",
                "",
                f"**Defect or risk:** {lesson['defect_or_risk']}",
                "",
                f"**Root cause:** {lesson['root_cause']}",
                "",
                f"**Locked preventive control:** {lesson['preventive_control']}",
                "",
                f"**Executable regression control:** {lesson['regression_control']}",
                "",
                f"**Release gate:** `{lesson['release_gate']}`",
                "",
            ]
        )
    lines.append(END)
    return "\n".join(lines)


def validate_text_hygiene(text: str, name: str) -> None:
    if "\r" in text:
        fail("LESSONS_OUTPUT_CR_BYTE", name)
    if not text.endswith("\n"):
        fail("LESSONS_OUTPUT_FINAL_LF_MISSING", name)
    for line_number, line in enumerate(text.split("\n"), start=1):
        if line.endswith((" ", "\t")):
            fail("LESSONS_OUTPUT_TRAILING_WHITESPACE", f"{name}:{line_number}")


def atomic_write(path: Path, text: str, encoding: str) -> None:
    validate_text_hygiene(text if text.endswith("\n") else text + "\n", str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding=encoding, newline="\n") as handle:
            handle.write(text)
            if not text.endswith("\n"):
                handle.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", required=True)
    parser.add_argument("--current-build", required=True)
    parser.add_argument(
        "--master-markdown",
        default="00_Governance/CERTIAURA_LOCKED_ACCUMULATED_LESSONS_AND_CONTINUOUS_LEARNING_STANDARD.md",
    )
    parser.add_argument(
        "--master-json",
        default="00_Governance/CERTIAURA_LOCKED_ACCUMULATED_LESSONS_AND_CONTINUOUS_LEARNING_STANDARD.control.json",
    )
    parser.add_argument("--report", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    repository = Path(args.repository).resolve()
    markdown_path = repository / args.master_markdown
    json_path = repository / args.master_json
    report_path = Path(args.report).resolve()

    if not (repository / ".git").is_dir():
        fail("LESSONS_REPOSITORY_INVALID", str(repository))
    if not markdown_path.is_file() or not json_path.is_file():
        fail("ACCUMULATED_LESSONS_SOURCE_MISSING", str(repository))

    master = read_json(json_path)
    existing = master.get("lessons")
    if not isinstance(existing, list):
        fail("ACCUMULATED_LESSONS_LEDGER_INVALID", str(json_path))

    matrices = sorted(
        (repository / "Documentation" / "Build_Records").glob(
            "*/LESSONS_LEARNED_CONTROL_MATRIX.json"
        )
    )
    if not matrices:
        fail("HISTORICAL_LESSONS_MATRICES_NOT_FOUND", str(repository))

    incoming = []
    discovered_builds = []
    historical_migrations = []

    for matrix in matrices:
        build_number = matrix.parent.name
        discovered_builds.append(build_number)
        normalised, migrations = normalise_matrix(
            read_json(matrix),
            build_number,
            matrix.relative_to(repository),
            args.current_build,
        )
        incoming.extend(normalised)
        historical_migrations.extend(migrations)

    current_matrix = (
        repository
        / "Documentation"
        / "Build_Records"
        / args.current_build
        / "LESSONS_LEARNED_CONTROL_MATRIX.json"
    )
    current_review = (
        repository
        / "Documentation"
        / "Build_Records"
        / args.current_build
        / "LESSONS_LEARNED_REVIEW.md"
    )
    if not current_matrix.is_file() or not current_review.is_file():
        fail("CURRENT_BUILD_LESSONS_RECORDS_MISSING", args.current_build)

    merged, changes = merge(existing, incoming)
    current_normalised, current_migrations = normalise_matrix(
        read_json(current_matrix),
        args.current_build,
        current_matrix.relative_to(repository),
        args.current_build,
    )
    if current_migrations:
        fail("CURRENT_LESSON_SCHEMA_MIGRATION_PROHIBITED", args.current_build)

    current_ids = {item["lesson_id"] for item in current_normalised}
    merged_ids = {item["lesson_id"] for item in merged}
    if not current_ids.issubset(merged_ids):
        fail(
            "CURRENT_BUILD_LESSONS_NOT_MERGED",
            ",".join(sorted(current_ids - merged_ids)),
        )

    expected_builds = set(master.get("coverage", {}).get("mandatory_expected_builds", []))
    discovered_matrix_builds = sorted(set(discovered_builds))
    missing_matrix_builds = sorted(expected_builds - set(discovered_matrix_builds))
    ledger_only_evidence = validate_ledger_only_historical_evidence(
        master,
        missing_matrix_builds,
    )
    covered_builds = sorted(set(discovered_matrix_builds) | set(missing_matrix_builds))
    uncovered_builds = sorted(expected_builds - set(covered_builds))
    if uncovered_builds:
        fail("HISTORICAL_LESSONS_COVERAGE_INCOMPLETE", ",".join(uncovered_builds))

    markdown = markdown_path.read_text(encoding="utf-8")
    if BEGIN not in markdown or END not in markdown:
        fail("LESSONS_LEDGER_MARKERS_MISSING", str(markdown_path))
    before, remainder = markdown.split(BEGIN, 1)
    _, after = remainder.split(END, 1)
    updated_markdown = before.rstrip() + "\n\n" + render_ledger(merged) + after
    if not updated_markdown.endswith("\n"):
        updated_markdown += "\n"

    master["lessons"] = merged
    master["coverage"]["current_status"] = "COMPLETE"
    master["coverage"]["last_discovered_builds"] = discovered_matrix_builds
    master["coverage"]["last_discovered_matrix_builds"] = discovered_matrix_builds
    master["coverage"]["last_ledger_only_builds"] = missing_matrix_builds
    master["coverage"]["last_covered_builds"] = covered_builds
    master["coverage"]["ledger_only_evidence_count"] = len(ledger_only_evidence)
    master["coverage"]["historical_schema_migration_count"] = len(historical_migrations)
    master["automatic_update"]["last_updated_build"] = args.current_build
    master["automatic_update"]["last_updated_utc"] = (
        dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    )
    master["automatic_update"]["strict_current_schema"] = True
    master["automatic_update"]["historical_schema_adapter"] = "VERSION_AWARE_RECORDED_MIGRATION"

    updated_json = json.dumps(master, indent=2, ensure_ascii=True) + "\n"
    validate_text_hygiene(updated_markdown, str(markdown_path))
    validate_text_hygiene(updated_json, str(json_path))

    report = {
        "result": "ACCUMULATED_LESSONS_UPDATE_VALIDATED",
        "apply_requested": args.apply,
        "current_build": args.current_build,
        "matrix_count": len(matrices),
        "discovered_builds": discovered_matrix_builds,
        "discovered_matrix_builds": discovered_matrix_builds,
        "ledger_only_builds": missing_matrix_builds,
        "covered_builds": covered_builds,
        "ledger_only_historical_evidence": ledger_only_evidence,
        "lesson_count_before": len(existing),
        "lesson_count_after": len(merged),
        "current_build_lesson_ids": sorted(current_ids),
        "changes": changes,
        "historical_coverage": "COMPLETE",
        "historical_coverage_mode": "MATRIX_OR_HASH_BOUND_AUTHORITATIVE_LEDGER",
        "strict_current_schema": "PASS",
        "historical_schema_adapter": "VERSION_AWARE_RECORDED_MIGRATION",
        "historical_schema_migration_count": len(historical_migrations),
        "historical_schema_migrations": historical_migrations,
        "markdown_json_parity": "PASS",
        "generated_text_hygiene": "PASS",
        "markdown_sha256_after": hashlib.sha256(
            updated_markdown.encode("utf-8")
        ).hexdigest().upper(),
        "json_sha256_after": hashlib.sha256(
            updated_json.encode("ascii")
        ).hexdigest().upper(),
    }

    if args.apply:
        atomic_write(markdown_path, updated_markdown, "utf-8")
        atomic_write(json_path, updated_json, "ascii")
    atomic_write(
        report_path,
        json.dumps(report, indent=2, ensure_ascii=True) + "\n",
        "ascii",
    )
    print("ACCUMULATED_LESSONS_UPDATE_VALIDATED")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
