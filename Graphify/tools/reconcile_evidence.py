#!/usr/bin/env python3
"""Deterministic manifest and repository-evidence reconciliation CLI.

Read-only with respect to application and Git content. Writes only the
requested manifest file or temp artifacts. Manifest format:

    <SHA-256><TAB><repository-relative path>

Tracked manifests are generated from git blob content (line-ending
independent and reproducible from any clean clone).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from semantic_validator import (
    TRANSIENT_MANIFEST_PARTS,
    TRANSIENT_MANIFEST_SUFFIXES,
    build_graphify_output_manifest,
    current_tracked_codebase_mapping,
    git,
    manifest_pair_stats,
    parse_manifest,
    sha256,
)


ROOT = Path(__file__).resolve().parents[2]
G = ROOT / "Graphify"


def generate_tracked_manifest(out_path: Path) -> dict[str, Any]:
    mapping, errors = current_tracked_codebase_mapping()
    if errors:
        raise RuntimeError("; ".join(errors))
    lines = [f"{mapping[path]}\t{path}" for path in sorted(mapping)]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    raw = out_path.read_bytes()
    return {
        "entries": len(lines),
        "raw_sha256": hashlib.sha256(raw).hexdigest().upper(),
        "bytes": len(raw),
        "path": str(out_path),
    }


def cmd_generate(args: argparse.Namespace) -> int:
    print(json.dumps(generate_tracked_manifest(Path(args.out)), indent=2))
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    historical = manifest_pair_stats(G / "AUDIT_CODEBASE_BASELINE_SHA256.txt", G / "AUDIT_CODEBASE_FINAL_SHA256.txt")
    canonical = manifest_pair_stats(G / "TRACKED_CODEBASE_BASELINE_SHA256.txt", G / "TRACKED_CODEBASE_FINAL_SHA256.txt")
    current_map, current_errors = current_tracked_codebase_mapping()
    canonical_final_map, _ = parse_manifest(G / "TRACKED_CODEBASE_FINAL_SHA256.txt")
    result = {
        "historical_full_tree_manifests": {
            "raw_baseline_sha256": sha256(G / "AUDIT_CODEBASE_BASELINE_SHA256.txt"),
            "raw_final_sha256": sha256(G / "AUDIT_CODEBASE_FINAL_SHA256.txt"),
            "raw_files_byte_identical": sha256(G / "AUDIT_CODEBASE_BASELINE_SHA256.txt") == sha256(G / "AUDIT_CODEBASE_FINAL_SHA256.txt"),
            **historical,
        },
        "canonical_tracked_manifests": {
            "raw_baseline_sha256": sha256(G / "TRACKED_CODEBASE_BASELINE_SHA256.txt"),
            "raw_final_sha256": sha256(G / "TRACKED_CODEBASE_FINAL_SHA256.txt"),
            "raw_files_byte_identical": sha256(G / "TRACKED_CODEBASE_BASELINE_SHA256.txt") == sha256(G / "TRACKED_CODEBASE_FINAL_SHA256.txt"),
            **canonical,
            "current_mapping_identical_to_final": current_map == canonical_final_map and not current_errors,
        },
    }
    print(json.dumps(result, indent=2))
    return 0 if (historical["mappings_identical"] and canonical["mappings_identical"] and current_map == canonical_final_map and not current_errors) else 1


def cmd_check_transient(args: argparse.Namespace) -> int:
    entries, scan_errors = build_graphify_output_manifest()
    problems = list(scan_errors)
    committed = json.loads((G / "GRAPHIFY_OUTPUT_MANIFEST.json").read_text(encoding="utf-8"))
    tracked = {line for line in git(["ls-files"]).splitlines() if line.startswith("Graphify/")}
    for entry in committed.get("files", []):
        rel = str(entry.get("path", ""))
        if set(rel.split("/")) & TRANSIENT_MANIFEST_PARTS or rel.endswith(TRANSIENT_MANIFEST_SUFFIXES):
            problems.append(f"committed output manifest contains transient entry: {rel}")
        if rel and f"Graphify/{rel}" not in tracked:
            problems.append(f"committed output manifest contains non-tracked entry: {rel}")
    result = {"committed_entries": len(committed.get("files", [])), "regenerated_entries": len(entries), "problems": problems}
    print(json.dumps(result, indent=2))
    return 0 if not problems else 1


def cmd_determinism(args: argparse.Namespace) -> int:
    with tempfile.TemporaryDirectory(prefix="mnemora-determinism-") as tmp:
        first = Path(tmp) / "first.txt"
        second = Path(tmp) / "second.txt"
        first_result = generate_tracked_manifest(first)
        second_result = generate_tracked_manifest(second)
        first_bytes = first.read_bytes()
        second_bytes = second.read_bytes()
        result = {
            "first": first_result,
            "second": second_result,
            "byte_identical": first_bytes == second_bytes,
            "raw_sha256_identical": first_result["raw_sha256"] == second_result["raw_sha256"],
        }
        print(json.dumps(result, indent=2))
        return 0 if (first_bytes == second_bytes and result["raw_sha256_identical"]) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate-tracked-manifest", help="Write the deterministic tracked codebase manifest")
    gen.add_argument("out", help="Output path (repository-relative or absolute)")
    gen.set_defaults(func=cmd_generate)
    cmp = sub.add_parser("compare", help="Structured comparison of historical and canonical manifests")
    cmp.set_defaults(func=cmd_compare)
    tr = sub.add_parser("check-transient", help="Check the Graphify output manifest for transient/non-tracked entries")
    tr.set_defaults(func=cmd_check_transient)
    det = sub.add_parser("determinism", help="Generate the tracked manifest twice and prove byte-identical output")
    det.set_defaults(func=cmd_determinism)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
