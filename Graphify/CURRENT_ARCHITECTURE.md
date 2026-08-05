# Current Architecture

This is a read-only static architecture map. Path plus symbol/unique anchor is authoritative; saved line numbers in `EXACT_LOCATION_REGISTRY.json` are secondary. Genuine Graphify 0.9.17 evidence remains under `graphify-out/`; static candidates are not runtime observations.

## Runtime composition

| Layer | Current owner and exact anchors | Significant effects |
| --- | --- | --- |
| Electron lifecycle | `codebase/main/index.js::app.whenReady`, `codebase/main/desktop/windowManager.js::WindowManager`, `codebase/main/desktop/tray.js::TrayManager` | Windows, tray, protocol, child-process cleanup |
| Renderer shell | `codebase/renderer/app/main.jsx::root`, `codebase/renderer/app/AppRouter.jsx::AppRouter`, `codebase/renderer/app/components/ControlPanel.tsx::ControlPanel` | Navigation and retained local feature entry |
| Renderer state | `codebase/renderer/features/meetings/meetingRecordingStore.ts`, `codebase/renderer/features/notes/noteStore.ts`, `codebase/renderer/features/settings/settingsStore.ts`, `codebase/renderer/features/transcription/transcriptionStore.ts` | UI state and IPC callers |
| Preload/type boundary | `codebase/preload/index.js::contextBridge.exposeInMainWorld`, `codebase/renderer/shared/types/electron.ts::ElectronAPI` | Renderer-to-main contract |
| IPC | `codebase/main/ipc/ipcHandlers.js::setupIpcHandlers` | Capability handlers, data/filesystem/process effects |
| Dictation | `codebase/main/features/dictation/hotkeyManager.js::HotkeyManager`, `codebase/renderer/features/dictation/App.jsx::App` | Global hotkey, microphone, local transcription, paste |
| Meeting capture | `codebase/renderer/features/meetings/meetingRecordingStore.ts`, `codebase/main/platform/windowsLoopbackAudioManager.js`, `codebase/main/features/meetings/meetingAecManager.js` | Microphone/system audio, AEC/mix, recovery |
| Transcription | `codebase/main/features/transcription/whisperServer.js::WhisperServer`, `codebase/main/features/transcription/whisper.js`, `codebase/main/features/transcription/modelDirUtils.js` | Bundled local process/models; no permitted runtime download |
| Diarization/speakers | `codebase/main/features/meetings/diarization.js`, `codebase/main/features/meetings/speakerEmbeddings.js`, `codebase/main/features/meetings/liveSpeakerIdentifier.js` | Sherpa helper/models, ONNX embeddings, persisted mappings |
| Notes/transcripts | `codebase/renderer/features/notes/components/NoteEditor.tsx::NoteEditor`, `codebase/renderer/features/notes/noteStore.ts::initializeNotes`, `codebase/main/infrastructure/persistence/database.js::saveNote` | Rich notes, structured segments, folders/tags, links and SQLite persistence |
| Exact/semantic search | `codebase/main/infrastructure/persistence/database.js::searchLocal`, `codebase/renderer/features/search/SearchView.tsx::SearchView`, `codebase/main/features/search/localEmbeddings.js::LocalEmbeddings`, `codebase/main/features/search/qdrantManager.js::QdrantManager`, `codebase/main/features/search/vectorIndex.js::search` | SQLite/FTS/text exact search and isolated local MiniLM/Qdrant semantic search |
| Persistence | `codebase/main/infrastructure/persistence/database.js::DatabaseManager`, `codebase/main/infrastructure/persistence/dataMigration.js`, `codebase/main/infrastructure/persistence/localBackup.js` | SQLite schema, forward migration, backup/restore |
| Runtime policy | `codebase/main/infrastructure/runtime/runtimeNetworkPolicy.js`, `codebase/main/infrastructure/runtime/process.js`, `codebase/main/infrastructure/runtime/sidecarReaper.js` | External-network denial and owned local processes |
| Native/model assets | `codebase/resources/bin/asset-manifest.json`, `codebase/native/helpers/`, `codebase/native/meeting-aec-helper/` | Pinned binaries/models and platform helpers |
| Packaging | `codebase/electron-builder.json`, `codebase/scripts/packaging/prepare-offline-assets.js`, `codebase/scripts/verification/verify-offline-assets.js` | NSIS and configured portable Windows targets; macOS/Linux config retained |

## Known current absences or incomplete areas

- No Git repository was found at planning time.
- No Kysely or OS keyring package/import was proven.
- No active loopback WebSocket dependency was proven; local Qdrant uses owned loopback HTTP.
- No Parakeet runtime engine/binary was proven; only stale or localization references were found.
- No local note-template implementation was proven.
- Offline model-pack import, local processing job queue, legacy migration hardening, offline first-launch proof, legal-file target set and release evidence remain planned additions or repairs.
- Existing removal-term hits include historical migration/legal/build-time candidates and stale translations/styles; every one requires deletion-interlock classification.
