# Mnemora Universal Rules Gap Report

## Executive Summary

- **Evaluated Universal Rules**: 22/22
- **SATISFIED**: 8
- **PARTIAL**: 12
- **MISSING**: 2
- **CONFLICT**: 0
- **NOT APPLICABLE**: 0
- **Master Plan Conflicts**: NONE
- **Task 2 Affected**: YES (Contract extended with characterization requirements; canonical disposition remains `NOT STARTED`)

## Summary Table

| Rule ID | Title | Status | Queue Change Required | Task 2 Affected |
| --- | --- | --- | --- | --- |
| `UAC-01` | APPLICATION INDEPENDENCE | **SATISFIED** | NO | NO |
| `UAC-02` | LOCAL-FIRST / OFFLINE-FIRST | **PARTIAL** | NO | NO |
| `UAC-03` | USER-SELECTED DATA ROOT SOVEREIGNTY | **PARTIAL** | YES | YES |
| `UAC-04` | NAS / PRIVATE-LAN SUPPORT | **MISSING** | YES | YES |
| `UAC-05` | CROSS-PLATFORM SUPPORT | **PARTIAL** | NO | NO |
| `UAC-06` | FEATURE-FIRST MODULAR MONOLITH | **PARTIAL** | YES | NO |
| `UAC-07` | HUMAN-READABLE FOLDER CONTRACT | **SATISFIED** | NO | NO |
| `UAC-08` | SMALL-MODEL NAVIGABILITY | **SATISFIED** | NO | NO |
| `UAC-09` | DETERMINISTIC NON-AI CORE | **SATISFIED** | NO | NO |
| `UAC-10` | AUTHORIZED MUTATION MODEL | **SATISFIED** | NO | NO |
| `UAC-11` | MUTATION AUDIT LOG / CHANGE FLAGGING | **MISSING** | YES | YES |
| `UAC-12` | RECOVERABILITY OVER MAGIC | **PARTIAL** | NO | YES |
| `UAC-13` | ORIGINALS VS DERIVED STATE | **PARTIAL** | NO | NO |
| `UAC-14` | DATABASE / SQLITE SAFETY | **PARTIAL** | NO | YES |
| `UAC-15` | SOURCE / PRIVATE DATA / GIT SEPARATION | **SATISFIED** | NO | NO |
| `UAC-16` | REPRODUCIBLE BUILDS | **PARTIAL** | NO | NO |
| `UAC-17` | THIRD-PARTY / DONOR PROVENANCE | **PARTIAL** | NO | NO |
| `UAC-18` | FAIL CLOSED | **PARTIAL** | NO | YES |
| `UAC-19` | UI / AI / PROVIDER REPLACEABILITY | **SATISFIED** | NO | NO |
| `UAC-20` | SCHEMA / VERSION SAFETY | **PARTIAL** | NO | YES |
| `UAC-21` | STABLE IDS / PORTABLE REFERENCES | **PARTIAL** | YES | YES |
| `UAC-22` | SELF-DESCRIBING PROJECT CONTRACT | **SATISFIED** | NO | NO |

---

## Detailed Rule Evaluations

### UAC-01 — APPLICATION INDEPENDENCE
- **Status**: **SATISFIED**
- **Evidence Paths**: `codebase/main/index.js`, `codebase/package.json`, `codebase/tests/integration/offlineFirstLaunch.test.js`, `Graphify/tools/semantic_validator.py`
- **Evidence Explanation**: Runtime codebase does not import, require, or depend on Hermes, Graphify, or external orchestrators. Core operations (audio capture, transcription, database persistence, search, backup, restore, UI) are local Node.js/Electron/SQLite code. SEM-044 validator checks ban hermes and Graphify imports across all tracked codebase files.
- **Affected Capability IDs**: `CAP-APP-SHELL`, `CAP-DATABASE`, `CAP-OFFLINE-FIRST-LAUNCH`
- **Affected Implementation Task IDs**: `TASK-CAP-APP-SHELL`, `TASK-CAP-DATABASE`, `TASK-CAP-OFFLINE-FIRST-LAUNCH`
- **Missing Implementation**: None
- **Queue Change Required**: NO
- **Master Plan Conflict**: NONE
- **Task 2 Affected**: NO

### UAC-02 — LOCAL-FIRST / OFFLINE-FIRST
- **Status**: **PARTIAL**
- **Evidence Paths**: `codebase/main/infrastructure/runtime/runtimeNetworkPolicy.js`, `codebase/main/features/transcription/whisper.js`, `Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md`, `Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md`
- **Evidence Explanation**: Master Plans mandate 100% offline execution and loopback-only binding (127.0.0.1). However, in the current donor codebase baseline (prior to executing Phase 4 deletion tasks), dormant cloud synchronization, remote auth, and telemetry remnants remain in codebase/ pending deletion under BDI interlocks.
- **Affected Capability IDs**: `CAP-NETWORK-POLICY`, `CAP-OFFLINE-FIRST-LAUNCH`, `CAP-REMOVE-CLOUD-SYNCHRONISATION`, `CAP-REMOVE-EXTERNAL-NETWORKING`, `CAP-REMOVE-AUTHENTICATION`
- **Affected Implementation Task IDs**: `TASK-CAP-NETWORK-POLICY`, `TASK-CAP-OFFLINE-FIRST-LAUNCH`, `TASK-DEL-CLOUD-SYNCHRONISATION`, `TASK-DEL-RUNTIME-EXTERNAL-NETWORKING`, `TASK-DEL-AUTHENTICATION`
- **Missing Implementation**: Execution of Phase 4 deletion tasks to cleanly excise all donor cloud/network code.
- **Queue Change Required**: NO
- **Master Plan Conflict**: NONE
- **Task 2 Affected**: NO

### UAC-03 — USER-SELECTED DATA ROOT SOVEREIGNTY
- **Status**: **PARTIAL**
- **Evidence Paths**: `codebase/main/infrastructure/persistence/database.js`, `codebase/main/index.js`, `codebase/main/features/settings/settingsManager.js`
- **Evidence Explanation**: User data is currently anchored to Electron default app.getPath('userData'). There is no mechanism for the user to select or move a custom application data root without data meaning loss. SQLite tables also record absolute paths rather than root-relative portable paths.
- **Affected Capability IDs**: `CAP-DATA-SAFETY`, `CAP-DATABASE`, `CAP-SETTINGS`
- **Affected Implementation Task IDs**: `TASK-CAP-DATA-SAFETY`, `TASK-CAP-DATABASE`, `TASK-CAP-SETTINGS`
- **Missing Implementation**: Explicit data-root resolution service, custom data-root configuration UI in settings, relative path resolution for stored assets, and safe migration workflow when moving the data root.
- **Queue Change Required**: YES
- **Master Plan Conflict**: NONE
- **Task 2 Affected**: YES

### UAC-04 — NAS / PRIVATE-LAN SUPPORT
- **Status**: **MISSING**
- **Evidence Paths**: `codebase/main/infrastructure/persistence/database.js`, `codebase/main/infrastructure/persistence/localBackup.js`, `Graphify/CONDITIONAL_DECISION_PACKAGES.json`
- **Evidence Explanation**: Current implementation has zero handling for network shares / NAS data roots. SQLite is known to suffer locking failures, latency timeouts, and corruption over network filesystems (SMB/NFS). Share unavailability, reconnection, latency, interrupted writes, and multi-instance concurrency on network drives are completely unaddressed in current code.
- **Affected Capability IDs**: `CAP-DATA-SAFETY`, `CAP-DATABASE`, `CAP-NAS`
- **Affected Implementation Task IDs**: `TASK-CAP-DATA-SAFETY`, `TASK-DEC-NAS`, `TASK-OUT-NAS-DEFAULT`, `TASK-OUT-NAS-DEVIATION`
- **Missing Implementation**: Technical architecture decision (DEC-NAS) for safe NAS support: separating canonical active SQLite working database locally with continuous or on-change replica/archive to NAS, vs proving direct SQLite-on-NAS with advisory locks. Handling share disconnects, latency, reconnection, one-writer locking, and multi-instance prevention.
- **Queue Change Required**: YES
- **Master Plan Conflict**: NONE
- **Task 2 Affected**: YES

### UAC-05 — CROSS-PLATFORM SUPPORT
- **Status**: **PARTIAL**
- **Evidence Paths**: `codebase/native/helpers/macos/mac_meeting_audio_tap.swift`, `codebase/native/helpers/linux/audio_portal_monitor.py`, `codebase/electron-builder.json`, `Graphify/CONDITIONAL_DECISION_PACKAGES.json`
- **Evidence Explanation**: Donor macOS and Linux helper source code is preserved in codebase/native/helpers/ under CAP-MACOS-LINUX and DEC-MACOS-LINUX. However, Mnemora first-release milestone is explicitly Windows-first (CAP-WINDOWS-INSTALLER, CAP-PORTABLE-WINDOWS). Cross-platform runtime execution, platform-specific hotkeys, and packaging have not been tested or proven on macOS or Linux.
- **Affected Capability IDs**: `CAP-MACOS-LINUX`, `CAP-WINDOWS-INSTALLER`, `CAP-PORTABLE-WINDOWS`, `CAP-NATIVE`
- **Affected Implementation Task IDs**: `TASK-DEC-MACOS-LINUX`, `TASK-OUT-MACOS-LINUX-DEFAULT`, `TASK-OUT-MACOS-LINUX-DEVIATION`, `TASK-CAP-WINDOWS-INSTALLER`
- **Missing Implementation**: macOS and Linux build pipelines, packaging scripts, and native helper runtime verification.
- **Queue Change Required**: NO
- **Master Plan Conflict**: NONE
- **Task 2 Affected**: NO

### UAC-06 — FEATURE-FIRST MODULAR MONOLITH
- **Status**: **PARTIAL**
- **Evidence Paths**: `codebase/main/features/dictation/`, `codebase/renderer/features/notes/`, `codebase/main/infrastructure/`, `codebase/renderer/shared/`
- **Evidence Explanation**: The codebase partially uses a feature-first structure with main/features/ and renderer/features/. However, generic dumping grounds still exist (codebase/main/infrastructure/, codebase/renderer/shared/utils/, etc.) containing mixed responsibilities across features.
- **Affected Capability IDs**: `CAP-REPOSITORY`, `CAP-SIMPLIFICATION`
- **Affected Implementation Task IDs**: `TASK-CAP-REPOSITORY`, `TASK-CAP-SIMPLIFICATION`
- **Missing Implementation**: Incremental migration of shared utilities to feature ownership during Phase 6 reorganization tasks.
- **Queue Change Required**: YES
- **Master Plan Conflict**: NONE
- **Task 2 Affected**: NO

### UAC-07 — HUMAN-READABLE FOLDER CONTRACT
- **Status**: **SATISFIED**
- **Evidence Paths**: `Graphify/FOLDER_OWNERSHIP_MAP.md`, `codebase/main/features/`, `codebase/renderer/features/`, `Graphify/REPOSITORY_INVENTORY.md`
- **Evidence Explanation**: All codebase and durable repository directories are self-describing, human-readable, and domain-oriented. Data files use clear folder hierarchies rather than opaque hash trees.
- **Affected Capability IDs**: `CAP-REPOSITORY`, `CAP-DATA-SAFETY`
- **Affected Implementation Task IDs**: `TASK-CAP-REPOSITORY`, `TASK-CAP-DATA-SAFETY`
- **Missing Implementation**: None
- **Queue Change Required**: NO
- **Master Plan Conflict**: NONE
- **Task 2 Affected**: NO

### UAC-08 — SMALL-MODEL NAVIGABILITY
- **Status**: **SATISFIED**
- **Evidence Paths**: `Graphify/MASTER_REQUIREMENT_REGISTER.json`, `Graphify/CAPABILITY_REGISTRY.json`, `Graphify/EXACT_LOCATION_REGISTRY.json`, `Graphify/IMPLEMENTATION_QUEUE.json`
- **Evidence Explanation**: The repository and planning architecture provide canonical IDs (REQ-*, CAP-*, TASK-*, LOC-*), deterministic cross-references, exact symbol mappings, and bounded scopes so that a 1B-class local model can accurately navigate without speculative guessing.
- **Affected Capability IDs**: `CAP-PLANNING-GOVERNANCE`, `CAP-EXACT-LOCATION`
- **Affected Implementation Task IDs**: `TASK-CAP-PLANNING-GOVERNANCE`, `TASK-CAP-EXACT-LOCATION`
- **Missing Implementation**: None
- **Queue Change Required**: NO
- **Master Plan Conflict**: NONE
- **Task 2 Affected**: NO

### UAC-09 — DETERMINISTIC NON-AI CORE
- **Status**: **SATISFIED**
- **Evidence Paths**: `codebase/main/infrastructure/persistence/database.js`, `codebase/main/features/transcription/whisper.js`, `Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md`
- **Evidence Explanation**: Core persistence, audio capture, state management, hotkeys, and indexing are 100% deterministic code. Speech recognition uses deterministic local Whisper inference (acoustic models only). Generative AI and cloud LLMs are explicitly forbidden from the release.
- **Affected Capability IDs**: `CAP-DATABASE`, `CAP-TRANSCRIPTION`, `CAP-REMOVE-LOCAL-GENERATIVE-AI`
- **Affected Implementation Task IDs**: `TASK-CAP-DATABASE`, `TASK-CAP-TRANSCRIPTION`, `TASK-DEL-LOCAL-GENERATIVE-AI`
- **Missing Implementation**: None
- **Queue Change Required**: NO
- **Master Plan Conflict**: NONE
- **Task 2 Affected**: NO

### UAC-10 — AUTHORIZED MUTATION MODEL
- **Status**: **SATISFIED**
- **Evidence Paths**: `Graphify/IMPLEMENTATION_QUEUE.json`, `Graphify/tools/execution_state.py`, `Graphify/tools/semantic_validator.py`
- **Evidence Explanation**: Codebase mutations are strictly bounded by single-task execution contracts enforcing files_expected_to_change and files_forbidden_from_changing. Application data mutations occur strictly through validated UI and IPC handlers. Arbitrary filesystem mutations are blocked.
- **Affected Capability IDs**: `CAP-IMPLEMENTATION-GOVERNANCE`, `CAP-DATA-SAFETY`
- **Affected Implementation Task IDs**: `TASK-CAP-IMPLEMENTATION-GOVERNANCE`, `TASK-CAP-DATA-SAFETY`
- **Missing Implementation**: None
- **Queue Change Required**: NO
- **Master Plan Conflict**: NONE
- **Task 2 Affected**: NO

### UAC-11 — MUTATION AUDIT LOG / CHANGE FLAGGING
- **Status**: **MISSING**
- **Evidence Paths**: `codebase/main/infrastructure/persistence/database.js`, `codebase/main/infrastructure/persistence/migrations/001_initial_schema.js`
- **Evidence Explanation**: Mnemora currently has application debug logs (electron-log/console), but does NOT have an append-oriented entity mutation audit log recording actor, operation, timestamp, previous hash, resulting hash, and reason. External/unrecognized changes to database or audio files are not detected, flagged, or reconciled.
- **Affected Capability IDs**: `CAP-DATA-SAFETY`, `CAP-DATABASE`, `CAP-MUTATION-LOG`
- **Affected Implementation Task IDs**: `TASK-CAP-DATA-SAFETY`, `TASK-CAP-MUTATION-LOG`
- **Missing Implementation**: Append-oriented mutation audit table/log, file-watcher / hash-check for external modification detection, and conflict reconciliation workflows (inspect diff, keep external, accept app, restore, reject).
- **Queue Change Required**: YES
- **Master Plan Conflict**: NONE
- **Task 2 Affected**: YES

### UAC-12 — RECOVERABILITY OVER MAGIC
- **Status**: **PARTIAL**
- **Evidence Paths**: `codebase/main/features/meetings/recordingRecovery.js`, `codebase/main/infrastructure/persistence/localBackup.js`, `codebase/main/infrastructure/persistence/dataMigration.js`
- **Evidence Explanation**: Recording recovery manager exists for interrupted audio. Migration and backup scripts exist in donor code. However, comprehensive transactional copy-before-transform, verified restore, and crash-interruption recovery are scheduled for implementation under TASK-CAP-DATA-SAFETY (which is NOT STARTED).
- **Affected Capability IDs**: `CAP-DATA-SAFETY`, `CAP-BACKUP`, `CAP-RESTORE`, `CAP-RECOVERY`
- **Affected Implementation Task IDs**: `TASK-CAP-DATA-SAFETY`, `TASK-CAP-BACKUP`, `TASK-CAP-RESTORE`, `TASK-CAP-RECOVERY`
- **Missing Implementation**: Implementation of verified copy-before-transform harness in Task 2.
- **Queue Change Required**: NO
- **Master Plan Conflict**: NONE
- **Task 2 Affected**: YES

### UAC-13 — ORIGINALS VS DERIVED STATE
- **Status**: **PARTIAL**
- **Evidence Paths**: `codebase/main/features/search/vectorIndex.js`, `codebase/main/features/notes/markdownMirror.js`, `codebase/main/infrastructure/persistence/database.js`
- **Evidence Explanation**: Architecture separates raw audio and notes from derived embeddings and search indexes. Full proof that vector indexes can be cleanly reconstructed from scratch without data loss is scheduled in TASK-CAP-SEARCH-SEMANTIC.
- **Affected Capability IDs**: `CAP-DATA-SAFETY`, `CAP-SEARCH-SEMANTIC`, `CAP-NOTES`
- **Affected Implementation Task IDs**: `TASK-CAP-DATA-SAFETY`, `TASK-CAP-SEARCH-SEMANTIC`, `TASK-CAP-NOTES`
- **Missing Implementation**: Index rebuild verification from raw notes and transcripts without data loss.
- **Queue Change Required**: NO
- **Master Plan Conflict**: NONE
- **Task 2 Affected**: NO

### UAC-14 — DATABASE / SQLITE SAFETY
- **Status**: **PARTIAL**
- **Evidence Paths**: `codebase/main/infrastructure/persistence/database.js`, `codebase/main/infrastructure/persistence/migrations/001_initial_schema.js`, `codebase/main/features/notes/markdownMirror.js`
- **Evidence Explanation**: SQLite is explicitly retained via Kysely and better-sqlite3. Schema migrations are forward-only. Notes have a Markdown mirror. However, database backup verification, integrity check PRAGMAs, and safe restore harnesses are currently unimplemented pending Task 2.
- **Affected Capability IDs**: `CAP-DATABASE`, `CAP-DATA-SAFETY`, `CAP-BACKUP`, `CAP-RESTORE`, `CAP-KYSELY`
- **Affected Implementation Task IDs**: `TASK-CAP-DATA-SAFETY`, `TASK-CAP-DATABASE`, `TASK-DEC-KYSELY`
- **Missing Implementation**: Verification of complete backups, schema dump exports, and PRAGMA integrity_check.
- **Queue Change Required**: NO
- **Master Plan Conflict**: NONE
- **Task 2 Affected**: YES

### UAC-15 — SOURCE / PRIVATE DATA / GIT SEPARATION
- **Status**: **SATISFIED**
- **Evidence Paths**: `.gitignore`, `Graphify/tools/semantic_validator.py`
- **Evidence Explanation**: Strict .gitignore rules prevent SQLite files, WAL files, private recordings, logs, .env, and build outputs from entering Git. SEM-044 actively validates that no tracked private data files or secrets exist in the git index.
- **Affected Capability IDs**: `CAP-IMPLEMENTATION-GOVERNANCE`, `CAP-DATA-SAFETY`
- **Affected Implementation Task IDs**: `TASK-GOV-001-PROVENANCE-BASELINE`, `TASK-CAP-IMPLEMENTATION-GOVERNANCE`
- **Missing Implementation**: None
- **Queue Change Required**: NO
- **Master Plan Conflict**: NONE
- **Task 2 Affected**: NO

### UAC-16 — REPRODUCIBLE BUILDS
- **Status**: **PARTIAL**
- **Evidence Paths**: `codebase/package.json`, `codebase/package-lock.json`, `codebase/electron-builder.json`
- **Evidence Explanation**: Package dependencies are pinned with package-lock.json. Packaging configuration is defined in electron-builder.json. However, fully offline reproducible native compilation and packaging have not yet been executed or proven on this repository.
- **Affected Capability IDs**: `CAP-PACKAGING`, `CAP-WINDOWS-INSTALLER`, `CAP-PORTABLE-WINDOWS`
- **Affected Implementation Task IDs**: `TASK-CAP-PACKAGING`, `TASK-CAP-WINDOWS-INSTALLER`, `TASK-DEC-PORTABLE-WINDOWS`
- **Missing Implementation**: Packaging pipeline execution and artifact verification under Phase 6 packaging tasks.
- **Queue Change Required**: NO
- **Master Plan Conflict**: NONE
- **Task 2 Affected**: NO

### UAC-17 — THIRD-PARTY / DONOR PROVENANCE
- **Status**: **PARTIAL**
- **Evidence Paths**: `codebase/LICENSE`, `Graphify/THIRD_PARTY_CODE_REGISTER.md`
- **Evidence Explanation**: Historical OpenWhispr MIT license and copyright notice are preserved in codebase/LICENSE. All top-level packages are catalogued in Graphify/THIRD_PARTY_CODE_REGISTER.md. Verification of bundled binary licenses (Whisper, FFmpeg, ONNX, Qdrant) is scheduled under TASK-CAP-THIRD-PARTY and TASK-CAP-LEGAL.
- **Affected Capability IDs**: `CAP-LEGAL`, `CAP-THIRD-PARTY`
- **Affected Implementation Task IDs**: `TASK-CAP-LEGAL`, `TASK-CAP-THIRD-PARTY`
- **Missing Implementation**: Execution of binary license verification tasks.
- **Queue Change Required**: NO
- **Master Plan Conflict**: NONE
- **Task 2 Affected**: NO

### UAC-18 — FAIL CLOSED
- **Status**: **PARTIAL**
- **Evidence Paths**: `codebase/main/infrastructure/runtime/runtimeNetworkPolicy.js`, `Graphify/tools/execution_state.py`
- **Evidence Explanation**: Governance tools fail closed on any ambiguity (blocking execution). Network policy blocks unauthorized egress. However, runtime data safety handlers in application code need verification in Task 2 to ensure corrupt databases or failed writes fail closed without silent data loss.
- **Affected Capability IDs**: `CAP-DATA-SAFETY`, `CAP-NETWORK-POLICY`
- **Affected Implementation Task IDs**: `TASK-CAP-DATA-SAFETY`, `TASK-CAP-NETWORK-POLICY`
- **Missing Implementation**: Fail-closed error boundaries in Task 2.
- **Queue Change Required**: NO
- **Master Plan Conflict**: NONE
- **Task 2 Affected**: YES

### UAC-19 — UI / AI / PROVIDER REPLACEABILITY
- **Status**: **SATISFIED**
- **Evidence Paths**: `codebase/main/features/transcription/whisper.js`, `codebase/main/features/search/vectorIndex.js`, `codebase/main/infrastructure/persistence/database.js`
- **Evidence Explanation**: Domain logic and user data (SQLite, WAV audio, Markdown notes) are fully decoupled from UI frameworks and specific models. Transcription engines can be swapped without touching stored notes or audio archives.
- **Affected Capability IDs**: `CAP-APP-SHELL`, `CAP-TRANSCRIPTION`, `CAP-SEARCH-SEMANTIC`
- **Affected Implementation Task IDs**: `TASK-CAP-APP-SHELL`, `TASK-CAP-TRANSCRIPTION`, `TASK-CAP-SEARCH-SEMANTIC`
- **Missing Implementation**: None
- **Queue Change Required**: NO
- **Master Plan Conflict**: NONE
- **Task 2 Affected**: NO

### UAC-20 — SCHEMA / VERSION SAFETY
- **Status**: **PARTIAL**
- **Evidence Paths**: `codebase/main/infrastructure/persistence/database.js`, `codebase/main/infrastructure/persistence/migrations/001_initial_schema.js`
- **Evidence Explanation**: Schema migrations use version numbers. Forward migrations are preserved. However, safe fail-closed behavior when encountering unsupported newer schemas (e.g. read-only safe mode or graceful rejection) is scheduled for implementation in TASK-CAP-DATA-SAFETY.
- **Affected Capability IDs**: `CAP-DATA-SAFETY`, `CAP-DATABASE`, `CAP-LEGACY-MIGRATION`
- **Affected Implementation Task IDs**: `TASK-CAP-DATA-SAFETY`, `TASK-CAP-DATABASE`, `TASK-CAP-LEGACY-MIGRATION`
- **Missing Implementation**: Newer-schema rejection test in Task 2.
- **Queue Change Required**: NO
- **Master Plan Conflict**: NONE
- **Task 2 Affected**: YES

### UAC-21 — STABLE IDS / PORTABLE REFERENCES
- **Status**: **PARTIAL**
- **Evidence Paths**: `codebase/main/infrastructure/persistence/database.js`, `Graphify/MASTER_REQUIREMENT_REGISTER.json`
- **Evidence Explanation**: Entities use stable IDs. However, current SQLite persistence stores absolute machine file paths for audio recordings. These must be replaced with portable relative references relative to the data root.
- **Affected Capability IDs**: `CAP-DATABASE`, `CAP-DATA-SAFETY`, `CAP-NOTES`
- **Affected Implementation Task IDs**: `TASK-CAP-DATA-SAFETY`, `TASK-CAP-DATABASE`, `TASK-CAP-NOTES`
- **Missing Implementation**: Migration of absolute paths to portable relative references.
- **Queue Change Required**: YES
- **Master Plan Conflict**: NONE
- **Task 2 Affected**: YES

### UAC-22 — SELF-DESCRIBING PROJECT CONTRACT
- **Status**: **SATISFIED**
- **Evidence Paths**: `Graphify/CAPABILITY_REGISTRY.json`, `Graphify/IMPLEMENTATION_QUEUE.json`, `Graphify/START-HERE.md`, `Graphify/REPOSITORY_FILE_INVENTORY.json`
- **Evidence Explanation**: Graphify contains machine-readable contracts describing all entities, schemas, versions, allowed mutations, dependencies, and validation methods without relying on undocumented conversation history.
- **Affected Capability IDs**: `CAP-PLANNING-GOVERNANCE`, `CAP-IMPLEMENTATION-GOVERNANCE`
- **Affected Implementation Task IDs**: `TASK-CAP-PLANNING-GOVERNANCE`, `TASK-CAP-IMPLEMENTATION-GOVERNANCE`
- **Missing Implementation**: None
- **Queue Change Required**: NO
- **Master Plan Conflict**: NONE
- **Task 2 Affected**: NO

---

## High-Risk Rules and Architecture Analysis

### UAC-01: Application Independence
Mnemora runtime codebase has zero dependencies on Hermes, Graphify, or external orchestration systems. Core desktop functions (recording, Whisper speech-to-text, SQLite persistence, note editing, exact search) run locally and deterministically. `TASK-CAP-OFFLINE-FIRST-LAUNCH` provides verifiable end-to-end launch verification under complete network isolation.

### UAC-03 & UAC-21: User-Selected Data Root & Portable Relative References
Current code hardcodes `app.getPath('userData')` and stores machine-specific absolute paths for audio recordings in the database. `TASK-CAP-DATA-SAFETY` is minimally extended to characterize data root boundary portability, ensure no absolute path lock-in, and mandate portable relative paths across folder moves.

### UAC-04: NAS / Private-LAN Support
Direct SQLite operation over network shares (SMB/NFS) carries severe risks of file lock collisions, latency-induced timeouts, and journal corruption. Rather than guessing or assuming direct network SQLite safety, decision package `DEC-NAS` (`TASK-DEC-NAS`, `TASK-OUT-NAS-DEFAULT`, `TASK-OUT-NAS-DEVIATION`) explicitly evaluates the choice between a local working SQLite database with continuous NAS replication/archival (default) versus direct network SQLite (deviation if proven).

### UAC-05: Cross-Platform Support
Source code for macOS and Linux native helpers is preserved in `codebase/native/helpers/`. Initial release proof is strictly Windows-first (`CAP-WINDOWS-INSTALLER`, `CAP-PORTABLE-WINDOWS`). The status is honestly audited as `PARTIAL` pending future cross-platform packaging verification.

### UAC-06: Feature-First Modular Monolith
Codebase contains `main/features/` and `renderer/features/`, but also generic dumping grounds (`main/infrastructure/`, `renderer/shared/utils/`). Audit confirms incremental retirement of generic dumping grounds into feature directories is scheduled across Phase 6 tasks without disruptive big-bang rewrites.

### UAC-11: Mutation Audit Log & External-Change Detection
Mnemora currently lacks an append-oriented entity mutation audit log and external modification detection. Capability `CAP-MUTATION-LOG` (`TASK-CAP-MUTATION-LOG`) is scheduled in Phase 5 to provide attributable mutation logging and file-watcher change detection with reconciliation workflows.

## Task 2 Disposition
Task-2 WIP remains safely preserved on recovery branch `recovery/task-cap-data-safety-blocked` (checkpoint `7932d83b3f49604f3b36b7a5966a72138a6c9323`). Canonical task disposition on `main` remains `NOT STARTED`. Its contract is extended with necessary data root, NAS safety, and external change characterization requirements before implementation resumes.
