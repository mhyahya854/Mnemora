# Semantic Planning-Completion Baseline

Recorded before the material derived-planning repairs of the 2026-08-02 planning-only run. This is an observation of the initial planning state, not application, test, build, package, installer, launch, regression, or release evidence.

## Scope and mutation boundary

- Workspace root: `C:\Users\mhyah\Downloads\Code\Mnemora`.
- Editable planning root: `C:\Users\mhyah\Downloads\Code\Mnemora\Graphify`.
- Read-only application root: `C:\Users\mhyah\Downloads\Code\Mnemora\codebase`.
- The actual application directory is lowercase `codebase`; `Codebase` in the Master Plan is a future target spelling and conveyed no rename authority in this run.
- Root entries observed: `codebase/` and `Graphify/`.
- Application mutation during baseline inspection: none.

## Immutable Master Plan baseline

| Source | Lines | Bytes | Pre-run SHA-256 |
| --- | ---: | ---: | --- |
| `Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md` | 215 | 17,082 | `BDF185A823422BCAA9BFEBA815A6852D8F7A5CD46B64714B2CD1DE3357A67F64` |
| `Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md` | 217 | 14,448 | `76B6EEC15778B1928F2CD9C0F73FA68C9F3363493062E31E0C904E620DE0AAC3` |
| `Graphify/Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-REPLACE.md` | 1,287 | 35,296 | `5E076498731C35ACF314904AAB3A39671F7026A166B5E847EFE3CCD4CF07304E` |

All 1,719 source lines were read. The three source files are immutable for this run.

## Git and provenance state

- No `.git` metadata exists at the workspace root, in `codebase`, or in an inspected parent through `C:\`.
- Branch, commit, staged, unstaged, deleted, and untracked states are unavailable because Git is absent.
- The current application inventory contains 24,839 files. A pre-existing saved SHA-256 is available for only 346 current application files; the other 24,493 have path-and-size baseline evidence only.
- A whole-tree post-run fingerprint can prove a final state but cannot retroactively provide byte-for-byte before/after equality for the 24,493 files that lacked a pre-run content hash. Final reporting must state this evidence boundary explicitly.
- The pre-existing 346 comparable application records matched at baseline inspection.

## Application structure observed

- Package root and dependency lock: `codebase/package.json`, `codebase/package-lock.json`.
- Electron main: `codebase/main/`, including desktop, features, infrastructure, IPC, platform, and workers.
- Preload and renderer roots: `codebase/preload/`, `codebase/renderer/`.
- Persistence and migrations: `codebase/main/infrastructure/persistence/`.
- Native sources and helpers: `codebase/native/`, including Windows, macOS, Linux, and meeting-AEC source.
- Models, binaries, and resources: `codebase/resources/`.
- Build, download, diagnostic, packaging, and verification scripts: `codebase/scripts/`.
- Tests and fixtures: `codebase/tests/`.
- Packaging configuration: `codebase/electron-builder.json`, `codebase/electron-builder.unsigned-win.json`, `codebase/packaging/`, package scripts, Vite/TypeScript configuration, and native build scripts.
- Existing generated/build and dependency trees, including `codebase/build-output/` and `codebase/node_modules/`, were inventory evidence only and not editable or authoritative source targets.

## Existing Graphify and planning state

- Genuine Graphify 0.9.17 artifacts existed under `Graphify/graphify-out/`; they remain generated static-analysis evidence, not Master Plan authority.
- The initial derived authorities claimed 536 requirements, 120 capabilities, 153 tasks, 31 deletion tasks, 11 conditional packages, 12 release gates, 5,619 exact-location entries, and 18/18 validation gates.
- Those totals were not accepted as semantic completion evidence. Counts can reconcile while requirement meaning, ownership, locations, dependency semantics, evidence types, and deletion dispositions remain wrong.
- The three immutable Master Plan files remained the sole product/transformation authority. `EXACT_LOCATION_REGISTRY.json` remained the sole exact-location authority; no Markdown mirror was permitted.

## Initial semantic defects requiring in-place repair

1. Product-scope lock lines were misclassified, including protected retained scope from Master Plan 2.
2. AEC was contaminated by the dictation dictionary echo filter instead of being anchored to meeting AEC and its native processor.
3. Exact search was contaminated by semantic-vector implementation rather than the SQLite `searchLocal` boundary.
4. Notes included MiniLM tokenizer/model assets; broad domain matching substituted lexical proximity for architectural ownership.
5. Many capability locations and targets were broad, vendor/generated, unrelated, or nonexistent, including playback, hotkeys, meeting notes, IPC, packaging, renderer, import, recovery, legal, Sherpa-ONNX, and macOS/Linux preservation.
6. Generic repository ownership and heuristic target selection obscured the real owned implementation boundary.
7. The 153-task dependency structure behaved as an artificial sequential chain rather than a semantic capability DAG.
8. Several test obligations used synthetic paths or invalid `npm test -- <path>` command shapes and did not distinguish existing tests from tests to create.
9. Deletion candidate classification treated MiniLM tokenizer vocabulary, OS login/startup language, OS `NSWorkspace` usage, visual “premium” adjectives, historical OpenWhispr compatibility, and legal attribution as active removed-product behavior.
10. Historical OpenWhispr migration and compatibility evidence was not consistently separated from active brand identity.
11. Integrity wording implied broader before/after proof than the available 346 pre-run content hashes support.
12. Operational handoff and completion reports inherited structurally passing but semantically unsound claims.

## In-place consolidation decision

- Repair existing requirement, capability, exact-location, queue, test, architecture, ownership, deletion, third-party, run-state, readiness, and verification authorities in place.
- Keep one machine-readable authority for each register and only deterministic human-readable views where useful.
- Preserve genuine Graphify output with honest provenance; do not invent graph nodes or runtime results.
- Use a minimal standard-library generator and validator, with negative fixtures for known semantic corruption classes.
- Do not create a parallel planning tree, backups, version copies, or an implementation branch.

## Baseline verdict

`SEMANTIC GRAPHIFY PLANNING INCOMPLETE — CONTINUE WORKING`

Reason: the initial derived planning reconciled structurally but failed semantic ownership, exact-location, dependency, test-evidence, deletion-disposition, integrity, and handoff requirements.

---

# 2026-08-05 Independent Semantic Audit Baseline

This section is the authoritative baseline of the second, independent semantic planning audit run. It was recorded before any repair batch of this run. It does not repeat the earlier baseline above; it records the state of the repository as found on 2026-08-05 and the audit methodology.

## Repository and Git state (as found)

- Repository root: `C:\Users\mhyah\Downloads\Code\Mnemora`.
- Starting main commit: `42bad4cc8e47443625df0346d838dc50909d636f`.
- origin/main at start: `42bad4cc8e47443625df0346d838dc50909d636f` (matched).
- Audit working branch: `graphify-semantic-audit` (created and pushed at the start of this run).
- Working tree at start: clean; no staged, unstaged, deleted, or untracked files before this audit.
- Remote: `git@github.com:mhyahya854/Mnemora.git` (origin).
- Git LFS tracked path: `codebase/resources/bin/whisper-models/ggml-base.bin` (exact-path rule in root `.gitattributes`).

## Immutable Master Plan hashes (pre-repair)

| Master Plan | SHA-256 |
| --- | --- |
| `Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md` | `BDF185A823422BCAA9BFEBA815A6852D8F7A5CD46B64714B2CD1DE3357A67F64` |
| `Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md` | `76B6EEC15778B1928F2CD9C0F73FA68C9F3363493062E31E0C904E620DE0AAC3` |
| `Graphify/Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-REPLACE.md` | `5E076498731C35ACF314904AAB3A39671F7026A166B5E847EFE3CCD4CF07304E` |

All 1,719 source lines were read completely in this audit run before any repair.

## Codebase read-only fingerprint evidence

- Baseline manifest: `Graphify/AUDIT_CODEBASE_BASELINE_SHA256.txt`.
- Scope: every file under `codebase/` (24,839 files), path plus full SHA-256, created before any repair batch.
- Whisper model: `codebase/resources/bin/whisper-models/ggml-base.bin`, size 147,951,465 bytes, SHA-256 `60ED5BC3DD14EEA856493D334349B405782DDCAF0028D4B5DF4088345FBA2EFE`, still governed by the exact LFS rule.

## Graphify authoritative files (as found)

`MASTER_REQUIREMENT_REGISTER.json`, `INTERPRETATION_REGISTER.json`, `CAPABILITY_REGISTRY.json`, `CAPABILITY_REGISTRY.md`, `EXACT_LOCATION_REGISTRY.json`, `IMPLEMENTATION_QUEUE.json`, `IMPLEMENTATION_QUEUE.md`, `CONDITIONAL_DECISION_PACKAGES.json`, `RELEASE_GATE_PLAN.json`, `TEST_MATRIX.json`, `TEST_MATRIX.md`, `RUN_STATE.md`, `COMPLETION_TRACKER.md`, `REPOSITORY_FILE_INVENTORY.json`, `REPOSITORY_INVENTORY.md`, `CURRENT_ARCHITECTURE.md`, `TARGET_ARCHITECTURE.md`, `FOLDER_OWNERSHIP_MAP.md`, `MOVE_LEDGER.md`, `DELETED_ITEMS_LEDGER.md`, `REPLACEMENT_MAP.md`, `READINESS_GATE.json`, `READINESS_GATE.md`, `GRAPHIFY_READINESS_REPORT.md`, `GRAPH_CONSISTENCY_REPORT.json`, `GRAPH_CONSISTENCY_REPORT.md`, `VERIFICATION_AUDIT.json`, `GRAPHIFY_OUTPUT_MANIFEST.json`, `PLANNING_COUNTS.md`, `PLANNING_VALIDATION_REPORT.json`, `PLANNING_VALIDATION_REPORT.md`, `START-HERE.md`, and generated graph/static-analysis evidence under `graphify-out/`.

## Existing validators and generators

- Validator entry point: `Graphify/tools/validate_planning.py` (delegates to `semantic_validator.py`).
- `Graphify/tools/semantic_validator.py`: 36 deterministic gates (SEM-001..SEM-036), including negative fixtures.
- Generator: `Graphify/tools/complete_planning.py` (regenerates all derived authorities from the Master Plans, reviewed rules in `semantic_rules.py`, and the codebase inventory).
- Other tools: `analyze_import_cycles.cjs`, `build_knowledge_layer.py`, `run_second_graphify_scan.py`, `verify_knowledge_layer.py`.

## Existing totals (as found, HEAD)

- Requirements: 536.
- Capabilities: 120.
- Implementation tasks: 158 (31 deletion tasks).
- Conditional decision packages: 11.
- Strict release gates: 12.
- Exact-location entries: 759.
- Interpretations: 7; unresolved conflicts: 0.

## Initial validator result (as found)

`FAIL` - 35/36 gates passed. The single failure:

- `SEM-031-GENERATOR-REPRODUCIBILITY`: running `complete_planning.py` changed the semantic authority fingerprint from `BE13917373AF3B6D2A4F1BA6AC1467C6B5BBABE6B9C5CA6289353078CF152876` to `4F947C7FD1657FF721702398BB381CCC895171F55A8F9E53A682A7801C195A97`, and the stored `VERIFICATION_AUDIT.json` / `PLANNING_VALIDATION_REPORT.json` still claimed `PASS` (stale 2026-08-02 evidence).

## Suspected heuristic generation and polluted mappings (as found)

1. The committed registries and the generator output were out of sync; the previous completion claim was therefore untrustworthy.
2. Independent review of the regeneration diff: the generator adds 26 deletion-evidence entries (and removes 5 placeholder entries) for five removal capabilities - cloud synchronisation, MCP, public API, upgrade systems, and usage quotas - anchored at genuine stale strings in `codebase/shared/i18n/en/translation.json` (for example "Sync across machines using your API key.", "MCP", "Upgrade to a paid plan to access the API", "Daily limit reached"). These are real stale-UI deletion candidates under Master Plan 2 sections 19-22, not keyword false positives. The generated state is adopted for this audit.
3. Areas still requiring independent verification in later batches: exact-location path/symbol existence and node_modules/vendor target restrictions; deletion-candidate false-positive classes (tokenizer assets, OS login items, historical migrations, legal attribution, offline/local messages); test-command validity against `codebase/package.json`; semantic dependency graph, phase/wave/order agreement; conditional-package and release-gate completeness; placeholders, orphans, duplicates, internal links, counts; codebase immutability.

## Audit methodology

1. Record Git state, Master Plan hashes, Whisper hash, and the full codebase SHA-256 manifest.
2. Read all three Master Plan files completely.
3. Run the deterministic validator and record the verdict.
4. Run the generator and diff every authority against HEAD; classify each change semantically before adopting it.
5. Independently cross-check the highest-risk claims with read-only scripts: path existence, symbol/anchor existence, package-script validity, DAG acyclicity, phase/wave/order monotonicity, deletion dispositions, and codebase immutability.
6. Repair generators/validators first, then regenerate authorities, then expand validators, then finalise handoff.
7. Commit and push after every coherent batch; verify remote branch matches local HEAD after every push.

## Planned repair batches

1. Record this independent audit baseline and the codebase manifest; commit and push.
2. Repair generator reproducibility; adopt the semantically reviewed regeneration; reconcile registries and verification reports; commit and push.
3. Requirement-by-requirement semantic verification and classification corrections.
4. Capability ownership and runtime-chain verification.
5. Exact-location path/symbol/vendor/generated-target verification.
6. Deletion-candidate disposition and interlock verification.
7. Semantic task dependency graph, phases, waves, and execution order verification.
8. Test and evidence contract verification against the real repository.
9. Conditional decision package and release-gate verification.
10. Validator expansion for any gaps found.
11. Final handoff consistency and completion conjunction.
12. Final validation and safe fast-forward integration to `main`.

## Baseline verdict for this audit run

`SEMANTIC GRAPHIFY PLANNING INCOMPLETE - CONTINUE WORKING`

Reason: the stored completion claim was stale; the generator and registries were out of sync, and the full independent conjunction had not yet been re-proven on this run.

## Audit batch records (2026-08-05)

Every coherent audit/fix batch is committed on `graphify-semantic-audit` and pushed to `origin`; each entry records the local/remote-verified commit.

| Batch | Commit | Content | Remote verified |
| --- | --- | --- | --- |
| 1 | `09e3fc4c8e77faae60c7ee0727801954ffdae0f3` | Independent audit baseline (this file) plus full codebase SHA-256 manifest `AUDIT_CODEBASE_BASELINE_SHA256.txt` | Yes |
| 2 | `6a708d1bf54905ecb86151c797965dd1b08ddafb` | Reconciled regenerated authorities with the deterministic generator; adopted 26 reviewed deletion-evidence entries (759 to 780 exact locations) for cloud synchronisation, MCP, public API, upgrade systems and usage quotas; validator 36/36 | Yes |
| 3 | `a1d739967d4a409847fdc948c941c28b201d7213` | Generator repair: real Git provenance state in RUN_STATE, REPOSITORY_INVENTORY and TASK-GOV-001; validator 36/36 | Yes |
| 4 | (recorded at audit completion) | Finalised implementation handoff (START-HERE current-state and push procedure) and completion tracker | Yes |

Independent read-only verification performed in this audit: requirement heading/line/section reconciliation (0 defects); scope-lock completeness (all 8 named capabilities on all 3 scope locks); capability ownership for AEC, exact search, semantic search, and notes (0 cross-domain contamination); exact-location path and symbol/anchor existence (0 real defects); no vendor/generated editable targets (only the legitimate `.git/` provenance target); test-command validity (0 missing scripts); existing-test path existence (0 missing); DAG acyclicity and topological order (0 defects); phase/wave/order monotonicity (0 defects); deletion false-positive classes for tokenizer, login-item, migration, and legal paths (0 active); governance/deletion evidence-type appropriateness (0 synthetic app tests); conditional packages (11/11 complete); release gates (12/12 complete); orphan/duplicate/placeholder counts (0).
