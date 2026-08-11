# Semantic Planning Validation Report

SEMANTIC GRAPHIFY PLANNING INCOMPLETE - CONTINUE WORKING

Checks: **42/43 passed**. Implementation: **IN PROGRESS**. Release: **NOT EVALUATED**. Next task: **TASK-CAP-DATA-SAFETY**.

| Gate | Result | Errors |
| --- | --- | ---: |
| SEM-001-MASTER-HASH - Master Plan hash integrity (canonical git blob content) | PASS | 0 |
| SEM-002-REQUIREMENT-SOURCE - Requirement source and line reconciliation | PASS | 0 |
| SEM-003-REQUIREMENT-CLASSIFICATION - Semantic requirement classifications | PASS | 0 |
| SEM-004-NAMED-CAPABILITIES - Named product-scope capability completeness | PASS | 0 |
| SEM-005-PROTECTED-SEPARATION - Protected retained scope is separated from deletion | PASS | 0 |
| SEM-006-CAPABILITY-OWNERSHIP - Capability-domain ownership | PASS | 0 |
| SEM-007-RUNTIME-CHAIN - Capability runtime-chain correctness | PASS | 0 |
| SEM-008-EXACT-SYMBOLS - Exact-location path, symbol and anchor reconciliation | PASS | 0 |
| SEM-009-VENDOR-TARGETS - Vendor/generated target restrictions | PASS | 0 |
| SEM-010-TARGET-OWNERSHIP - Target ownership and collision rules | PASS | 0 |
| SEM-011-DELETION-DISPOSITIONS - Deletion candidates have reviewed dispositions | PASS | 0 |
| SEM-012-KNOWN-FALSE-POSITIVES - Tokenizer, login-item, historical, legal and offline-message exclusions | PASS | 0 |
| SEM-013-DELETION-INTERLOCKS - Seven Binding Deletion Interlock gates | PASS | 0 |
| SEM-014-DELETION-LAYERS - Deletion architectural-layer coverage | PASS | 0 |
| SEM-015-TASK-CONTRACTS - Implementation-ready task contracts | PASS | 0 |
| SEM-016-SEMANTIC-DEPENDENCIES - Real semantic task dependencies | PASS | 0 |
| SEM-017-DAG - Dependency graph acyclicity | PASS | 0 |
| SEM-018-TOPOLOGICAL-ORDER - Topological execution order | PASS | 0 |
| SEM-019-PHASE-WAVE - Phase, wave and order agreement | PASS | 0 |
| SEM-020-TEST-COMMANDS - Test-command and package-script validity | PASS | 0 |
| SEM-021-TEST-REFERENCE-STATUS - Existing-versus-planned test distinction | PASS | 0 |
| SEM-022-EVIDENCE-APPROPRIATENESS - Evidence type appropriateness | PASS | 0 |
| SEM-023-CONDITIONAL-PACKAGES - Conditional decision package completeness | PASS | 0 |
| SEM-024-RELEASE-GATES - Strict Release Conjunction traceability | PASS | 0 |
| SEM-025-INTERPRETATIONS - Master Plan interpretation register | PASS | 0 |
| SEM-026-PLACEHOLDERS - Placeholder and vague-language detection | PASS | 0 |
| SEM-027-ORPHANS - Orphan requirement/capability/task detection | PASS | 0 |
| SEM-028-DUPLICATE-AUTHORITY - Duplicate IDs and authority detection | PASS | 0 |
| SEM-029-INTERNAL-LINKS - Internal Graphify link integrity | PASS | 0 |
| SEM-030-COUNTS - Cross-authority count reconciliation | PASS | 0 |
| SEM-031-GENERATOR-REPRODUCIBILITY - Generator semantic reproducibility | PASS | 0 |
| SEM-032-INTEGRITY-WORDING - Codebase-integrity wording accuracy | PASS | 0 |
| SEM-033-NO-CODEBASE-MUTATION - No forbidden codebase mutation within available baseline evidence | PASS | 0 |
| SEM-034-HANDOFF - Authoritative implementation handoff consistency | PASS | 0 |
| SEM-035-DATA-OFFLINE-WINDOWS - Data safety, offline, and Windows release planning | PASS | 0 |
| SEM-036-KNOWN-NEGATIVES - Known-negative validator fixtures | PASS | 0 |
| SEM-037-TRANSIENT-OUTPUT-MANIFEST - Transient and non-tracked Graphify output-manifest detection | PASS | 0 |
| SEM-038-CANONICAL-MANIFEST-COMPARISON - Canonical tracked manifest structure and equality | PASS | 0 |
| SEM-039-MANIFEST-HONESTY - Raw-file versus normalized-mapping honesty | PASS | 0 |
| SEM-040-PROTECTED-CONTENT - Protected Master Plan and tracked codebase content unchanged | PASS | 0 |
| SEM-041-RECONCILIATION-REPORT - Final repository reconciliation report consistency | FAIL | 1 |
| SEM-042-REPO-CLEAN-PRERUN - Pre-run tracked working tree cleanliness | PASS | 0 |
| SEM-043-EXECUTION-STATE - Durable task execution state, evidence, dependencies, and selector | PASS | 0 |

## Failures

- `SEM-041-RECONCILIATION-REPORT`: FINAL-REPOSITORY-RECONCILIATION.json verified commit does not equal the parent commit (or HEAD when HEAD has no parent)
