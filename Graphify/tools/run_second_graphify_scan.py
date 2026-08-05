#!/usr/bin/env python3
"""Run Mnemora's validating Graphify scan without touching application files."""

from __future__ import annotations

import collections
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.build import build_from_json
from graphify.cluster import cluster, score_all
from graphify.diagnostics import diagnose_extraction
from graphify.export import to_json
from graphify.extract import extract
from graphify.report import generate


ROOT = Path(__file__).resolve().parents[2]
GRAPHIFY = ROOT / "Graphify"
OUT = GRAPHIFY / "graphify-out"
INITIAL = OUT / "initial"


def source_path(value: str | None) -> Path | None:
    if not value:
        return None
    p = Path(value)
    return p if p.is_absolute() else ROOT / value


def allowed(value: str | None) -> bool:
    if not value:
        return True
    normalized = str(value).replace("\\", "/").lower()
    return "/node_modules/" not in "/" + normalized and "/build-output/" not in "/" + normalized


initial_detect = json.loads((INITIAL / ".graphify_detect.json").read_text(encoding="utf-8"))
files = {
    kind: [p for p in values if allowed(p)]
    for kind, values in initial_detect["files"].items()
}

# Graphify's generic detector treats a directory named "build" as generated output.
# In this repository, codebase/scripts/build contains hand-maintained native build
# scripts. Explicitly restore all source-code extensions while still excluding the
# real node_modules and build-output trees.
source_extensions = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".c", ".cc", ".cpp", ".h", ".hpp", ".swift", ".m", ".mm", ".py", ".ps1"}
code_paths = {str(Path(p).resolve()).lower(): p for p in files["code"]}
for path in (ROOT / "codebase").rglob("*"):
    if not path.is_file() or path.suffix.lower() not in source_extensions or not allowed(str(path)):
        continue
    code_paths.setdefault(str(path.resolve()).lower(), str(path.resolve()))
files["code"] = sorted(code_paths.values())

# Keep the semantic corpus source-grounded. Operational Graphify files are validated
# as registries, not recursively embedded into their own source graph.
for kind in ("document", "paper", "image", "video"):
    files[kind] = [p for p in files[kind] if "/graphify/" not in p.replace("\\", "/").lower() or "/graphify/master plan/" in p.replace("\\", "/").lower()]

word_count = 0
for values in files.values():
    for value in values:
        p = Path(value)
        try:
            word_count += len(p.read_text(encoding="utf-8", errors="ignore").split())
        except OSError:
            pass

detection = {
    **initial_detect,
    "files": files,
    "total_files": sum(len(v) for v in files.values()),
    "total_words": word_count,
    "warning": "Second source-authoritative scan excludes installed dependencies and generated build-output symbols; both remain in the complete inventory.",
    "scan_root": str(ROOT),
    "second_scan_timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
(OUT / ".graphify_detect.json").write_text(json.dumps(detection, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

code_files = [Path(p) for p in files["code"]]
ast = extract(code_files, cache_root=GRAPHIFY, parallel=False)


def normalize_graph_source(value: str | None) -> str | None:
    if not value:
        return value
    path = Path(value)
    if not path.is_absolute():
        graphify_relative = (GRAPHIFY / path).resolve()
        root_relative = (ROOT / path).resolve()
        path = graphify_relative if graphify_relative.exists() else root_relative
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


for node in ast.get("nodes", []):
    node["source_file"] = normalize_graph_source(node.get("source_file"))
for edge in ast.get("edges", []):
    edge["source_file"] = normalize_graph_source(edge.get("source_file"))
(OUT / ".graphify_ast.json").write_text(json.dumps(ast, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

semantic_source = json.loads((OUT / ".graphify_semantic.json").read_text(encoding="utf-8"))
semantic_nodes = [n for n in semantic_source.get("nodes", []) if allowed(n.get("source_file"))]
semantic_ids = {str(n.get("id")) for n in semantic_nodes}
semantic_edges = [
    e for e in semantic_source.get("edges", [])
    if allowed(e.get("source_file")) and str(e.get("source")) in semantic_ids and str(e.get("target")) in semantic_ids
]
semantic_hyperedges = [h for h in semantic_source.get("hyperedges", []) if allowed(h.get("source_file"))]
semantic = {"nodes": semantic_nodes, "edges": semantic_edges, "hyperedges": semantic_hyperedges}
(OUT / ".graphify_semantic.json").write_text(json.dumps(semantic, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

nodes = []
canonical_nodes: dict[str, dict] = {}
for raw_node in ast.get("nodes", []):
    node_id = str(raw_node.get("id"))
    if node_id not in canonical_nodes:
        node = dict(raw_node)
        node["source_evidence"] = [{"source_file": raw_node.get("source_file"), "source_location": raw_node.get("source_location")}]
        canonical_nodes[node_id] = node
        nodes.append(node)
    else:
        canonical_nodes[node_id]["source_evidence"].append({"source_file": raw_node.get("source_file"), "source_location": raw_node.get("source_location")})
seen = set(canonical_nodes)
for node in semantic_nodes:
    if str(node.get("id")) not in seen:
        nodes.append(node)
        seen.add(str(node.get("id")))
edges = list(ast.get("edges", [])) + semantic_edges

# Graphify AST intentionally names external modules with ref_* endpoints. Materialize
# them as truthful external-reference nodes so dependency edges are not silently dropped.
endpoint_context: dict[str, dict] = {}
for edge in edges:
    for endpoint in (str(edge.get("source")), str(edge.get("target"))):
        if endpoint not in seen:
            endpoint_context.setdefault(endpoint, edge)
for endpoint, edge in sorted(endpoint_context.items()):
    label = re.sub(r"^ref_", "", endpoint).replace("_", " ").strip() or endpoint
    nodes.append({
        "id": endpoint,
        "label": label,
        "file_type": "concept",
        "source_file": edge.get("source_file"),
        "source_location": edge.get("source_location"),
        "_origin": "external_reference",
    })
    seen.add(endpoint)

# Repair four source-proven relationships that the generic extractors cannot infer:
# one exported alias and three non-code image asset loads. The unused logo stays
# orphaned deliberately and is classified by Ponytail rather than given a fake edge.
def source_module_id(source_file: str) -> str | None:
    candidates = [n for n in nodes if str(n.get("source_file", "")).replace("\\", "/") == source_file]
    if not candidates:
        return None
    basename = Path(source_file).name.lower()
    candidates.sort(key=lambda n: (str(n.get("label", "")).lower() != basename, str(n.get("source_location")) != "L1", len(str(n.get("id")))))
    return str(candidates[0].get("id"))


source_proven_edges = [
    ("codebase/renderer/features/settings/settingsStore.ts", "codebase_renderer_features_settings_settingsstore_selectresolveduploadtranscription", "contains", "L364"),
    ("codebase/renderer/app/components/ControlPanelSidebar.tsx", "codebase_renderer_assets_icon_mnemora_application_icon", "loads_asset", "L3"),
    ("codebase/main/desktop/tray.js", "codebase_renderer_assets_icontemplate_3x_circular_monogram_icon", "loads_asset", "L138"),
    ("codebase/scripts/build/compile-macos-icon.js", "codebase_renderer_assets_mnemora_icon_assets_icon_mnemora_brand_icon", "builds_asset_bundle", "L15"),
]
existing_edge_keys = {(str(e.get("source")), str(e.get("target")), str(e.get("relation"))) for e in edges}
for source_file, target, relation, source_location in source_proven_edges:
    source = source_module_id(source_file)
    if target not in seen and relation == "contains":
        target = next((str(n.get("id")) for n in nodes if str(n.get("source_file", "")).replace("\\", "/") == source_file and n.get("label") == "selectResolvedUploadTranscription"), target)
    key = (source, target, relation)
    if source and source in seen and target in seen and key not in existing_edge_keys:
        edges.append({
            "source": source, "target": target, "relation": relation,
            "context": "source-proven static asset/alias reference", "confidence": "EXTRACTED",
            "source_file": source_file, "source_location": source_location, "weight": 1.0,
            "_origin": "graph_repair",
        })
        existing_edge_keys.add(key)

merged = {
    "nodes": nodes,
    "edges": edges,
    "hyperedges": semantic_hyperedges,
    "input_tokens": semantic_source.get("input_tokens", 0),
    "output_tokens": semantic_source.get("output_tokens", 0),
}
(OUT / ".graphify_extract.json").write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

graph = build_from_json(merged, root=str(ROOT), directed=False)
if graph.number_of_nodes() == 0:
    raise SystemExit("Graphify second scan produced an empty graph")
communities = cluster(graph)
cohesion = score_all(graph, communities)
gods = god_nodes(graph)
surprises = surprising_connections(graph, communities)

node_by_id = {str(n.get("id")): n for n in nodes}


def community_label(member_ids: list[str]) -> str:
    path_tokens: list[str] = []
    labels: list[str] = []
    for node_id in member_ids:
        node = node_by_id.get(str(node_id), {})
        labels.append(str(node.get("label", "")))
        source = str(node.get("source_file", "")).replace("\\", "/")
        parts = [p for p in source.split("/") if p]
        for marker in ("features", "services", "persistence", "ipc", "native", "renderer", "main", "tests", "scripts"):
            if marker in parts:
                idx = parts.index(marker)
                path_tokens.extend(parts[idx:idx + 2])
                break
    common = [x for x, _ in collections.Counter(path_tokens).most_common(2) if x]
    if not common:
        common = [x for x, _ in collections.Counter(labels).most_common(2) if x]
    words = []
    for value in common:
        words.extend(re.findall(r"[A-Za-z0-9]+", value))
    words = words[:4]
    if len(words) < 2:
        words.append("References" if any(str(node_by_id.get(str(i), {}).get("_origin")) == "external_reference" for i in member_ids) else "Runtime")
    return " ".join(w.capitalize() for w in words[:5])


labels = {cid: community_label(members) for cid, members in communities.items()}
questions = suggest_questions(graph, communities, labels)
written = to_json(graph, communities, str(OUT / "graph.json"), force=True, community_labels=labels)
if not written:
    raise SystemExit("Graphify refused to write the validated graph")
tokens = {"input": merged.get("input_tokens", 0), "output": merged.get("output_tokens", 0)}
report = generate(graph, communities, cohesion, labels, gods, surprises, detection, tokens, str(ROOT), suggested_questions=questions)
(OUT / "GRAPH_REPORT.md").write_text(report, encoding="utf-8")
(OUT / ".graphify_analysis.json").write_text(json.dumps({
    "communities": {str(k): v for k, v in communities.items()},
    "cohesion": {str(k): v for k, v in cohesion.items()},
    "gods": gods, "surprises": surprises, "questions": questions,
}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(OUT / ".graphify_labels.json").write_text(json.dumps({str(k): v for k, v in labels.items()}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

health = diagnose_extraction(merged, directed=False, root=str(ROOT), extract_path=OUT / ".graphify_extract.json")
(OUT / "GRAPH_HEALTH.json").write_text(json.dumps(health, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")

node_ids = [str(n.get("id")) for n in nodes]
stale = []
for node in nodes:
    source = source_path(node.get("source_file"))
    if node.get("_origin") != "external_reference" and source and not source.exists():
        stale.append(str(node.get("source_file")))

marker = {
    "completed_at": detection["second_scan_timestamp"],
    "initial": {
        "supported_files": initial_detect["total_files"],
        "nodes": json.loads((INITIAL / ".graphify_extract.json").read_text(encoding="utf-8"))["nodes"].__len__(),
        "edges": json.loads((INITIAL / ".graphify_extract.json").read_text(encoding="utf-8"))["edges"].__len__(),
    },
    "final": {
        "supported_files": detection["total_files"], "code_files": len(code_files),
        "nodes": len(nodes), "edges": len(edges), "communities": len(communities),
        "external_reference_nodes": len(endpoint_context), "stale_paths": len(set(stale)),
        "duplicate_node_ids": len(node_ids) - len(set(node_ids)),
        "dangling_endpoint_edges": health.get("dangling_endpoint_edges", 0),
        "missing_endpoint_edges": health.get("missing_endpoint_edges", 0),
    },
    "repair": "Removed generated build-output symbols from source authority; retained them in inventory; restored hand-maintained scripts/build sources hidden by generic detector rules; materialized Graphify ref_* external endpoints; refreshed line locations and community labels.",
}
failed = [k for k in ("stale_paths", "duplicate_node_ids", "dangling_endpoint_edges", "missing_endpoint_edges") if marker["final"][k] != 0]
if failed:
    raise SystemExit("Second Graphify scan failed: " + ", ".join(failed))
(OUT / "SECOND_SCAN_COMPLETE").write_text(json.dumps(marker, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(marker, indent=2, ensure_ascii=False))
