# Folder Ownership Map

| Current prefix | Authoritative module owner | Allowed responsibility | Forbidden dumping-ground behavior |
| --- | --- | --- | --- |
| `codebase/main/desktop/` | Electron shell | Windows, tray, menu, drag and development-server lifecycle | Feature repositories, cloud clients, unrelated utilities |
| `codebase/main/features/dictation/` | Dictation | Hotkey, capture orchestration, paste and dictation text behavior | Meeting persistence or hosted providers |
| `codebase/main/features/meetings/` | Meetings and speakers | Meeting lifecycle, recovery, diarization, speaker management | Generic persistence or remote calendar |
| `codebase/main/features/notes/` | Notes | Note repository and local organization | Remote AI rewriting |
| `codebase/main/features/search/` | Exact/semantic search | Exact search, MiniLM embeddings, local vector lifecycle | Generative AI or external search |
| `codebase/main/features/transcription/` | Local transcription | Whisper/local engines, models, FFmpeg and repositories | Runtime downloads or hosted transcription |
| `codebase/main/infrastructure/persistence/` | SQLite/data safety | Schema, repositories shared by capability, migrations, backup | Feature UI or network clients |
| `codebase/main/infrastructure/runtime/` | Local runtime | Environment, process lifecycle, logging, network policy, job queue | Product-specific UI logic |
| `codebase/main/ipc/` | Typed IPC boundary | Handler registration and validation only | Business logic monolith growth |
| `codebase/main/platform/` | Platform integration | OS-specific hotkey/audio/paste/process adapters | Cross-platform product state |
| `codebase/preload/` | Preload boundary | Minimal typed context bridge | Database, filesystem or feature business logic |
| `codebase/renderer/app/` | Renderer shell | Router, window chrome, top-level composition | Feature stores and repositories |
| `codebase/renderer/features/<capability>/` | Named feature owner | Components, hooks and state for one capability | Generic cross-feature dumping ground |
| `codebase/renderer/shared/` | Renderer shared primitives | Proven multi-feature UI/types/hooks | Speculative abstractions |
| `codebase/native/` | Native source | Platform helpers and meeting AEC source | Downloaded opaque binaries without provenance |
| `codebase/resources/` | Bundled assets | Pinned checksummed models/binaries and local assets | Runtime-downloaded mutable assets |
| `codebase/scripts/downloads/` | Build-time acquisition | Isolated pinned/checksummed build inputs | Installed runtime reachability |
| `codebase/scripts/packaging/` | Packaging | Asset staging and package hooks | Runtime capability code |
| `codebase/tests/` | Verification | Unit, fixture and real-integration contracts | Fabricated release evidence |
| `Graphify/` | Planning/evidence governance | Master authority, registries, tasks and saved evidence | Application source or parallel plan trees |

Moves and monolith decomposition require preserved imports, tests and a provenance checkpoint; directory preference alone is not authority.
