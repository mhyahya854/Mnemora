# Universal App Constitution Audit: Mnemora

## Audit Overview

- **Subject**: Mnemora Desktop Dictation & Knowledge Management
- **Auditor**: Architecture & Implementation Governance
- **Authority**: `Graphify/UNIVERSAL_APP_CONSTITUTION.md` and `Graphify/UNIVERSAL_APP_CONSTITUTION.json`
- **Master Plan Baseline**:
  - `Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md` (`BDF185A823422BCAA9BFEBA815A6852D8F7A5CD46B64714B2CD1DE3357A67F64`)
  - `Master Plan/02-EVERYTHING-WE-ARE-DELETING.md` (`76B6EEC15778B1928F2CD9C0F73FA68C9F3363493062E31E0C904E620DE0AAC3`)
  - `Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-REPLACE.md` (`5E076498731C35ACF314904AAB3A39671F7026A166B5E847EFE3CCD4CF07304E`)
- **Governance Correction Record**:
  - Governance commit `6a9858a060ea7676363731e86950be1273f99d18` adopted an incomplete 10-article version (Articles A through J).
  - The prior audit concluded `PASS — FULLY COMPLIANT; ZERO MASTER PLAN CONFLICTS` without evaluating the complete 22-principle Constitution.
  - This correction expands the authority to the full 22-rule binding Constitution (`UAC-01` through `UAC-22`).
  - The prior PASS cannot be used as evidence of UAC-01..UAC-22 compliance.
- **Audit Verdict**: **22 RULES EVALUATED — PLANNING RECONCILED; ZERO MASTER PLAN CONFLICTS**
  - Satisfied: 8 rules
  - Partial (in planning / pending tasks): 12 rules
  - Missing (queue coverage added): 2 rules (`UAC-04`, `UAC-11`)
  - Conflicts: 0
  - Not Applicable: 0

---

## Evaluation of All 22 Binding Rules

### UAC-01: APPLICATION INDEPENDENCE
- **Status**: **SATISFIED**
- **Evidence**: `codebase/main/index.js`, `codebase/package.json`, `codebase/tests/integration/offlineFirstLaunch.test.js`, `Graphify/tools/semantic_validator.py`
- **Finding**: Runtime codebase does not import, require, or depend on Hermes, Graphify, or external orchestrators. Core operations (audio capture, transcription, database persistence, search, backup, restore, UI) are local Node.js/Electron/SQLite code. SEM-044 validator checks ban hermes and Graphify imports across all tracked codebase files.

### UAC-02: LOCAL-FIRST / OFFLINE-FIRST
- **Status**: **PARTIAL**
- **Evidence**: `codebase/main/infrastructure/runtime/runtimeNetworkPolicy.js`, `codebase/main/features/transcription/whisper.js`, `Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md`, `Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md`
- **Finding**: Master Plans mandate 100% offline execution and loopback-only binding (127.0.0.1). However, in the current donor codebase baseline (prior to executing Phase 4 deletion tasks), dormant cloud synchronization, remote auth, and telemetry remnants remain in codebase/ pending deletion under BDI interlocks.
- **Implementation Plan**: Covered by `TASK-CAP-NETWORK-POLICY`, `TASK-CAP-OFFLINE-FIRST-LAUNCH`, `TASK-DEL-CLOUD-SYNCHRONISATION`, `TASK-DEL-RUNTIME-EXTERNAL-NETWORKING`, `TASK-DEL-AUTHENTICATION`.

### UAC-03: USER-SELECTED DATA ROOT SOVEREIGNTY
- **Status**: **PARTIAL**
- **Evidence**: `codebase/main/infrastructure/persistence/database.js`, `codebase/main/index.js`, `codebase/main/features/settings/settingsManager.js`
- **Finding**: User data is currently anchored to Electron default app.getPath('userData'). There is no mechanism for the user to select or move a custom application data root without data meaning loss. SQLite tables also record absolute paths rather than root-relative portable paths.
- **Implementation Plan**: Covered by `TASK-CAP-DATA-SAFETY`, `TASK-CAP-DATABASE`, `TASK-CAP-SETTINGS`.

### UAC-04: NAS / PRIVATE-LAN SUPPORT
- **Status**: **MISSING**
- **Evidence**: `codebase/main/infrastructure/persistence/database.js`, `codebase/main/infrastructure/persistence/localBackup.js`, `Graphify/CONDITIONAL_DECISION_PACKAGES.json`
- **Finding**: Current implementation has zero handling for network shares / NAS data roots. SQLite is known to suffer locking failures, latency timeouts, and corruption over network filesystems (SMB/NFS). Share unavailability, reconnection, latency, interrupted writes, and multi-instance concurrency on network drives are completely unaddressed in current code.
- **Implementation Plan**: Covered by `TASK-CAP-DATA-SAFETY`, `TASK-DEC-NAS`, `TASK-OUT-NAS-DEFAULT`, `TASK-OUT-NAS-DEVIATION`.

### UAC-05: CROSS-PLATFORM SUPPORT
- **Status**: **PARTIAL**
- **Evidence**: `codebase/native/helpers/macos/mac_meeting_audio_tap.swift`, `codebase/native/helpers/linux/audio_portal_monitor.py`, `codebase/electron-builder.json`, `Graphify/CONDITIONAL_DECISION_PACKAGES.json`
- **Finding**: Donor macOS and Linux helper source code is preserved in codebase/native/helpers/ under CAP-MACOS-LINUX and DEC-MACOS-LINUX. However, Mnemora first-release milestone is explicitly Windows-first (CAP-WINDOWS-INSTALLER, CAP-PORTABLE-WINDOWS). Cross-platform runtime execution, platform-specific hotkeys, and packaging have not been tested or proven on macOS or Linux.
- **Implementation Plan**: Covered by `TASK-DEC-MACOS-LINUX`, `TASK-OUT-MACOS-LINUX-DEFAULT`, `TASK-OUT-MACOS-LINUX-DEVIATION`, `TASK-CAP-WINDOWS-INSTALLER`.

### UAC-06: FEATURE-FIRST MODULAR MONOLITH
- **Status**: **PARTIAL**
- **Evidence**: `codebase/main/features/dictation/`, `codebase/renderer/features/notes/`, `codebase/main/infrastructure/`, `codebase/renderer/shared/`
- **Finding**: The codebase partially uses a feature-first structure with main/features/ and renderer/features/. However, generic dumping grounds still exist (codebase/main/infrastructure/, codebase/renderer/shared/utils/, etc.) containing mixed responsibilities across features.
- **Implementation Plan**: Covered by `TASK-CAP-REPOSITORY`, `TASK-CAP-SIMPLIFICATION`.

### UAC-07: HUMAN-READABLE FOLDER CONTRACT
- **Status**: **SATISFIED**
- **Evidence**: `Graphify/FOLDER_OWNERSHIP_MAP.md`, `codebase/main/features/`, `codebase/renderer/features/`, `Graphify/REPOSITORY_INVENTORY.md`
- **Finding**: All codebase and durable repository directories are self-describing, human-readable, and domain-oriented. Data files use clear folder hierarchies rather than opaque hash trees.

### UAC-08: SMALL-MODEL NAVIGABILITY
- **Status**: **SATISFIED**
- **Evidence**: `Graphify/MASTER_REQUIREMENT_REGISTER.json`, `Graphify/CAPABILITY_REGISTRY.json`, `Graphify/EXACT_LOCATION_REGISTRY.json`, `Graphify/IMPLEMENTATION_QUEUE.json`
- **Finding**: The repository and planning architecture provide canonical IDs (REQ-*, CAP-*, TASK-*, LOC-*), deterministic cross-references, exact symbol mappings, and bounded scopes so that a 1B-class local model can accurately navigate without speculative guessing.

### UAC-09: DETERMINISTIC NON-AI CORE
- **Status**: **SATISFIED**
- **Evidence**: `codebase/main/infrastructure/persistence/database.js`, `codebase/main/features/transcription/whisper.js`, `Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md`
- **Finding**: Core persistence, audio capture, state management, hotkeys, and indexing are 100% deterministic code. Speech recognition uses deterministic local Whisper inference (acoustic models only). Generative AI and cloud LLMs are explicitly forbidden from the release.

### UAC-10: AUTHORIZED MUTATION MODEL
- **Status**: **SATISFIED**
- **Evidence**: `Graphify/IMPLEMENTATION_QUEUE.json`, `Graphify/tools/execution_state.py`, `Graphify/tools/semantic_validator.py`
- **Finding**: Codebase mutations are strictly bounded by single-task execution contracts enforcing files_expected_to_change and files_forbidden_from_changing. Application data mutations occur strictly through validated UI and IPC handlers. Arbitrary filesystem mutations are blocked.

### UAC-11: MUTATION AUDIT LOG / CHANGE FLAGGING
- **Status**: **MISSING**
- **Evidence**: `codebase/main/infrastructure/persistence/database.js`, `codebase/main/infrastructure/persistence/migrations/001_initial_schema.js`
- **Finding**: Mnemora currently has application debug logs (electron-log/console), but does NOT have an append-oriented entity mutation audit log recording actor, operation, timestamp, previous hash, resulting hash, and reason. External/unrecognized changes to database or audio files are not detected, flagged, or reconciled.
- **Implementation Plan**: Covered by `TASK-CAP-DATA-SAFETY`, `TASK-CAP-MUTATION-LOG`.

### UAC-12: RECOVERABILITY OVER MAGIC
- **Status**: **PARTIAL**
- **Evidence**: `codebase/main/features/meetings/recordingRecovery.js`, `codebase/main/infrastructure/persistence/localBackup.js`, `codebase/main/infrastructure/persistence/dataMigration.js`
- **Finding**: Recording recovery manager exists for interrupted audio. Migration and backup scripts exist in donor code. However, comprehensive transactional copy-before-transform, verified restore, and crash-interruption recovery are scheduled for implementation under TASK-CAP-DATA-SAFETY (which is NOT STARTED).
- **Implementation Plan**: Covered by `TASK-CAP-DATA-SAFETY`, `TASK-CAP-BACKUP`, `TASK-CAP-RESTORE`, `TASK-CAP-RECOVERY`.

### UAC-13: ORIGINALS VS DERIVED STATE
- **Status**: **PARTIAL**
- **Evidence**: `codebase/main/features/search/vectorIndex.js`, `codebase/main/features/notes/markdownMirror.js`, `codebase/main/infrastructure/persistence/database.js`
- **Finding**: Architecture separates raw audio and notes from derived embeddings and search indexes. Full proof that vector indexes can be cleanly reconstructed from scratch without data loss is scheduled in TASK-CAP-SEARCH-SEMANTIC.
- **Implementation Plan**: Covered by `TASK-CAP-DATA-SAFETY`, `TASK-CAP-SEARCH-SEMANTIC`, `TASK-CAP-NOTES`.

### UAC-14: DATABASE / SQLITE SAFETY
- **Status**: **PARTIAL**
- **Evidence**: `codebase/main/infrastructure/persistence/database.js`, `codebase/main/infrastructure/persistence/migrations/001_initial_schema.js`, `codebase/main/features/notes/markdownMirror.js`
- **Finding**: SQLite is explicitly retained via Kysely and better-sqlite3. Schema migrations are forward-only. Notes have a Markdown mirror. However, database backup verification, integrity check PRAGMAs, and safe restore harnesses are currently unimplemented pending Task 2.
- **Implementation Plan**: Covered by `TASK-CAP-DATA-SAFETY`, `TASK-CAP-DATABASE`, `TASK-DEC-KYSELY`.

### UAC-15: SOURCE / PRIVATE DATA / GIT SEPARATION
- **Status**: **SATISFIED**
- **Evidence**: `.gitignore`, `Graphify/tools/semantic_validator.py`
- **Finding**: Strict .gitignore rules prevent SQLite files, WAL files, private recordings, logs, .env, and build outputs from entering Git. SEM-044 actively validates that no tracked private data files or secrets exist in the git index.

### UAC-16: REPRODUCIBLE BUILDS
- **Status**: **PARTIAL**
- **Evidence**: `codebase/package.json`, `codebase/package-lock.json`, `codebase/electron-builder.json`
- **Finding**: Package dependencies are pinned with package-lock.json. Packaging configuration is defined in electron-builder.json. However, fully offline reproducible native compilation and packaging have not yet been executed or proven on this repository.
- **Implementation Plan**: Covered by `TASK-CAP-PACKAGING`, `TASK-CAP-WINDOWS-INSTALLER`, `TASK-DEC-PORTABLE-WINDOWS`.

### UAC-17: THIRD-PARTY / DONOR PROVENANCE
- **Status**: **PARTIAL**
- **Evidence**: `codebase/LICENSE`, `Graphify/THIRD_PARTY_CODE_REGISTER.md`
- **Finding**: Historical OpenWhispr MIT license and copyright notice are preserved in codebase/LICENSE. All top-level packages are catalogued in Graphify/THIRD_PARTY_CODE_REGISTER.md. Verification of bundled binary licenses (Whisper, FFmpeg, ONNX, Qdrant) is scheduled under TASK-CAP-THIRD-PARTY and TASK-CAP-LEGAL.
- **Implementation Plan**: Covered by `TASK-CAP-LEGAL`, `TASK-CAP-THIRD-PARTY`.

### UAC-18: FAIL CLOSED
- **Status**: **PARTIAL**
- **Evidence**: `codebase/main/infrastructure/runtime/runtimeNetworkPolicy.js`, `Graphify/tools/execution_state.py`
- **Finding**: Governance tools fail closed on any ambiguity (blocking execution). Network policy blocks unauthorized egress. However, runtime data safety handlers in application code need verification in Task 2 to ensure corrupt databases or failed writes fail closed without silent data loss.
- **Implementation Plan**: Covered by `TASK-CAP-DATA-SAFETY`, `TASK-CAP-NETWORK-POLICY`.

### UAC-19: UI / AI / PROVIDER REPLACEABILITY
- **Status**: **SATISFIED**
- **Evidence**: `codebase/main/features/transcription/whisper.js`, `codebase/main/features/search/vectorIndex.js`, `codebase/main/infrastructure/persistence/database.js`
- **Finding**: Domain logic and user data (SQLite, WAV audio, Markdown notes) are fully decoupled from UI frameworks and specific models. Transcription engines can be swapped without touching stored notes or audio archives.

### UAC-20: SCHEMA / VERSION SAFETY
- **Status**: **PARTIAL**
- **Evidence**: `codebase/main/infrastructure/persistence/database.js`, `codebase/main/infrastructure/persistence/migrations/001_initial_schema.js`
- **Finding**: Schema migrations use version numbers. Forward migrations are preserved. However, safe fail-closed behavior when encountering unsupported newer schemas (e.g. read-only safe mode or graceful rejection) is scheduled for implementation in TASK-CAP-DATA-SAFETY.
- **Implementation Plan**: Covered by `TASK-CAP-DATA-SAFETY`, `TASK-CAP-DATABASE`, `TASK-CAP-LEGACY-MIGRATION`.

### UAC-21: STABLE IDS / PORTABLE REFERENCES
- **Status**: **PARTIAL**
- **Evidence**: `codebase/main/infrastructure/persistence/database.js`, `Graphify/MASTER_REQUIREMENT_REGISTER.json`
- **Finding**: Entities use stable IDs. However, current SQLite persistence stores absolute machine file paths for audio recordings. These must be replaced with portable relative references relative to the data root.
- **Implementation Plan**: Covered by `TASK-CAP-DATA-SAFETY`, `TASK-CAP-DATABASE`, `TASK-CAP-NOTES`.

### UAC-22: SELF-DESCRIBING PROJECT CONTRACT
- **Status**: **SATISFIED**
- **Evidence**: `Graphify/CAPABILITY_REGISTRY.json`, `Graphify/IMPLEMENTATION_QUEUE.json`, `Graphify/START-HERE.md`, `Graphify/REPOSITORY_FILE_INVENTORY.json`
- **Finding**: Graphify contains machine-readable contracts describing all entities, schemas, versions, allowed mutations, dependencies, and validation methods without relying on undocumented conversation history.

---

## High-Risk Rules Reconciliation

### UAC-01: Hermes / Application Independence
Verified: Zero imports of `hermes` or `Graphify` exist in codebase. Core desktop functions run independently offline. Status: **SATISFIED**.

### UAC-03: User-Selected Portable Data Root
Verified: Electron default user data path used currently. Queue coverage extended under `TASK-CAP-DATA-SAFETY` and `TASK-CAP-SETTINGS`. Status: **PARTIAL**.

### UAC-04: NAS / Private-LAN Support
Verified: Direct SQLite on network shares is unproven and unsafe without locking protection. Conditional decision package `DEC-NAS` (`TASK-DEC-NAS`, `TASK-OUT-NAS-DEFAULT`, `TASK-OUT-NAS-DEVIATION`) added to queue. Status: **MISSING (QUEUE COVERAGE ADDED)**.

### UAC-05: Cross-Platform Support
Verified: macOS/Linux helper sources preserved; initial release focused on Windows proof. Status: **PARTIAL**.

### UAC-06: Feature-First Modular Monolith
Verified: Feature directories exist; generic dumping ground retirement scheduled under Phase 6 tasks. Status: **PARTIAL**.

### UAC-11: Mutation Audit Log & External-Change Detection
Verified: Append-oriented mutation log and change flagging missing in current codebase. Capability `CAP-MUTATION-LOG` (`TASK-CAP-MUTATION-LOG`) added to queue. Status: **MISSING (QUEUE COVERAGE ADDED)**.

### UAC-14: SQLite / Data Transparency
Verified: SQLite retained via Kysely and better-sqlite3; data safety harness in Task 2. Status: **PARTIAL**.

### UAC-15: Source / Private Data / Git Separation
Verified: .gitignore and SEM-044 enforce clean git index without user data or secrets. Status: **SATISFIED**.

### UAC-16: Reproducible Builds
Verified: package-lock.json and electron-builder.json pin build configuration; packaging tasks in Phase 6. Status: **PARTIAL**.

### UAC-17: Third-Party Provenance
Verified: Historical MIT license preserved in codebase/LICENSE; third-party register complete. Status: **PARTIAL**.

### UAC-18: Fail Closed
Verified: Task execution state and network policy fail closed; runtime data safety handlers in Task 2. Status: **PARTIAL**.

### UAC-19: UI / AI / Provider Replaceability
Verified: Data layer decoupled from UI and transcription models. Status: **SATISFIED**.

### UAC-20: Schema / Version Safety
Verified: Forward migrations preserved; newer-schema rejection test in Task 2. Status: **PARTIAL**.

### UAC-21: Stable IDs / Portable References
Verified: Stable entity IDs used; relative reference migration scheduled in Task 2. Status: **PARTIAL**.

### UAC-22: Self-Describing Project Contract
Verified: Machine-readable contracts in Graphify/ provide complete project context. Status: **SATISFIED**.

---

## Master Plan Conflict Analysis

- **Master Plan 1** (`Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md`): **ZERO CONFLICTS** (Hash: `BDF185A823422BCAA9BFEBA815A6852D8F7A5CD46B64714B2CD1DE3357A67F64`)
- **Master Plan 2** (`Master Plan/02-EVERYTHING-WE-ARE-DELETING.md`): **ZERO CONFLICTS** (Hash: `76B6EEC15778B1928F2CD9C0F73FA68C9F3363493062E31E0C904E620DE0AAC3`)
- **Master Plan 3** (`Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-REPLACE.md`): **ZERO CONFLICTS** (Hash: `5E076498731C35ACF314904AAB3A39671F7026A166B5E847EFE3CCD4CF07304E`)

All three Master Plans fully align with and reinforce the Universal App Constitution. No Master Plan text requires amendment.

---

## Tool Provenance Reconciliation

The historical citation of Ponytail in Phase 1 planning remains documented in `PONYTAIL_FINDINGS.json`. No runtime Ponytail tool exists or is executed. Task evidence templates require direct runtime tool logging only.
