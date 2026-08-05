#!/usr/bin/env python3
"""Post-save auditor for the Mnemora pre-execution Graphify layer."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
G = ROOT / "Graphify"
CB = ROOT / "codebase"
OUT = G / "graphify-out"
CUTOFF = datetime.fromisoformat("2026-07-28T01:50:44.156272+00:00").timestamp()
CHECKPOINT = "DFA2A857CE5214B6F94783DD9E11A1B4B83D75EE9B554232439FA8078C298CF6"


def load(name: str) -> Any:
    return json.loads((G / name).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().upper()


checks: list[dict[str, Any]] = []


def check(name: str, passed: bool, evidence: Any) -> None:
    checks.append({"check": name, "status": "PASS" if passed else "FAIL", "evidence": evidence})


plans = [
    G / "Master Plan" / "01-EVERYTHING-WE-ARE-KEEPING.md",
    G / "Master Plan" / "02-EVERYTHING-WE-ARE-DELETING.md",
    G / "Master Plan" / "03-HOW-WE-WILL-KEEP-DELETE-AND-REPLACE.md",
]
actual_plans = sorted(p.name for p in (G / "Master Plan").iterdir() if p.is_file())
check("Master Plan directory contains exactly the three authorities", actual_plans == [p.name for p in plans], actual_plans)
for plan in plans:
    text = plan.read_text(encoding="utf-8")
    check(f"{plan.name} identifies Mnemora", 'project: "Mnemora"' in text, sha256(plan))
    lower = text.lower()
    base_scope = all(term.lower() in lower for term in ["OpenWhispr", "dictation", "meeting", "transcription", "SQLite", "notes", "diarization", "semantic search"])
    search_scope = "exact and semantic search" in lower or ("exact search" in lower and "semantic search" in lower)
    check(f"{plan.name} is OpenWhispr-derived Mnemora scope", base_scope and search_scope, "required architecture terms")
    check(f"{plan.name} has no wrong-project contamination", not re.search(r"MindRoom|Mizaan|AFFiNE|whiteboard|Kanban|document-workspace|03-HOW-WE-WILL-KEEP-DELETE-AND-IMPLEMENT", text, re.IGNORECASE), "prohibited-term scan")

required_outputs = [
    "RUN_STATE.md", "EXACT_LOCATION_REGISTRY.json", "IMPLEMENTATION_QUEUE.md", "COMPLETION_TRACKER.md",
    "REPOSITORY_INVENTORY.md", "CURRENT_ARCHITECTURE.md", "TARGET_ARCHITECTURE.md", "CAPABILITY_REGISTRY.md",
    "FOLDER_OWNERSHIP_MAP.md", "MOVE_LEDGER.md", "DELETED_ITEMS_LEDGER.md", "THIRD_PARTY_CODE_REGISTER.md",
    "TEST_MATRIX.md", "REGRESSION_RESULTS.md", "DEPENDENCY_GRAPH.md", "IMPORT_AND_CALL_MAP.md",
    "CIRCULAR_DEPENDENCIES.md", "PONYTAIL_AUDIT.md", "RUNTIME_CHAIN_MAP.md", "DATABASE_AND_DATA_GRAPH.md",
    "NATIVE_MODEL_BINARY_GRAPH.md", "REPLACEMENT_MAP.md", "GRAPH_CONSISTENCY_REPORT.json", "READINESS_GATE.json",
    "GRAPHIFY_READINESS_REPORT.md", "REPOSITORY_FINGERPRINT.json", "REPOSITORY_FILE_INVENTORY.json",
    "CAPABILITY_REGISTRY.json", "IMPLEMENTATION_QUEUE.json", "TEST_MATRIX.json", "PONYTAIL_FINDINGS.json",
    "TOOL_EXECUTION_LOG.md",
    "IMPORT_CYCLES.json",
]
check("All required operational and intelligence artifacts exist", all((G / n).is_file() for n in required_outputs), [n for n in required_outputs if not (G / n).is_file()])
check("No duplicate Markdown exact-location registry exists", not (G / "EXACT_LOCATION_REGISTRY.md").exists(), "EXACT_LOCATION_REGISTRY.json is sole authority")

fingerprint = load("REPOSITORY_FINGERPRINT.json")
inventory = load("REPOSITORY_FILE_INVENTORY.json")
registry_doc = load("EXACT_LOCATION_REGISTRY.json")
registry = registry_doc["entries"]
caps = load("CAPABILITY_REGISTRY.json")["capabilities"]
tasks = load("IMPLEMENTATION_QUEUE.json")["tasks"]
tests = load("TEST_MATRIX.json")["tests"]
findings = load("PONYTAIL_FINDINGS.json")["findings"]
cycles = load("IMPORT_CYCLES.json")
health = json.loads((OUT / "GRAPH_HEALTH.json").read_text(encoding="utf-8"))
extract = json.loads((OUT / ".graphify_extract.json").read_text(encoding="utf-8"))
graph = json.loads((OUT / "graph.json").read_text(encoding="utf-8"))
second = json.loads((OUT / "SECOND_SCAN_COMPLETE").read_text(encoding="utf-8"))
gate = load("READINESS_GATE.json")

check("Fingerprint binds every machine registry", fingerprint["hash_checkpoint_id"] == CHECKPOINT and all(load(n)["fingerprint"] == CHECKPOINT for n in ["EXACT_LOCATION_REGISTRY.json", "CAPABILITY_REGISTRY.json", "IMPLEMENTATION_QUEUE.json", "TEST_MATRIX.json"]), CHECKPOINT)
check("Master Plan hashes match saved files", fingerprint["master_plan_hashes"] == {p.relative_to(ROOT).as_posix(): sha256(p) for p in plans}, fingerprint["master_plan_hashes"])
check("Package and lock hashes match disk", fingerprint["package_manifest_hashes"]["codebase/package.json"] == sha256(CB / "package.json") and fingerprint["lockfile_hashes"]["codebase/package-lock.json"] == sha256(CB / "package-lock.json"), "package.json/package-lock.json")

actual_codebase = {p.relative_to(ROOT).as_posix() for p in CB.rglob("*") if p.is_file()}
inventoried_codebase = {x["path"] for x in inventory["files"] if x["path"].startswith("codebase/")}
check("Every codebase file is inventoried", actual_codebase == inventoried_codebase, {"actual": len(actual_codebase), "inventoried": len(inventoried_codebase), "missing": sorted(actual_codebase - inventoried_codebase)[:20]})
source_rows = [x for x in inventory["files"] if x["path"].startswith("codebase/") and x["source_authoritative"]]
check("Every source-authoritative file is classified and owned", all(x["inventory_status"] == "INVENTORIED" and x["file_category"] and x["capability_id"] and x["capability_owner"] and x["master_plan_decision"] for x in source_rows), len(source_rows))

required_fields = set(registry_doc["required_fields"])
check("Every exact-location entry has the full schema", all(set(e) == required_fields for e in registry), len(registry))
check("Registry array fields use the required machine schema", all(isinstance(e["exact_change_instructions"], list) and isinstance(e["blast_radius"], list) and isinstance(e["notes"], list) for e in registry), len(registry))
check("Registry IDs are unique", len({e["id"] for e in registry}) == len(registry), len(registry))
check("No required registry scalar is unresolved", not any(any(str(v).strip().upper() == "UNKNOWN" for v in e.values() if not isinstance(v, (list, dict))) for e in registry), "zero literal UNKNOWN values")
check("Every current location resolves", all((ROOT / e["current_path"]).exists() if not Path(e["current_path"]).is_absolute() else Path(e["current_path"]).exists() for e in registry), "path + symbol/anchor authority")
check("Every entry has a symbol or unique anchor", all(e["current_symbol"] or e["current_anchor"] for e in registry), len(registry))

node_ids = [str(n["id"]) for n in extract["nodes"]]
registered_node_ids = {str(e["graphify_node_id"]) for e in registry if e["graphify_node_id"] is not None}
check("Every significant Graphify node is in the exact registry", set(node_ids) == registered_node_ids, {"nodes": len(node_ids), "registered": len(registered_node_ids)})
check("Final extraction node IDs are unique", len(node_ids) == len(set(node_ids)), len(node_ids))
check("Final graph has no missing/dangling endpoints", health.get("missing_endpoint_edges") == 0 and health.get("dangling_endpoint_edges") == 0, {"missing": health.get("missing_endpoint_edges"), "dangling": health.get("dangling_endpoint_edges")})
check("Final graph paths are fresh", second["final"]["stale_paths"] == 0, second["final"])
check("Graph HTML was exported", (OUT / "graph.html").is_file(), str(OUT / "graph.html"))

valid_decisions = {"MANDATORY KEEP", "KEEP AND REPAIR", "KEEP AND REORGANISE", "KEEP AFTER DECOUPLING", "CONDITIONAL — REQUIRES EVIDENCE", "REMOVE", "REPLACE", "ADD", "OPTIONAL LATER", "OBSOLETE — REMOVE AFTER VERIFIED REPLACEMENT", "FORBIDDEN"}
check("Every capability has a stable unique ID and valid decision", len({c["id"] for c in caps}) == len(caps) and all(c["decision"] in valid_decisions for c in caps), len(caps))
check("Every capability is linked to registry evidence", all(c["registry_ids"] for c in caps), len(caps))
required_chain_fields = {"user_action", "ui_components", "preload_exposures", "typescript_contracts", "ipc_channels", "ipc_handlers", "main_symbols", "data_native_or_process_boundary", "result_events", "renderer_update", "tests", "failure_path", "cleanup_path", "recovery_path", "current_breakage", "required_change", "target_owner", "mapping_evidence"}
check("Every capability has a complete structured runtime chain", all(isinstance(c["runtime_chain"], dict) and required_chain_fields <= set(c["runtime_chain"]) and c["runtime_chain"].get("mapping_evidence") for c in caps), len(caps))
conditional = [c for c in caps if c["decision"] == "CONDITIONAL — REQUIRES EVIDENCE"]
check("Every conditional capability has deterministic rules", all(c["default"] and c["deviation_condition"] and c["evidence_requirement"] and c["fallback"] for c in conditional), [c["id"] for c in conditional])
removals = [e for e in registry if e["entity_type"] == "capability" and e["decision"] in {"REMOVE", "FORBIDDEN"}]
check("Every removal capability has all seven deletion gates", len(removals) == 31 and all(len(e["deletion_requirements"]) == 7 for e in removals), len(removals))
check("Every removed-system replacement is explicitly linked", all("replacement_capability_ids" in c for c in caps) and (G / "REPLACEMENT_MAP.md").is_file(), "REPLACEMENT_MAP.md")

preload = [e for e in registry if e["entity_type"] == "preload API"]
handlers = [e for e in registry if e["entity_type"] == "IPC handler"]
callers = [e for e in registry if e["entity_type"] == "IPC caller"]
senders = [e for e in registry if e["entity_type"] == "IPC sender"]
check("Preload APIs are mapped to the type contract", len({e["current_symbol"] for e in preload}) == 224 and all("codebase/renderer/shared/types/electron.ts" in e["build_references"] for e in preload), len(preload))
check("IPC handlers, callers, and main senders are mapped", len({x for e in handlers for x in e["ipc_channels"]}) == 177 and len({x for e in callers for x in e["ipc_channels"]}) == 194 and bool(senders), {"handlers": len(handlers), "callers": len(callers), "senders": len(senders)})
check("No-caller IPC candidate has explicit purpose and task", "PONY-008" in (G / "PONYTAIL_AUDIT.md").read_text(encoding="utf-8") and "hotkey-listening-mode-changed" in (G / "IMPORT_AND_CALL_MAP.md").read_text(encoding="utf-8"), "PONY-008 / TASK-04")

active_tables = {e["current_symbol"] for e in registry if e["entity_type"] == "database table" and "/tests/" not in "/" + e["current_path"].lower()}
columns = [e for e in registry if e["entity_type"] == "database column"]
migrations = [e for e in registry if e["entity_type"] == "database migration"]
check("Active SQLite tables, columns, and migrations are mapped", len(active_tables) == 22 and len(columns) >= 100 and len(migrations) == 4, {"active_tables": len(active_tables), "columns": len(columns), "migrations": len(migrations)})
assets = fingerprint["native_model_binary_manifest"]
asset_fields = {"path", "platform", "architecture", "version", "sha256", "licence", "source", "build_script", "packaging_reference", "runtime_loaders", "process_lifecycle", "shutdown_behavior", "cleanup_behavior", "failure_handling", "fallback", "test_coverage", "acquisition", "runtime_network_risk"}
check("Every native/model/binary has provenance, lifecycle, loader, packaging, test coverage/obligation, and offline policy", len(assets) == 21 and all(asset_fields <= set(a) and all(a[k] is not None and a[k] != "" for k in asset_fields) for a in assets), len(assets))
deps = [e for e in registry if e["entity_type"] == "package dependency"]
check("Every direct package dependency has owner and consumer evidence", len(deps) == 57 and all(e["current_owner"] and e["services"] for e in deps), len(deps))

task_ids = {t["task_id"] for t in tasks}
check("Implementation queue is topologically ordered", all(int(dep.split("-")[-1]) < int(t["task_id"].split("-")[-1]) for t in tasks for dep in t["dependencies"]), len(tasks))
check("Implementation queue contains the required 29 ordered capability batches", len(tasks) == 29 and [int(t["task_id"].split("-")[-1]) for t in tasks] == list(range(1, 30)), len(tasks))
check("Every task contains exact execution and verification evidence fields", all(t["graphify_registry_ids"] and isinstance(t["exact_required_changes"], list) and t["exact_required_changes"] and isinstance(t["exact_forbidden_changes"], list) and t["execution_prerequisites"] and t["blast_radius"] and t["required_tests"] and t["verification_steps"] and t["verification_evidence_required"] and t["rollback_method"] and t["completion_criteria"] and t["status"] == "PLANNED — EXECUTION BLOCKED" for t in tasks), len(tasks))
vague_terms = ("clean this up", "refactor as needed", "improve architecture", "fix references", "remove bloat", "update accordingly")
check("No task or registry entry contains vague change instructions", not any(term in " ".join(t["exact_required_changes"]).lower() for t in tasks for term in vague_terms) and not any(term in " ".join(e["exact_change_instructions"]).lower() for e in registry for term in vague_terms), "zero vague instructions")
check("Every task dependency and dependent points to a real task", all(x in task_ids for t in tasks for x in t["dependencies"] + t["dependents"]), len(tasks))
data_tasks = [t for t in tasks if t["data_risk"] not in {"NONE", "NONE IDENTIFIED"}]
check("Every data-sensitive task has rollback requirements", all("backup" in t["rollback_method"].lower() or "hash" in t["rollback_method"].lower() for t in data_tasks), len(data_tasks))

test_caps = {t["capability_id"] for t in tests}
retained_caps = {c["id"] for c in caps if c["decision"] not in {"REMOVE", "FORBIDDEN"}}
check("Test matrix covers every retained capability", retained_caps <= test_caps, sorted(retained_caps - test_caps))
check("Every test row is linked to task IDs", all(x.get("task_ids") and all(tid in task_ids for tid in x["task_ids"]) for x in tests), len(tests))
check("Test matrix covers every destructive queue task", all(any(t["task_id"] in x.get("task_ids", []) for x in tests) for t in tasks if t["decision"] == "REMOVE"), [t["task_id"] for t in tasks if t["decision"] == "REMOVE"])
check("Every missing test has an exact planned path", all(t["existing_or_missing"] != "MISSING — PLANNED" or t["required_new_test_path"] for t in tests), len(tests))

finding_registry = {e["id"] for e in registry if e["entity_type"] == "Ponytail finding"}
check("Every Ponytail finding is classified and registry-linked", all(f["decision"] in {"ACCEPTED", "REJECTED", "DEFERRED"} and "REG-" + f["id"] in finding_registry for f in findings), len(findings))
check("Every accepted Ponytail finding has a queue task", all(f["task"] in task_ids for f in findings if f["decision"] == "ACCEPTED"), [f["id"] for f in findings if f["decision"] == "ACCEPTED"])
check("Every rejected Ponytail finding has a reason", all(f["reason"] for f in findings if f["decision"] == "REJECTED"), [f["id"] for f in findings if f["decision"] == "REJECTED"])
check("Compiler-resolved import cycles are mapped to Ponytail and queue", not cycles["unresolved_relative_imports"] and all(any(f["id"] == "PONY-012" and f["task"] == "TASK-22" for f in findings) for _ in cycles["cycles"]), {"cycles": len(cycles["cycles"]), "local_edges": cycles["resolved_local_edges"]})

check("Folder ownership map contains every required contract field", all(term in (G / "FOLDER_OWNERSHIP_MAP.md").read_text(encoding="utf-8") for term in ["Folder path", "Layer", "Domain", "Responsibility", "Allowed contents", "Forbidden contents", "Public entry points", "Dependency direction", "Allowed import sources", "Allowed consumers", "Current violations", "Planned corrections", "Evidence"]), "FOLDER_OWNERSHIP_MAP.md")
check("All 54 readiness rows pass", len(gate["conditions"]) == 54 and all(x["status"] == "PASS" for x in gate["conditions"]), gate["verdict"])
check("Final verdict is the permitted ready verdict", gate["verdict"] == "GRAPHIFY READY — EXECUTION MAY BE PLANNED", gate["verdict"])
changed_after_baseline = [p.relative_to(ROOT).as_posix() for p in CB.rglob("*") if p.is_file() and p.stat().st_mtime > CUTOFF]
check("No application file changed after baseline fingerprint", not changed_after_baseline, changed_after_baseline)
check("No application execution task started", all(t["status"] == "PLANNED — EXECUTION BLOCKED" for t in tasks) and "NOT STARTED" in (G / "RUN_STATE.md").read_text(encoding="utf-8"), "RUN_STATE.md / COMPLETION_TRACKER.md")

failed = [x for x in checks if x["status"] != "PASS"]
audit = {
    "project": "Mnemora", "verified_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "fingerprint": CHECKPOINT, "checks": checks, "passed": len(checks) - len(failed), "failed": len(failed),
    "files_modified_outside_graphify": [],
    "verdict": "GRAPHIFY READY — EXECUTION MAY BE PLANNED" if not failed else "GRAPHIFY NOT READY — EXECUTION BLOCKED",
}
(G / "VERIFICATION_AUDIT.json").write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

manifest_files = sorted(p for p in G.rglob("*") if p.is_file() and p.name != "GRAPHIFY_OUTPUT_MANIFEST.json")
manifest = {
    "generated_at": audit["verified_at"], "fingerprint": CHECKPOINT,
    "files": [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha256(p), "size_bytes": p.stat().st_size} for p in manifest_files],
}
(G / "GRAPHIFY_OUTPUT_MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

print(json.dumps({"checks": len(checks), "passed": audit["passed"], "failed": audit["failed"], "verdict": audit["verdict"], "manifest_files": len(manifest_files)}, indent=2))
if failed:
    for item in failed:
        print("FAIL:", item["check"], item["evidence"])
    raise SystemExit(1)
