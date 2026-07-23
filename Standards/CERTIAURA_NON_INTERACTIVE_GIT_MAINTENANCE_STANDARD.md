# Certiaura Non-Interactive Git Maintenance Standard

Build: `0057`

Canonical commit, push and closure workflows must not launch interactive automatic garbage-collection or maintenance prompts. The workflow must preserve the prior local values and presence state for `gc.auto`, `maintenance.auto` and `gc.autoDetach`, temporarily set safe non-interactive values, execute the controlled Git operations with `GIT_TERMINAL_PROMPT=0`, and restore the prior local configuration in a `finally` block.

The control must never delete `.git/objects` manually. Any maintenance requirement is deferred to a separate operator-controlled maintenance step after repository integrity and remote alignment are verified.
