# Final Repository Reconciliation

This report is machine-generated from the reconciliation validator. Tracked Git parity, Git LFS verification and local-only inventory claims are reported separately; GitHub parity applies only to tracked and Git LFS-managed content.

## Repository identity

- Repository URL: `git@github.com:mhyahya854/Mnemora.git`
- Default branch: `main`
- Branch at verification: `main (canonical default branch; linear history integrated from graphify-final-reconciliation)`
- Verified commit: `6383a3a98d63cc894497c6e6036142fc3bcbeeec`
- Verified tree: `c6b6252b8e8a6475a5204968f8b33d43268a71e1`
- Tracked file count: 433
- Tracked codebase file count: 346
- Git LFS file count: 1

## Protected content

- `Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md`: `BDF185A823422BCAA9BFEBA815A6852D8F7A5CD46B64714B2CD1DE3357A67F64` (canonical git blob content)
- `Master Plan/02-EVERYTHING-WE-ARE-DELETING.md`: `76B6EEC15778B1928F2CD9C0F73FA68C9F3363493062E31E0C904E620DE0AAC3` (canonical git blob content)
- `Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-REPLACE.md`: `5E076498731C35ACF314904AAB3A39671F7026A166B5E847EFE3CCD4CF07304E` (canonical git blob content)

## Historical full-tree manifests (LOCAL ONLY - NOT GITHUB-VERIFIED)

- Raw baseline SHA-256: `201FC0BDAE689102ED823385C8F8EFEAB1A3739C65EAB8743398DFE94F8D0006`
- Raw final SHA-256: `6AA22642525633E6E59E51FB1EB281D4AAE78602B15FAF7744E7FF9B1EF4CF6C`
- Raw files byte-identical: False
- Normalized baseline entries: 24839
- Normalized final entries: 24839
- Added: 0; missing: 0; changed: 0; duplicates: 0; malformed: 0
- Normalized path-to-SHA-256 mappings identical: True

## Canonical tracked manifests (GitHub-verifiable)

- Raw baseline SHA-256: `A500B0D0A7CAC3A6EB236BBEBA59C949AC38D88A886E7A6F717E1320797CE3BE`
- Raw final SHA-256: `A500B0D0A7CAC3A6EB236BBEBA59C949AC38D88A886E7A6F717E1320797CE3BE`
- Raw files byte-identical: True
- Normalized baseline entries: 346
- Normalized final entries: 346
- Added: 0; missing: 0; changed: 0; duplicates: 0; malformed: 0
- Normalized path-to-SHA-256 mappings identical: True
- Current git mapping identical to final manifest: True

## Transient exclusions

- Excluded categories: .git, .log, .mypy_cache, .pyc, .pyo, .pytest_cache, .ruff_cache, .swo, .swp, .tmp, __pycache__, ~
- Graphify output-manifest entries: 68

## Validation

- Gate count: 43; passed: 43; failed: 0; verdict: PASS
- Commands: python -B Graphify/tools/semantic_validator.py --self-test-only, python -B Graphify/tools/validate_planning.py, python -B Graphify/tools/validate_planning.py --full-codebase

## Local-only inventory audit

- RUN in the original full-tree repository; SKIPPED in clean clones (tracked Git parity above is the GitHub-verifiable claim; detailed per-environment evidence is in PLANNING_VALIDATION_REPORT.json)

## Working tree

- Pre-run working tree: CLEAN

## Status

- Implementation: IN PROGRESS; release: NOT EVALUATED
