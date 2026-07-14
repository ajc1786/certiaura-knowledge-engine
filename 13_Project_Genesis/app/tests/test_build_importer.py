from pathlib import Path
from tempfile import TemporaryDirectory

from genesis.core.build_importer import BuildPackImporter


def test_preview_and_import():
    with TemporaryDirectory() as temp:
        root = Path(temp)
        repo = root / "repo"
        pack = root / "pack"

        repo.mkdir()
        pack.mkdir()
        (repo / ".git").mkdir()

        (pack / "Documentation").mkdir()
        (pack / "Documentation" / "example.md").write_text(
            "# Example",
            encoding="utf-8",
        )

        importer = BuildPackImporter(repo, pack)

        preview = importer.preview()
        assert preview["valid"] is True
        assert preview["new_files"] == 1
        assert preview["replace_files"] == 0

        result = importer.import_pack()
        assert result["files_copied"] == 1
        assert (repo / "Documentation" / "example.md").exists()


if __name__ == "__main__":
    test_preview_and_import()
    print("Build Pack Import test passed.")
