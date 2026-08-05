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
