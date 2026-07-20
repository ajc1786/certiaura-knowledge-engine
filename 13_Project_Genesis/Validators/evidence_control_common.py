from __future__ import annotations
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path, PurePosixPath
from typing import Any

@dataclass
class ValidationResult:
    valid: bool
    errors: list[str]
    warnings: list[str]
    def to_dict(self): return asdict(self)

def load_json(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")
    return data

def require(data: dict[str, Any], fields: list[str], errors: list[str]) -> None:
    for field in fields:
        if field not in data or data[field] is None or data[field] == "":
            errors.append(f"Missing required field: {field}")

def require_enum(data: dict[str, Any], field: str, allowed: set[str], errors: list[str]) -> None:
    if data.get(field) not in allowed:
        errors.append(f"{field} must be one of {sorted(allowed)}")

def require_nonempty_list(data: dict[str, Any], field: str, errors: list[str]) -> None:
    value = data.get(field)
    if not isinstance(value, list) or not value:
        errors.append(f"{field} must be a non-empty list")

def require_human(reviewer: Any, errors: list[str]) -> None:
    if not isinstance(reviewer, dict) or reviewer.get("human") is not True:
        errors.append("An accountable human reviewer is required")

def require_sha256(value: Any, field: str, errors: list[str]) -> None:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-fA-F]{64}", value) is None:
        errors.append(f"{field} must be a 64-character SHA-256 value")

def cli(validate):
    if len(sys.argv) != 2:
        print(json.dumps({"valid": False, "errors": ["Usage: validator <record.json>"], "warnings": []}, indent=2))
        raise SystemExit(2)
    try:
        result = validate(load_json(sys.argv[1]))
    except Exception as exc:
        result = ValidationResult(False, [str(exc)], [])
    print(json.dumps(result.to_dict(), indent=2))
    raise SystemExit(0 if result.valid else 1)
