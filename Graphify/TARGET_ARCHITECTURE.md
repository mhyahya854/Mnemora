# Target Architecture

The target is a fully local Electron desktop application organized by capability ownership, with typed internal IPC, SQLite persistence, bundled local engines/assets, explicit process lifecycle, runtime network denial and proof-driven packaging. This is a planning target, not an implemented state.

## Invariants

- Renderer code calls only declared preload APIs; preload, TypeScript declarations, IPC channels, handlers and services change together.
- User data remains local in SQLite/filesystem storage with backup-before-transform, forward migrations, integrity, idempotency and recovery.
- Whisper.cpp is the required local fallback. Parakeet and Sherpa-ONNX remain separate conditional packages governed by evidence.
- Qdrant and every loopback service are bundled, owned, lifecycle-managed and allow-listed; external runtime networking and downloads remain absent.
- Removed systems are absent across the complete UI-to-package chain while historical migrations, legal provenance and explicit legacy compatibility remain labelled.
- Windows installer/build/offline launch proof is mandatory. macOS/Linux source/configuration is preserved and receives applicable CI/static or honest hardware status.

## Capability ownership and exact targets

| Capability | Owner | Target paths | Target symbols | Decision |
| --- | --- | --- | --- | --- |
| CAP-AEC | Meeting audio | codebase/main/features/meetings/meetingAecManager.js | MeetingAecManager | KEEP AND REPAIR |
| CAP-APP-SHELL | Desktop shell | codebase/main/index.js | app.whenReady | MANDATORY KEEP |
| CAP-AUDIO | Meeting audio | codebase/main/features/meetings/audioUtils.js | owned::cap-audio | KEEP AND REPAIR |
| CAP-AUDIO-MIXING | Meeting audio | codebase/renderer/features/meetings/meetingRecordingStore.ts | owned::cap-audio-mixing | KEEP AND REPAIR |
| CAP-BACKUP | SQLite persistence | codebase/main/infrastructure/persistence/localBackup.js | owned::cap-backup | MANDATORY KEEP |
| CAP-CLIPBOARD | Dictation | codebase/main/features/dictation/clipboard.js | owned::cap-clipboard | KEEP AND REPAIR |
| CAP-DATA-SAFETY | SQLite persistence | codebase/main/infrastructure/persistence/database.js | owned::cap-data-safety | MANDATORY KEEP |
| CAP-DATABASE | SQLite persistence | codebase/main/infrastructure/persistence/database.js | DatabaseManager | MANDATORY KEEP |
| CAP-DELETION-GOVERNANCE | Graphify governance | Graphify/DELETED_ITEMS_LEDGER.md | owned::cap-deletion-governance | MANDATORY KEEP |
| CAP-DIARIZATION | Diarization and speakers | codebase/main/features/meetings/diarization.js | DiarizationManager | MANDATORY KEEP |
| CAP-DICTATION | Dictation | codebase/main/features/dictation/clipboard.js | owned::cap-dictation | MANDATORY KEEP |
| CAP-EXACT-LOCATION | Graphify governance | Graphify/EXACT_LOCATION_REGISTRY.json | owned::cap-exact-location | MANDATORY KEEP |
| CAP-EXPORT | Import and export | codebase/main/ipc/ipcHandlers.js | export handlers | MANDATORY KEEP |
| CAP-FFMPEG | Local transcription | codebase/main/features/transcription/ffmpegUtils.js | owned::cap-ffmpeg | MANDATORY KEEP |
| CAP-FOLDERS | Notes | codebase/renderer/features/notes/useFolderManagement.ts | useFolderManagement | MANDATORY KEEP |
| CAP-HOTKEY | Dictation | codebase/main/features/dictation/hotkeyManager.js | HotkeyManager | KEEP AND REPAIR |
| CAP-I18N | Localisation | codebase/shared/i18n/en/translation.json | local translation catalogue | KEEP AND REPAIR |
| CAP-IMPLEMENTATION-GOVERNANCE | Graphify governance | Graphify/IMPLEMENTATION_QUEUE.json | owned::cap-implementation-governance | MANDATORY KEEP |
| CAP-IMPORT | Import and export | codebase/renderer/features/notes/components/UploadAudioView.tsx | UploadAudioView | MANDATORY KEEP |
| CAP-IMPORT-AUDIO | Import and export | codebase/renderer/features/notes/components/UploadAudioView.tsx | UploadAudioView | MANDATORY KEEP |
| CAP-IMPORT-EXPORT | Import and export | codebase/main/ipc/ipcHandlers.js | local import and export handlers | KEEP AND REPAIR |
| CAP-IMPORT-VIDEO | Import and export | codebase/renderer/features/notes/components/UploadAudioView.tsx | UploadAudioView | MANDATORY KEEP |
| CAP-IPC | Electron IPC | codebase/main/ipc/ipcHandlers.js | IPCHandlers | KEEP AND REPAIR |
| CAP-KEYRING | Settings and platform security | codebase/main/infrastructure/persistence/localSecretStore.js | LocalSecretStore | CONDITIONAL - REQUIRES EVIDENCE |
| CAP-KYSELY | SQLite persistence | codebase/main/infrastructure/persistence/database.js | persistence query boundary | CONDITIONAL - REQUIRES EVIDENCE |
| CAP-LEGACY-MIGRATION | SQLite persistence | codebase/main/infrastructure/persistence/dataMigration.js | owned::cap-legacy-migration | ADD |
| CAP-LEGAL | Legal and licensing | codebase/LICENSE | license text | MANDATORY KEEP |
| CAP-LINKED-NOTES | Notes | codebase/renderer/features/notes/components/NoteEditor.tsx | owned::cap-linked-notes | MANDATORY KEEP |
| CAP-LINKED-PLAYBACK | Playback | codebase/renderer/features/notes/components/MeetingTranscriptView.tsx | owned::cap-linked-playback | MANDATORY KEEP |
| CAP-LOOPBACK-WEBSOCKETS | Runtime network policy | codebase/main/infrastructure/runtime/runtimeNetworkPolicy.js | owned::cap-loopback-websockets | CONDITIONAL - REQUIRES EVIDENCE |
| CAP-MACOS-LINUX | Cross-platform source | codebase/native/helpers | platform helper source roots | CONDITIONAL - REQUIRES EVIDENCE |
| CAP-MARKDOWN-GOVERNANCE | Repository governance | Graphify/ | owned::cap-markdown-governance | MANDATORY KEEP |
| CAP-MEETING | Meeting workflow | codebase/renderer/features/meetings/meetingRecordingStore.ts | startRecording | MANDATORY KEEP |
| CAP-MEETING-DETECTION | Meeting workflow | codebase/main/features/meetings/meetingDetectionEngine.js | owned::cap-meeting-detection | CONDITIONAL - REQUIRES EVIDENCE |
| CAP-MEETING-NOTES | Notes | codebase/renderer/features/notes/components/NoteEditor.tsx | NoteEditor | MANDATORY KEEP |
| CAP-MICROPHONE | Meeting audio | codebase/renderer/features/meetings/meetingRecordingStore.ts | owned::cap-microphone | MANDATORY KEEP |
| CAP-MICROPHONE-DICTATION | Dictation | codebase/renderer/features/dictation/useAudioRecording.js | owned::cap-microphone-dictation | MANDATORY KEEP |
| CAP-MICROPHONE-SELECTION | Dictation | codebase/renderer/features/transcription/audioDeviceUtils.ts | owned::cap-microphone-selection | KEEP AND REPAIR |
| CAP-MINILM | Search | codebase/main/features/search/localEmbeddings.js | LocalEmbeddings | KEEP AND REPAIR |
| CAP-MODEL-DISCOVERY | Local model handling | codebase/main/features/transcription/modelDirUtils.js | owned::cap-model-discovery | MANDATORY KEEP |
| CAP-MODEL-PACK | Local model handling | codebase/main/features/transcription/downloadUtils.js | owned::cap-model-pack | ADD |
| CAP-MODELS | Local model handling | codebase/main/features/transcription/modelDirUtils.js | owned::cap-models | KEEP AND REPAIR |
| CAP-NATIVE | Platform-native helpers | codebase/native/helpers | platform helper source roots | KEEP AND REPAIR |
| CAP-NETWORK-POLICY | Runtime network policy | codebase/main/infrastructure/runtime/runtimeNetworkPolicy.js | installRuntimeNetworkPolicy | ADD |
| CAP-NOTE-TEMPLATES | Notes | codebase/renderer/features/notes/noteTemplates.ts | local note template contract | CONDITIONAL - REQUIRES EVIDENCE |
| CAP-NOTES | Notes | codebase/renderer/features/notes/components/NoteEditor.tsx | NoteEditor | KEEP AND REPAIR |
| CAP-NOTIFICATIONS | Desktop shell | codebase/renderer/features/meetings/MeetingNotificationCard.tsx | MeetingNotificationCard | MANDATORY KEEP |
| CAP-OFFLINE-FIRST-LAUNCH | Release verification | codebase/tests/integration/offlineFirstLaunch.test.js | offline installed-launch proof | ADD |
| CAP-ONBOARDING | Renderer application | codebase/renderer/features/onboarding/OnboardingFlow.tsx | owned::cap-onboarding | KEEP AND REPAIR |
| CAP-PACKAGING | Windows packaging | codebase/electron-builder.json | electron-builder configuration | MANDATORY KEEP |
| CAP-PARAKEET | Local transcription | codebase/main/features/transcription/parakeetEngine.js | ParakeetEngine | CONDITIONAL - REQUIRES EVIDENCE |
| CAP-PERSONAL-NOTES | Notes | codebase/renderer/features/notes/components/PersonalNotesView.tsx | owned::cap-personal-notes | MANDATORY KEEP |
| CAP-PLANNING-GOVERNANCE | Graphify governance | Graphify/Master Plan/ | owned::cap-planning-governance | MANDATORY KEEP |
| CAP-PLAYBACK | Playback | codebase/renderer/features/notes/components/MeetingRecordingPill.tsx | MeetingRecordingPill | MANDATORY KEEP |
| CAP-PORTABLE-WINDOWS | Windows packaging | codebase/electron-builder.json | owned::cap-portable-windows | CONDITIONAL - REQUIRES EVIDENCE |
| CAP-PROCESSING-JOBS | Local processing | codebase/main/infrastructure/runtime/localJobQueue.js | LocalJobQueue | ADD |
| CAP-PROVENANCE | Repository governance | .git/ | owned::cap-provenance | MANDATORY KEEP |
| CAP-QDRANT | Search | codebase/main/features/search/qdrantManager.js | owned::cap-qdrant | CONDITIONAL - REQUIRES EVIDENCE |
| CAP-RECORDING-OVERLAY | Dictation | codebase/renderer/features/transcription/TranscriptionPreviewOverlay.tsx | owned::cap-recording-overlay | KEEP AND REPAIR |
| CAP-RECOVERY | Meeting workflow | codebase/main/features/meetings/recordingRecovery.js | recoverInterruptedRecordings | KEEP AND REPAIR |
| CAP-RELEASE | Graphify governance | Graphify/RELEASE_GATE_PLAN.json | owned::cap-release | MANDATORY KEEP |
| CAP-REMOVE-ACCOUNTS | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-accounts | REMOVE |
| CAP-REMOVE-ACTION-ITEM-EXTRACTION | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-action-item-extraction | REMOVE |
| CAP-REMOVE-ACTIVE-OPENWHISPR-IDENTITY | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-active-openwhispr-identity | REMOVE |
| CAP-REMOVE-AI-AGENTS | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-ai-agents | REMOVE |
| CAP-REMOVE-AI-REWRITING | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-ai-rewriting | REMOVE |
| CAP-REMOVE-ANALYTICS | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-analytics | REMOVE |
| CAP-REMOVE-API-KEYS | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-api-keys | REMOVE |
| CAP-REMOVE-AUTHENTICATION | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-authentication | REMOVE |
| CAP-REMOVE-AUTOMATIC-UPDATER | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-automatic-updater | REMOVE |
| CAP-REMOVE-BILLING | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-billing | REMOVE |
| CAP-REMOVE-CALENDAR | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-calendar | REMOVE |
| CAP-REMOVE-CHAT | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-chat | REMOVE |
| CAP-REMOVE-CLOUD-SYNCHRONISATION | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-cloud-synchronisation | REMOVE |
| CAP-REMOVE-HOSTED-AI | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-hosted-ai | REMOVE |
| CAP-REMOVE-HOSTED-TRANSCRIPTION | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-hosted-transcription | REMOVE |
| CAP-REMOVE-INVITATIONS | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-invitations | REMOVE |
| CAP-REMOVE-LOCAL-GENERATIVE-AI | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-local-generative-ai | FORBIDDEN |
| CAP-REMOVE-MCP | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-mcp | REMOVE |
| CAP-REMOVE-ORGANISATIONS | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-organisations | REMOVE |
| CAP-REMOVE-PUBLIC-API | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-public-api | REMOVE |
| CAP-REMOVE-REFERRALS | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-referrals | REMOVE |
| CAP-REMOVE-RUNTIME-EXTERNAL-LINKS | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-runtime-external-links | REMOVE |
| CAP-REMOVE-RUNTIME-EXTERNAL-NETWORKING | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-runtime-external-networking | REMOVE |
| CAP-REMOVE-RUNTIME-MODEL-DOWNLOADS | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-runtime-model-downloads | REMOVE |
| CAP-REMOVE-SHARING | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-sharing | REMOVE |
| CAP-REMOVE-SUMMARISATION | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-summarisation | REMOVE |
| CAP-REMOVE-TEAMS | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-teams | REMOVE |
| CAP-REMOVE-TELEMETRY | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-telemetry | REMOVE |
| CAP-REMOVE-UPGRADE-SYSTEMS | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-upgrade-systems | REMOVE |
| CAP-REMOVE-USAGE-QUOTAS | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-usage-quotas | REMOVE |
| CAP-REMOVE-WORKSPACES | Excluded-system removal | ABSENT_FROM_ACTIVE_PRODUCT | absence::cap-remove-workspaces | REMOVE |
| CAP-RENDERER | Renderer application | codebase/renderer/app/AppRouter.jsx | AppRouter | KEEP AND REPAIR |
| CAP-REPOSITORY | Repository governance | codebase/package.json | repository package root | KEEP AND REPAIR |
| CAP-RESTORE | SQLite persistence | codebase/main/infrastructure/persistence/localBackup.js | owned::cap-restore | MANDATORY KEEP |
| CAP-SEARCH-EXACT | Search | codebase/main/infrastructure/persistence/database.js | DatabaseManager.searchLocal | MANDATORY KEEP |
| CAP-SEARCH-SEMANTIC | Search | codebase/main/features/search/vectorIndex.js | vectorIndex.search | MANDATORY KEEP |
| CAP-SEGMENTS | Local transcription | codebase/main/infrastructure/persistence/database.js | transcript segment persistence | MANDATORY KEEP |
| CAP-SETTINGS | Settings and platform security | codebase/renderer/features/settings/SettingsPage.tsx | owned::cap-settings | MANDATORY KEEP |
| CAP-SHERPA-ONNX | Local transcription | codebase/main/features/meetings/diarization.js | DiarizationManager | CONDITIONAL - REQUIRES EVIDENCE |
| CAP-SIMPLIFICATION | Repository governance | Graphify/PONYTAIL_AUDIT.md | owned::cap-simplification | KEEP AND REPAIR |
| CAP-SNIPPETS | Notes | codebase/renderer/features/snippets/SnippetsView.tsx | SnippetsView | MANDATORY KEEP |
| CAP-SPEAKER-EMBEDDINGS | Diarization and speakers | codebase/main/features/meetings/speakerEmbeddings.js | owned::cap-speaker-embeddings | KEEP AND REPAIR |
| CAP-SPEAKER-LABELS | Diarization and speakers | codebase/renderer/features/meetings/transcriptSpeakerState.ts | owned::cap-speaker-labels | MANDATORY KEEP |
| CAP-SPEAKER-NAMING | Diarization and speakers | codebase/renderer/features/notes/components/MeetingTranscriptView.tsx | owned::cap-speaker-naming | MANDATORY KEEP |
| CAP-SPEAKER-PERSISTENCE | Diarization and speakers | codebase/main/infrastructure/persistence/database.js | owned::cap-speaker-persistence | KEEP AND REPAIR |
| CAP-SPEAKER-RENAMING | Diarization and speakers | codebase/renderer/features/notes/components/MeetingTranscriptView.tsx | owned::cap-speaker-renaming | MANDATORY KEEP |
| CAP-SYSTEM-AUDIO | Meeting audio | codebase/main/platform/windowsLoopbackAudioManager.js | owned::cap-system-audio | KEEP AND REPAIR |
| CAP-TAGS | Notes | codebase/main/infrastructure/persistence/database.js | DatabaseManager.getTags | MANDATORY KEEP |
| CAP-TESTING | Graphify governance | codebase/tests | test roots | KEEP AND REPAIR |
| CAP-THIRD-PARTY | Legal and licensing | Graphify/THIRD_PARTY_CODE_REGISTER.md | owned::cap-third-party | MANDATORY KEEP |
| CAP-TRANSCRIPT-EDIT | Local transcription | codebase/main/infrastructure/persistence/database.js | updateTranscriptSegment | MANDATORY KEEP |
| CAP-TRANSCRIPT-HISTORY | Local transcription | codebase/main/infrastructure/persistence/database.js | transcript history persistence | KEEP AND REPAIR |
| CAP-TRANSCRIPTION | Local transcription | codebase/main/features/transcription/whisper.js | WhisperManager | MANDATORY KEEP |
| CAP-TRAY | Desktop shell | codebase/main/desktop/tray.js | owned::cap-tray | MANDATORY KEEP |
| CAP-VAD | Local transcription | codebase/main/features/transcription/whisperVadConfig.js | owned::cap-vad | MANDATORY KEEP |
| CAP-VOICE-FINGERPRINTING | Diarization and speakers | codebase/main/features/meetings/speakerEmbeddings.js | owned::cap-voice-fingerprinting | CONDITIONAL - REQUIRES EVIDENCE |
| CAP-WHISPER | Local transcription | codebase/main/features/transcription/whisper.js | owned::cap-whisper | MANDATORY KEEP |
| CAP-WINDOW-LIFECYCLE | Desktop shell | codebase/main/desktop/windowManager.js | owned::cap-window-lifecycle | MANDATORY KEEP |
| CAP-WINDOWS-INSTALLER | Windows packaging | codebase/electron-builder.json | Windows installer targets | MANDATORY KEEP |
