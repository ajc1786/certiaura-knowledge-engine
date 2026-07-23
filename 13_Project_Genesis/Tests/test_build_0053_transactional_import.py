from __future__ import annotations

import csv
import importlib.util
import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "13_Project_Genesis/Import/run_build_0053_import.py"
spec = importlib.util.spec_from_file_location("import0053", SCRIPT)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout.strip()


class TransactionTests(unittest.TestCase):
    def make_repo(self, td: str) -> tuple[Path, str]:
        repo = Path(td) / "repo"
        repo.mkdir()
        git(repo, "init")
        git(repo, "config", "user.email", "test@example.com")
        git(repo, "config", "user.name", "Test")

        governance = repo / "00_Governance"
        governance.mkdir()
        governance_files = [
            "CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md",
            "CERTIAURA_LOCKED_ACCUMULATED_LESSONS_AND_CONTINUOUS_LEARNING_STANDARD.md",
            "CERTIAURA_LOCKED_ACCUMULATED_LESSONS_AND_CONTINUOUS_LEARNING_STANDARD.control.json",
        ]
        (governance / governance_files[0]).write_text("# checkpoint\n", encoding="utf-8")
        (governance / governance_files[1]).write_text("# lessons\n", encoding="utf-8")
        (governance / governance_files[2]).write_text("{}\n", encoding="utf-8")

        documentation = repo / "Documentation"
        documentation.mkdir()
        headers = [
            "Universal Asset Identifier",
            "Repository Path",
            "Asset Title",
            "Asset Type",
            "Knowledge System",
            "Version",
            "Status",
            "Owner",
            "Build Provenance",
        ]
        # Canonical Build 0052 topology: governance control files exist in Git
        # but are not registered as formal assets in the Master Asset Register.
        rows = [
            [
                "CERT-SYS-000001",
                "Standards/EXISTING_CANONICAL_STANDARD.md",
                "Existing canonical standard",
                "Controlled Standard",
                "SYS",
                "1.0.0",
                "ACTIVE",
                "Certiaura Governance",
                "0052",
            ]
        ]
        with (documentation / "Master_Asset_Register.csv").open(
            "w", encoding="utf-8", newline=""
        ) as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(headers)
            writer.writerows(rows)

        build_record = documentation / "Build_Records/0052"
        build_record.mkdir(parents=True)
        predecessor_paths = [
            f"00_Governance/{name}" for name in governance_files
        ]
        for index in range(1, 55):
            rel = f"Synthetic_Predecessor/Build_0052/path_{index:02d}.txt"
            target = repo / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(f"predecessor {index}\n", encoding="utf-8")
            predecessor_paths.append(rel)
        predecessor_paths.extend(
            [
                "Documentation/Build_Records/0052/ASSET_INTENT_MANIFEST.json",
                "Documentation/Build_Records/0052/CANDIDATE_DELIVERY.json",
            ]
        )
        self.assertEqual(len(predecessor_paths), 59)
        predecessor_manifest = {
            "schema_version": "2.0.0",
            "build_number": "0052",
            "candidate": "RC6",
            "files": [
                {"repository_path": rel, "classification": "SUPPORTING_FILE"}
                for rel in predecessor_paths
            ],
        }
        (build_record / "ASSET_INTENT_MANIFEST.json").write_text(
            json.dumps(predecessor_manifest, indent=2) + "\n", encoding="utf-8"
        )
        (build_record / "CANDIDATE_DELIVERY.json").write_text(
            json.dumps(
                {"build_number": "0052", "candidate": "RC6"}, indent=2
            )
            + "\n",
            encoding="utf-8",
        )

        git(repo, "add", ".")
        git(repo, "commit", "-m", "synthetic Build 0052 baseline")
        return repo, git(repo, "rev-parse", "HEAD")

    def make_zip(self, td: str) -> Path:
        archive = Path(td) / "build.zip"
        manifest = json.loads(
            (ROOT / "Documentation/Build_Records/0053/ASSET_INTENT_MANIFEST.json").read_text(
                encoding="utf-8"
            )
        )
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as output:
            for item in manifest["files"]:
                rel = item["repository_path"]
                output.write(ROOT / rel, rel)
        return archive

    def test_forced_failure_rolls_back_and_clean_reapply_succeeds(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo, head = self.make_repo(td)
            package = self.make_zip(td)
            backup = Path(td) / "backups"
            before = git(repo, "status", "--porcelain")
            forced = mod.run_import(
                package,
                repo,
                backup,
                Path(td) / "forced.json",
                True,
                True,
                expected_predecessor_commit=head,
            )
            self.assertEqual(forced["result"], "ROLLBACK_STATE_EXACT")
            self.assertEqual(git(repo, "status", "--porcelain"), before)
            clean = mod.run_import(
                package,
                repo,
                backup,
                Path(td) / "clean.json",
                True,
                False,
                expected_predecessor_commit=head,
            )
            self.assertEqual(clean["result"], "CLEAN_REAPPLY_VALIDATED")
            change_paths = {item["repository_path"] for item in clean["register_changes"]}
            self.assertNotIn(
                "00_Governance/CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md",
                change_paths,
            )
            self.assertNotIn(
                "00_Governance/CERTIAURA_LOCKED_ACCUMULATED_LESSONS_AND_CONTINUOUS_LEARNING_STANDARD.md",
                change_paths,
            )
            self.assertNotIn(
                "00_Governance/CERTIAURA_LOCKED_ACCUMULATED_LESSONS_AND_CONTINUOUS_LEARNING_STANDARD.control.json",
                change_paths,
            )
            self.assertTrue(
                (
                    repo
                    / "Standards/RETATRUTIDE_GOVERNED_KNOWLEDGE_CHANGE_IMPLEMENTATION_STANDARD.md"
                ).exists()
            )

    def test_generated_reports_are_lf_and_stage_byte_identically(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo, head = self.make_repo(td)
            git(repo, "config", "core.autocrlf", "true")
            package = self.make_zip(td)
            clean = mod.run_import(
                package,
                repo,
                Path(td) / "backups",
                Path(td) / "clean.json",
                True,
                False,
                expected_predecessor_commit=head,
            )
            self.assertEqual(clean["result"], "CLEAN_REAPPLY_VALIDATED")
            generated_reports = [
                "Documentation/Build_Records/0053/ASSET_REGISTER_CHANGE_REPORT.json",
                "Documentation/Build_Records/0053/CANONICAL_IMPORT_REPORT.json",
                "Documentation/Build_Records/0053/POST_IMPORT_REPOSITORY_VALIDATION.json",
                "Documentation/Build_Records/0053/PREDECESSOR_CANONICAL_EVIDENCE.json",
            ]
            for rel in generated_reports:
                self.assertNotIn(b"\r\n", (repo / rel).read_bytes(), rel)
            manifest_path = repo / "Documentation/Build_Records/0053/ASSET_INTENT_MANIFEST.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            owned = sorted(
                {
                    item["repository_path"]
                    for item in manifest["files"] + manifest["generated_files"]
                }
            )
            subprocess.run(
                ["git", "-C", str(repo), "add", "--all", "--", *owned],
                check=True,
            )
            verifier = repo / "13_Project_Genesis/Validators/verify_staged_byte_equality.py"
            result = subprocess.run(
                [
                    "python",
                    "-B",
                    str(verifier),
                    str(repo),
                    str(manifest_path),
                    "--report",
                    str(Path(td) / "byte_report.json"),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_rc1_invented_governance_registration_assumption_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo, _ = self.make_repo(td)
            manifest = json.loads(
                (ROOT / "Documentation/Build_Records/0053/ASSET_INTENT_MANIFEST.json").read_text(
                    encoding="utf-8"
                )
            )
            bad_manifest = json.loads(json.dumps(manifest))
            governance_paths = {
                "00_Governance/CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md",
                "00_Governance/CERTIAURA_LOCKED_ACCUMULATED_LESSONS_AND_CONTINUOUS_LEARNING_STANDARD.md",
                "00_Governance/CERTIAURA_LOCKED_ACCUMULATED_LESSONS_AND_CONTINUOUS_LEARNING_STANDARD.control.json",
            }
            for item in bad_manifest["generated_files"]:
                if item["repository_path"] in governance_paths:
                    item["classification"] = "FORMAL_ASSET"
                    item["intended_action"] = "UPDATE"
            register = repo / "Documentation/Master_Asset_Register.csv"
            before = register.read_bytes()
            with self.assertRaisesRegex(
                RuntimeError,
                "formal UPDATE asset absent from Master Asset Register",
            ):
                mod.reconcile_register(repo, bad_manifest, "Build 0053 RC1")
            self.assertEqual(register.read_bytes(), before)


    def test_post_import_failure_rollback_restores_staged_repository(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo, head = self.make_repo(td)
            package = self.make_zip(td)
            clean = mod.run_import(
                package,
                repo,
                Path(td) / "backups",
                Path(td) / "clean.json",
                True,
                False,
                expected_predecessor_commit=head,
            )
            manifest = json.loads(
                (repo / "Documentation/Build_Records/0053/ASSET_INTENT_MANIFEST.json").read_text(
                    encoding="utf-8"
                )
            )
            owned = sorted(
                {
                    item["repository_path"]
                    for item in manifest["files"] + manifest["generated_files"]
                }
            )
            subprocess.run(
                ["git", "-C", str(repo), "add", "--all", "--", *owned],
                check=True,
            )
            self.assertNotEqual(git(repo, "status", "--porcelain"), "")
            rollback = mod.rollback_from_backup(
                repo,
                clean["backup_path"],
                Path(td) / "rollback.json",
            )
            self.assertEqual(rollback["result"], "ROLLBACK_STATE_EXACT")
            self.assertEqual(git(repo, "rev-parse", "HEAD"), head)
            self.assertEqual(git(repo, "status", "--porcelain"), "")



if __name__ == "__main__":
    unittest.main()
