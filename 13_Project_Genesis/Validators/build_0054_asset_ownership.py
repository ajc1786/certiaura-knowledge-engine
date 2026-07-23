from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_manifest(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def package_paths(manifest: dict[str, Any]) -> list[str]:
    return sorted({str(item["repository_path"]).replace("\\", "/") for item in manifest.get("files", [])})


def generated_paths(manifest: dict[str, Any]) -> list[str]:
    return sorted({str(item["repository_path"]).replace("\\", "/") for item in manifest.get("generated_files", [])})


def owned_paths(manifest: dict[str, Any]) -> list[str]:
    return sorted(set(package_paths(manifest)) | set(generated_paths(manifest)))


def approved_overlap_paths(manifest: dict[str, Any]) -> set[str]:
    result = set()
    for item in manifest.get("generated_files", []) + manifest.get("files", []):
        if item.get("approved_predecessor_overlap") is True:
            result.add(str(item["repository_path"]).replace("\\", "/"))
    return result
