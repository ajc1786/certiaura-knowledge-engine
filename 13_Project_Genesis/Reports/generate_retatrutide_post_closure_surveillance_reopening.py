from __future__ import annotations
import argparse, hashlib, json, shutil
from datetime import datetime, timezone
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec
ROOT = Path(__file__).resolve().parents[2]
VP = ROOT / "13_Project_Genesis/Validators/validate_retatrutide_post_closure_surveillance_reopening.py"
spec = spec_from_file_location("v", VP)
mod = module_from_spec(spec)
spec.loader.exec_module(mod)
def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()
def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ["surveillance", "review", "reopening", "analytics"]:
        parser.add_argument(name, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--now")
    args = parser.parse_args()
    sources = [args.surveillance, args.review, args.reopening, args.analytics]
    objects = [json.loads(path.read_text(encoding="utf-8")) for path in sources]
    blob = json.dumps(objects)
    if mod.DIRECT.search(blob) or mod.TREATMENT.search(blob):
        raise SystemExit("prohibited content")
    surveillance, review, reopening, analytics = objects
    if surveillance.get("urgent_routing_active") and surveillance.get("surveillance_state") != "LOCKED_URGENT_ROUTING":
        raise SystemExit("urgent routing precedence violated")
    if reopening.get("reviewer_actor_role") == reopening.get("generator_actor_role"):
        raise SystemExit("reviewer separation required")
    if reopening.get("decision") == "REOPEN_APPROVED" and not str(reopening.get("trigger_id", "")).strip():
        raise SystemExit("reopening trigger required")
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    names = ["post_closure_surveillance.json", "periodic_review.json", "reopening_decision.json", "recurrence_analytics.json"]
    for source, name in zip(sources, names):
        shutil.copyfile(source, output / name)
    manifest = {"build_provenance": "CERT-BUILD-0051", "generated_at": args.now or now(), "components": []}
    for name in names:
        path = output / name
        manifest["components"].append({"path": name, "sha256": sha(path), "bytes": path.stat().st_size})
    (output / "bundle_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    summary = (
        "# Retatrutide Post-Closure Surveillance and Reopening Summary\n\n"
        f"Surveillance state: {surveillance.get('surveillance_state')}\n\n"
        f"Periodic review: {review.get('review_state')}\n\n"
        f"Reopening decision: {reopening.get('decision')}\n\n"
        f"Recurrence state: {analytics.get('recurrence_state')}\n"
    )
    (output / "post_closure_summary.md").write_text(summary, encoding="utf-8", newline="\n")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
