# Move Ledger

No application file was moved in this planning run.

| Move ID | Current path | Intended target | Trigger | Preconditions | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- |
| MOVE-001-ROOT-CASING | `codebase/` | `Codebase/` as named by the Master Plan target tree | Future implementation task under explicit mutation authority | Git/hash provenance, casing-safe Windows procedure, import/build/package path audit, no user data inside move scope | Pre/post path inventory, hashes, Git diff, test/build/package evidence | PLANNED; NOT AUTHORIZED IN THIS RUN |
| MOVE-002-MARKDOWN | Any non-legal application Markdown proven outside vendor/generated roots | `Graphify/` or an owned documentation target | Future repository-governance task | Classify package/vendor/generated files; preserve required legal plain-text files; repair references | Exact source/target ledger and link/package checks | PLANNED; current authoritative inventory found no such source Markdown outside excluded roots |
| MOVE-003-MONOLITHS | Oversized mixed-owner symbols such as `codebase/main/ipc/ipcHandlers.js::setupIpcHandlers` | Capability-owned IPC registration modules selected during implementation | Characterization and ownership proof | Complete caller/handler/service/data map; focused tests; reversible batch | Import/call diff, handler parity, cycle and regression evidence | PLANNED |

The lowercase `codebase` path remains the authoritative current location until MOVE-001 is genuinely executed and verified.
