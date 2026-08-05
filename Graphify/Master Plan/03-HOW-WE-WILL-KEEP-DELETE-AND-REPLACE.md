---
title: "How We Will Keep, Delete, Replace, Reorganise, and Verify"
project: "Mnemora"
status: "AUTHORITATIVE"
updated: "2026-07-28"
document_role: "Master Plan 3 of 3"
---

# Binding Operational Control Block

## 6.1 Correct-file law

- The authoritative execution file is:
  `03-HOW-WE-WILL-KEEP-DELETE-AND-REPLACE.md`
- `DELETE-AND-IMPLEMENT.md` is non-authoritative.
- No implementation model may substitute another similarly named file.

## 6.2 Autonomous execution law

The future implementation model is authorised to:

- Read files
- Map code
- Create Codebase and Graphify
- Move files
- Repair imports
- Repair IPC
- Repair SQLite
- Remove mapped excluded systems
- Install or rebuild required local dependencies
- Run tests
- Build
- Package
- Launch the application
- Repair failures
- Continue through all phases

It must not repeatedly ask permission for ordinary implementation work.

## 6.3 Preservation-first law

- Keep working local code by default.
- Repair before replacing.
- Recover exact upstream code before inventing replacement code.
- Copy licence-compatible code only when necessary.
- Avoid style-only rewrites.
- Avoid parallel permanent implementations.
- Preserve validation, error handling, cleanup, recovery, native behaviour, tests, and data compatibility.

## 6.4 No-data-loss law

Never:

- Delete real user databases
- Delete real recordings
- Delete real notes
- Delete real transcripts
- Delete real exports
- Delete real backups
- Test migrations against the user’s only database
- Overwrite a non-empty Mnemora database
- Delete original OpenWhispr data automatically

## 6.5 No-destructive-Git law

Explicitly forbid active use of:

- `git reset --hard`
- `git clean -fd`
- `git clean -fdx`
- `git checkout .`
- `git checkout <file>`
- `git restore .`
- Any command that discards staged, unstaged, deleted, or untracked user work

Correct mistakes through:

- `git revert <commit>`
- A new corrective commit
- Manual restoration of the specific changed lines or files without disturbing unrelated work

## 6.6 No-false-completion law

The project is not complete merely because:

- Plans exist
- Graphify ran
- Files moved
- Cloud UI disappeared
- Typecheck passed
- Unit tests passed
- Renderer built
- An installer exists
- A completion message was written

Completion requires every applicable gate in the Strict Release Conjunction.

## 6.7 Continue-until-complete law

Continue through:

- Baseline
- Mapping
- Classification
- Removal
- Repair
- Reorganisation
- Implementation
- Real integration testing
- Windows build
- Windows packaging
- Offline first launch
- Final Ponytail audit
- Final Graphify scan
- Final release gate

---

# Git Safety Protocol

## If Git exists

Record:

- Repository root
- Current branch
- Current commit
- Staged changes
- Unstaged changes
- Deleted files
- Untracked files

Preserve all existing work before creating the migration working branch.

Never clean the working tree by deleting untracked files.

## If Git does not exist

Before any code edit, movement, or deletion:

1. Confirm the actual repository root.
2. Inspect whether repository history exists in a parent directory or recoverable metadata.
3. Recover existing provenance where possible.
4. If no recoverable Git history exists, initialise Git.
5. Create a path-specific `.gitignore`.
6. Inspect every path that would be ignored.
7. Confirm required fixtures, models, binaries, migrations, media, and reproducible build assets remain tracked or reproducibly acquired.
8. Commit the untouched baseline.
9. Record the baseline commit hash.
10. Create a migration working branch.

Do not use broad ignore patterns such as:

- `*.db`
- `*.sqlite`
- `*.bin`
- `*.onnx`
- `*.wav`
- `*.mp3`

Use path-specific exclusions based on the real repository, such as:

- `Codebase/node_modules/`
- `Codebase/dist/`
- `Codebase/release/`
- `Codebase/coverage/`
- `Codebase/.cache/`
- `Codebase/runtime-data/`
- `Codebase/temp/`

---

# Mnemora — How We Will Keep, Delete, Replace, Reorganise, and Verify

> **Project identity and scope lock:** Mnemora uses an OpenWhispr-derived architecture. Its retained product scope is Dictation, Meeting recording, Local transcription, SQLite, Notes, Diarization, and Exact and semantic search.

## 1. Purpose

This document defines the autonomous execution method for transforming the original OpenWhispr-derived repository into Mnemora.

It governs:

- How Graphify reads the Master Plan
- How Graphify maps the actual Codebase
- How retained code is protected
- How unwanted systems are proven removable
- How replacements and missing local capabilities are implemented
- How exact code locations and statuses are tracked
- How source code and Markdown planning are separated
- How copied upstream code is integrated
- How tests, builds, packaging, and offline proof run continuously
- How completion is decided using evidence rather than optimistic prose

This is an execution specification. It is not permission to stop after producing another plan.

---

# 2. Final Root Structure

The final project root contains two principal folders:

```text
Mnemora/
├── Codebase/
└── Graphify/
```

## Codebase

`Codebase/` contains the complete runnable application:

- Electron main process
- Preload
- React renderer
- Native helpers
- Models and binaries
- Resources and assets
- Tests and fixtures
- Scripts
- Build configuration
- Packaging and installer resources
- Plain-text legal notices

`Codebase/` contains zero tracked Markdown files.

## Graphify

`Graphify/` contains every plan, map, registry, report, prompt, decision, audit, status file, test record, proof index, completion tracker, and Markdown document.

The runtime application must never depend on Graphify.

---

# 3. Authoritative Master Plan

Graphify must completely read:

```text
Graphify/Master Plan/
├── 01-EVERYTHING-WE-ARE-KEEPING.md
├── 02-EVERYTHING-WE-ARE-DELETING.md
└── 03-HOW-WE-WILL-KEEP-DELETE-AND-REPLACE.md
```

These three files are the highest-level transformation source of truth.

The installed Graphify-compatible AI must not:

- Read only a summary
- Skip long sections
- Replace the plan with a shorter interpretation
- Weaken requirements
- Mark work complete because a file exists
- Trust inherited status without examining code and tests

When documents conflict, use:

1. These three Master Plan files
2. Current explicit user requirements
3. Current authoritative Mnemora plans
4. Current completion tracker
5. Verified behaviour and tests
6. Current implementation
7. Historical reports
8. Assumptions

Graphify maintains an authoritative-source register with original path, new path, purpose, status, scope, conflicts, adopted resolution, and replacement document.

---

# 4. Graphify Scan Process

Graphify uses whichever compatible local AI/model is installed.

Before changing code:

1. Confirm the real repository root
2. Record Git branch, commit, staged changes, unstaged changes, deletions, and untracked files
3. Read repository instructions
4. Read all three Master Plan files
5. Identify package, source, test, native, resource, script, build, packaging, and documentation roots
6. Run baseline verification
7. Run a real deep Graphify scan

Use the actual equivalent of:

```text
/graphify . --mode deep
```

After every meaningful batch:

```text
/graphify . --update
```

Before final approval:

```text
/graphify . --mode deep
```

Graphify data may not be fabricated manually. If Graphify is unavailable or broken, diagnose, repair, install, configure, and rerun it autonomously before recording a genuine external blocker.

---

# 5. What Graphify Must Map

Graphify maps:

- Applications and packages
- Source, test, native, model, resource, build, and packaging roots
- Every source file
- Every exported function
- Every significant internal function
- Classes and methods
- React components
- Hooks and stores
- Services, repositories, adapters, providers
- Commands and native commands
- Renderer calls
- Preload methods
- IPC channels and handlers
- Routes, windows, dialogs, and overlays
- Event handlers
- Workers and background jobs
- Database tables, columns, schemas, migrations, models
- Types, constants, settings, environment variables, feature flags
- Build and packaging scripts
- Assets, models, and binaries
- Tests and fixtures
- Imports, exports, callers, and callees
- Dynamic imports and string-based references
- Runtime registrations
- Platform-specific implementations
- Planned and missing capabilities

For every significant capability or symbol, Graphify determines:

- Where it is defined
- What imports it
- What calls it
- What it calls
- What it reads and writes
- What events it emits and consumes
- Which UI, route, command, or hotkey exposes it
- Which IPC and preload layers connect it
- Which tests cover it
- Which configuration enables it
- Which retained or removed feature depends on it
- What would break if it moved or disappeared

---

# Graphify Operational Structure

## 9.1 Authoritative Master Plan

- `01-EVERYTHING-WE-ARE-KEEPING.md`
- `02-EVERYTHING-WE-ARE-DELETING.md`
- `03-HOW-WE-WILL-KEEP-DELETE-AND-REPLACE.md`

## 9.2 Continuous operational core

Update only after a coherent dependency-safe capability batch:

1. `RUN_STATE.md`
2. `EXACT_LOCATION_REGISTRY.json`
3. `IMPLEMENTATION_QUEUE.md`
4. `COMPLETION_TRACKER.md`

Use `OPEN_BLOCKERS.md` only for a genuinely unresolved blocker.

Do not update administrative files after every one-line edit.

## 9.3 Phase-boundary documents

- `REPOSITORY_INVENTORY.md`
- `CURRENT_ARCHITECTURE.md`
- `TARGET_ARCHITECTURE.md`
- `CAPABILITY_REGISTRY.md`
- `FOLDER_OWNERSHIP_MAP.md`
- `MOVE_LEDGER.md`
- `DELETED_ITEMS_LEDGER.md`
- `THIRD_PARTY_CODE_REGISTER.md`
- `TEST_MATRIX.md`
- `REGRESSION_RESULTS.md`

## 9.4 Final-only or generated documents

- `DEPENDENCY_GRAPH.md`
- `IMPORT_AND_CALL_MAP.md`
- `CIRCULAR_DEPENDENCIES.md`
- `PONYTAIL_AUDIT.md`
- `FINAL_GRAPH_AUDIT.md`
- `FINAL_CODEBASE_MAP.md`
- `FINAL_FOLDER_TREE.md`
- `FINAL_CAPABILITY_MATRIX.md`
- `FINAL_CHANGE_SUMMARY.md`
- `FINAL_HANDOFF.md`

Generated maps must come from Graphify or real static-analysis tools.

They must not be fabricated manually.

## 9.5 Registry authority

`EXACT_LOCATION_REGISTRY.json` is authoritative.

Remove mandatory requirements for:

- `EXACT_LOCATION_REGISTRY.md`
- Duplicate current-to-target mirrors
- Duplicate symbol-ownership mirrors
- Duplicate location queues
- Every previously proposed Graphify report

Human summaries may exist only where they add information not already stored in the JSON registry.

---

# 7. Exact Location and Status Tracking

For each kept, deleted, moved, repaired, replaced, or added item, Graphify requires these fields:

- Stable capability ID
- Capability name
- Entity type
- Decision
- Status
- Current path
- Current symbol or unique anchor
- Current line range as secondary information
- Graphify node ID where available
- Intended target path
- Intended target symbol
- Capability owner
- Module owner
- Dependencies
- Dependents
- Renderer entry point
- Preload exposure
- IPC channel
- IPC handler
- Service
- Database or filesystem effect
- Native dependency
- Runtime registration
- Configuration references
- Tests
- Required changes
- Verification evidence
- Last verified commit or hash checkpoint

Path plus symbol or unique anchor is authoritative.

Line number alone is not authoritative.

Required statuses:

- `NOT STARTED`
- `DISCOVERED`
- `MAPPED`
- `DEPENDENCIES VERIFIED`
- `READY TO KEEP`
- `READY TO MOVE`
- `READY TO DELETE`
- `IN PROGRESS`
- `MOVED`
- `DELETED`
- `REPAIRED`
- `IMPLEMENTED`
- `VERIFICATION REQUIRED`
- `VERIFIED COMPLETE`
- `BLOCKED`
- `OBSOLETE`
- `RELEASE REJECTED`

---

# 8. Capability Ownership and Folder Specificity

Every meaningful item receives one authoritative owner:

- Application
- Package
- File
- Function
- Class
- Component
- Hook
- Store
- Service
- IPC channel
- Worker
- Route
- Event
- Database table
- Migration
- Native helper
- Test
- Asset

This does not mean one folder per trivial function.

It means every function belongs to the narrowest coherent capability module.

A target structure may resemble:

```text
Codebase/
├── src/
│   ├── app/
│   │   ├── bootstrap/
│   │   ├── routing/
│   │   ├── composition/
│   │   ├── windows/
│   │   ├── tray/
│   │   └── network-policy/
│   ├── features/
│   │   ├── dictation/
│   │   ├── meetings/
│   │   ├── recordings/
│   │   ├── transcription/
│   │   ├── diarization/
│   │   ├── speakers/
│   │   ├── playback/
│   │   ├── notes/
│   │   ├── folders/
│   │   ├── tags/
│   │   ├── snippets/
│   │   ├── history/
│   │   ├── exact-search/
│   │   ├── semantic-search/
│   │   ├── media-import/
│   │   ├── export/
│   │   ├── backup-restore/
│   │   ├── model-management/
│   │   ├── onboarding/
│   │   ├── settings/
│   │   └── legacy-data-migration/
│   ├── platform/
│   │   ├── electron/
│   │   ├── audio/
│   │   ├── database/
│   │   ├── sqlite/
│   │   ├── filesystem/
│   │   ├── ffmpeg/
│   │   ├── whisper/
│   │   ├── sherpa-onnx/
│   │   ├── onnx/
│   │   ├── qdrant/
│   │   ├── native/
│   │   └── operating-system/
│   └── shared/
│       ├── ui/
│       ├── validation/
│       ├── errors/
│       ├── logging/
│       ├── types/
│       └── test-support/
├── native/
├── resources/
├── scripts/
├── tests/
├── packaging/
└── configuration/
```

Graphify adapts this to the real framework and dependency graph. It must not fragment code merely to increase folder count.

---

# Monolith Decomposition Procedure

1. Large size alone is not a reason to split.
2. Prove multiple responsibilities exist.
3. Map every exported symbol.
4. Map significant internal symbols.
5. Map static callers.
6. Map dynamic callers.
7. Map runtime registrations.
8. Map renderer, preload, IPC, service, database, filesystem, native, and test relationships.
9. Assign a real capability owner.
10. Add or verify characterisation tests.
11. Extract one dependency-safe capability at a time.
12. Start with low-risk leaf logic.
13. Use a temporary compatibility facade only when required.
14. Never duplicate implementation logic.
15. Migrate callers incrementally.
16. Run targeted checks after each extraction.
17. Run real IPC or persistence integration tests after each capability batch.
18. Remove the compatibility facade when no callers remain.
19. Delete the original monolith only when:
    - No logic remains
    - No exports remain
    - No runtime registrations remain
    - No imports remain
    - No dynamic references remain
20. Prove no duplicate, backup, commented-out, or competing implementation remains.

The work unit is:

`One coherent dependency-safe capability batch`

Do not impose:

`One top-level directory per commit`

---

# Git-or-Hash Batch Checkpoint Rule

Every coherent dependency-safe mutation batch must be recoverable.

## When Git is available

Record:

- Batch ID
- Capability ID
- Starting commit
- Ending commit
- Changed files
- Added files
- Deleted files
- Moved files
- Tests run
- Exit codes
- Verification evidence
- Completion timestamp

Commit the verified batch before starting the next batch.

## When Git is temporarily unavailable but repository provenance is still being recovered

Create a hash-manifest checkpoint containing:

- Batch ID
- Capability ID
- Repository root
- Pre-mutation SHA-256 for every changed file
- Post-mutation SHA-256 for every changed file
- Original path
- Target path
- Mutation type
- Reason
- Dependencies
- Dependents
- Runtime registrations
- Database impact
- Native impact
- Tests selected
- Tests executed
- Exit codes
- Evidence paths
- Failed checks
- Repair actions
- Remaining risks
- Start timestamp
- Completion timestamp
- Model/tool identity
- Last verified repository state

The checkpoint must allow recovery of the pre-mutation state.

Store immutable pre-mutation file copies or a reversible text/binary delta alongside the manifest. Hashes alone verify identity and do not satisfy recoverability.

Do not initialise a new Git repository merely to satisfy the batching rule before provenance-first Git recovery has been attempted.

Once Git is safely established, subsequent batches must use Git commits rather than hash-only checkpoints.

---

# 9. How We Keep Code

Before keeping an implementation, Graphify identifies:

1. Purpose
2. User-facing entry point
3. Callers and consumers
4. Imports and exports
5. Runtime registrations
6. IPC and preload chain
7. Configuration
8. Database and filesystem effects
9. Native dependencies
10. Tests
11. Platform behaviour
12. Cloud or removed-system coupling
13. Blast radius

Classification:

- `KEEP AS-IS`: local, correctly owned, working, tested
- `KEEP AND REORGANISE`: working but misplaced
- `KEEP AFTER DECOUPLING`: local logic mixed with removed architecture
- `KEEP AFTER REPAIR`: required but incomplete or damaged
- `KEEP IF VERIFIED`: apparent value but insufficient evidence
- `KEEP AS OPTIONAL OFFLINE COMPONENT`: useful but not mandatory for default install

No working local implementation is rewritten merely for style.

---

# 10. How We Delete Code

Before deletion, prove:

- No required static import or re-export
- No required caller
- No required dynamic or string-based reference
- No IPC, route, event, command, or DI registration
- No build or packaging reference
- No native load
- No migration or fixture dependency
- No platform-specific use
- No required side effect
- No legal requirement
- No future Master Plan dependency

A text search with zero results is not enough.

Deletion steps:

1. Record candidate and evidence
2. Record replacement or reason no replacement exists
3. Delete implementation
4. Remove imports and exports
5. Remove route/IPC/preload/type chain
6. Remove settings, fields, flags, environment variables, and translations
7. Remove dependency
8. Update or remove obsolete tests
9. Remove empty folders
10. Run targeted checks
11. Run broader checks
12. Test affected workflow
13. Update Graphify
14. Update exact-location and deletion ledgers

---

# 11. How We Replace Removed Systems

| Removed | Replacement |
|---|---|
| Authentication/accounts | Direct local launch |
| Cloud sync | SQLite plus local backup/restore |
| Workspaces/teams | Local folders and tags |
| Sharing | Local-only ownership |
| Hosted transcription | Whisper.cpp and optional local Parakeet |
| Cloud fallback | Local-only engine fallback |
| Hosted AI/agents/chat | Exact and semantic search |
| Calendar | Manual meetings and local process detection |
| Public API/MCP | Internal typed Electron IPC |
| Billing/quotas | Model, disk, index, and backup health |
| Runtime updater | Manual installer releases |
| Runtime downloads | Bundled assets and offline model packs |
| External network | Loopback-only runtime policy |

---

# 12. How We Implement Missing Features

For every missing or partial required capability:

1. Assign stable capability ID
2. Assign authoritative target folder
3. Define target files and public entry point
4. Define internal modules
5. Define UI, state, IPC, persistence, native, and test ownership
6. Identify current callers
7. Identify code to repair or replace
8. Record expected Graphify relationships
9. Implement one coherent path
10. Run targeted tests
11. Run full workflow
12. Update registry and status

Required additions include where absent:

- Safe legacy OpenWhispr-to-Mnemora data migration
- Local backup, verification, preview, and restore
- Local model-pack import and checksums
- Local processing job queue
- Recording recovery
- Structured transcript segment editing
- Speaker management
- Exact transcript search
- Semantic transcript search
- Index rebuild/recovery
- Media import queue and failure recovery
- Complete export formats
- Local onboarding and settings
- Runtime external-network enforcement
- Clean offline installation proof
- Real SQLite integration-test harness

---

# Reuse-First Integration

When a capability is missing or damaged, search in this order:

1. Current working tree
2. Current Git history
3. Exact OpenWhispr fork point
4. Compatible upstream OpenWhispr implementation
5. Mature licence-compatible external implementation
6. New minimal implementation only when necessary

Before copying code, verify:

- No working equivalent already exists
- Correct upstream version
- Compatible licence
- Required assets
- Required dependencies
- No hidden cloud call
- No authentication coupling
- No sync coupling
- No telemetry
- No updater
- No billing
- No remote API
- No runtime download
- No competing implementation

Record:

- Repository
- Commit or tag
- Licence
- Copied files
- Copied tests
- Destination
- Modifications
- Removed unwanted behaviour
- Dependencies
- Verification evidence

Copy only the smallest coherent implementation and its useful tests and required assets. Preserve attribution, validation, error handling, cleanup, recovery, native behaviour, performance-sensitive behaviour, and edge cases. Adapt paths, names, IPC, database, and UI only as required. Remove auth, cloud, sync, telemetry, billing, updater, runtime-download, remote-API, and external-network coupling. Integrate the result into one authoritative location, remove superseded duplicates, and run applicable upstream and Mnemora tests.

Do not copy unknown-licence code, copy an entire project for one module, keep parallel implementations, recreate upstream code from memory, or hide network behaviour.

Search results containing words such as `token`, `auth`, `cloud`, `openai`, or `http` are review candidates.

They are not automatic deletion authorisation.

---

# 14. Moving the Application into Codebase

Before moving:

- Confirm root and Git state
- Identify package, source, tests, native, resources, scripts, packaging, build outputs, CI, and Markdown
- Record exact current and target locations

Then move in dependency-safe batches using `git mv` where possible:

1. Create Codebase
2. Move package configuration
3. Move source
4. Move tests
5. Move native code
6. Move resources/models/binaries
7. Move scripts
8. Move packaging
9. Update working directories, relative paths, aliases, Electron/native/assets/tests/CI/release paths
10. Install and rebuild dependencies from Codebase
11. Run targeted and broad verification
12. Update Graphify

Do not move everything blindly and repair later.

---

# 15. Moving Markdown into Graphify

Search tracked files for:

- `*.md`
- `*.markdown`
- `*.mdown`
- `*.mkd`

For each:

1. Identify purpose and authority
2. Choose Graphify destination
3. Move with history
4. Update links and scripts
5. Replace runtime dependence with code/configuration where necessary
6. Verify build and packaging
7. Record original/new paths
8. Prove Codebase has zero tracked Markdown

Plain-text legal notices may remain in Codebase. User-created Markdown exports are unaffected.

---

# 16. Generic Folder Cleanup

Audit folders named helpers, utils, services, common, shared, misc, other, temp, new, old, legacy, stuff, or general.

For each contained symbol:

1. Identify primary capability
2. Decide whether genuinely shared
3. Define target owner
4. Move
5. Repair imports/registrations
6. Test
7. Remove empty folder

`shared` is allowed only for semantically independent code genuinely used by multiple capabilities.

---

# 17. IPC Audit

Every retained Electron feature must be verified through:

```text
Renderer caller
→ preload exposure
→ TypeScript declaration
→ IPC channel
→ IPC handler
→ local service
→ database/filesystem/native/local process
→ tests
```

For removed systems, delete the full chain.

No caller may target a missing handler. No preload API may expose a removed feature. No type may describe a nonexistent API. No dead handler may remain registered.

---

# Database and Legacy Migration Safety

## Historical migrations

- Never delete or rewrite historical migrations blindly.
- Existing users may require them to reach the current schema.
- Add new forward migrations.
- Distinguish historical terminology from active product behaviour.

## Copy before transform

- Use disposable database copies for tests.
- Create a timestamped backup before a production migration that may alter user data.
- Record source schema version.
- Record destination schema version.
- Record database checksum where practical.
- Record migration result.

## Idempotency and interruption recovery

Every migration must:

- Detect whether it has already been applied
- Avoid duplicate transformation
- Use transactions where supported
- Preserve foreign keys
- Maintain a migration journal
- Recover safely after interruption
- Protect non-empty destination databases
- Preserve original OpenWhispr data
- Never silently overwrite Mnemora data

## Content-integrity verification

Validate:

- Record counts
- Primary keys
- Foreign keys
- Meeting-to-transcript relationships
- Transcript segment order
- Speaker assignments
- Note links
- Folder relationships
- Tag relationships
- Snippets
- Attachments
- Recording file references
- Settings
- Semantic-index rebuild state

Do not prescribe one universal SQL migration algorithm without inspecting the real schema.

---

# 19. SQLite Native Binding

A Node/Electron ABI mismatch is not a hard blocker.

Inspect Node version, Electron version, ABI, OS, architecture, better-sqlite3 version, installed binary, postinstall, rebuild behaviour, test runtime, and packaging runtime.

Resolve using the correct combination of:

- Reinstall
- `electron-builder install-app-deps`
- `electron-rebuild`
- Node-target rebuild
- Electron-target rebuild
- Compatible package version
- Separate Node and Electron test commands
- Real disposable SQLite harness
- Package-script correction

Do not replace real SQLite integration tests with mocks.

---

# 20. Continuous Execution Loop

For every coherent dependency-safe capability batch:

```text
READ MASTER PLAN
→ READ RUN STATE
→ QUERY EXACT LOCATION REGISTRY
→ MAP DEPENDENCIES
→ CLASSIFY KEEP/REMOVE/REPLACE/REPAIR/ADD/CONDITIONAL
→ CHANGE ONE DEPENDENCY-SAFE CAPABILITY BATCH
→ UPDATE IMPORTS, TYPES, REGISTRATIONS, AND TESTS
→ RUN TARGETED CHECKS
→ REPAIR FAILURES
→ RUN BROADER CHECKS
→ TEST AFFECTED WORKFLOW
→ UPDATE CONTINUOUS GRAPHIFY CORE
→ CREATE GIT OR HASH CHECKPOINT
→ CONTINUE
```

Do not carry known regressions into the next phase.

---

# Testing Evidence Matrix

## Mocks are allowed for

- Pure unit logic
- Failure injection
- Deterministic edge cases
- Isolated boundaries when the real boundary is separately tested

## Mocks are insufficient as final proof for

- SQLite persistence
- Database migration
- IPC round trips
- Filesystem import/export
- Backup and restore
- Local process startup
- Native binding compatibility
- Runtime network enforcement
- Packaged application behaviour
- Installer launch

## Required real evidence

- Disposable real SQLite databases
- Real migration fixtures
- Real filesystem fixtures
- Real renderer/preload/main IPC round trips
- Real bundled local-process startup
- Real Windows production build
- Real Windows packaged application launch
- Real offline network interception or observation

## Hardware-dependent status

Use only:

- `VERIFIED ON HARDWARE`
- `UNVERIFIED — REQUIRED HARDWARE UNAVAILABLE`
- `FAILED`

Unavailable hardware is not a pass.

---

# 21. Tests and Verification

Use actual repository commands and record working directory, runtime, exit code, output, classification, repair, and rerun.

Run where applicable:

- Install
- Native rebuild
- Formatting
- Lint
- Static analysis
- Typecheck
- Unit tests
- SQLite tests
- Migration tests
- Integration tests
- IPC tests
- Native tests
- Renderer build
- Electron build
- Production build
- Packaging
- Installer validation
- Application launch
- Offline policy tests

Add meaningful tests where required behaviour lacks proof.

Complete workflows:

- Dictation
- Meeting recording
- Microphone and system audio
- Diarization and speaker rename
- Notes, folders, tags, snippets
- Exact and semantic search
- Import and export
- Backup and restore
- Restart persistence
- Offline first launch

---

# 22. Runtime Offline Enforcement

Allowed at runtime:

- Electron IPC
- Local files
- Packaged assets
- localhost
- `127.0.0.1`
- IPv6 loopback
- Local Whisper
- Local Qdrant
- Approved local bundled processes

Blocked:

- External HTTP/HTTPS
- External WebSockets/EventSource
- External redirects
- Auth, cloud, calendar, sync, update, telemetry, analytics, model download, and web-search traffic

Implement before renderer windows load.

Test:

- Loopback remains functional
- External requests are blocked
- Redirects and new windows are blocked
- Automatic external links are blocked
- Logs remain local
- Core workflows remain functional

---

# 23. Ponytail Simplification

Run Ponytail only after correctness and ownership are established.

Audit unnecessary wrappers, pass-through services, duplicate helpers/validation/conversion/types, dead flags, excessive factories, unnecessary state, compatibility layers, and generic dumping grounds.

Never remove validation, error handling, cleanup, type safety, resource lifecycle, platform behaviour, tests, or readability.

Record accepted and rejected simplifications.

---

# 24. Autonomous Authority

The implementation AI is authorised to:

- Read all files
- Create Codebase and Graphify
- Move files
- Edit imports, IPC, database, tests, scripts, build, and packaging
- Delete mapped unwanted code and proven dead code
- Install/rebuild dependencies
- Copy and integrate licence-compatible code
- Run tests, builds, packaging, and application launch
- Create disposable test data
- Repair failures
- Continue through phases

It must not ask whether to continue, delete mapped excluded systems, run tests, update imports, repair failures, or begin the next phase.

Only a genuine ambiguity involving real user data, missing private credentials, irreplaceable assets, or irreconcilable authoritative requirements may be recorded as a blocker. All other work continues.

---

# 25. Completion Tracking

`Graphify/11-Completion/COMPLETION_TRACKER.md` uses:

- `✅ VERIFIED`
- `❌ INCOMPLETE`
- `⛔ GENUINELY EXTERNALLY BLOCKED`

Track at minimum:

- Root and Git state
- Master Plan read
- Codebase and Graphify created
- Markdown migration complete
- No Markdown in Codebase
- Baseline and deep Graphify scan
- Corpus inventory and capability map
- Exact-location registry
- Target architecture and ownership
- Reorganisation and import repair
- Runtime registrations
- Duplicate consolidation
- Dead-code and unused-folder removal
- Dependency cleanup
- Missing feature implementation
- SQLite proof
- Ponytail audit
- Final deep scan
- Typecheck, lint, unit/database/integration/Electron tests
- Renderer/production builds
- Packaging
- Clean offline test
- Final regression

Do not use vague statuses such as mostly complete, should work, or probably unused.

---

# Strict Release Conjunction

Release approval is a conjunction, not a score. Every applicable gate must pass with evidence tied to the last verified commit or hash checkpoint:

1. **Authority gate:** The three authoritative Master Plan files are present, completely read, mutually consistent, and identified as Mnemora and OpenWhispr-derived.
2. **Provenance gate:** Repository root, baseline state, branch, commit or recoverable hash state, existing user work, and every mutation batch are recorded without destructive Git cleanup.
3. **Mapping gate:** The final Graphify scan, exact-location registry, dependency relationships, runtime registrations, ownership, moves, deletions, and third-party provenance agree with the saved repository.
4. **Preservation gate:** Retained local behaviour, validation, error handling, cleanup, recovery, native behaviour, tests, and data compatibility remain functional.
5. **Deletion gate:** Every removed system passes all seven gates in the Binding Deletion Interlock and is absent across the full architectural chain.
6. **Capability gate:** Dictation, meeting recording, local transcription, SQLite persistence, notes, diarization, exact search, semantic search, import/export, backup/restore, playback, settings, and every other mandatory retained capability pass their complete affected workflows.
7. **Data-safety gate:** Historical migrations, forward migrations, disposable-copy tests, backups, idempotency, interruption recovery, content-integrity checks, legacy OpenWhispr preservation, and non-empty Mnemora database protection are proven.
8. **Real-integration gate:** Every applicable item in the Testing Evidence Matrix has real evidence; mocks alone do not satisfy a real boundary.
9. **Offline gate:** Runtime external-network enforcement is active before renderer windows load, loopback services still work, external traffic and redirects are blocked, and an offline first launch passes.
10. **Windows release gate:** Native bindings, production build, packaged application, installer, installation, and launch pass on Windows.
11. **Audit gate:** The final Ponytail audit and final deep Graphify scan are complete, their findings are resolved or explicitly rejected with evidence, and the final registry and completion documents match reality.
12. **Hardware gate:** Required hardware-dependent checks use only the permitted hardware statuses. `UNVERIFIED — REQUIRED HARDWARE UNAVAILABLE` and `FAILED` do not pass an applicable release gate.

A gate may be marked not applicable only with a recorded product-scope reason and evidence. No partial pass, average score, administrative status, or success message can compensate for a failed, blocked, unverified, or unevidenced applicable gate.

---

# 26. Final Approval

The project is complete only when:

- The three Master Plan files remain authoritative
- Codebase contains the complete working application and no tracked Markdown
- Graphify contains all project intelligence and Markdown
- Every significant symbol is mapped and owned
- Every retained capability works
- Every deleted system is absent across every layer
- Every replacement and missing required capability is implemented
- Working original code was preserved where valid
- Copied code is licence-compatible and attributed
- Duplicates and proven dead code are removed
- Exact-location registry matches the final graph
- SQLite, typecheck, lint, tests, builds, packaging, and offline proof pass
- Completion documents match reality

If anything required remains incomplete:

```text
PROJECT NOT COMPLETE — RELEASE REJECTED
```

If every requirement is proven:

```text
PROJECT COMPLETE — FINAL ARCHITECTURE VERIFIED
```
