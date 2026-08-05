# Implementation Dependency Graph

This is the planning task DAG derived from `IMPLEMENTATION_QUEUE.json`. Genuine code-relationship evidence remains under `graphify-out/`; it is distinct from this implementation-order graph. No application task has been executed.

- Task nodes: 158
- Semantic dependency edges: 323
- Root task: `TASK-GOV-001-PROVENANCE-BASELINE`
- Final leaf task: `TASK-REL-11-AUDIT`
- Maximum dependency depth: 17
- Cycles: 0
- Deterministic topological-order validation: PASS

| Phase | Tasks | Incoming semantic edges | First order | Last order |
| --- | --- | --- | --- | --- |
| PHASE-01-AUTHORITY-AND-PROVENANCE | 1 | 0 | 1 | 1 |
| PHASE-02-CHARACTERIZATION-AND-DATA-SAFETY | 12 | 31 | 2 | 13 |
| PHASE-03-DECOUPLING-AND-RETAINED-PROTECTION | 23 | 55 | 14 | 36 |
| PHASE-04-EXCLUDED-SYSTEM-REMOVAL | 32 | 62 | 37 | 68 |
| PHASE-05-RETAINED-CAPABILITIES | 69 | 136 | 69 | 137 |
| PHASE-06-REORGANIZATION-AND-CLEANUP | 9 | 16 | 138 | 146 |
| PHASE-07-INTEGRATION-AND-RELEASE-EVIDENCE | 12 | 23 | 147 | 158 |

For exact prerequisites and dependents, use each task's `semantic_dependencies` and `dependents` fields. `execution_order` is a reproducible linearization for handoff; it does not create dependencies that are absent from the DAG.
