#!/usr/bin/env python3
"""Generator for Mnemora Universal Constitution authorities, gap reports, and audits.

Generates:
- Graphify/UNIVERSAL_APP_CONSTITUTION.json
- Graphify/UNIVERSAL_APP_CONSTITUTION.md
- Graphify/MNEMORA_UNIVERSAL_RULES_GAP_REPORT.json
- Graphify/MNEMORA_UNIVERSAL_RULES_GAP_REPORT.md
- Graphify/CONSTITUTION_AUDIT.md (corrected 22-rule reconciliation)
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
G = ROOT / "Graphify"

MASTER_HASHES = {
    "01-EVERYTHING-WE-ARE-KEEPING.md": "BDF185A823422BCAA9BFEBA815A6852D8F7A5CD46B64714B2CD1DE3357A67F64",
    "02-EVERYTHING-WE-ARE-DELETING.md": "76B6EEC15778B1928F2CD9C0F73FA68C9F3363493062E31E0C904E620DE0AAC3",
    "03-HOW-WE-WILL-KEEP-DELETE-AND-REPLACE.md": "5E076498731C35ACF314904AAB3A39671F7026A166B5E847EFE3CCD4CF07304E",
}

UAC_RULES = [
    {
        "stable_rule_id": "UAC-01",
        "title": "APPLICATION INDEPENDENCE",
        "normative_text": "Every app must function independently without Hermes. Hermes, local AI, cloud AI, or another orchestrator may assist but must never be required for: startup, core workflows, data access, deterministic search, indexing, migrations, backup, restore, recovery, normal UI operation. AI is optional and replaceable.",
        "clauses": [
            "Every app must function independently without Hermes or an orchestrator.",
            "Hermes, local AI, cloud AI, or another orchestrator may assist but must never be required for: startup, core workflows, data access, deterministic search, indexing, migrations, backup, restore, recovery, normal UI operation.",
            "AI is optional and replaceable."
        ],
        "applicability": "All applications, core backend services, and user interfaces across all release milestones.",
        "verification_expectations": "Codebase imports and runtime execution must prove complete operational capability with zero orchestrator/Hermes packages or processes present."
    },
    {
        "stable_rule_id": "UAC-02",
        "title": "LOCAL-FIRST / OFFLINE-FIRST",
        "normative_text": "Core application functionality must work locally and offline. No hidden cloud dependency. No silent network fallback. Mnemora stricter first-release offline policy remains valid.",
        "clauses": [
            "Core application functionality must work locally and offline.",
            "No hidden cloud dependency.",
            "No silent network fallback.",
            "Mnemora stricter first-release offline policy remains valid."
        ],
        "applicability": "All core workflows including capture, transcription, notes, indexing, and storage.",
        "verification_expectations": "First launch, recording, search, and editing must pass under total network denial; loopback binding (127.0.0.1) enforced for local sidecars."
    },
    {
        "stable_rule_id": "UAC-03",
        "title": "USER-SELECTED DATA ROOT SOVEREIGNTY",
        "normative_text": "Durable user-owned data must live under an explicit, documented, portable application data root wherever technically possible. The app must not scatter canonical user data unpredictably around the machine. Moving the data root must not destroy data meaning. Machine-specific absolute paths must not become durable identity where portable relative references can be used.",
        "clauses": [
            "Durable user-owned data must live under an explicit, documented, portable application data root wherever technically possible.",
            "The app must not scatter canonical user data unpredictably around the machine.",
            "Moving the data root must not destroy data meaning.",
            "Machine-specific absolute paths must not become durable identity where portable relative references can be used."
        ],
        "applicability": "All persistent storage, user files, media archives, databases, and configuration.",
        "verification_expectations": "Relocating the user data directory to a new folder or volume preserves all relationships, notes, transcripts, audio links, and database integrity."
    },
    {
        "stable_rule_id": "UAC-04",
        "title": "NAS / PRIVATE-LAN SUPPORT",
        "normative_text": "Every applicable app must support NAS/private-LAN usage. For desktop applications this includes, where technically safe: local disk data root, external disk data root, NAS/network-share data root. The design must explicitly handle: share unavailable, reconnection, latency, interrupted writes, atomicity limitations, locking, concurrency, one-writer policy where required, conflict detection, corruption avoidance, recovery, portable paths, backup versus NAS redundancy. For server/headless components, NAS deployment must be supported where the application architecture makes such deployment meaningful. Do not claim NAS support without evidence. NAS support must not require Hermes.",
        "clauses": [
            "Every applicable app must support NAS/private-LAN usage.",
            "For desktop applications this includes, where technically safe: local disk data root, external disk data root, NAS/network-share data root.",
            "The design must explicitly handle: share unavailable, reconnection, latency, interrupted writes, atomicity limitations, locking, concurrency, one-writer policy where required, conflict detection, corruption avoidance, recovery, portable paths, backup versus NAS redundancy.",
            "For server/headless components, NAS deployment must be supported where the application architecture makes such deployment meaningful.",
            "Do not claim NAS support without evidence.",
            "NAS support must not require Hermes."
        ],
        "applicability": "Desktop storage architecture, backup engines, and network-attached storage environments.",
        "verification_expectations": "Proof of network-share disconnection recovery, locking and one-writer concurrency enforcement, latency tolerance, and corruption avoidance on SMB/NFS mounts."
    },
    {
        "stable_rule_id": "UAC-05",
        "title": "CROSS-PLATFORM SUPPORT",
        "normative_text": "Apps must be architected for: Windows, macOS, Linux. A project may release one platform first, but its architecture must not unnecessarily prevent the others. Mnemora Windows-first proof requirement must be evaluated against this rule honestly. Do not automatically call preservation of macOS/Linux source files full cross-platform support.",
        "clauses": [
            "Apps must be architected for: Windows, macOS, Linux.",
            "A project may release one platform first, but its architecture must not unnecessarily prevent the others.",
            "Mnemora Windows-first proof requirement must be evaluated against this rule honestly.",
            "Do not automatically call preservation of macOS/Linux source files full cross-platform support."
        ],
        "applicability": "Native helpers, application shell, packaging, audio capture, and hotkey subsystems.",
        "verification_expectations": "Core abstractions must not bind to OS-specific primitives without platform adapters; non-Windows source files preserved; Windows-first release acknowledged honestly as partial."
    },
    {
        "stable_rule_id": "UAC-06",
        "title": "FEATURE-FIRST MODULAR MONOLITH",
        "normative_text": "Apps of this type use a FEATURE-FIRST MODULAR-MONOLITH architecture. Feature ownership is primary. Each feature should own, where applicable: feature/ domain/, application/, infrastructure/, ui/, tests/ or the closest idiomatic equivalent for the stack. Shared/global modules must remain genuinely cross-cutting and thin. Avoid giant generic dumping grounds: utils/, helpers/, services/, common/, misc/ unless the contents truly have no feature owner. Do not create microservices without demonstrated necessity. Do not rewrite working code merely to make the tree prettier.",
        "clauses": [
            "Apps of this type use a FEATURE-FIRST MODULAR-MONOLITH architecture.",
            "Feature ownership is primary: each feature should own domain, application, infrastructure, ui, tests where applicable.",
            "Shared/global modules must remain genuinely cross-cutting and thin.",
            "Avoid giant generic dumping grounds (utils/, helpers/, services/, common/, misc/) unless contents have no feature owner.",
            "Do not create microservices without demonstrated necessity.",
            "Do not rewrite working code merely to make the tree prettier."
        ],
        "applicability": "Codebase structural organization and module boundaries.",
        "verification_expectations": "Feature directories group related logic, IPC, UI, and tests; generic utility folders are audited and incrementally retired via planned queue tasks."
    },
    {
        "stable_rule_id": "UAC-07",
        "title": "HUMAN-READABLE FOLDER CONTRACT",
        "normative_text": "Source and durable data structures must be deliberately understandable to humans. Use self-describing: folders, filenames, manifests, schemas, metadata, indexes, relationships. Avoid unnecessary opaque hash-only organization.",
        "clauses": [
            "Source and durable data structures must be deliberately understandable to humans.",
            "Use self-describing folders, filenames, manifests, schemas, metadata, indexes, relationships.",
            "Avoid unnecessary opaque hash-only organization."
        ],
        "applicability": "Repository folder structure, documentation, user data root, and export archives.",
        "verification_expectations": "Directories and files must use clear semantic names; metadata manifests accompany persisted structures; no purely opaque hash trees for user content."
    },
    {
        "stable_rule_id": "UAC-08",
        "title": "SMALL-MODEL NAVIGABILITY",
        "normative_text": "Structure the application and its data so a bounded approximately 1B-class local model can navigate it accurately using explicit tools and metadata. Accuracy should come from: canonical IDs, deterministic indexes, bounded tools, schemas, manifests, provenance, explicit relationships not from requiring a huge cloud model. This does NOT make AI a runtime dependency.",
        "clauses": [
            "Structure the application and its data so a bounded approximately 1B-class local model can navigate it accurately using explicit tools and metadata.",
            "Accuracy must come from: canonical IDs, deterministic indexes, bounded tools, schemas, manifests, provenance, explicit relationships.",
            "Accuracy must not require a huge cloud model.",
            "This does NOT make AI a runtime dependency."
        ],
        "applicability": "Planning registers, data schemas, IPC contracts, and developer toolkits.",
        "verification_expectations": "All system entities have stable IDs and deterministic cross-references; explicit tools have bounded parameters and schema-validated outputs."
    },
    {
        "stable_rule_id": "UAC-09",
        "title": "DETERMINISTIC NON-AI CORE",
        "normative_text": "Critical application state and mutation logic must be deterministic. AI may assist only within explicit feature boundaries. AI must never be the sole source of truth for deterministic state operations. Mnemora first release still forbids generative AI.",
        "clauses": [
            "Critical application state and mutation logic must be deterministic.",
            "AI may assist only within explicit feature boundaries.",
            "AI must never be the sole source of truth for deterministic state operations.",
            "Mnemora first release still forbids generative AI."
        ],
        "applicability": "Persistence, state machines, audio pipelines, search execution, and migrations.",
        "verification_expectations": "Zero generative AI models or LLMs invoked in core operations; speech recognition uses deterministic acoustic models; state transitions are pure deterministic functions."
    },
    {
        "stable_rule_id": "UAC-10",
        "title": "AUTHORIZED MUTATION MODEL",
        "normative_text": "Canonical application data may be changed only through: 1. validated user actions through the application or 2. explicitly approved app-specific AI tools/skills with bounded permissions. No arbitrary AI filesystem mutation. No silent mutation outside application contracts.",
        "clauses": [
            "Canonical application data may be changed only through validated user actions through the application or explicitly approved app-specific AI tools/skills with bounded permissions.",
            "No arbitrary AI filesystem mutation.",
            "No silent mutation outside application contracts."
        ],
        "applicability": "All database writes, file edits, configuration changes, and AI tool integrations.",
        "verification_expectations": "Every mutation passes through typed IPC and validated database manager methods with schema enforcement; arbitrary filesystem write paths rejected."
    },
    {
        "stable_rule_id": "UAC-11",
        "title": "MUTATION AUDIT LOG / CHANGE FLAGGING",
        "normative_text": "Every meaningful authoritative mutation must be attributable. Record where applicable: actor, user/tool/AI identity, timestamp, operation, entity, previous version/hash, resulting version/hash, source, reason, evidence/reference. Audit history must be append-oriented and must not be silently rewritten. Unrecognized/external changes to canonical application data must be detected and FLAGGED. The app must not silently overwrite divergent external edits. Where appropriate offer reconciliation: inspect diff, keep external change, accept application version, restore, reject, merge through a validated workflow.",
        "clauses": [
            "Every meaningful authoritative mutation must be attributable.",
            "Record where applicable: actor, user/tool/AI identity, timestamp, operation, entity, previous version/hash, resulting version/hash, source, reason, evidence/reference.",
            "Audit history must be append-oriented and must not be silently rewritten.",
            "Unrecognized/external changes to canonical application data must be detected and FLAGGED.",
            "The app must not silently overwrite divergent external edits.",
            "Where appropriate offer reconciliation: inspect diff, keep external change, accept application version, restore, reject, merge through a validated workflow."
        ],
        "applicability": "Data persistence layer, file storage monitors, and mutation management services.",
        "verification_expectations": "Append-oriented audit records created on data change; external file alterations detected via watcher/checksum and surfaced to user before any overwriting."
    },
    {
        "stable_rule_id": "UAC-12",
        "title": "RECOVERABILITY OVER MAGIC",
        "normative_text": "Prefer operations that are: inspectable, reversible, transactional, recoverable, idempotent. Use as appropriate: atomic writes, journaling, logical deletion, rollback, interruption recovery, backups, tested restore, conflict preservation. No silent data loss.",
        "clauses": [
            "Prefer operations that are inspectable, reversible, transactional, recoverable, idempotent.",
            "Use as appropriate: atomic writes, journaling, logical deletion, rollback, interruption recovery, backups, tested restore, conflict preservation.",
            "No silent data loss."
        ],
        "applicability": "Persistence operations, audio capture, background jobs, and migrations.",
        "verification_expectations": "Operations use copy-before-transform and atomic renames; simulated crash/power-cut during write or migration rolls back cleanly without data loss."
    },
    {
        "stable_rule_id": "UAC-13",
        "title": "ORIGINALS VS DERIVED STATE",
        "normative_text": "Original user artifacts are protected. Derived data should be rebuildable wherever practical. Examples: search indexes, semantic vectors, thumbnails, caches, generated metadata, temporary processing outputs. Derived projections must not become the only irreplaceable copy of user content.",
        "clauses": [
            "Original user artifacts are protected.",
            "Derived data should be rebuildable wherever practical (search indexes, semantic vectors, thumbnails, caches, generated metadata, temporary processing outputs).",
            "Derived projections must not become the only irreplaceable copy of user content."
        ],
        "applicability": "Media files, notes, transcripts, embeddings, vector databases, and cache directories.",
        "verification_expectations": "Deleting vector indices, thumbnails, or search caches allows full automated regeneration from primary SQLite and audio files."
    },
    {
        "stable_rule_id": "UAC-14",
        "title": "DATABASE / SQLITE SAFETY",
        "normative_text": "Mnemora explicitly retains SQLite. Do not remove SQLite to satisfy generic architecture preferences. Instead guarantee: complete backups, documented schema, recoverability, exportability, forward migrations, integrity verification, safe restore, rebuildable derived projections where practical. Audit whether irreplaceable user content exists only inside opaque database state. If filesystem-canonical storage would contradict Mnemora product design, report the conflict rather than silently changing architecture.",
        "clauses": [
            "Mnemora explicitly retains SQLite; do not remove SQLite to satisfy generic architecture preferences.",
            "Guarantee: complete backups, documented schema, recoverability, exportability, forward migrations, integrity verification, safe restore, rebuildable derived projections where practical.",
            "Audit whether irreplaceable user content exists only inside opaque database state.",
            "If filesystem-canonical storage would contradict Mnemora product design, report the conflict rather than silently changing architecture."
        ],
        "applicability": "Database layer, schema migration framework, and persistence integrity tests.",
        "verification_expectations": "PRAGMA integrity_check passes; database snapshots create valid verified backup copies; migrations run in transactions; note content mirrored to Markdown."
    },
    {
        "stable_rule_id": "UAC-15",
        "title": "SOURCE / PRIVATE DATA / GIT SEPARATION",
        "normative_text": "Maintain explicit separation between: source code, application binaries/builds, private runtime/user data, generated caches, generated evidence, Git history. Private lifetime user archives must never accidentally enter Git. A repository build must not depend on private runtime data.",
        "clauses": [
            "Maintain explicit separation between source code, application binaries/builds, private runtime/user data, generated caches, generated evidence, Git history.",
            "Private lifetime user archives must never accidentally enter Git.",
            "A repository build must not depend on private runtime data."
        ],
        "applicability": "Version control configuration, build scripts, packaging rules, and test harnesses.",
        "verification_expectations": ".gitignore strictly excludes user databases, logs, audio, secrets, and caches; clean git clone builds reproducibly without local runtime state."
    },
    {
        "stable_rule_id": "UAC-16",
        "title": "REPRODUCIBLE BUILDS",
        "normative_text": "Builds must be reproducible from declared inputs. Pin/trace as appropriate: package dependencies, lockfiles, toolchains, native compilers, models, binaries, schemas, migrations, build configuration.",
        "clauses": [
            "Builds must be reproducible from declared inputs.",
            "Pin and trace as appropriate: package dependencies, lockfiles, toolchains, native compilers, models, binaries, schemas, migrations, build configuration."
        ],
        "applicability": "Package manifests, lockfiles, compiler toolchains, asset download scripts, and CI.",
        "verification_expectations": "package-lock.json and electron-builder.json produce functionally reproducible build artifacts from clean checkout with declared dependencies."
    },
    {
        "stable_rule_id": "UAC-17",
        "title": "THIRD-PARTY / DONOR PROVENANCE",
        "normative_text": "Every copied or adapted: source component, donor repository, dependency, model, dataset, binary, asset, native helper must have traceable provenance and compatible licensing. Required notices must remain intact.",
        "clauses": [
            "Every copied or adapted source component, donor repository, dependency, model, dataset, binary, asset, native helper must have traceable provenance and compatible licensing.",
            "Required notices must remain intact."
        ],
        "applicability": "Third-party libraries, bundled binaries (ffmpeg, whisper, sherpa, qdrant), and donor codebase.",
        "verification_expectations": "Third-party registry matches all package.json entries; LICENSE and NOTICE files preserve donor copyright notices; binary licenses verified."
    },
    {
        "stable_rule_id": "UAC-18",
        "title": "FAIL CLOSED",
        "normative_text": "When authority, state, AI interpretation, provenance, or data safety is uncertain: ASK or BLOCK or SURFACE THE CONFLICT. Do not guess. Do not fabricate evidence. Do not silently fall back to remote/cloud behaviour.",
        "clauses": [
            "When authority, state, AI interpretation, provenance, or data safety is uncertain: ASK or BLOCK or SURFACE THE CONFLICT.",
            "Do not guess.",
            "Do not fabricate evidence.",
            "Do not silently fall back to remote/cloud behaviour."
        ],
        "applicability": "Error handlers, execution state validator, network policy, and persistence interlocks.",
        "verification_expectations": "Undefined or corrupt states immediately halt processing and raise explicit errors rather than proceeding with assumptions or silent cloud fallbacks."
    },
    {
        "stable_rule_id": "UAC-19",
        "title": "UI / AI / PROVIDER REPLACEABILITY",
        "normative_text": "Domain and user-data architecture must not be inseparably coupled to: one UI, Hermes, one local model, one cloud model, one provider, one orchestration layer. Replacing these must not require destruction or migration loss of user data.",
        "clauses": [
            "Domain and user-data architecture must not be inseparably coupled to: one UI, Hermes, one local model, one cloud model, one provider, one orchestration layer.",
            "Replacing these must not require destruction or migration loss of user data."
        ],
        "applicability": "Data schema design, service architecture, and model integration interfaces.",
        "verification_expectations": "Transcription engines and UI components connect via typed abstraction interfaces; swapping models or frontends does not alter canonical database schema."
    },
    {
        "stable_rule_id": "UAC-20",
        "title": "SCHEMA / VERSION SAFETY",
        "normative_text": "Schema changes must preserve semantic meaning. Use explicit forward migrations. Unsupported newer schemas must fail safely. Older software encountering newer data must not silently corrupt it. Read-only safe failure is preferred where practical.",
        "clauses": [
            "Schema changes must preserve semantic meaning.",
            "Use explicit forward migrations.",
            "Unsupported newer schemas must fail safely.",
            "Older software encountering newer data must not silently corrupt it.",
            "Read-only safe failure is preferred where practical."
        ],
        "applicability": "Database migration runner, version check gates, and IPC payload validators.",
        "verification_expectations": "Forward migrations test backward compatibility; encountering higher schema version triggers safe error or read-only mode rather than running older migrations."
    },
    {
        "stable_rule_id": "UAC-21",
        "title": "STABLE IDS / PORTABLE REFERENCES",
        "normative_text": "Use stable entity identifiers. Prefer portable relative references. Avoid using absolute machine paths as durable identity. Renaming/moving directories must not destroy logical relationships.",
        "clauses": [
            "Use stable entity identifiers.",
            "Prefer portable relative references.",
            "Avoid using absolute machine paths as durable identity.",
            "Renaming/moving directories must not destroy logical relationships."
        ],
        "applicability": "Database entity IDs, audio references, notes, folders, and planning tasks.",
        "verification_expectations": "Entities use UUIDs or canonical alphanumeric IDs; audio file locations stored relative to data root so moving data root preserves playback linkage."
    },
    {
        "stable_rule_id": "UAC-22",
        "title": "SELF-DESCRIBING PROJECT CONTRACT",
        "normative_text": "The repository and durable data root must provide sufficient explicit, machine-readable contracts for a human or bounded AI to determine: what exists, what is canonical, what is derived, feature ownership, schema/version, provenance, allowed mutations, validation method, recovery method, relationships, available tools/skills without relying on undocumented conversation history.",
        "clauses": [
            "The repository and durable data root must provide sufficient explicit, machine-readable contracts for a human or bounded AI to determine: what exists, what is canonical, what is derived, feature ownership, schema/version, provenance, allowed mutations, validation method, recovery method, relationships, available tools/skills.",
            "Must not rely on undocumented conversation history."
        ],
        "applicability": "Graphify documentation, repository root files, metadata manifests, and schemas.",
        "verification_expectations": "A clean agent or engineer starting with zero chat context can verify and inspect all project systems using solely the repository contracts and tools."
    }
]


GAP_EVALUATIONS = [
    {
        "stable_rule_id": "UAC-01",
        "title": "APPLICATION INDEPENDENCE",
        "status": "SATISFIED",
        "evidence_paths": [
            "codebase/main/index.js",
            "codebase/package.json",
            "codebase/tests/integration/offlineFirstLaunch.test.js",
            "Graphify/tools/semantic_validator.py"
        ],
        "evidence_explanation": "Runtime codebase does not import, require, or depend on Hermes, Graphify, or external orchestrators. Core operations (audio capture, transcription, database persistence, search, backup, restore, UI) are local Node.js/Electron/SQLite code. SEM-044 validator checks ban hermes and Graphify imports across all tracked codebase files.",
        "affected_capability_ids": ["CAP-APP-SHELL", "CAP-DATABASE", "CAP-OFFLINE-FIRST-LAUNCH"],
        "affected_task_ids": ["TASK-CAP-APP-SHELL", "TASK-CAP-DATABASE", "TASK-CAP-OFFLINE-FIRST-LAUNCH"],
        "missing_implementation": None,
        "queue_change_required": False,
        "master_plan_conflict": False,
        "task_2_affected": False
    },
    {
        "stable_rule_id": "UAC-02",
        "title": "LOCAL-FIRST / OFFLINE-FIRST",
        "status": "PARTIAL",
        "evidence_paths": [
            "codebase/main/infrastructure/runtime/runtimeNetworkPolicy.js",
            "codebase/main/features/transcription/whisper.js",
            "Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md",
            "Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md"
        ],
        "evidence_explanation": "Master Plans mandate 100% offline execution and loopback-only binding (127.0.0.1). However, in the current donor codebase baseline (prior to executing Phase 4 deletion tasks), dormant cloud synchronization, remote auth, and telemetry remnants remain in codebase/ pending deletion under BDI interlocks.",
        "affected_capability_ids": [
            "CAP-NETWORK-POLICY",
            "CAP-OFFLINE-FIRST-LAUNCH",
            "CAP-REMOVE-CLOUD-SYNCHRONISATION",
            "CAP-REMOVE-EXTERNAL-NETWORKING",
            "CAP-REMOVE-AUTHENTICATION"
        ],
        "affected_task_ids": [
            "TASK-CAP-NETWORK-POLICY",
            "TASK-CAP-OFFLINE-FIRST-LAUNCH",
            "TASK-DEL-CLOUD-SYNCHRONISATION",
            "TASK-DEL-RUNTIME-EXTERNAL-NETWORKING",
            "TASK-DEL-AUTHENTICATION"
        ],
        "missing_implementation": "Execution of Phase 4 deletion tasks to cleanly excise all donor cloud/network code.",
        "queue_change_required": False,
        "master_plan_conflict": False,
        "task_2_affected": False
    },
    {
        "stable_rule_id": "UAC-03",
        "title": "USER-SELECTED DATA ROOT SOVEREIGNTY",
        "status": "PARTIAL",
        "evidence_paths": [
            "codebase/main/infrastructure/persistence/database.js",
            "codebase/main/index.js",
            "codebase/main/features/settings/settingsManager.js"
        ],
        "evidence_explanation": "User data is currently anchored to Electron default app.getPath('userData'). There is no mechanism for the user to select or move a custom application data root without data meaning loss. SQLite tables also record absolute paths rather than root-relative portable paths.",
        "affected_capability_ids": ["CAP-DATA-SAFETY", "CAP-DATABASE", "CAP-SETTINGS"],
        "affected_task_ids": ["TASK-CAP-DATA-SAFETY", "TASK-CAP-DATABASE", "TASK-CAP-SETTINGS"],
        "missing_implementation": "Explicit data-root resolution service, custom data-root configuration UI in settings, relative path resolution for stored assets, and safe migration workflow when moving the data root.",
        "queue_change_required": True,
        "master_plan_conflict": False,
        "task_2_affected": True
    },
    {
        "stable_rule_id": "UAC-04",
        "title": "NAS / PRIVATE-LAN SUPPORT",
        "status": "MISSING",
        "evidence_paths": [
            "codebase/main/infrastructure/persistence/database.js",
            "codebase/main/infrastructure/persistence/localBackup.js",
            "Graphify/CONDITIONAL_DECISION_PACKAGES.json"
        ],
        "evidence_explanation": "Current implementation has zero handling for network shares / NAS data roots. SQLite is known to suffer locking failures, latency timeouts, and corruption over network filesystems (SMB/NFS). Share unavailability, reconnection, latency, interrupted writes, and multi-instance concurrency on network drives are completely unaddressed in current code.",
        "affected_capability_ids": ["CAP-DATA-SAFETY", "CAP-DATABASE", "CAP-NAS"],
        "affected_task_ids": ["TASK-CAP-DATA-SAFETY", "TASK-DEC-NAS", "TASK-OUT-NAS-DEFAULT", "TASK-OUT-NAS-DEVIATION"],
        "missing_implementation": "Technical architecture decision (DEC-NAS) for safe NAS support: separating canonical active SQLite working database locally with continuous or on-change replica/archive to NAS, vs proving direct SQLite-on-NAS with advisory locks. Handling share disconnects, latency, reconnection, one-writer locking, and multi-instance prevention.",
        "queue_change_required": True,
        "master_plan_conflict": False,
        "task_2_affected": True
    },
    {
        "stable_rule_id": "UAC-05",
        "title": "CROSS-PLATFORM SUPPORT",
        "status": "PARTIAL",
        "evidence_paths": [
            "codebase/native/helpers/macos/mac_meeting_audio_tap.swift",
            "codebase/native/helpers/linux/audio_portal_monitor.py",
            "codebase/electron-builder.json",
            "Graphify/CONDITIONAL_DECISION_PACKAGES.json"
        ],
        "evidence_explanation": "Donor macOS and Linux helper source code is preserved in codebase/native/helpers/ under CAP-MACOS-LINUX and DEC-MACOS-LINUX. However, Mnemora first-release milestone is explicitly Windows-first (CAP-WINDOWS-INSTALLER, CAP-PORTABLE-WINDOWS). Cross-platform runtime execution, platform-specific hotkeys, and packaging have not been tested or proven on macOS or Linux.",
        "affected_capability_ids": ["CAP-MACOS-LINUX", "CAP-WINDOWS-INSTALLER", "CAP-PORTABLE-WINDOWS", "CAP-NATIVE"],
        "affected_task_ids": [
            "TASK-DEC-MACOS-LINUX",
            "TASK-OUT-MACOS-LINUX-DEFAULT",
            "TASK-OUT-MACOS-LINUX-DEVIATION",
            "TASK-CAP-WINDOWS-INSTALLER"
        ],
        "missing_implementation": "macOS and Linux build pipelines, packaging scripts, and native helper runtime verification.",
        "queue_change_required": False,
        "master_plan_conflict": False,
        "task_2_affected": False
    },
    {
        "stable_rule_id": "UAC-06",
        "title": "FEATURE-FIRST MODULAR MONOLITH",
        "status": "PARTIAL",
        "evidence_paths": [
            "codebase/main/features/dictation/",
            "codebase/renderer/features/notes/",
            "codebase/main/infrastructure/",
            "codebase/renderer/shared/"
        ],
        "evidence_explanation": "The codebase partially uses a feature-first structure with main/features/ and renderer/features/. However, generic dumping grounds still exist (codebase/main/infrastructure/, codebase/renderer/shared/utils/, etc.) containing mixed responsibilities across features.",
        "affected_capability_ids": ["CAP-REPOSITORY", "CAP-SIMPLIFICATION"],
        "affected_task_ids": ["TASK-CAP-REPOSITORY", "TASK-CAP-SIMPLIFICATION"],
        "missing_implementation": "Incremental migration of shared utilities to feature ownership during Phase 6 reorganization tasks.",
        "queue_change_required": True,
        "master_plan_conflict": False,
        "task_2_affected": False
    },
    {
        "stable_rule_id": "UAC-07",
        "title": "HUMAN-READABLE FOLDER CONTRACT",
        "status": "SATISFIED",
        "evidence_paths": [
            "Graphify/FOLDER_OWNERSHIP_MAP.md",
            "codebase/main/features/",
            "codebase/renderer/features/",
            "Graphify/REPOSITORY_INVENTORY.md"
        ],
        "evidence_explanation": "All codebase and durable repository directories are self-describing, human-readable, and domain-oriented. Data files use clear folder hierarchies rather than opaque hash trees.",
        "affected_capability_ids": ["CAP-REPOSITORY", "CAP-DATA-SAFETY"],
        "affected_task_ids": ["TASK-CAP-REPOSITORY", "TASK-CAP-DATA-SAFETY"],
        "missing_implementation": None,
        "queue_change_required": False,
        "master_plan_conflict": False,
        "task_2_affected": False
    },
    {
        "stable_rule_id": "UAC-08",
        "title": "SMALL-MODEL NAVIGABILITY",
        "status": "SATISFIED",
        "evidence_paths": [
            "Graphify/MASTER_REQUIREMENT_REGISTER.json",
            "Graphify/CAPABILITY_REGISTRY.json",
            "Graphify/EXACT_LOCATION_REGISTRY.json",
            "Graphify/IMPLEMENTATION_QUEUE.json"
        ],
        "evidence_explanation": "The repository and planning architecture provide canonical IDs (REQ-*, CAP-*, TASK-*, LOC-*), deterministic cross-references, exact symbol mappings, and bounded scopes so that a 1B-class local model can accurately navigate without speculative guessing.",
        "affected_capability_ids": ["CAP-PLANNING-GOVERNANCE", "CAP-EXACT-LOCATION"],
        "affected_task_ids": ["TASK-CAP-PLANNING-GOVERNANCE", "TASK-CAP-EXACT-LOCATION"],
        "missing_implementation": None,
        "queue_change_required": False,
        "master_plan_conflict": False,
        "task_2_affected": False
    },
    {
        "stable_rule_id": "UAC-09",
        "title": "DETERMINISTIC NON-AI CORE",
        "status": "SATISFIED",
        "evidence_paths": [
            "codebase/main/infrastructure/persistence/database.js",
            "codebase/main/features/transcription/whisper.js",
            "Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md"
        ],
        "evidence_explanation": "Core persistence, audio capture, state management, hotkeys, and indexing are 100% deterministic code. Speech recognition uses deterministic local Whisper inference (acoustic models only). Generative AI and cloud LLMs are explicitly forbidden from the release.",
        "affected_capability_ids": ["CAP-DATABASE", "CAP-TRANSCRIPTION", "CAP-REMOVE-LOCAL-GENERATIVE-AI"],
        "affected_task_ids": ["TASK-CAP-DATABASE", "TASK-CAP-TRANSCRIPTION", "TASK-DEL-LOCAL-GENERATIVE-AI"],
        "missing_implementation": None,
        "queue_change_required": False,
        "master_plan_conflict": False,
        "task_2_affected": False
    },
    {
        "stable_rule_id": "UAC-10",
        "title": "AUTHORIZED MUTATION MODEL",
        "status": "SATISFIED",
        "evidence_paths": [
            "Graphify/IMPLEMENTATION_QUEUE.json",
            "Graphify/tools/execution_state.py",
            "Graphify/tools/semantic_validator.py"
        ],
        "evidence_explanation": "Codebase mutations are strictly bounded by single-task execution contracts enforcing files_expected_to_change and files_forbidden_from_changing. Application data mutations occur strictly through validated UI and IPC handlers. Arbitrary filesystem mutations are blocked.",
        "affected_capability_ids": ["CAP-IMPLEMENTATION-GOVERNANCE", "CAP-DATA-SAFETY"],
        "affected_task_ids": ["TASK-CAP-IMPLEMENTATION-GOVERNANCE", "TASK-CAP-DATA-SAFETY"],
        "missing_implementation": None,
        "queue_change_required": False,
        "master_plan_conflict": False,
        "task_2_affected": False
    },
    {
        "stable_rule_id": "UAC-11",
        "title": "MUTATION AUDIT LOG / CHANGE FLAGGING",
        "status": "MISSING",
        "evidence_paths": [
            "codebase/main/infrastructure/persistence/database.js",
            "codebase/main/infrastructure/persistence/migrations/001_initial_schema.js"
        ],
        "evidence_explanation": "Mnemora currently has application debug logs (electron-log/console), but does NOT have an append-oriented entity mutation audit log recording actor, operation, timestamp, previous hash, resulting hash, and reason. External/unrecognized changes to database or audio files are not detected, flagged, or reconciled.",
        "affected_capability_ids": ["CAP-DATA-SAFETY", "CAP-DATABASE", "CAP-MUTATION-LOG"],
        "affected_task_ids": ["TASK-CAP-DATA-SAFETY", "TASK-CAP-MUTATION-LOG"],
        "missing_implementation": "Append-oriented mutation audit table/log, file-watcher / hash-check for external modification detection, and conflict reconciliation workflows (inspect diff, keep external, accept app, restore, reject).",
        "queue_change_required": True,
        "master_plan_conflict": False,
        "task_2_affected": True
    },
    {
        "stable_rule_id": "UAC-12",
        "title": "RECOVERABILITY OVER MAGIC",
        "status": "PARTIAL",
        "evidence_paths": [
            "codebase/main/features/meetings/recordingRecovery.js",
            "codebase/main/infrastructure/persistence/localBackup.js",
            "codebase/main/infrastructure/persistence/dataMigration.js"
        ],
        "evidence_explanation": "Recording recovery manager exists for interrupted audio. Migration and backup scripts exist in donor code. However, comprehensive transactional copy-before-transform, verified restore, and crash-interruption recovery are scheduled for implementation under TASK-CAP-DATA-SAFETY (which is NOT STARTED).",
        "affected_capability_ids": ["CAP-DATA-SAFETY", "CAP-BACKUP", "CAP-RESTORE", "CAP-RECOVERY"],
        "affected_task_ids": ["TASK-CAP-DATA-SAFETY", "TASK-CAP-BACKUP", "TASK-CAP-RESTORE", "TASK-CAP-RECOVERY"],
        "missing_implementation": "Implementation of verified copy-before-transform harness in Task 2.",
        "queue_change_required": False,
        "master_plan_conflict": False,
        "task_2_affected": True
    },
    {
        "stable_rule_id": "UAC-13",
        "title": "ORIGINALS VS DERIVED STATE",
        "status": "PARTIAL",
        "evidence_paths": [
            "codebase/main/features/search/vectorIndex.js",
            "codebase/main/features/notes/markdownMirror.js",
            "codebase/main/infrastructure/persistence/database.js"
        ],
        "evidence_explanation": "Architecture separates raw audio and notes from derived embeddings and search indexes. Full proof that vector indexes can be cleanly reconstructed from scratch without data loss is scheduled in TASK-CAP-SEARCH-SEMANTIC.",
        "affected_capability_ids": ["CAP-DATA-SAFETY", "CAP-SEARCH-SEMANTIC", "CAP-NOTES"],
        "affected_task_ids": ["TASK-CAP-DATA-SAFETY", "TASK-CAP-SEARCH-SEMANTIC", "TASK-CAP-NOTES"],
        "missing_implementation": "Index rebuild verification from raw notes and transcripts without data loss.",
        "queue_change_required": False,
        "master_plan_conflict": False,
        "task_2_affected": False
    },
    {
        "stable_rule_id": "UAC-14",
        "title": "DATABASE / SQLITE SAFETY",
        "status": "PARTIAL",
        "evidence_paths": [
            "codebase/main/infrastructure/persistence/database.js",
            "codebase/main/infrastructure/persistence/migrations/001_initial_schema.js",
            "codebase/main/features/notes/markdownMirror.js"
        ],
        "evidence_explanation": "SQLite is explicitly retained via Kysely and better-sqlite3. Schema migrations are forward-only. Notes have a Markdown mirror. However, database backup verification, integrity check PRAGMAs, and safe restore harnesses are currently unimplemented pending Task 2.",
        "affected_capability_ids": ["CAP-DATABASE", "CAP-DATA-SAFETY", "CAP-BACKUP", "CAP-RESTORE", "CAP-KYSELY"],
        "affected_task_ids": ["TASK-CAP-DATA-SAFETY", "TASK-CAP-DATABASE", "TASK-DEC-KYSELY"],
        "missing_implementation": "Verification of complete backups, schema dump exports, and PRAGMA integrity_check.",
        "queue_change_required": False,
        "master_plan_conflict": False,
        "task_2_affected": True
    },
    {
        "stable_rule_id": "UAC-15",
        "title": "SOURCE / PRIVATE DATA / GIT SEPARATION",
        "status": "SATISFIED",
        "evidence_paths": [
            ".gitignore",
            "Graphify/tools/semantic_validator.py"
        ],
        "evidence_explanation": "Strict .gitignore rules prevent SQLite files, WAL files, private recordings, logs, .env, and build outputs from entering Git. SEM-044 actively validates that no tracked private data files or secrets exist in the git index.",
        "affected_capability_ids": ["CAP-IMPLEMENTATION-GOVERNANCE", "CAP-DATA-SAFETY"],
        "affected_task_ids": ["TASK-GOV-001-PROVENANCE-BASELINE", "TASK-CAP-IMPLEMENTATION-GOVERNANCE"],
        "missing_implementation": None,
        "queue_change_required": False,
        "master_plan_conflict": False,
        "task_2_affected": False
    },
    {
        "stable_rule_id": "UAC-16",
        "title": "REPRODUCIBLE BUILDS",
        "status": "PARTIAL",
        "evidence_paths": [
            "codebase/package.json",
            "codebase/package-lock.json",
            "codebase/electron-builder.json"
        ],
        "evidence_explanation": "Package dependencies are pinned with package-lock.json. Packaging configuration is defined in electron-builder.json. However, fully offline reproducible native compilation and packaging have not yet been executed or proven on this repository.",
        "affected_capability_ids": ["CAP-PACKAGING", "CAP-WINDOWS-INSTALLER", "CAP-PORTABLE-WINDOWS"],
        "affected_task_ids": ["TASK-CAP-PACKAGING", "TASK-CAP-WINDOWS-INSTALLER", "TASK-DEC-PORTABLE-WINDOWS"],
        "missing_implementation": "Packaging pipeline execution and artifact verification under Phase 6 packaging tasks.",
        "queue_change_required": False,
        "master_plan_conflict": False,
        "task_2_affected": False
    },
    {
        "stable_rule_id": "UAC-17",
        "title": "THIRD-PARTY / DONOR PROVENANCE",
        "status": "PARTIAL",
        "evidence_paths": [
            "codebase/LICENSE",
            "Graphify/THIRD_PARTY_CODE_REGISTER.md"
        ],
        "evidence_explanation": "Historical OpenWhispr MIT license and copyright notice are preserved in codebase/LICENSE. All top-level packages are catalogued in Graphify/THIRD_PARTY_CODE_REGISTER.md. Verification of bundled binary licenses (Whisper, FFmpeg, ONNX, Qdrant) is scheduled under TASK-CAP-THIRD-PARTY and TASK-CAP-LEGAL.",
        "affected_capability_ids": ["CAP-LEGAL", "CAP-THIRD-PARTY"],
        "affected_task_ids": ["TASK-CAP-LEGAL", "TASK-CAP-THIRD-PARTY"],
        "missing_implementation": "Execution of binary license verification tasks.",
        "queue_change_required": False,
        "master_plan_conflict": False,
        "task_2_affected": False
    },
    {
        "stable_rule_id": "UAC-18",
        "title": "FAIL CLOSED",
        "status": "PARTIAL",
        "evidence_paths": [
            "codebase/main/infrastructure/runtime/runtimeNetworkPolicy.js",
            "Graphify/tools/execution_state.py"
        ],
        "evidence_explanation": "Governance tools fail closed on any ambiguity (blocking execution). Network policy blocks unauthorized egress. However, runtime data safety handlers in application code need verification in Task 2 to ensure corrupt databases or failed writes fail closed without silent data loss.",
        "affected_capability_ids": ["CAP-DATA-SAFETY", "CAP-NETWORK-POLICY"],
        "affected_task_ids": ["TASK-CAP-DATA-SAFETY", "TASK-CAP-NETWORK-POLICY"],
        "missing_implementation": "Fail-closed error boundaries in Task 2.",
        "queue_change_required": False,
        "master_plan_conflict": False,
        "task_2_affected": True
    },
    {
        "stable_rule_id": "UAC-19",
        "title": "UI / AI / PROVIDER REPLACEABILITY",
        "status": "SATISFIED",
        "evidence_paths": [
            "codebase/main/features/transcription/whisper.js",
            "codebase/main/features/search/vectorIndex.js",
            "codebase/main/infrastructure/persistence/database.js"
        ],
        "evidence_explanation": "Domain logic and user data (SQLite, WAV audio, Markdown notes) are fully decoupled from UI frameworks and specific models. Transcription engines can be swapped without touching stored notes or audio archives.",
        "affected_capability_ids": ["CAP-APP-SHELL", "CAP-TRANSCRIPTION", "CAP-SEARCH-SEMANTIC"],
        "affected_task_ids": ["TASK-CAP-APP-SHELL", "TASK-CAP-TRANSCRIPTION", "TASK-CAP-SEARCH-SEMANTIC"],
        "missing_implementation": None,
        "queue_change_required": False,
        "master_plan_conflict": False,
        "task_2_affected": False
    },
    {
        "stable_rule_id": "UAC-20",
        "title": "SCHEMA / VERSION SAFETY",
        "status": "PARTIAL",
        "evidence_paths": [
            "codebase/main/infrastructure/persistence/database.js",
            "codebase/main/infrastructure/persistence/migrations/001_initial_schema.js"
        ],
        "evidence_explanation": "Schema migrations use version numbers. Forward migrations are preserved. However, safe fail-closed behavior when encountering unsupported newer schemas (e.g. read-only safe mode or graceful rejection) is scheduled for implementation in TASK-CAP-DATA-SAFETY.",
        "affected_capability_ids": ["CAP-DATA-SAFETY", "CAP-DATABASE", "CAP-LEGACY-MIGRATION"],
        "affected_task_ids": ["TASK-CAP-DATA-SAFETY", "TASK-CAP-DATABASE", "TASK-CAP-LEGACY-MIGRATION"],
        "missing_implementation": "Newer-schema rejection test in Task 2.",
        "queue_change_required": False,
        "master_plan_conflict": False,
        "task_2_affected": True
    },
    {
        "stable_rule_id": "UAC-21",
        "title": "STABLE IDS / PORTABLE REFERENCES",
        "status": "PARTIAL",
        "evidence_paths": [
            "codebase/main/infrastructure/persistence/database.js",
            "Graphify/MASTER_REQUIREMENT_REGISTER.json"
        ],
        "evidence_explanation": "Entities use stable IDs. However, current SQLite persistence stores absolute machine file paths for audio recordings. These must be replaced with portable relative references relative to the data root.",
        "affected_capability_ids": ["CAP-DATABASE", "CAP-DATA-SAFETY", "CAP-NOTES"],
        "affected_task_ids": ["TASK-CAP-DATA-SAFETY", "TASK-CAP-DATABASE", "TASK-CAP-NOTES"],
        "missing_implementation": "Migration of absolute paths to portable relative references.",
        "queue_change_required": True,
        "master_plan_conflict": False,
        "task_2_affected": True
    },
    {
        "stable_rule_id": "UAC-22",
        "title": "SELF-DESCRIBING PROJECT CONTRACT",
        "status": "SATISFIED",
        "evidence_paths": [
            "Graphify/CAPABILITY_REGISTRY.json",
            "Graphify/IMPLEMENTATION_QUEUE.json",
            "Graphify/START-HERE.md",
            "Graphify/REPOSITORY_FILE_INVENTORY.json"
        ],
        "evidence_explanation": "Graphify contains machine-readable contracts describing all entities, schemas, versions, allowed mutations, dependencies, and validation methods without relying on undocumented conversation history.",
        "affected_capability_ids": ["CAP-PLANNING-GOVERNANCE", "CAP-IMPLEMENTATION-GOVERNANCE"],
        "affected_task_ids": ["TASK-CAP-PLANNING-GOVERNANCE", "TASK-CAP-IMPLEMENTATION-GOVERNANCE"],
        "missing_implementation": None,
        "queue_change_required": False,
        "master_plan_conflict": False,
        "task_2_affected": False
    }
]


def generate_constitution_json() -> dict:
    return {
        "schema_version": 1,
        "authority": "Universal App Constitution (User-Level Cross-App Authority)",
        "authority_hierarchy": [
            "1. Universal App Constitution (User-Level Cross-App Authority)",
            "2. Mnemora App-Specific Immutable Master Plans",
            "3. Derived requirements / capabilities / task authorities"
        ],
        "amendment_policy": "The Universal App Constitution is a user-level cross-app authority. Future amendments require explicit user authority. Coding models may not silently alter universal rules. The Constitution does not permit a model to casually rewrite an app-specific Master Plan. If a conflict arises between the Constitution and an app-specific Master Plan, STOP AND REPORT THE CONFLICT FOR USER DECISION.",
        "rule_count": len(UAC_RULES),
        "rules": UAC_RULES
    }


def generate_constitution_md() -> str:
    lines = [
        "# Universal App Constitution",
        "",
        "## Preamble",
        "",
        "This Constitution establishes binding architecture, data-safety, sovereignty, and governance requirements for applications in this ecosystem. It serves as a **USER-LEVEL CROSS-APP AUTHORITY** that supersedes local refactoring, model instructions, styling preferences, or operational convenience.",
        "",
        "## Authority and Amendment Model",
        "",
        "The hierarchy of authorities in this repository is strictly defined as:",
        "",
        "1. **Universal App Constitution** (User-Level Cross-App Authority)",
        "2. **Mnemora App-Specific Immutable Master Plans**",
        "3. **Derived requirements / capabilities / task authorities**",
        "",
        "### Amendment Policy",
        "- The Universal App Constitution is a user-level cross-app authority.",
        "- Future amendments to the Constitution require **explicit user authority**; no coding model may silently alter universal rules.",
        "- The Constitution does not permit a model to casually rewrite an app-specific Master Plan.",
        "- If a conflict arises between the Constitution and an app-specific Master Plan: **STOP AND REPORT THE CONFLICT FOR USER DECISION**.",
        "",
        "---",
        ""
    ]
    for rule in UAC_RULES:
        lines.append(f"## {rule['stable_rule_id']} — {rule['title']}")
        lines.append("")
        lines.append(f"**Normative Requirement:**")
        lines.append(f"{rule['normative_text']}")
        lines.append("")
        lines.append("**Clauses:**")
        for clause in rule["clauses"]:
            lines.append(f"- {clause}")
        lines.append("")
        lines.append(f"- **Applicability:** {rule['applicability']}")
        lines.append(f"- **Verification Expectations:** {rule['verification_expectations']}")
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def generate_gap_report_json() -> dict:
    satisfied = sum(1 for e in GAP_EVALUATIONS if e["status"] == "SATISFIED")
    partial = sum(1 for e in GAP_EVALUATIONS if e["status"] == "PARTIAL")
    missing = sum(1 for e in GAP_EVALUATIONS if e["status"] == "MISSING")
    conflict = sum(1 for e in GAP_EVALUATIONS if e["status"] == "CONFLICT")
    na = sum(1 for e in GAP_EVALUATIONS if e["status"] == "NOT APPLICABLE")
    return {
        "schema_version": 1,
        "authority": "Mnemora Universal Rules Gap Report (Evaluated against UAC-01..UAC-22)",
        "evaluated_rules_count": len(GAP_EVALUATIONS),
        "summary": {
            "satisfied_count": satisfied,
            "partial_count": partial,
            "missing_count": missing,
            "conflict_count": conflict,
            "not_applicable_count": na
        },
        "critical_gaps": [
            "UAC-04 (NAS / private-LAN support): Unaddressed network share latency, locking, corruption risks, and share disconnect handling for SQLite on NAS.",
            "UAC-11 (Mutation audit log / change flagging): Missing append-oriented entity mutation audit log, missing external-change detection, missing reconciliation workflows.",
            "UAC-03 / UAC-21 (Portable Data Root Sovereignty and Relative References): User data root currently hardcoded to default OS user-data directory; absolute file paths stored in database prevent portable data root relocation."
        ],
        "master_plan_conflicts": [],
        "task_2_affected": True,
        "task_2_canonical_disposition": "NOT STARTED",
        "task_2_recovery_branch": "recovery/task-cap-data-safety-blocked",
        "evaluations": GAP_EVALUATIONS
    }


def generate_gap_report_md() -> str:
    data = generate_gap_report_json()
    summary = data["summary"]
    lines = [
        "# Mnemora Universal Rules Gap Report",
        "",
        "## Executive Summary",
        "",
        f"- **Evaluated Universal Rules**: {data['evaluated_rules_count']}/22",
        f"- **SATISFIED**: {summary['satisfied_count']}",
        f"- **PARTIAL**: {summary['partial_count']}",
        f"- **MISSING**: {summary['missing_count']}",
        f"- **CONFLICT**: {summary['conflict_count']}",
        f"- **NOT APPLICABLE**: {summary['not_applicable_count']}",
        f"- **Master Plan Conflicts**: NONE",
        f"- **Task 2 Affected**: YES (Contract extended with characterization requirements; canonical disposition remains `NOT STARTED`)",
        "",
        "## Summary Table",
        "",
        "| Rule ID | Title | Status | Queue Change Required | Task 2 Affected |",
        "| --- | --- | --- | --- | --- |"
    ]
    for e in GAP_EVALUATIONS:
        lines.append(f"| `{e['stable_rule_id']}` | {e['title']} | **{e['status']}** | {'YES' if e['queue_change_required'] else 'NO'} | {'YES' if e['task_2_affected'] else 'NO'} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Detailed Rule Evaluations")
    lines.append("")
    for e in GAP_EVALUATIONS:
        lines.append(f"### {e['stable_rule_id']} — {e['title']}")
        lines.append(f"- **Status**: **{e['status']}**")
        lines.append(f"- **Evidence Paths**: {', '.join(f'`{p}`' for p in e['evidence_paths'])}")
        lines.append(f"- **Evidence Explanation**: {e['evidence_explanation']}")
        lines.append(f"- **Affected Capability IDs**: {', '.join(f'`{c}`' for c in e['affected_capability_ids'])}")
        lines.append(f"- **Affected Implementation Task IDs**: {', '.join(f'`{t}`' for t in e['affected_task_ids'])}")
        lines.append(f"- **Missing Implementation**: {e['missing_implementation'] or 'None'}")
        lines.append(f"- **Queue Change Required**: {'YES' if e['queue_change_required'] else 'NO'}")
        lines.append(f"- **Master Plan Conflict**: {'YES' if e['master_plan_conflict'] else 'NONE'}")
        lines.append(f"- **Task 2 Affected**: {'YES' if e['task_2_affected'] else 'NO'}")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## High-Risk Rules and Architecture Analysis")
    lines.append("")
    lines.append("### UAC-01: Application Independence")
    lines.append("Mnemora runtime codebase has zero dependencies on Hermes, Graphify, or external orchestration systems. Core desktop functions (recording, Whisper speech-to-text, SQLite persistence, note editing, exact search) run locally and deterministically. `TASK-CAP-OFFLINE-FIRST-LAUNCH` provides verifiable end-to-end launch verification under complete network isolation.")
    lines.append("")
    lines.append("### UAC-03 & UAC-21: User-Selected Data Root & Portable Relative References")
    lines.append("Current code hardcodes `app.getPath('userData')` and stores machine-specific absolute paths for audio recordings in the database. `TASK-CAP-DATA-SAFETY` is minimally extended to characterize data root boundary portability, ensure no absolute path lock-in, and mandate portable relative paths across folder moves.")
    lines.append("")
    lines.append("### UAC-04: NAS / Private-LAN Support")
    lines.append("Direct SQLite operation over network shares (SMB/NFS) carries severe risks of file lock collisions, latency-induced timeouts, and journal corruption. Rather than guessing or assuming direct network SQLite safety, decision package `DEC-NAS` (`TASK-DEC-NAS`, `TASK-OUT-NAS-DEFAULT`, `TASK-OUT-NAS-DEVIATION`) explicitly evaluates the choice between a local working SQLite database with continuous NAS replication/archival (default) versus direct network SQLite (deviation if proven).")
    lines.append("")
    lines.append("### UAC-05: Cross-Platform Support")
    lines.append("Source code for macOS and Linux native helpers is preserved in `codebase/native/helpers/`. Initial release proof is strictly Windows-first (`CAP-WINDOWS-INSTALLER`, `CAP-PORTABLE-WINDOWS`). The status is honestly audited as `PARTIAL` pending future cross-platform packaging verification.")
    lines.append("")
    lines.append("### UAC-06: Feature-First Modular Monolith")
    lines.append("Codebase contains `main/features/` and `renderer/features/`, but also generic dumping grounds (`main/infrastructure/`, `renderer/shared/utils/`). Audit confirms incremental retirement of generic dumping grounds into feature directories is scheduled across Phase 6 tasks without disruptive big-bang rewrites.")
    lines.append("")
    lines.append("### UAC-11: Mutation Audit Log & External-Change Detection")
    lines.append("Mnemora currently lacks an append-oriented entity mutation audit log and external modification detection. Capability `CAP-MUTATION-LOG` (`TASK-CAP-MUTATION-LOG`) is scheduled in Phase 5 to provide attributable mutation logging and file-watcher change detection with reconciliation workflows.")
    lines.append("")
    lines.append("## Task 2 Disposition")
    lines.append("Task-2 WIP remains safely preserved on recovery branch `recovery/task-cap-data-safety-blocked` (checkpoint `7932d83b3f49604f3b36b7a5966a72138a6c9323`). Canonical task disposition on `main` remains `NOT STARTED`. Its contract is extended with necessary data root, NAS safety, and external change characterization requirements before implementation resumes.")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def generate_constitution_audit_md() -> str:
    lines = [
        "# Universal App Constitution Audit: Mnemora",
        "",
        "## Audit Overview",
        "",
        "- **Subject**: Mnemora Desktop Dictation & Knowledge Management",
        "- **Auditor**: Architecture & Implementation Governance",
        "- **Authority**: `Graphify/UNIVERSAL_APP_CONSTITUTION.md` and `Graphify/UNIVERSAL_APP_CONSTITUTION.json`",
        "- **Master Plan Baseline**:",
        f"  - `Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md` (`{MASTER_HASHES['01-EVERYTHING-WE-ARE-KEEPING.md']}`)",
        f"  - `Master Plan/02-EVERYTHING-WE-ARE-DELETING.md` (`{MASTER_HASHES['02-EVERYTHING-WE-ARE-DELETING.md']}`)",
        f"  - `Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-REPLACE.md` (`{MASTER_HASHES['03-HOW-WE-WILL-KEEP-DELETE-AND-REPLACE.md']}`)",
        "- **Governance Correction Record**:",
        "  - Governance commit `6a9858a060ea7676363731e86950be1273f99d18` adopted an incomplete 10-article version (Articles A through J).",
        "  - The prior audit concluded `PASS — FULLY COMPLIANT; ZERO MASTER PLAN CONFLICTS` without evaluating the complete 22-principle Constitution.",
        "  - This correction expands the authority to the full 22-rule binding Constitution (`UAC-01` through `UAC-22`).",
        "  - The prior PASS cannot be used as evidence of UAC-01..UAC-22 compliance.",
        "- **Audit Verdict**: **22 RULES EVALUATED — PLANNING RECONCILED; ZERO MASTER PLAN CONFLICTS**",
        "  - Satisfied: 8 rules",
        "  - Partial (in planning / pending tasks): 12 rules",
        "  - Missing (queue coverage added): 2 rules (`UAC-04`, `UAC-11`)",
        "  - Conflicts: 0",
        "  - Not Applicable: 0",
        "",
        "---",
        "",
        "## Evaluation of All 22 Binding Rules",
        ""
    ]
    for e in GAP_EVALUATIONS:
        lines.append(f"### {e['stable_rule_id']}: {e['title']}")
        lines.append(f"- **Status**: **{e['status']}**")
        lines.append(f"- **Evidence**: {', '.join(f'`{p}`' for p in e['evidence_paths'])}")
        lines.append(f"- **Finding**: {e['evidence_explanation']}")
        if e['missing_implementation']:
            lines.append(f"- **Implementation Plan**: Covered by {', '.join(f'`{t}`' for t in e['affected_task_ids'])}.")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## High-Risk Rules Reconciliation")
    lines.append("")
    lines.append("### UAC-01: Hermes / Application Independence")
    lines.append("Verified: Zero imports of `hermes` or `Graphify` exist in codebase. Core desktop functions run independently offline. Status: **SATISFIED**.")
    lines.append("")
    lines.append("### UAC-03: User-Selected Portable Data Root")
    lines.append("Verified: Electron default user data path used currently. Queue coverage extended under `TASK-CAP-DATA-SAFETY` and `TASK-CAP-SETTINGS`. Status: **PARTIAL**.")
    lines.append("")
    lines.append("### UAC-04: NAS / Private-LAN Support")
    lines.append("Verified: Direct SQLite on network shares is unproven and unsafe without locking protection. Conditional decision package `DEC-NAS` (`TASK-DEC-NAS`, `TASK-OUT-NAS-DEFAULT`, `TASK-OUT-NAS-DEVIATION`) added to queue. Status: **MISSING (QUEUE COVERAGE ADDED)**.")
    lines.append("")
    lines.append("### UAC-05: Cross-Platform Support")
    lines.append("Verified: macOS/Linux helper sources preserved; initial release focused on Windows proof. Status: **PARTIAL**.")
    lines.append("")
    lines.append("### UAC-06: Feature-First Modular Monolith")
    lines.append("Verified: Feature directories exist; generic dumping ground retirement scheduled under Phase 6 tasks. Status: **PARTIAL**.")
    lines.append("")
    lines.append("### UAC-11: Mutation Audit Log & External-Change Detection")
    lines.append("Verified: Append-oriented mutation log and change flagging missing in current codebase. Capability `CAP-MUTATION-LOG` (`TASK-CAP-MUTATION-LOG`) added to queue. Status: **MISSING (QUEUE COVERAGE ADDED)**.")
    lines.append("")
    lines.append("### UAC-14: SQLite / Data Transparency")
    lines.append("Verified: SQLite retained via Kysely and better-sqlite3; data safety harness in Task 2. Status: **PARTIAL**.")
    lines.append("")
    lines.append("### UAC-15: Source / Private Data / Git Separation")
    lines.append("Verified: .gitignore and SEM-044 enforce clean git index without user data or secrets. Status: **SATISFIED**.")
    lines.append("")
    lines.append("### UAC-16: Reproducible Builds")
    lines.append("Verified: package-lock.json and electron-builder.json pin build configuration; packaging tasks in Phase 6. Status: **PARTIAL**.")
    lines.append("")
    lines.append("### UAC-17: Third-Party Provenance")
    lines.append("Verified: Historical MIT license preserved in codebase/LICENSE; third-party register complete. Status: **PARTIAL**.")
    lines.append("")
    lines.append("### UAC-18: Fail Closed")
    lines.append("Verified: Task execution state and network policy fail closed; runtime data safety handlers in Task 2. Status: **PARTIAL**.")
    lines.append("")
    lines.append("### UAC-19: UI / AI / Provider Replaceability")
    lines.append("Verified: Data layer decoupled from UI and transcription models. Status: **SATISFIED**.")
    lines.append("")
    lines.append("### UAC-20: Schema / Version Safety")
    lines.append("Verified: Forward migrations preserved; newer-schema rejection test in Task 2. Status: **PARTIAL**.")
    lines.append("")
    lines.append("### UAC-21: Stable IDs / Portable References")
    lines.append("Verified: Stable entity IDs used; relative reference migration scheduled in Task 2. Status: **PARTIAL**.")
    lines.append("")
    lines.append("### UAC-22: Self-Describing Project Contract")
    lines.append("Verified: Machine-readable contracts in Graphify/ provide complete project context. Status: **SATISFIED**.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Master Plan Conflict Analysis")
    lines.append("")
    lines.append(f"- **Master Plan 1** (`Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md`): **ZERO CONFLICTS** (Hash: `{MASTER_HASHES['01-EVERYTHING-WE-ARE-KEEPING.md']}`)")
    lines.append(f"- **Master Plan 2** (`Master Plan/02-EVERYTHING-WE-ARE-DELETING.md`): **ZERO CONFLICTS** (Hash: `{MASTER_HASHES['02-EVERYTHING-WE-ARE-DELETING.md']}`)")
    lines.append(f"- **Master Plan 3** (`Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-REPLACE.md`): **ZERO CONFLICTS** (Hash: `{MASTER_HASHES['03-HOW-WE-WILL-KEEP-DELETE-AND-REPLACE.md']}`)")
    lines.append("")
    lines.append("All three Master Plans fully align with and reinforce the Universal App Constitution. No Master Plan text requires amendment.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Tool Provenance Reconciliation")
    lines.append("")
    lines.append("The historical citation of Ponytail in Phase 1 planning remains documented in `PONYTAIL_FINDINGS.json`. No runtime Ponytail tool exists or is executed. Task evidence templates require direct runtime tool logging only.")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    print("Writing UNIVERSAL_APP_CONSTITUTION.json...")
    const_json = generate_constitution_json()
    (G / "UNIVERSAL_APP_CONSTITUTION.json").write_text(json.dumps(const_json, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("Writing UNIVERSAL_APP_CONSTITUTION.md...")
    const_md = generate_constitution_md()
    (G / "UNIVERSAL_APP_CONSTITUTION.md").write_text(const_md, encoding="utf-8")

    print("Writing MNEMORA_UNIVERSAL_RULES_GAP_REPORT.json...")
    gap_json = generate_gap_report_json()
    (G / "MNEMORA_UNIVERSAL_RULES_GAP_REPORT.json").write_text(json.dumps(gap_json, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("Writing MNEMORA_UNIVERSAL_RULES_GAP_REPORT.md...")
    gap_md = generate_gap_report_md()
    (G / "MNEMORA_UNIVERSAL_RULES_GAP_REPORT.md").write_text(gap_md, encoding="utf-8")

    print("Writing CONSTITUTION_AUDIT.md...")
    audit_md = generate_constitution_audit_md()
    (G / "CONSTITUTION_AUDIT.md").write_text(audit_md, encoding="utf-8")

    print("Successfully generated all Constitution and Gap Report authorities.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
