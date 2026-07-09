from pathlib import Path


class RepositoryManager:
    REQUIRED_FOLDERS = [
        "00_Governance",
        "01_Knowledge_Systems",
        "02_Peptides",
        "03_Biology",
        "04_Conditions",
        "05_Monitoring",
        "06_Evidence",
        "07_Goals",
        "Documentation",
    ]

    REQUIRED_FILES = [
        "README.md",
        "00_Governance/Governance_Continuity_Standard.md",
        "00_Governance/Universal_Asset_Relationship_Standard_UARS.md",
        "Documentation/Master_Asset_Register.csv",
        "Documentation/CHANGELOG.md",
    ]

    def __init__(self, repo_path: Path):
        self.repo_path = Path(repo_path)

    def validate(self):
        errors = []

        if not self.repo_path.exists():
            errors.append("Repository path does not exist.")
            return {"valid": False, "errors": errors}

        for folder in self.REQUIRED_FOLDERS:
            if not (self.repo_path / folder).is_dir():
                errors.append(f"Missing folder: {folder}")

        for file in self.REQUIRED_FILES:
            if not (self.repo_path / file).is_file():
                errors.append(f"Missing file: {file}")

        return {"valid": len(errors) == 0, "errors": errors}

    def asset_register_path(self):
        return self.repo_path / "Documentation" / "Master_Asset_Register.csv"

    def changelog_path(self):
        return self.repo_path / "Documentation" / "CHANGELOG.md"

    def summary(self):
        validation = self.validate()
        markdown_files = list(self.repo_path.rglob("*.md")) if self.repo_path.exists() else []
        json_files = list(self.repo_path.rglob("*.json")) if self.repo_path.exists() else []

        return {
            "repo": str(self.repo_path),
            "markdown_files": len(markdown_files),
            "json_files": len(json_files),
            "asset_register_present": self.asset_register_path().exists(),
            "changelog_present": self.changelog_path().exists(),
            "validation_status": "PASS" if validation["valid"] else "FAIL",
        }
