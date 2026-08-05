---
title: "Everything We Are Keeping"
project: "Mnemora"
status: "AUTHORITATIVE"
updated: "2026-07-28"
document_role: "Master Plan 1 of 3"
---

# Mnemora — Everything We Are Keeping

> **Project identity and scope lock:** Mnemora uses an OpenWhispr-derived architecture. Its retained product scope is Dictation, Meeting recording, Local transcription, SQLite, Notes, Diarization, and Exact and semantic search.

## Governing Rule

This document defines every original capability, implementation, dependency, asset, workflow, and architectural element that Mnemora intends to preserve. A file existing is not proof that a capability is complete. Graphify must map it, locate every implementation layer, separate unwanted coupling, test it, and classify it using these deterministic labels:

- `MANDATORY KEEP`
- `KEEP AND REPAIR`
- `KEEP AND REORGANISE`
- `KEEP AFTER DECOUPLING`
- `CONDITIONAL — REQUIRES EVIDENCE`
- `OPTIONAL LATER`
- `OBSOLETE — REMOVE AFTER VERIFIED REPLACEMENT`
- `FORBIDDEN`

Every conditional item must include:
- Mandatory default
- Deviation condition
- Required evidence
- Fallback

> Preserve working local code wherever possible. Repair before replacing. Recover exact upstream code before writing a new version. Copy and integrate licence-compatible code only when necessary.

## 1. Product and legal identity

- Classification: `MANDATORY KEEP`
- Keep the MIT licence, the original OpenWhispr copyright notice, all required permission notices, and all third-party notices.
- Keep acknowledgements and licences for Whisper, whisper.cpp, NVIDIA Parakeet, sherpa-onnx, ONNX Runtime, FFmpeg, Qdrant, MiniLM or any retained embedding model, Electron, React, Tiptap, shadcn/ui, Radix UI, and all retained native helpers or models.
- Allow old OpenWhispr names only in legal attribution, source-history records, legacy data migration, and legacy protocol compatibility.
- Legal files in Codebase must use plain-text filenames without extensions: `LICENSE`, `NOTICE`, `THIRD-PARTY-NOTICES`. No `.md` legal exceptions are permitted in Codebase.

## 2. Core desktop stack

- Classification: `MANDATORY KEEP`
- Electron, React, React DOM, TypeScript, Vite, Tailwind CSS, shadcn/ui, Radix UI, Zustand, better-sqlite3, FFmpeg, ONNX Runtime, Whisper.cpp, MiniLM embeddings, Tiptap, i18next, React i18next, Zod, ps-list, required archive libraries, and required native audio/paste helpers.
- Keep the current framework family. Do not rewrite React, replace Electron with Tauri, replace SQLite wholesale, or recreate transcription engines from scratch.
- **Kysely**: Classification: `CONDITIONAL — REQUIRES EVIDENCE`. Default: Keep when it provides useful type-safe local SQLite querying. Remove only when Graphify proves: it is used only by removed systems, or it duplicates another persistence layer; migration is safe; real tests prove no regression; removal provides measurable maintenance benefit. Do not order a full database rewrite for style. Fallback: Direct better-sqlite3 queries or verified existing query builder.

## 3. Application shell

- Classification: `KEEP AFTER DECOUPLING`
- Electron lifecycle, main-process window creation, renderer windows, preload bridge, typed internal IPC, system tray, window controls, single-instance behaviour, local custom protocol handling after renaming, platform permissions, dark/light appearance, local logging, and local crash diagnostics.
- Keep routing, preload, and IPC only after cloud, account, agent, and updater routes are separated from retained local routes.
- **WebSockets**: External WebSockets are forbidden. Loopback-only WebSockets are allowed only for a named, owned, bundled local service. Remove unused WebSocket packages.

## 4. Voice dictation

- Classification: `KEEP AND REPAIR`
- Global dictation hotkey, microphone selection, microphone capture, recording overlay, audio-level feedback, VAD, start/stop, cancellation, retry, local transcription, preview, automatic copy/paste, dictation history, language selection, local model selection, progress, error recovery, accessibility permissions, and platform paste/key/text-monitor helpers.
- Repair interrupted transcription recovery, source-audio association, local-engine labelling, and user-controlled dictation-audio retention where missing.

## 5. Local transcription engines

- **Whisper.cpp**: Classification: `MANDATORY KEEP`. Rules: Default bundled local transcription engine; required for dictation; required for meeting transcription; must not depend on runtime downloads; must have model validation, process cleanup, progress, retry, and error handling.
- **Parakeet and Sherpa-ONNX**: Classification: `CONDITIONAL — REQUIRES EVIDENCE`. Default: Preserve the existing working local implementation; treat as an optional offline engine or offline model pack; do not remove merely to reduce installer size; do not make mandatory in the default installer without packaging and platform evidence; Whisper.cpp remains fallback.
- Use a local-only fallback chain: preferred bundled engine, alternate bundled engine, then a clear local model/install error.

## 6. Local model handling

- Classification: `MANDATORY KEEP`
- Local model discovery, validation, bundled paths, metadata, versioning, platform/architecture checks, checksums, local storage configuration, model health, offline model-pack import, and bundled default model detection.
- Build-time acquisition scripts may remain only if they are unreachable from the installed application and clearly classified as build tooling.

## 7. Meeting recording

- Classification: `KEEP AND REPAIR`
- Manual start/stop, microphone capture, system audio, duration, recording status, overlays, meeting pill/banner, echo cancellation, audio mixing, recording finalisation, recording recovery, live transcription, post-meeting transcription, history, local metadata, playback, transcript-linked playback, local process-based meeting detection, local notifications, and tray controls.
- Repair crash recovery, processing stages, retry, storage estimates, and raw-audio retention controls.
- **Raw recordings**: Classification: `MANDATORY KEEP`. Default: Retain source recordings; delete only after: successful transcription, successful persistence, recovery confirmation, and explicit user-configured retention policy. Never silently delete recoverable source audio. Fallback: Retain original WAV/MP3 files in local storage.

## 8. Audio processing

- Classification: `MANDATORY KEEP`
- FFmpeg, normalisation, format conversion, WAV generation, channel/sample-rate conversion, microphone audio, system audio, audio-level detection, VAD, echo-cancellation helpers, native audio taps, platform-specific microphone/system-audio helpers, local temporary processing, cleanup, validation, recovery, duration detection, supported-format detection, local mixing, and local chunking required by local inference.

## 9. Speaker diarization

- Classification: `KEEP AND REPAIR`
- Local diarization models, speaker segmentation, speaker labels, timestamped speaker segments, local speaker embeddings, local voice fingerprinting (Classification: `CONDITIONAL — REQUIRES EVIDENCE`; Default: Keep if locally verified reliable without external services; Fallback: Manual speaker assignment and renaming), persisted assignments, renaming, transcript formatting, conversation segmentation, reprocessing, and model health.
- Complete merge/split speakers, rename-all, delete local profile, re-run diarization, colour consistency, and navigation by speaker.

## 10. Transcripts and history

- Classification: `MANDATORY KEEP`
- Dictation history, meeting transcripts, imported-media transcripts, timestamped segments, speaker labels, original and edited text, transcript editing, recording/meeting association, language, engine/model metadata, date, duration, processing status, indexing, reopening, safe deletion, local persistence, and export.
- Preserve structured transcript segments with start/end times, speaker ID, original text, edited text, confidence scores, source recording, and processing state.

## 11. Notes

- Classification: `KEEP AND REPAIR`
- Rich-text notes, Tiptap editor, creation, editing, autosave, deletion, valid note history, local folders, local SQLite persistence, meeting-linked notes, transcript-linked notes, audio/import note surfaces, realtime transcription banner, meeting note interface, local services, local IPC, and valid note tests.
- Complete personal notes, meeting notes, exact timestamp links, pinned/recent notes, local templates (Classification: `CONDITIONAL — REQUIRES EVIDENCE`; Default: Keep if implemented and tested locally; Fallback: Standard blank note creation), and note-source indicators.

## 12. Folders, tags, and snippets

- Classification: `KEEP AND REPAIR`
- Local folders, create/rename/delete, assigning notes to folders, local tags, snippets, local organisation logic, direct SQLite persistence, and valid tests.
- Complete nested folders, counts, multi-tagging, filters, batch movement, safe orphan handling, constraints, and backup/export support.

## 13. Exact search

- Classification: `MANDATORY KEEP`
- Note-title, note-body, transcript, speaker, folder, tag, date, meeting, and source-type search; exact highlighting; local indexes; and opening results.

## 14. Semantic search

- Classification: `MANDATORY KEEP`
- MiniLM embeddings, local ONNX inference, note vector index, transcript-chunk index, cosine similarity, chunking, reindexing, local ranking, localhost-only vector communication, and local process management.
- **Qdrant**: Classification: `CONDITIONAL — REQUIRES EVIDENCE`. Default: Preserve the current working local semantic-search implementation first. Do not invent performance thresholds. Do not add another vector dependency merely for theoretical comparison. Compare realistic Mnemora: search quality, recall, latency, startup reliability, recovery, package size, and maintenance burden. Replace only when another local solution (such as embedded SQLite vector search or local ONNX/MiniLM memory index) is clearly simpler without behavioural regression. Fallback: Retain Qdrant local process or embedded SQLite vector index.
- Complete unified exact/semantic search, filters, timestamp jumps, index health, rebuild, stale/deleted cleanup, missing/corrupt recovery, and background indexing.
- Semantic search is a retained local capability and is not an AI chatbot.
- **Local generative AI**: Classification: `FORBIDDEN FOR FIRST RELEASE`. Remove any implication that local LLM artefacts may remain as active features. Do not include: llama-server, local summarisation, action-item extraction, rewrite, agents, or chat.

## 15. Local actions and clipboard

- Classification: `MANDATORY KEEP`
- Normal clipboard access for dictation paste, local file selection, direct local note/folder/tag operations, direct SQLite services, local export, and local backup actions.

## 16. Notifications and process detection

- Classification: `KEEP AFTER DECOUPLING`
- Local meeting-process detection (Classification: `CONDITIONAL — REQUIRES EVIDENCE`; Default: Keep if reliably detecting local meeting processes without cloud calls; Fallback: Manual meeting start/stop), local application detection, recording/transcription notifications, model/storage/backup/recovery notifications, and local tray actions.

## 17. Internal IPC

- Classification: `KEEP AFTER DECOUPLING`
- Keep typed internal Electron IPC for recording, audio, transcription, diarization, meetings, transcripts, notes, folders, tags, snippets, search/indexing, import/export, backup/restore, models, settings, permissions, hotkeys, playback, data paths, and diagnostics.
- Every retained capability must be complete from renderer caller through preload, types, handler, service, local effect, and tests.

## 18. SQLite and local persistence

- Classification: `MANDATORY KEEP`
- SQLite, better-sqlite3, Kysely (subject to Section 2 conditional rules), existing valid persistence and migrations, transactions, foreign keys, local file references, and local audio storage.
- Final local entities include meetings, recordings, transcripts, transcript segments, speakers, speaker embeddings/assignments, notes, note links, folders, tags, relations, snippets, attachments, settings, jobs, backups, migrations, semantic-index state, and legacy migration journal.
- **OS keyring**: Classification: `CONDITIONAL — REQUIRES EVIDENCE`. Default: Remove if no retained local-security feature uses it. Keep only for explicit local requirements such as: local encryption keys, encrypted backup keys, or protected local secrets. Do not keep merely because installed. Do not delete merely because cloud credentials disappear. Fallback: Local encrypted SQLite configuration table or standard OS secure storage for explicit local secrets.

## 19. Import and export

- Classification: `MANDATORY KEEP`
- Existing local audio/video import, file pickers, FFmpeg processing, validation, transcription, progress, cancellation, retry, history, and support for WAV, MP3, M4A, MP4, and other validated formats.
- Existing export plus plain text, Markdown user export, JSON, SRT/VTT where timestamps exist, meeting notes, transcript bundles, and full local backup archives.
- All project documentation belongs in Graphify; zero tracked Markdown is permitted inside Codebase. User-exported Markdown files remain supported as output artifacts.

## 20. Playback

- Classification: `KEEP AND REPAIR`
- Recording playback, transcript association, media controls, timeline/seek, playback state, and missing-audio handling.
- Complete segment-to-seek, current-segment highlighting, speed, skip controls, speaker navigation, timestamps, and retention state.

## 21. Settings

- Classification: `KEEP AFTER DECOUPLING`
- Appearance/theme, hotkeys, microphone/audio, transcription language/engine/model, meetings, diarization, notes, search/indexing, storage, audio retention, backup, export defaults, model health, offline model-pack import, index status/reindex, network status, privacy diagnostics, database/data folders, temporary-file cleanup, local logs, and About.

## 22. Native and platform components

- Classification: `MANDATORY KEEP`
- **Platform scope**: Windows installer and Windows offline proof are mandatory. Preserve valid macOS and Linux source/configuration. Verify macOS/Linux only on appropriate systems or CI. Missing macOS/Linux hardware does not block Windows release. Do not claim unsupported platforms are verified.
- Windows key/microphone/system-audio/text-monitor/fast-paste helpers; macOS audio tap/microphone/fast-paste/media remote; Linux key/system-audio/fast-paste helpers; meeting AEC helper; FFmpeg; Whisper/Sherpa/ONNX/Qdrant binaries where retained under conditional rules; and required native libraries.

## 23. Packaging

- Classification: `MANDATORY KEEP`
- Electron Builder, Windows installer, shortcuts, rebranded icons, native packaging, permissions, macOS/Linux build configuration for later proof, local schema migrations, version display, and user-data preservation on uninstall by default.
- **Portable build**: Classification: `CONDITIONAL — VERIFY PRODUCT REQUIREMENT`. Default: Preserve an existing working portable target; do not invent it as mandatory; test it if retained. Fallback: Standard Windows NSIS installer.

## 24. Tests and proof

- Classification: `KEEP AND REPAIR`
- Keep and repair valid unit, integration, renderer, database, transcription, native, build, packaging, fixture, and platform-specific tests.

## 25. Preservation-first policy

- Classification: `MANDATORY KEEP`
- Keep working local code by default. Repair before replacing. Recover exact upstream code before inventing a new implementation. Preserve validation, error handling, cleanup, recovery, native behaviour, performance-sensitive code, tests, and data compatibility.

## 26. Conditional keeps summary

- Every conditional item (`CONDITIONAL — REQUIRES EVIDENCE`) must be evaluated against its mandatory default, deviation condition, required evidence, and fallback before modification:
  1. Qdrant versus embedded vector index
  2. Parakeet and Sherpa-ONNX default packaging
  3. Kysely query builder retention
  4. Loopback-only WebSockets for bundled local services
  5. OS keyring for local encryption/secret keys
  6. Local voice fingerprinting reliability
  7. Local process-based meeting detection
  8. Local note templates
  9. Portable Windows build target
  10. macOS/Linux source preservation and CI verification

## Final Keep Acceptance

Every retained item must have:

- An authoritative capability owner
- An exact current and target path
- A symbol or unique anchor
- Mapped dependencies and dependents
- Complete renderer, preload, IPC, service, storage, and native relationships where applicable
- Relevant tests
- Successful builds
- Complete workflow evidence
- Offline verification

Nothing is considered kept merely because code survived deletion. It must remain connected, functional, tested, and correctly located.
