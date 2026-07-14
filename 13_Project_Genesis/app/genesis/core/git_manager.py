from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import glob
import os
import shutil
import subprocess


class GitOperationError(RuntimeError):
    pass


class GitManager:
    def __init__(self, repo_path: Path):
        self.repo_path = Path(repo_path).expanduser().resolve()
        self.git_executable = self._find_git()
        self._validate_repository()

    def _find_git(self) -> str:
        candidates: List[str] = []

        system_git = shutil.which("git")
        if system_git:
            candidates.append(system_git)

        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            patterns = [
                os.path.join(
                    local_app_data,
                    "GitHubDesktop",
                    "app-*",
                    "resources",
                    "app",
                    "git",
                    "cmd",
                    "git.exe",
                ),
                os.path.join(
                    local_app_data,
                    "GitHubDesktop",
                    "app-*",
                    "resources",
                    "app",
                    "git",
                    "mingw64",
                    "bin",
                    "git.exe",
                ),
            ]

            for pattern in patterns:
                candidates.extend(
                    sorted(glob.glob(pattern), reverse=True)
                )

        program_files = [
            os.environ.get("ProgramFiles"),
            os.environ.get("ProgramFiles(x86)"),
        ]

        for root in program_files:
            if root:
                candidates.append(os.path.join(root, "Git", "cmd", "git.exe"))

        for candidate in candidates:
            if candidate and Path(candidate).is_file():
                return str(Path(candidate).resolve())

        raise GitOperationError(
            "Git could not be found. Install Git for Windows or ensure "
            "GitHub Desktop is installed."
        )

    def _run(
        self,
        args: List[str],
        *,
        timeout: int = 90,
        check: bool = True,
    ) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"

        try:
            result = subprocess.run(
                [self.git_executable, *args],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
            )
        except subprocess.TimeoutExpired as exc:
            raise GitOperationError(
                f"Git command timed out: git {' '.join(args)}"
            ) from exc
        except OSError as exc:
            raise GitOperationError(
                f"Git could not be started: {exc}"
            ) from exc

        if check and result.returncode != 0:
            detail = (result.stderr or result.stdout or "").strip()
            raise GitOperationError(
                f"Git command failed:\n"
                f"git {' '.join(args)}\n\n"
                f"{detail or 'No error details were returned.'}"
            )

        return result

    def _validate_repository(self):
        if not self.repo_path.is_dir():
            raise GitOperationError("Repository path does not exist.")

        result = self._run(
            ["rev-parse", "--is-inside-work-tree"],
            check=False,
        )

        if result.returncode != 0 or result.stdout.strip().lower() != "true":
            raise GitOperationError(
                "The selected folder is not a valid Git repository."
            )

    def status_short(self) -> List[str]:
        output = self._run(
            ["status", "--short", "--untracked-files=all"]
        ).stdout

        return [
            line.rstrip()
            for line in output.splitlines()
            if line.strip()
        ]

    def current_branch(self) -> str:
        branch = self._run(
            ["branch", "--show-current"]
        ).stdout.strip()

        if not branch:
            raise GitOperationError(
                "Could not determine the current Git branch."
            )

        return branch

    def remote_url(self, remote: str = "origin") -> str:
        result = self._run(
            ["remote", "get-url", remote],
            check=False,
        )

        if result.returncode != 0:
            return remote

        return result.stdout.strip() or remote

    def fetch(self, remote: str = "origin"):
        self._run(
            ["fetch", remote],
            timeout=120,
        )

    def ahead_behind(self) -> Dict[str, int]:
        result = self._run(
            [
                "rev-list",
                "--left-right",
                "--count",
                "HEAD...@{upstream}",
            ],
            check=False,
        )

        if result.returncode != 0:
            return {"ahead": 0, "behind": 0, "upstream_known": False}

        parts = result.stdout.strip().split()
        if len(parts) != 2:
            return {"ahead": 0, "behind": 0, "upstream_known": False}

        return {
            "ahead": int(parts[0]),
            "behind": int(parts[1]),
            "upstream_known": True,
        }

    def summary(self) -> Dict[str, object]:
        changes = self.status_short()
        return {
            "branch": self.current_branch(),
            "change_count": len(changes),
            "git_executable": self.git_executable,
        }

    def commit_and_push(
        self,
        message: str,
        remote: str = "origin",
    ) -> Dict[str, str]:
        message = message.strip()
        if not message:
            raise GitOperationError("Commit message cannot be empty.")

        changes = self.status_short()
        if not changes:
            raise GitOperationError(
                "There are no uncommitted changes to commit."
            )

        branch = self.current_branch()

        # Fetch first so we do not knowingly push from a branch that is behind.
        self.fetch(remote)
        sync = self.ahead_behind()

        if sync["upstream_known"] and sync["behind"] > 0:
            raise GitOperationError(
                "The local branch is behind the remote branch. "
                "Pull the latest changes before committing and pushing."
            )

        self._run(["add", "-A"])

        # Confirm staging actually produced content.
        staged = self._run(
            ["diff", "--cached", "--name-only"]
        ).stdout.strip()

        if not staged:
            raise GitOperationError(
                "No staged changes were found after running git add -A."
            )

        self._run(["commit", "-m", message])

        commit = self._run(
            ["rev-parse", "--short", "HEAD"]
        ).stdout.strip()

        push = self._run(
            ["push", remote, branch],
            timeout=180,
            check=False,
        )

        if push.returncode != 0:
            detail = (push.stderr or push.stdout or "").strip()
            raise GitOperationError(
                "The commit was created locally, but the push failed.\n\n"
                f"Local commit: {commit}\n"
                f"Branch: {branch}\n\n"
                f"{detail or 'No push error details were returned.'}\n\n"
                "The commit has NOT been lost. Open GitHub Desktop and push "
                "the existing local commit, or resolve the reported Git issue."
            )

        return {
            "commit": commit,
            "branch": branch,
            "remote": self.remote_url(remote),
        }
