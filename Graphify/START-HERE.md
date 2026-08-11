# Mnemora implementation handoff

This is the single authoritative entry point for an implementation run. Implementation has not started; every task remains NOT STARTED. The current application root is the lowercase `codebase/` folder; `Codebase/` is only a future target named by the Master Plan. The derived planning is subordinate to all three immutable Master Plan files. Planning generation never turns a planning contract into implementation evidence.

## Authority order

1. `Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md`
2. `Master Plan/02-EVERYTHING-WE-ARE-DELETING.md`
3. `Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-REPLACE.md`
4. `MASTER_REQUIREMENT_REGISTER.json`
5. `INTERPRETATION_REGISTER.json`
6. `CAPABILITY_REGISTRY.json`
7. `EXACT_LOCATION_REGISTRY.json`
8. `IMPLEMENTATION_QUEUE.json`
9. `CONDITIONAL_DECISION_PACKAGES.json` and `RELEASE_GATE_PLAN.json`

## Scope and editable boundaries

- Repository root: the Git worktree root discovered by `git rev-parse --show-toplevel` (machine-specific absolute path intentionally not embedded).
- Current application root: `codebase/`; the lowercase path remains authoritative until a future casing-safe move task is executed.
- Current repository state: Git is present at the repository root. The semantic planning audit is performed on the `graphify-semantic-audit` branch and is fast-forward-integrated into `main` by the audit-run completion step; the generation-time branch is recorded in `RUN_STATE.md`.
- The completed run represented here edited only `Graphify/`. A future implementation run may edit application-owned files only when the active queue task names them under `files_expected_to_change`; the three Master Plan files and every task's `files_forbidden_from_changing` remain immutable boundaries.
- Installed dependencies, generated output, user databases, recordings, notes, transcripts, exports and backups are never implementation targets. Destructive tests use disposable verified copies.

## State-inspection commands

Run from the repository root before taking implementation authority:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath 'Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md','Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md','Graphify/Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-REPLACE.md'
git rev-parse --show-toplevel
git status --short --branch
python -B Graphify/tools/validate_planning.py --full-codebase
```

If Git is still absent, record that exact result; do not treat the Git command failure as permission to mutate. Follow `TASK-GOV-001-PROVENANCE-BASELINE` and the Master Plan's hash-checkpoint fallback.

## Execution root and current next task

`TASK-GOV-001-PROVENANCE-BASELINE`

The immutable execution root is ordering index 1 in `IMPLEMENTATION_QUEUE.json`. The current derived `next_task_id` is `TASK-GOV-001-PROVENANCE-BASELINE` with disposition `NOT STARTED`. Establish Git or the Master Plan-permitted recoverable hash checkpoint before any application mutation. Do not begin a later task merely because its files appear familiar.

## Dependency-safe phase and wave sequence

| Phase | First index | Last index | Tasks | Waves |
| --- | --- | --- | --- | --- |
| PHASE-01-AUTHORITY-AND-PROVENANCE | 1 | 1 | 1 | WAVE-01 |
| PHASE-02-CHARACTERIZATION-AND-DATA-SAFETY | 2 | 13 | 12 | WAVE-02, WAVE-02Z |
| PHASE-03-DECOUPLING-AND-RETAINED-PROTECTION | 14 | 36 | 23 | WAVE-03, WAVE-03Z |
| PHASE-04-EXCLUDED-SYSTEM-REMOVAL | 37 | 68 | 32 | WAVE-04, WAVE-04Z |
| PHASE-05-RETAINED-CAPABILITIES | 69 | 137 | 69 | WAVE-05, WAVE-05C, WAVE-05D, WAVE-05E, WAVE-05Z |
| PHASE-06-REORGANIZATION-AND-CLEANUP | 138 | 146 | 9 | WAVE-06, WAVE-06Z |
| PHASE-07-INTEGRATION-AND-RELEASE-EVIDENCE | 147 | 158 | 12 | WAVE-07 |

`semantic_dependencies` is the authoritative prerequisite relation. `execution_order`/`ordering_index` is its deterministic topological handoff order, not an artificial immediate-predecessor chain. A future model may parallelize only tasks whose `semantic_dependencies` are complete and whose files/data boundaries do not overlap. For each conditional package, one outcome is implemented and the other must receive an evidence-linked `NOT APPLICABLE` disposition; neither branch may be silently skipped.

## Resume protocol

1. Read every line of all three Master Plan files and verify the hashes below.
2. Run `python Graphify/tools/validate_planning.py` from the Mnemora root. Stop on any failure.
3. Read `RUN_STATE.md` and `IMPLEMENTATION_QUEUE.json`; use the derived `next_task_id`, which is the first ordering-index task that is neither `COMPLETE` nor evidence-linked `NOT APPLICABLE` and whose semantic dependencies are terminal.
4. If that task is `BLOCKED`, stop on it. The selector never skips a blocked next task. Otherwise confirm all dependency task evidence has a valid checkpoint identity.
5. Execute exactly one recoverable capability batch, save every required artifact, write its `execution_state`, rerun planning validation, and do not change the Master Plan.
6. Never use a planning-complete status as implementation or release evidence.

## Durable execution-state protocol

`IMPLEMENTATION_QUEUE.json` remains the single task authority. Planning fields are regenerated task definitions. The nested `execution_state` object is mutable implementation state and is preserved by stable task ID across deterministic generation:

```json
{
  "disposition": "NOT STARTED | COMPLETE | NOT APPLICABLE | BLOCKED",
  "evidence_references": [],
  "checkpoint_identity": null,
  "blocked_reason": null,
  "not_applicable_basis": null
}
```

- `COMPLETE` requires terminal semantic dependencies, every required evidence reference, existing evidence files, and a checkpoint identity.
- `NOT APPLICABLE` requires terminal semantic dependencies, evidence, a checkpoint identity, and the exact Master Plan or conditional-decision reachability basis.
- `BLOCKED` requires a reason and remains the selected task; optional evidence and checkpoint fields must appear together.
- `NOT STARTED` carries no execution evidence. The queue's top-level status, counts, checkpoint and next-task pointer are derived from task state and validated against it.

## Conditional decisions and task completion

For each record in `CONDITIONAL_DECISION_PACKAGES.json`, collect the named evidence at its decision phase, record the selected `DEFAULT` or `DEVIATION` outcome with artifact paths and checkpoint identity, execute only that outcome's downstream task, and mark the unreachable sibling task `NOT APPLICABLE` with the authorizing decision record. Do not invent thresholds or delete a package merely to simplify packaging.

A task becomes `COMPLETE` only after its preconditions and `semantic_dependencies` are terminal, every required artifact exists, exact locations are reconciled, commands/manual methods have saved results, acceptance and completion criteria pass, and no stop condition is active. Write the task's durable `execution_state` and linked evidence at one Git/hash checkpoint; deterministic generation reconciles `EXACT_LOCATION_REGISTRY.json`, derives `RUN_STATE.md`, and regenerates Markdown views without replacing task state.

## Provenance and false-completion controls

Use one focused Git commit per recoverable capability batch when Git exists. When it does not, save pre/post path, byte-size and SHA-256 inventories plus the reversible delta before continuing. Never reset, clean, restore, stash or discard unrelated work. Planning status, file existence, mocks, administrative success text and an unavailable-hardware waiver cannot substitute for required real evidence.

After every coherent batch, review the exact diff, verify only permitted `Graphify/` paths changed, run the deterministic validator, commit, push to the configured origin, fetch origin, and confirm the local branch HEAD equals the remote branch HEAD before starting the next batch. Use `git push` without force; never rewrite history or discard unrelated work.

Evaluate all gates in `RELEASE_GATE_PLAN.json` only after their evidence-producing tasks finish. A gate fails when any applicable requirement/task lacks same-checkpoint proof; `NOT APPLICABLE` requires an explicit Master Plan or conditional-decision reachability basis, and absent hardware is `HARDWARE UNAVAILABLE`, not `PASS`. Final release approval requires the conjunction of all applicable gates.

## Immutable source hashes

| Master Plan | SHA-256 |
| --- | --- |
| 01-EVERYTHING-WE-ARE-KEEPING.md | BDF185A823422BCAA9BFEBA815A6852D8F7A5CD46B64714B2CD1DE3357A67F64 |
| 02-EVERYTHING-WE-ARE-DELETING.md | 76B6EEC15778B1928F2CD9C0F73FA68C9F3363493062E31E0C904E620DE0AAC3 |
| 03-HOW-WE-WILL-KEEP-DELETE-AND-REPLACE.md | 5E076498731C35ACF314904AAB3A39671F7026A166B5E847EFE3CCD4CF07304E |

## Evidence still to collect during implementation

- Characterisation, targeted, real-integration and regression logs for every queue task.
- Disposable-copy database migration, backup, integrity, idempotency, interruption and recovery results.
- Seven completed interlocks and full-layer disposition for every deletion task.
- The 11 conditional evidence packages and exactly one selected outcome per package.
- Runtime network observation, owned-loopback allow-list and offline first-launch evidence.
- Windows production build, package, clean installation, installed launch and offline workflow evidence.
- macOS/Linux static or CI evidence plus honest `HARDWARE UNAVAILABLE` records where physical hardware is absent.
- Final Graphify scan, final simplification audit, release-gate reconciliation and independent approval.
