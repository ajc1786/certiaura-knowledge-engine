from pathlib import Path
import json
BUILD_PROVENANCE = "CERT-BUILD-0050"
MANIFEST_PATH = Path("Documentation/Build_Records/0050/ASSET_INTENT_MANIFEST.json")
def owned_paths(repository: Path) -> list[str]:
    manifest=json.loads((repository/MANIFEST_PATH).read_text(encoding="utf-8"))
    if manifest.get("build_id") != BUILD_PROVENANCE: raise ValueError("build provenance mismatch")
    return [item["path"] for item in manifest["files"] if item.get("build_provenance")==BUILD_PROVENANCE]
