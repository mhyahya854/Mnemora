# Universal App Constitution

## Preamble

This Constitution establishes binding architecture, data-safety, sovereignty, and governance requirements for applications in this ecosystem. It serves as a **USER-LEVEL CROSS-APP AUTHORITY** that supersedes local refactoring, model instructions, styling preferences, or operational convenience.

## Authority and Amendment Model

The hierarchy of authorities in this repository is strictly defined as:

1. **Universal App Constitution** (User-Level Cross-App Authority)
2. **Mnemora App-Specific Immutable Master Plans**
3. **Derived requirements / capabilities / task authorities**

### Amendment Policy
- The Universal App Constitution is a user-level cross-app authority.
- Future amendments to the Constitution require **explicit user authority**; no coding model may silently alter universal rules.
- The Constitution does not permit a model to casually rewrite an app-specific Master Plan.
- If a conflict arises between the Constitution and an app-specific Master Plan: **STOP AND REPORT THE CONFLICT FOR USER DECISION**.

---

## UAC-01 — APPLICATION INDEPENDENCE

**Normative Requirement:**
Every app must function independently without Hermes. Hermes, local AI, cloud AI, or another orchestrator may assist but must never be required for: startup, core workflows, data access, deterministic search, indexing, migrations, backup, restore, recovery, normal UI operation. AI is optional and replaceable.

**Clauses:**
- Every app must function independently without Hermes or an orchestrator.
- Hermes, local AI, cloud AI, or another orchestrator may assist but must never be required for: startup, core workflows, data access, deterministic search, indexing, migrations, backup, restore, recovery, normal UI operation.
- AI is optional and replaceable.

- **Applicability:** All applications, core backend services, and user interfaces across all release milestones.
- **Verification Expectations:** Codebase imports and runtime execution must prove complete operational capability with zero orchestrator/Hermes packages or processes present.

---

## UAC-02 — LOCAL-FIRST / OFFLINE-FIRST

**Normative Requirement:**
Core application functionality must work locally and offline. No hidden cloud dependency. No silent network fallback. Mnemora stricter first-release offline policy remains valid.

**Clauses:**
- Core application functionality must work locally and offline.
- No hidden cloud dependency.
- No silent network fallback.
- Mnemora stricter first-release offline policy remains valid.

- **Applicability:** All core workflows including capture, transcription, notes, indexing, and storage.
- **Verification Expectations:** First launch, recording, search, and editing must pass under total network denial; loopback binding (127.0.0.1) enforced for local sidecars.

---

## UAC-03 — USER-SELECTED DATA ROOT SOVEREIGNTY

**Normative Requirement:**
Durable user-owned data must live under an explicit, documented, portable application data root wherever technically possible. The app must not scatter canonical user data unpredictably around the machine. Moving the data root must not destroy data meaning. Machine-specific absolute paths must not become durable identity where portable relative references can be used.

**Clauses:**
- Durable user-owned data must live under an explicit, documented, portable application data root wherever technically possible.
- The app must not scatter canonical user data unpredictably around the machine.
- Moving the data root must not destroy data meaning.
- Machine-specific absolute paths must not become durable identity where portable relative references can be used.

- **Applicability:** All persistent storage, user files, media archives, databases, and configuration.
- **Verification Expectations:** Relocating the user data directory to a new folder or volume preserves all relationships, notes, transcripts, audio links, and database integrity.

---

## UAC-04 — NAS / PRIVATE-LAN SUPPORT

**Normative Requirement:**
Every applicable app must support NAS/private-LAN usage. For desktop applications this includes, where technically safe: local disk data root, external disk data root, NAS/network-share data root. The design must explicitly handle: share unavailable, reconnection, latency, interrupted writes, atomicity limitations, locking, concurrency, one-writer policy where required, conflict detection, corruption avoidance, recovery, portable paths, backup versus NAS redundancy. For server/headless components, NAS deployment must be supported where the application architecture makes such deployment meaningful. Do not claim NAS support without evidence. NAS support must not require Hermes.

**Clauses:**
- Every applicable app must support NAS/private-LAN usage.
- For desktop applications this includes, where technically safe: local disk data root, external disk data root, NAS/network-share data root.
- The design must explicitly handle: share unavailable, reconnection, latency, interrupted writes, atomicity limitations, locking, concurrency, one-writer policy where required, conflict detection, corruption avoidance, recovery, portable paths, backup versus NAS redundancy.
- For server/headless components, NAS deployment must be supported where the application architecture makes such deployment meaningful.
- Do not claim NAS support without evidence.
- NAS support must not require Hermes.

- **Applicability:** Desktop storage architecture, backup engines, and network-attached storage environments.
- **Verification Expectations:** Proof of network-share disconnection recovery, locking and one-writer concurrency enforcement, latency tolerance, and corruption avoidance on SMB/NFS mounts.

---

## UAC-05 — CROSS-PLATFORM SUPPORT

**Normative Requirement:**
Apps must be architected for: Windows, macOS, Linux. A project may release one platform first, but its architecture must not unnecessarily prevent the others. Mnemora Windows-first proof requirement must be evaluated against this rule honestly. Do not automatically call preservation of macOS/Linux source files full cross-platform support.

**Clauses:**
- Apps must be architected for: Windows, macOS, Linux.
- A project may release one platform first, but its architecture must not unnecessarily prevent the others.
- Mnemora Windows-first proof requirement must be evaluated against this rule honestly.
- Do not automatically call preservation of macOS/Linux source files full cross-platform support.

- **Applicability:** Native helpers, application shell, packaging, audio capture, and hotkey subsystems.
- **Verification Expectations:** Core abstractions must not bind to OS-specific primitives without platform adapters; non-Windows source files preserved; Windows-first release acknowledged honestly as partial.

---

## UAC-06 — FEATURE-FIRST MODULAR MONOLITH

**Normative Requirement:**
Apps of this type use a FEATURE-FIRST MODULAR-MONOLITH architecture. Feature ownership is primary. Each feature should own, where applicable: feature/ domain/, application/, infrastructure/, ui/, tests/ or the closest idiomatic equivalent for the stack. Shared/global modules must remain genuinely cross-cutting and thin. Avoid giant generic dumping grounds: utils/, helpers/, services/, common/, misc/ unless the contents truly have no feature owner. Do not create microservices without demonstrated necessity. Do not rewrite working code merely to make the tree prettier.

**Clauses:**
- Apps of this type use a FEATURE-FIRST MODULAR-MONOLITH architecture.
- Feature ownership is primary: each feature should own domain, application, infrastructure, ui, tests where applicable.
- Shared/global modules must remain genuinely cross-cutting and thin.
- Avoid giant generic dumping grounds (utils/, helpers/, services/, common/, misc/) unless contents have no feature owner.
- Do not create microservices without demonstrated necessity.
- Do not rewrite working code merely to make the tree prettier.

- **Applicability:** Codebase structural organization and module boundaries.
- **Verification Expectations:** Feature directories group related logic, IPC, UI, and tests; generic utility folders are audited and incrementally retired via planned queue tasks.

---

## UAC-07 — HUMAN-READABLE FOLDER CONTRACT

**Normative Requirement:**
Source and durable data structures must be deliberately understandable to humans. Use self-describing: folders, filenames, manifests, schemas, metadata, indexes, relationships. Avoid unnecessary opaque hash-only organization.

**Clauses:**
- Source and durable data structures must be deliberately understandable to humans.
- Use self-describing folders, filenames, manifests, schemas, metadata, indexes, relationships.
- Avoid unnecessary opaque hash-only organization.

- **Applicability:** Repository folder structure, documentation, user data root, and export archives.
- **Verification Expectations:** Directories and files must use clear semantic names; metadata manifests accompany persisted structures; no purely opaque hash trees for user content.

---

## UAC-08 — SMALL-MODEL NAVIGABILITY

**Normative Requirement:**
Structure the application and its data so a bounded approximately 1B-class local model can navigate it accurately using explicit tools and metadata. Accuracy should come from: canonical IDs, deterministic indexes, bounded tools, schemas, manifests, provenance, explicit relationships not from requiring a huge cloud model. This does NOT make AI a runtime dependency.

**Clauses:**
- Structure the application and its data so a bounded approximately 1B-class local model can navigate it accurately using explicit tools and metadata.
- Accuracy must come from: canonical IDs, deterministic indexes, bounded tools, schemas, manifests, provenance, explicit relationships.
- Accuracy must not require a huge cloud model.
- This does NOT make AI a runtime dependency.

- **Applicability:** Planning registers, data schemas, IPC contracts, and developer toolkits.
- **Verification Expectations:** All system entities have stable IDs and deterministic cross-references; explicit tools have bounded parameters and schema-validated outputs.

---

## UAC-09 — DETERMINISTIC NON-AI CORE

**Normative Requirement:**
Critical application state and mutation logic must be deterministic. AI may assist only within explicit feature boundaries. AI must never be the sole source of truth for deterministic state operations. Mnemora first release still forbids generative AI.

**Clauses:**
- Critical application state and mutation logic must be deterministic.
- AI may assist only within explicit feature boundaries.
- AI must never be the sole source of truth for deterministic state operations.
- Mnemora first release still forbids generative AI.

- **Applicability:** Persistence, state machines, audio pipelines, search execution, and migrations.
- **Verification Expectations:** Zero generative AI models or LLMs invoked in core operations; speech recognition uses deterministic acoustic models; state transitions are pure deterministic functions.

---

## UAC-10 — AUTHORIZED MUTATION MODEL

**Normative Requirement:**
Canonical application data may be changed only through: 1. validated user actions through the application or 2. explicitly approved app-specific AI tools/skills with bounded permissions. No arbitrary AI filesystem mutation. No silent mutation outside application contracts.

**Clauses:**
- Canonical application data may be changed only through validated user actions through the application or explicitly approved app-specific AI tools/skills with bounded permissions.
- No arbitrary AI filesystem mutation.
- No silent mutation outside application contracts.

- **Applicability:** All database writes, file edits, configuration changes, and AI tool integrations.
- **Verification Expectations:** Every mutation passes through typed IPC and validated database manager methods with schema enforcement; arbitrary filesystem write paths rejected.

---

## UAC-11 — MUTATION AUDIT LOG / CHANGE FLAGGING

**Normative Requirement:**
Every meaningful authoritative mutation must be attributable. Record where applicable: actor, user/tool/AI identity, timestamp, operation, entity, previous version/hash, resulting version/hash, source, reason, evidence/reference. Audit history must be append-oriented and must not be silently rewritten. Unrecognized/external changes to canonical application data must be detected and FLAGGED. The app must not silently overwrite divergent external edits. Where appropriate offer reconciliation: inspect diff, keep external change, accept application version, restore, reject, merge through a validated workflow.

**Clauses:**
- Every meaningful authoritative mutation must be attributable.
- Record where applicable: actor, user/tool/AI identity, timestamp, operation, entity, previous version/hash, resulting version/hash, source, reason, evidence/reference.
- Audit history must be append-oriented and must not be silently rewritten.
- Unrecognized/external changes to canonical application data must be detected and FLAGGED.
- The app must not silently overwrite divergent external edits.
- Where appropriate offer reconciliation: inspect diff, keep external change, accept application version, restore, reject, merge through a validated workflow.

- **Applicability:** Data persistence layer, file storage monitors, and mutation management services.
- **Verification Expectations:** Append-oriented audit records created on data change; external file alterations detected via watcher/checksum and surfaced to user before any overwriting.

---

## UAC-12 — RECOVERABILITY OVER MAGIC

**Normative Requirement:**
Prefer operations that are: inspectable, reversible, transactional, recoverable, idempotent. Use as appropriate: atomic writes, journaling, logical deletion, rollback, interruption recovery, backups, tested restore, conflict preservation. No silent data loss.

**Clauses:**
- Prefer operations that are inspectable, reversible, transactional, recoverable, idempotent.
- Use as appropriate: atomic writes, journaling, logical deletion, rollback, interruption recovery, backups, tested restore, conflict preservation.
- No silent data loss.

- **Applicability:** Persistence operations, audio capture, background jobs, and migrations.
- **Verification Expectations:** Operations use copy-before-transform and atomic renames; simulated crash/power-cut during write or migration rolls back cleanly without data loss.

---

## UAC-13 — ORIGINALS VS DERIVED STATE

**Normative Requirement:**
Original user artifacts are protected. Derived data should be rebuildable wherever practical. Examples: search indexes, semantic vectors, thumbnails, caches, generated metadata, temporary processing outputs. Derived projections must not become the only irreplaceable copy of user content.

**Clauses:**
- Original user artifacts are protected.
- Derived data should be rebuildable wherever practical (search indexes, semantic vectors, thumbnails, caches, generated metadata, temporary processing outputs).
- Derived projections must not become the only irreplaceable copy of user content.

- **Applicability:** Media files, notes, transcripts, embeddings, vector databases, and cache directories.
- **Verification Expectations:** Deleting vector indices, thumbnails, or search caches allows full automated regeneration from primary SQLite and audio files.

---

## UAC-14 — DATABASE / SQLITE SAFETY

**Normative Requirement:**
Mnemora explicitly retains SQLite. Do not remove SQLite to satisfy generic architecture preferences. Instead guarantee: complete backups, documented schema, recoverability, exportability, forward migrations, integrity verification, safe restore, rebuildable derived projections where practical. Audit whether irreplaceable user content exists only inside opaque database state. If filesystem-canonical storage would contradict Mnemora product design, report the conflict rather than silently changing architecture.

**Clauses:**
- Mnemora explicitly retains SQLite; do not remove SQLite to satisfy generic architecture preferences.
- Guarantee: complete backups, documented schema, recoverability, exportability, forward migrations, integrity verification, safe restore, rebuildable derived projections where practical.
- Audit whether irreplaceable user content exists only inside opaque database state.
- If filesystem-canonical storage would contradict Mnemora product design, report the conflict rather than silently changing architecture.

- **Applicability:** Database layer, schema migration framework, and persistence integrity tests.
- **Verification Expectations:** PRAGMA integrity_check passes; database snapshots create valid verified backup copies; migrations run in transactions; note content mirrored to Markdown.

---

## UAC-15 — SOURCE / PRIVATE DATA / GIT SEPARATION

**Normative Requirement:**
Maintain explicit separation between: source code, application binaries/builds, private runtime/user data, generated caches, generated evidence, Git history. Private lifetime user archives must never accidentally enter Git. A repository build must not depend on private runtime data.

**Clauses:**
- Maintain explicit separation between source code, application binaries/builds, private runtime/user data, generated caches, generated evidence, Git history.
- Private lifetime user archives must never accidentally enter Git.
- A repository build must not depend on private runtime data.

- **Applicability:** Version control configuration, build scripts, packaging rules, and test harnesses.
- **Verification Expectations:** .gitignore strictly excludes user databases, logs, audio, secrets, and caches; clean git clone builds reproducibly without local runtime state.

---

## UAC-16 — REPRODUCIBLE BUILDS

**Normative Requirement:**
Builds must be reproducible from declared inputs. Pin/trace as appropriate: package dependencies, lockfiles, toolchains, native compilers, models, binaries, schemas, migrations, build configuration.

**Clauses:**
- Builds must be reproducible from declared inputs.
- Pin and trace as appropriate: package dependencies, lockfiles, toolchains, native compilers, models, binaries, schemas, migrations, build configuration.

- **Applicability:** Package manifests, lockfiles, compiler toolchains, asset download scripts, and CI.
- **Verification Expectations:** package-lock.json and electron-builder.json produce functionally reproducible build artifacts from clean checkout with declared dependencies.

---

## UAC-17 — THIRD-PARTY / DONOR PROVENANCE

**Normative Requirement:**
Every copied or adapted: source component, donor repository, dependency, model, dataset, binary, asset, native helper must have traceable provenance and compatible licensing. Required notices must remain intact.

**Clauses:**
- Every copied or adapted source component, donor repository, dependency, model, dataset, binary, asset, native helper must have traceable provenance and compatible licensing.
- Required notices must remain intact.

- **Applicability:** Third-party libraries, bundled binaries (ffmpeg, whisper, sherpa, qdrant), and donor codebase.
- **Verification Expectations:** Third-party registry matches all package.json entries; LICENSE and NOTICE files preserve donor copyright notices; binary licenses verified.

---

## UAC-18 — FAIL CLOSED

**Normative Requirement:**
When authority, state, AI interpretation, provenance, or data safety is uncertain: ASK or BLOCK or SURFACE THE CONFLICT. Do not guess. Do not fabricate evidence. Do not silently fall back to remote/cloud behaviour.

**Clauses:**
- When authority, state, AI interpretation, provenance, or data safety is uncertain: ASK or BLOCK or SURFACE THE CONFLICT.
- Do not guess.
- Do not fabricate evidence.
- Do not silently fall back to remote/cloud behaviour.

- **Applicability:** Error handlers, execution state validator, network policy, and persistence interlocks.
- **Verification Expectations:** Undefined or corrupt states immediately halt processing and raise explicit errors rather than proceeding with assumptions or silent cloud fallbacks.

---

## UAC-19 — UI / AI / PROVIDER REPLACEABILITY

**Normative Requirement:**
Domain and user-data architecture must not be inseparably coupled to: one UI, Hermes, one local model, one cloud model, one provider, one orchestration layer. Replacing these must not require destruction or migration loss of user data.

**Clauses:**
- Domain and user-data architecture must not be inseparably coupled to: one UI, Hermes, one local model, one cloud model, one provider, one orchestration layer.
- Replacing these must not require destruction or migration loss of user data.

- **Applicability:** Data schema design, service architecture, and model integration interfaces.
- **Verification Expectations:** Transcription engines and UI components connect via typed abstraction interfaces; swapping models or frontends does not alter canonical database schema.

---

## UAC-20 — SCHEMA / VERSION SAFETY

**Normative Requirement:**
Schema changes must preserve semantic meaning. Use explicit forward migrations. Unsupported newer schemas must fail safely. Older software encountering newer data must not silently corrupt it. Read-only safe failure is preferred where practical.

**Clauses:**
- Schema changes must preserve semantic meaning.
- Use explicit forward migrations.
- Unsupported newer schemas must fail safely.
- Older software encountering newer data must not silently corrupt it.
- Read-only safe failure is preferred where practical.

- **Applicability:** Database migration runner, version check gates, and IPC payload validators.
- **Verification Expectations:** Forward migrations test backward compatibility; encountering higher schema version triggers safe error or read-only mode rather than running older migrations.

---

## UAC-21 — STABLE IDS / PORTABLE REFERENCES

**Normative Requirement:**
Use stable entity identifiers. Prefer portable relative references. Avoid using absolute machine paths as durable identity. Renaming/moving directories must not destroy logical relationships.

**Clauses:**
- Use stable entity identifiers.
- Prefer portable relative references.
- Avoid using absolute machine paths as durable identity.
- Renaming/moving directories must not destroy logical relationships.

- **Applicability:** Database entity IDs, audio references, notes, folders, and planning tasks.
- **Verification Expectations:** Entities use UUIDs or canonical alphanumeric IDs; audio file locations stored relative to data root so moving data root preserves playback linkage.

---

## UAC-22 — SELF-DESCRIBING PROJECT CONTRACT

**Normative Requirement:**
The repository and durable data root must provide sufficient explicit, machine-readable contracts for a human or bounded AI to determine: what exists, what is canonical, what is derived, feature ownership, schema/version, provenance, allowed mutations, validation method, recovery method, relationships, available tools/skills without relying on undocumented conversation history.

**Clauses:**
- The repository and durable data root must provide sufficient explicit, machine-readable contracts for a human or bounded AI to determine: what exists, what is canonical, what is derived, feature ownership, schema/version, provenance, allowed mutations, validation method, recovery method, relationships, available tools/skills.
- Must not rely on undocumented conversation history.

- **Applicability:** Graphify documentation, repository root files, metadata manifests, and schemas.
- **Verification Expectations:** A clean agent or engineer starting with zero chat context can verify and inspect all project systems using solely the repository contracts and tools.

---
