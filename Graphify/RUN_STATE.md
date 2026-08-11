# Run State

## Current checkpoint

- Mode: validated derived planning with durable implementation execution state.
- Repository root: the Git worktree root discovered by `git rev-parse --show-toplevel` (machine-specific absolute path intentionally not embedded).
- Current application root: `codebase/` (lowercase path is authoritative current evidence).
- Git: present at the repository root; branch, commit, staged, unstaged, deleted and untracked states are verified at implementation time by `TASK-GOV-001-PROVENANCE-BASELINE` and recorded in the audit baseline (the checked-out branch name is intentionally not embedded so generated evidence is identical across clones).
- Provenance fallback: `REPOSITORY_FILE_INVENTORY.json` plus `REPOSITORY_FINGERPRINT.json`; the immutable execution root is `TASK-GOV-001-PROVENANCE-BASELINE`.
- Immutable Master Plan files: verified against the SHA-256 values below before derived generation.
- Implementation status: `NOT STARTED`; task counts: `{"BLOCKED": 0, "COMPLETE": 0, "NOT APPLICABLE": 0, "NOT STARTED": 158}`.
- Latest terminal task checkpoint: `NONE`.
- Release status: not evaluated by task execution state.

## Planning authorities

- Requirements: 536 in `MASTER_REQUIREMENT_REGISTER.json`.
- Capabilities: 120 in `CAPABILITY_REGISTRY.json`.
- Exact-location entries: 780 in `EXACT_LOCATION_REGISTRY.json`.
- Implementation tasks: 158 in `IMPLEMENTATION_QUEUE.json`.
- Deletion tasks: 31.
- Conditional decision packages: 11.
- Strict release gates: 12.
- Interpretations: 7; unresolved derived conflicts: 0.

## Resume pointer

Read `START-HERE.md`. The current next task is `TASK-GOV-001-PROVENANCE-BASELINE` with disposition `NOT STARTED`; `BLOCKED` is a stop barrier, never a skip condition. Re-run `python -B Graphify/tools/validate_planning.py` before execution.

## Master Plan hashes

| Master Plan | SHA-256 |
| --- | --- |
| 01-EVERYTHING-WE-ARE-KEEPING.md | BDF185A823422BCAA9BFEBA815A6852D8F7A5CD46B64714B2CD1DE3357A67F64 |
| 02-EVERYTHING-WE-ARE-DELETING.md | 76B6EEC15778B1928F2CD9C0F73FA68C9F3363493062E31E0C904E620DE0AAC3 |
| 03-HOW-WE-WILL-KEEP-DELETE-AND-REPLACE.md | 5E076498731C35ACF314904AAB3A39671F7026A166B5E847EFE3CCD4CF07304E |
