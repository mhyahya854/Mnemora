# Circular Dependencies

The installed TypeScript compiler resolved 455 local edges across 267 JS/TS-family files and 1105 import specifiers; Tarjan SCC found 1 cycle. All 12 non-code relative references resolved to real assets/configuration, and 0 relative imports remain unresolved. Raw evidence is `IMPORT_CYCLES.json`.

| Cycle | Files | Directed edges | Decision/task |
| --- | --- | --- | --- |
| CYCLE-001 | codebase/renderer/features/meetings/meetingRecordingStore.ts, codebase/renderer/features/meetings/transcriptSpeakerState.ts | codebase/renderer/features/meetings/transcriptSpeakerState.ts → codebase/renderer/features/meetings/meetingRecordingStore.ts, codebase/renderer/features/meetings/meetingRecordingStore.ts → codebase/renderer/features/meetings/transcriptSpeakerState.ts | PONY-012 / TASK-22 |

No queue task depends on a later task. Recompute the directed import SCCs after every future capability batch.
