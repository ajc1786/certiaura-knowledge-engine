# Project Genesis v1.2 — Commit & Push

## Status

Functional Git commit and push workflow added to the desktop application.

## New capability

The **Commit & Push** button now:

1. Reads the current Git repository status.
2. Shows all uncommitted changes for review.
3. Requires a non-empty commit message.
4. Shows a final confirmation summary.
5. Fetches the remote repository.
6. Checks whether the local branch is behind its upstream branch.
7. Stages all current changes with `git add -A`.
8. Creates a local commit.
9. Pushes the current branch to `origin`.
10. Reports the resulting commit identifier.

## Safety controls

- No action occurs when there are no changes.
- A commit message is mandatory.
- Changes are shown before commit.
- Final confirmation is required.
- The remote is fetched before the commit is published.
- Commit & Push is blocked when the local branch is known to be behind.
- If commit succeeds but push fails, Genesis clearly states that the local commit still exists.
- Git terminal prompts are disabled so the application does not hang waiting for invisible input.
- Genesis searches for Git on PATH and in common GitHub Desktop installation locations.

## Important operating rule

The current v1.2 workflow stages **all current repository changes**.

The user must therefore review the Git status list before confirming Commit & Push.

## Next planned development

The next logical Project Genesis improvement is not automatically assumed by this release. Future work should follow the Certiaura Master Project Charter, the current production priority and any explicit founder instruction.
