from __future__ import annotations
import json
from pathlib import Path
from typing import Iterable
BUILD_PROVENANCE = "CERT-BUILD-0049"
MANIFEST_PATH = Path("Documentation/Build_Records/0049/ASSET_INTENT_MANIFEST.json")
def owned_paths(repository_root: Path, classifications: Iterable[str] | None = None) -> list[str]:
    manifest=json.loads((repository_root/MANIFEST_PATH).read_text(encoding="utf-8"))
    allowed=set(classifications or []); paths=[]
    for item in manifest.get("files",[]):
        if item.get("build_provenance") != BUILD_PROVENANCE: continue
        if allowed and item.get("classification") not in allowed: continue
        path=item.get("path")
        if not isinstance(path,str) or not path: raise ValueError("Owned manifest item has no exact path")
        paths.append(path)
    if len(paths)!=len(set(paths)): raise ValueError("Duplicate exact paths in Asset Intent Manifest")
    return sorted(paths)
