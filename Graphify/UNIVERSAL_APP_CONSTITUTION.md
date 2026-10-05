# Universal App Constitution

## Preamble

This Constitution establishes binding architecture, data-safety, sovereignty, and governance requirements for applications in this ecosystem. No local refactoring, model instruction, styling preference, or operational convenience may supersede these articles.

---

## Article A: Local-First and Offline Sovereignty

1. **Complete Offline Execution**: The application must provide full core functionality without requiring an active network connection, remote server, external API, or cloud infrastructure.
2. **Loopback Isolation**: Native service processes (e.g., local Whisper servers, search indices, sidecars) must bind strictly to loopback interfaces (`127.0.0.1` / `::1`) and reject external network access.
3. **No Silent Network Egress**: The application must never emit telemetry, diagnostics, user content, or background requests to external network endpoints without explicit, informed user consent.
4. **Offline Asset Self-Containment**: All runtime models, tokenizers, fixtures, locales, and native binaries required for core execution must be bundled or installable offline from local storage.

---

## Article B: Non-Negotiable Data Safety & Zero Content Loss

1. **No-Data-Loss Law**: Real user content—including audio recordings, transcripts, notes, tags, folder hierarchies, snippets, database files, and backups—must never be silently altered, truncated, overwritten, or deleted.
2. **Copy Before Transform**: Any operation that migrates, repairs, restructures, or transforms user data must first create a verified, timestamped backup copy.
3. **Transactional Safety & Rollback**: Schema and data migrations must execute within atomic transactions where supported and safely roll back to the pre-migration state upon failure or interruption.
4. **Checksum & Journal Verification**: Migrations and backup restorations must verify source and destination checksums, record a durable journal of outcomes, and maintain idempotent rerun safety.
5. **Disposable Fixture Rule**: Destructive tests, migration tests, interruption tests, and recovery drills must run strictly on disposable verified copies and never touch actual user production databases.

---

## Article C: Absolute Privacy & Zero Telemetry

1. **Zero External Tracking**: The application must not integrate remote telemetry, analytics frameworks, third-party crash reporters, or user-activity trackers.
2. **Local Storage of Secrets**: Application settings, encryption keys, and secure configuration must remain exclusively in local OS secure stores or local protected configuration tables.
3. **Clean Version Control**: User data, database WAL files, private keys, authentication tokens, credentials, and personal recordings must never be committed to tracked version control.

---

## Article D: Strict Provenance & Auditability

1. **Cryptographic Checkpoints**: Durable execution state, planning baselines, and release milestones must be linked to verifiable Git commit SHAs and cryptographic content digests.
2. **Reproducible Planning & Regeneration**: Machine-readable planning registers and derived reports must be deterministically reproducible from immutable planning authorities without timestamp churn.
3. **Transparent Tool & Model Provenance**: Tool execution logs, model identities, and audit records must truthfully report the exact tools, scripts, and workflows used. Unverified or decorative tool claims must not be propagated.

---

## Article E: Preservation-First Architecture

1. **Behavior Over Aesthetics**: Existing, working architectural components, native integration bridges, and platform-specific behaviors must be characterized and protected before refactoring. Code must never be rewritten merely for visual or stylistic preference.
2. **Binding Deletion Interlocks**: Systems designated for deletion must pass full multi-layer analysis (UI, routes, IPC, services, database, filesystem, native effects, settings, dependencies, tests) before removal.
3. **Historical Migration Preservation**: Historical migrations must not be deleted or rewritten simply because they refer to decommissioned systems; forward migrations must be used for schema progression.

---

## Article F: Bounded Explicit Contracts & Isolation

1. **Explicit IPC Contracts**: Inter-process communication between UI renderers, preload bridges, and main backend processes must use explicitly declared, type-safe channels. Dynamic, open-ended, or ambient bridges are prohibited.
2. **Filesystem Boundary Containment**: File access must be bounded to authorized application user-data, cache, and resource directories. Directory traversal, arbitrary root access, and unvalidated file paths are strictly rejected.
3. **Native Process Containment**: Platform-native helpers and binaries must have verified lifecycle management, graceful shutdown handlers, and clean process isolation.

---

## Article G: Human-Readable Folder Contract

1. **Deliberate Understandability**: The durable repository, workspace, and data hierarchy must be intuitively understandable to a human engineer or technical user.
2. **Self-Describing Artifacts**: Directories, filenames, manifests, schemas, and evidence files must clearly declare their identity, purpose, and relationship to the wider system.
3. **Deterministic Structure**: Directory layouts must avoid opaque hash-only hierarchies where transparent domain-oriented paths can be maintained without ambiguity.

---

## Article H: Small-Model Navigability

1. **Deterministic Discoverability**: Repositories and metadata must be structured so that a compact, 1B-class local model or bounded assistant (e.g., Hermes-class) can navigate, inspect, and reason about the system without guessing.
2. **Explicit Indices & Canonical IDs**: Navigation must be anchored in explicit machine-readable registers, canonical entity IDs, schema contracts, and deterministic cross-references rather than ambient associative recall.
3. **Bounded Context Windows**: Machine-readable authorities must provide concise, targeted registries enabling focused context retrieval without consuming massive context windows.

---

## Article I: Deterministic Non-AI Core

1. **Deterministic Truth**: Core application state, persistence, business logic, migration rules, security policies, and data integrity guarantees must be strictly deterministic code.
2. **AI Role Boundary**: Artificial intelligence models may assist, propose, summarize, or transcribe within authorized feature boundaries, but must never be the sole authority for state mutation or data preservation.
3. **Generative AI Restriction**: In accordance with Mnemora's Master Plans, the core application must not introduce generative AI features, hallucination-prone synthetic summarization, or cloud-hosted LLMs into the offline dictation core.

---

## Article J: Authorized Mutation Model

1. **Contract-Authorized Mutation**: No codebase file or persistent data structure may be modified without an explicit, approved task contract specifying:
   - Stable task identifier and capability owner
   - Exact purpose and implementation actions
   - Explicit `files_expected_to_change`
   - Explicit `files_forbidden_from_changing`
   - Preconditions, terminal dependencies, and characterization requirements
2. **Scope Firewall**: Codebase mutations outside the declared `files_expected_to_change` of an active or terminal task are strictly unauthorized and must be rejected by repository validators.
3. **Task Atomicity**: Each implementation run executes exactly one authorized task, validates its complete conjunction of requirements, records durable execution evidence, and stops cleanly before beginning any subsequent task.

---

## Amendment and Governance Process

1. **Immutable Master Plans**: The three foundation documents (`Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md`, `Master Plan/02-EVERYTHING-WE-ARE-DELETING.md`, `Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-REPLACE.md`) remain permanent architectural authorities whose SHA-256 digests must be verified before every implementation task.
2. **Constitution Governance**: Any amendment to this Constitution requires an explicit governance task, comprehensive cross-repository gap analysis, validator gate reconciliation, and formal delivery approval.
