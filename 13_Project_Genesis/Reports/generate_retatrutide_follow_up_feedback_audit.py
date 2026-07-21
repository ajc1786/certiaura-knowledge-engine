from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Validators"))

from validate_retatrutide_follow_up_feedback_audit import (
    validate_acknowledgement,
    validate_amendment,
    validate_feedback,
    validate_follow_up,
)


def load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dump(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("acknowledgement")
    parser.add_argument("follow_up")
    parser.add_argument("feedback")
    parser.add_argument("amendment")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--now", default="CONTROLLED_RUNTIME")
    args = parser.parse_args()

    inputs = [
        (args.acknowledgement, validate_acknowledgement, "acknowledgement.json"),
        (args.follow_up, validate_follow_up, "follow_up_review.json"),
        (args.feedback, validate_feedback, "clinician_feedback.json"),
        (args.amendment, validate_amendment, "export_amendment_audit.json"),
    ]

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []

    for source, validator, filename in inputs:
        payload = load(source)
        errors = validator(payload)
        if errors:
            raise SystemExit(filename + ": " + "; ".join(errors))
        target = output / filename
        dump(target, payload)
        manifest.append(
            {
                "path": filename,
                "sha256": sha256(target),
                "bytes": target.stat().st_size,
            }
        )

    audit = {
        "schema_version": "1.0.0",
        "build_provenance": "CERT-BUILD-0049",
        "generated_at": args.now,
        "state": "AUDIT_BUNDLE_READY_FOR_HUMAN_REVIEW",
        "components": [item[2] for item in inputs],
        "safety_boundary": "NO_DIAGNOSIS_NO_PRESCRIBING_NO_AUTONOMOUS_DOSE_CHANGE",
    }
    audit_path = output / "follow_up_feedback_audit_bundle.json"
    dump(audit_path, audit)
    manifest.append(
        {
            "path": audit_path.name,
            "sha256": sha256(audit_path),
            "bytes": audit_path.stat().st_size,
        }
    )

    dump(
        output / "bundle_manifest.json",
        {"build_provenance": "CERT-BUILD-0049", "files": manifest},
    )
    (output / "audit_summary.md").write_text(
        "# Retatrutide Follow-Up and Feedback Audit Summary\n\n"
        "State: AUDIT_BUNDLE_READY_FOR_HUMAN_REVIEW\n\n"
        "No diagnosis, prescribing or autonomous dose change is produced.\n",
        encoding="utf-8",
        newline="\n",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
