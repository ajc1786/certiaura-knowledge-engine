from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import subprocess

from genesis.core.git_manager import GitManager


def run_git(cwd: Path, *args: str):
    subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )


def test_status_and_local_commit():
    if not shutil.which("git"):
        print("SKIP: git is not available on PATH for this test.")
        return

    with TemporaryDirectory() as temp:
        repo = Path(temp) / "repo"
        repo.mkdir()

        run_git(repo, "init")
        run_git(repo, "config", "user.email", "test@example.com")
        run_git(repo, "config", "user.name", "Genesis Test")

        test_file = repo / "example.txt"
        test_file.write_text("Genesis v1.2", encoding="utf-8")

        manager = GitManager(repo)
        status = manager.status_short()

        assert len(status) == 1
        assert "example.txt" in status[0]

        # This test intentionally does not call commit_and_push because
        # that method requires a real remote.
        run_git(repo, "add", "-A")
        run_git(repo, "commit", "-m", "Test commit")

        assert manager.status_short() == []


if __name__ == "__main__":
    test_status_and_local_commit()
    print("GitManager local test passed.")
