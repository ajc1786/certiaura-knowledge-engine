from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import shutil


class BuildPackImporter:
    """
    Safely imports an extracted Certiaura Build Pack into the selected repository.

    v1.1 rules:
    - The build pack must be a folder.
    - The repository and build pack must be different locations.
    - .git content is never imported.
    - Files are copied preserving relative paths.
    - Existing files are replaced only after user confirmation in the UI.
    """

    EXCLUDED_PARTS = {
        ".git",
        "__pycache__",
        ".pytest_cache",
    }

    def __init__(self, repo_path: Path, build_pack_path: Path):
        self.repo_path = Path(repo_path).expanduser().resolve()
        self.build_pack_path = Path(build_pack_path).expanduser().resolve()

    def _errors(self) -> List[str]:
        errors: List[str] = []

        if not self.repo_path.exists():
            errors.append("Repository path does not exist.")
        elif not self.repo_path.is_dir():
            errors.append("Repository path is not a folder.")

        if not self.build_pack_path.exists():
            errors.append("Build Pack path does not exist.")
        elif not self.build_pack_path.is_dir():
            errors.append("Build Pack path is not a folder.")

        if self.repo_path == self.build_pack_path:
            errors.append("Build Pack folder cannot be the repository itself.")

        try:
            self.build_pack_path.relative_to(self.repo_path)
            errors.append(
                "Build Pack folder cannot be located inside the repository. "
                "Extract it to Downloads or another temporary folder."
            )
        except ValueError:
            pass

        try:
            self.repo_path.relative_to(self.build_pack_path)
            errors.append(
                "Repository cannot be located inside the selected Build Pack folder."
            )
        except ValueError:
            pass

        if self.repo_path.exists() and not (self.repo_path / ".git").exists():
            errors.append(
                "Selected repository does not contain a .git folder. "
                "Select the local certiaura-knowledge-engine repository."
            )

        return errors

    def _source_files(self) -> List[Path]:
        files: List[Path] = []

        if not self.build_pack_path.exists():
            return files

        for path in self.build_pack_path.rglob("*"):
            if not path.is_file():
                continue

            relative = path.relative_to(self.build_pack_path)

            if any(part in self.EXCLUDED_PARTS for part in relative.parts):
                continue

            files.append(path)

        return files

    def preview(self) -> Dict[str, object]:
        errors = self._errors()
        if errors:
            return {
                "valid": False,
                "errors": errors,
                "build_pack": str(self.build_pack_path),
                "new_files": 0,
                "replace_files": 0,
                "directories_scanned": 0,
            }

        files = self._source_files()
        new_files = 0
        replace_files = 0
        directories = set()

        for source in files:
            relative = source.relative_to(self.build_pack_path)
            target = self.repo_path / relative

            directories.add(str(relative.parent))

            if target.exists():
                replace_files += 1
            else:
                new_files += 1

        if not files:
            errors.append("The selected Build Pack contains no importable files.")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "build_pack": str(self.build_pack_path),
            "new_files": new_files,
            "replace_files": replace_files,
            "directories_scanned": len(directories),
        }

    def import_pack(self) -> Dict[str, int]:
        preview = self.preview()

        if not preview["valid"]:
            raise ValueError("Invalid Build Pack: " + "; ".join(preview["errors"]))

        files = self._source_files()
        new_files = 0
        replaced_files = 0

        for source in files:
            relative = source.relative_to(self.build_pack_path)
            target = self.repo_path / relative

            target.parent.mkdir(parents=True, exist_ok=True)

            if target.exists():
                replaced_files += 1
            else:
                new_files += 1

            shutil.copy2(source, target)

        return {
            "files_copied": len(files),
            "new_files": new_files,
            "replaced_files": replaced_files,
        }
