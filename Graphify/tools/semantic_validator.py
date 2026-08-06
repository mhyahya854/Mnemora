#!/usr/bin/env python3
"""Deterministic structural and semantic validator for Mnemora planning.

The validator reads application files but writes only derived reports in Graphify.
It does not execute application tests, builds, packaging, migrations, or Git writes.
"""

from __future__ import annotations

import argparse
import collections
import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

from semantic_rules import PRODUCT_SCOPE_CAPS, REMOVAL_CAPS, VENDOR_OR_GENERATED_MARKERS


ROOT = Path(__file__).resolve().parents[2]
G = ROOT / "Graphify"
CB = ROOT / "codebase"
MP = G / "Master Plan"
MASTER_HASHES = {
    "01-EVERYTHING-WE-ARE-KEEPING.md": "BDF185A823422BCAA9BFEBA815A6852D8F7A5CD46B64714B2CD1DE3357A67F64",
    "02-EVERYTHING-WE-ARE-DELETING.md": "76B6EEC15778B1928F2CD9C0F73FA68C9F3363493062E31E0C904E620DE0AAC3",
    "03-HOW-WE-WILL-KEEP-DELETE-AND-REPLACE.md": "5E076498731C35ACF314904AAB3A39671F7026A166B5E847EFE3CCD4CF07304E",
}
AUTHORITY_FILES = [
    "MASTER_REQUIREMENT_REGISTER.json", "INTERPRETATION_REGISTER.json", "CAPABILITY_REGISTRY.json",
    "EXACT_LOCATION_REGISTRY.json", "IMPLEMENTATION_QUEUE.json", "TEST_MATRIX.json",
    "CONDITIONAL_DECISION_PACKAGES.json", "RELEASE_GATE_PLAN.json",
]
BDI_IDS = {
    "BDI-1-STATIC-IMPORT-EXPORT", "BDI-2-DYNAMIC-AND-STRING-REFERENCES", "BDI-3-RUNTIME-REGISTRATION",
    "BDI-4-DATABASE-SETTINGS-ENVIRONMENT", "BDI-5-NATIVE-ASSET-BUILD-PACKAGING",
    "BDI-6-TEST-FIXTURE", "BDI-7-LICENCE-FUTURE-PLAN",
}
DELETION_LAYERS = {
    "UI", "navigation", "route", "component", "hook/store", "preload", "TypeScript contract",
    "IPC channel", "IPC handler", "service", "database/filesystem/native effect", "settings",
    "environment variables", "dependency", "tests", "fixtures", "translations", "build", "packaging",
}
DISPOSITIONS = {
    "ACTIVE REMOVAL CANDIDATE", "RETAINED DEPENDENCY - DO NOT DELETE", "HISTORICAL MIGRATION - PRESERVE",
    "LEGAL/ATTRIBUTION - PRESERVE", "BUILD-TIME ONLY - REVIEW UNDER BUILD RULE",
    "POSITIVE OFFLINE/LOCAL MESSAGE - RETAIN", "FALSE POSITIVE", "REQUIRES IMPLEMENTATION-TIME STATIC PROOF",
    "REQUIRES IMPLEMENTATION-TIME DYNAMIC PROOF", "REQUIRES PACKAGED-APPLICATION PROOF",
}
LOCATION_CLASSES = {
    "OWNED SOURCE", "OWNED TEST", "CONFIGURATION", "DATABASE/MIGRATION", "NATIVE SOURCE",
    "BUNDLED RUNTIME ASSET", "THIRD-PARTY DEPENDENCY", "GENERATED OUTPUT", "VENDOR FILE",
    "FUTURE TARGET", "ABSENT - PLANNED ADDITION", "HISTORICAL MIGRATION", "LEGAL/ATTRIBUTION",
}
TASK_FIELDS = {
    "stable_task_id", "capability_id", "master_requirement_ids", "exact_purpose", "current_paths",
    "current_symbols", "intended_target_paths", "intended_target_symbols", "presence_absence_status",
    "preconditions", "semantic_dependencies", "dependents", "phase", "wave", "execution_order",
    "files_expected_to_change", "files_forbidden_from_changing", "characterisation_tests_required_before_change",
    "exact_implementation_actions", "data_impact", "migration_impact", "ipc_impact", "native_impact",
    "packaging_impact", "offline_verification_impact", "targeted_verification", "real_integration_verification",
    "broader_regression_verification", "rollback_or_recovery_strategy", "required_evidence_artifacts",
    "acceptance_criteria", "completion_criteria", "stop_conditions", "risk_classification", "ordering_rationale",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().upper()


def load(name: str) -> Any:
    return json.loads((G / name).read_text(encoding="utf-8"))


def dump(name: str, value: Any) -> None:
    (G / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


TRANSIENT_MANIFEST_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".git"}
TRANSIENT_MANIFEST_SUFFIXES = (".pyc", ".pyo", ".swp", ".swo", ".tmp", ".log", "~")
VERIFIER_OUTPUT_FILES = {
    "Graphify/FINAL-REPOSITORY-RECONCILIATION.json",
    "Graphify/FINAL-REPOSITORY-RECONCILIATION.md",
    "Graphify/PLANNING_VALIDATION_REPORT.json",
    "Graphify/PLANNING_VALIDATION_REPORT.md",
    "Graphify/VERIFICATION_AUDIT.json",
    "Graphify/READINESS_GATE.json",
    "Graphify/READINESS_GATE.md",
    "Graphify/GRAPH_CONSISTENCY_REPORT.json",
    "Graphify/GRAPH_CONSISTENCY_REPORT.md",
    "Graphify/GRAPHIFY_READINESS_REPORT.md",
    "Graphify/GRAPHIFY_OUTPUT_MANIFEST.json",
}


def git(args: list[str]) -> str:
    """Read-only git helper returning trimmed stdout (empty string on failure)."""
    try:
        result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return ""


def git_blob_sha256(rel_path: str) -> str:
    """Canonical SHA-256 of committed blob content (line-ending independent)."""
    try:
        result = subprocess.run(["git", "cat-file", "blob", f"HEAD:{rel_path}"], cwd=ROOT, capture_output=True)
        if result.returncode == 0:
            return hashlib.sha256(result.stdout).hexdigest().upper()
    except Exception:
        pass
    return sha256(ROOT / rel_path)


def parse_manifest(path: Path) -> tuple[dict[str, str], list[str]]:
    """Parse HASH\\tpath manifest lines into a normalized path -> SHA-256 mapping.

    Normalization: forward slashes, no leading ./, no duplicate separators,
    no unresolved . or .. components. Duplicate paths and case-insensitive
    collisions are reported as errors rather than silently merged.
    """
    mapping: dict[str, str] = {}
    lower_to_norm: dict[str, str] = {}
    errors: list[str] = []
    if not path.is_file():
        return mapping, [f"{path.name}: missing manifest"]
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            errors.append(f"{path.name}:{number}: blank entry")
            continue
        if "\t" not in line:
            errors.append(f"{path.name}:{number}: malformed entry (missing tab)")
            continue
        digest, _, raw_path = line.partition("\t")
        raw_path = raw_path.strip()
        if not re.fullmatch(r"[0-9A-Fa-f]{64}", digest):
            errors.append(f"{path.name}:{number}: invalid SHA-256 value {digest!r}")
        if not raw_path:
            errors.append(f"{path.name}:{number}: blank path")
            continue
        parts = [part for part in raw_path.replace("\\", "/").split("/") if part not in ("", ".")]
        if any(part == ".." for part in parts):
            errors.append(f"{path.name}:{number}: unresolved parent component {raw_path!r}")
            continue
        norm = "/".join(parts)
        if not norm or norm.startswith("/") or ":" in norm.split("/", 1)[0] or len(norm) > 512:
            errors.append(f"{path.name}:{number}: invalid path {raw_path!r}")
            continue
        key = norm.lower()
        if key in lower_to_norm:
            if lower_to_norm[key] != norm:
                errors.append(f"{path.name}:{number}: case-insensitive collision {lower_to_norm[key]!r} vs {norm!r}")
            elif mapping.get(norm) != digest.upper():
                errors.append(f"{path.name}:{number}: duplicate path with conflicting hash {norm!r}")
            else:
                errors.append(f"{path.name}:{number}: duplicate path {norm!r}")
            continue
        lower_to_norm[key] = norm
        mapping[norm] = digest.upper()
    return mapping, errors


def current_tracked_codebase_mapping() -> tuple[dict[str, str], list[str]]:
    """Canonical tracked mapping: SHA-256 of each git blob under codebase/."""
    mapping: dict[str, str] = {}
    errors: list[str] = []
    result = subprocess.run(["git", "ls-files", "-s", "-z", "--", "codebase"], cwd=ROOT, capture_output=True)
    if result.returncode != 0:
        return mapping, ["git ls-files -- codebase failed"]
    for raw in result.stdout.decode("utf-8", errors="replace").split("\0"):
        if not raw:
            continue
        parts = raw.split(" ", 2)
        if len(parts) < 3 or "\t" not in parts[2]:
            continue
        blob_sha, path = parts[1], parts[2].split("\t", 1)[1]
        blob_out = subprocess.run(["git", "cat-file", "blob", blob_sha], cwd=ROOT, capture_output=True)
        if blob_out.returncode != 0:
            errors.append(f"cannot read tracked blob for {path}")
            continue
        mapping[path.replace("\\", "/")] = hashlib.sha256(blob_out.stdout).hexdigest().upper()
    return mapping, errors


def graphify_tracked_set() -> set[str]:
    return {line for line in git(["ls-files"]).splitlines() if line.startswith("Graphify/")}


def build_graphify_output_manifest() -> tuple[list[dict[str, Any]], list[str]]:
    """Deterministic Graphify output manifest: sorted tracked files, transient excluded."""
    tracked = graphify_tracked_set()
    entries: list[dict[str, Any]] = []
    errors: list[str] = []
    for path in sorted(G.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(G).as_posix()
        if "graphify-out" in path.parts or path.name == "GRAPHIFY_OUTPUT_MANIFEST.json":
            continue
        if set(path.parts) & TRANSIENT_MANIFEST_PARTS or rel.endswith(TRANSIENT_MANIFEST_SUFFIXES):
            continue
        if f"Graphify/{rel}" not in tracked:
            errors.append(f"untracked Graphify file present: {rel}")
            continue
        entries.append({"path": rel, "size_bytes": path.stat().st_size, "sha256": sha256(path)})
    return entries, errors


def write(name: str, value: str) -> None:
    (G / name).write_text(value.rstrip() + "\n", encoding="utf-8")


def duplicates(values: Iterable[str]) -> list[str]:
    counts = collections.Counter(values)
    return sorted(value for value, count in counts.items() if count > 1)


def count_by(items: list[dict[str, Any]], field: str) -> dict[str, int]:
    counts: collections.Counter[str] = collections.Counter()
    for item in items:
        values = item.get(field, [])
        if not isinstance(values, list):
            values = [values]
        counts.update(str(value) for value in values)
    return dict(sorted(counts.items()))


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[`*_>#]", "", value)).strip().lower()


def normalized_tokens(value: str) -> list[str]:
    """Markdown-insensitive tokens used for ordered source reconciliation."""
    return re.findall(r"[a-z0-9]+", normalize(value))


def is_ordered_subsequence(needle: list[str], haystack: list[str]) -> bool:
    position = 0
    for token in haystack:
        if position < len(needle) and token == needle[position]:
            position += 1
    return position == len(needle)


class Checks:
    def __init__(self) -> None:
        self.items: list[dict[str, Any]] = []

    def add(self, check_id: str, name: str, errors: Iterable[str], details: dict[str, Any] | None = None) -> None:
        failures = list(errors)
        self.items.append({
            "check_id": check_id,
            "name": name,
            "status": "PASS" if not failures else "FAIL",
            "error_count": len(failures),
            "errors": failures[:250],
            "details": details or {},
        })


def strip_volatile(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: strip_volatile(item) for key, item in sorted(value.items()) if key not in {"generated_at", "validated_at", "verified_at"}}
    if isinstance(value, list):
        return [strip_volatile(item) for item in value]
    return value


def semantic_authority_fingerprint() -> str:
    payload = {name: strip_volatile(load(name)) for name in AUTHORITY_FILES}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest().upper()


def requirement_source_errors(requirements: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    by_file: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for requirement in requirements:
        by_file[requirement["source_master_plan"]].append(requirement)
        path = MP / requirement["source_master_plan"]
        if not path.is_file():
            errors.append(f"{requirement['stable_requirement_id']}: missing source file")
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        start, end = requirement.get("source_line_start"), requirement.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 1 or end < start or end > len(lines):
            errors.append(f"{requirement['stable_requirement_id']}: invalid line range")
            continue
        actual = normalized_tokens(" ".join(lines[start - 1:end]))
        excerpt = normalized_tokens(requirement.get("source_excerpt", ""))
        # A contextual contract may join an introducing paragraph to one later
        # bullet while its contiguous range also contains sibling bullets.  Its
        # exact excerpt must therefore occur in order, not necessarily adjacent.
        if excerpt and not is_ordered_subsequence(excerpt, actual):
            errors.append(f"{requirement['stable_requirement_id']}: excerpt does not reconcile with source lines {start}-{end}")
        if not str(requirement.get("source_anchor", "")).endswith(f"-L{start}"):
            errors.append(f"{requirement['stable_requirement_id']}: source anchor does not encode line {start}")
    # Independently require every substantive Master Plan line to fall within a
    # normalized requirement range. Headings/front matter/separators are metadata.
    for name in MASTER_HASHES:
        lines = (MP / name).read_text(encoding="utf-8").splitlines()
        covered: set[int] = set()
        for requirement in by_file[name]:
            covered.update(range(requirement["source_line_start"], requirement["source_line_end"] + 1))
        frontmatter = False
        fence = False
        for number, line in enumerate(lines, 1):
            stripped = line.strip()
            if number == 1 and stripped == "---":
                frontmatter = True
                continue
            if frontmatter:
                if stripped == "---": frontmatter = False
                continue
            if stripped.startswith("```"):
                fence = not fence
                continue
            is_table_header = stripped.startswith("|") and number < len(lines) and bool(re.match(r"^\|[\s:|-]+\|$", lines[number].strip()))
            if not stripped or stripped == "---" or re.match(r"^#{1,6}\s+", stripped) or re.match(r"^\|[\s:|-]+\|$", stripped) or is_table_header:
                continue
            if re.match(r"(?i)^[-*+]\s+classification:\s*", stripped):
                continue
            if number not in covered:
                errors.append(f"{name}: substantive source line {number} is not covered by a requirement record")
    return errors


def scope_lock_errors(requirements: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    locks = [item for item in requirements if "retained product scope" in item["requirement_summary"].lower()]
    if {(item["source_master_plan_code"], item["source_line_start"]) for item in locks} != {("MP1", 11), ("MP2", 11), ("MP3", 175)}:
        errors.append("The three exact product-scope declarations were not independently normalized")
    for item in locks:
        if item["requirement_type"] != "Product requirement":
            errors.append(f"{item['stable_requirement_id']}: product scope is not a Product requirement")
        if set(item["capability_ids"]) != set(PRODUCT_SCOPE_CAPS):
            errors.append(f"{item['stable_requirement_id']}: product scope capability set is incomplete or contaminated")
        if item["source_master_plan_code"] == "MP2" and item["retained_or_removed_scope"] != "PROTECTED RETAINED SCOPE":
            errors.append(f"{item['stable_requirement_id']}: MP2 scope lock is not protected retained scope")
    return errors


def capability_runtime_errors(capabilities: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    by_id = {item["id"]: item for item in capabilities}
    expected_owners = {
        "CAP-AEC": "Meeting audio", "CAP-DICTATION": "Dictation", "CAP-MEETING": "Meeting workflow",
        "CAP-PLAYBACK": "Playback", "CAP-VAD": "Local transcription", "CAP-SEARCH-EXACT": "Search",
        "CAP-SEARCH-SEMANTIC": "Search", "CAP-NOTES": "Notes", "CAP-KEYRING": "Settings and platform security",
        "CAP-NETWORK-POLICY": "Runtime network policy", "CAP-BACKUP": "SQLite persistence",
        "CAP-IMPORT-EXPORT": "Import and export", "CAP-KYSELY": "SQLite persistence",
    }
    for capability_id, owner in expected_owners.items():
        if by_id.get(capability_id, {}).get("owner") != owner:
            errors.append(f"{capability_id}: owner is not {owner}")
    for cap in capabilities:
        if not cap.get("owner") or not cap.get("module_owner"):
            errors.append(f"{cap['id']}: missing owner")
        if cap.get("semantic_review_status") != "REVIEWED AGAINST MASTER PLAN AND CURRENT DOMAIN":
            errors.append(f"{cap['id']}: missing semantic review disposition")
        for path in cap.get("current_paths", []):
            if not (ROOT / path).exists():
                errors.append(f"{cap['id']}: current path absent: {path}")
        if "dependencies" not in cap or "dependents" not in cap:
            errors.append(f"{cap['id']}: capability dependency fields are absent")
        for dependency in cap.get("dependencies", []):
            if dependency not in by_id:
                errors.append(f"{cap['id']}: unknown capability dependency {dependency}")
            elif cap["id"] not in by_id[dependency].get("dependents", []):
                errors.append(f"{cap['id']}: dependency relation to {dependency} is not bidirectional")
    aec = by_id["CAP-AEC"]
    if any("dictionaryEchoFilter" in path for path in aec["current_paths"]) or "dictionaryEchoFilter" in json.dumps(aec.get("runtime_chain", {})):
        errors.append("CAP-AEC contains the dictionary text echo filter")
    if not {"codebase/main/features/meetings/meetingAecManager.js", "codebase/native/meeting-aec-helper/src/aec_processor.cc"}.issubset(aec["current_paths"]):
        errors.append("CAP-AEC lacks the actual meeting/native AEC boundary")
    exact = by_id["CAP-SEARCH-EXACT"]
    exact_payload = json.dumps({"current_paths": exact["current_paths"], "runtime_chain": exact.get("runtime_chain", {})})
    if any(term in exact_payload for term in ("localEmbeddings", "qdrant", "vectorIndex", "onnxWorker")):
        errors.append("CAP-SEARCH-EXACT contains semantic-vector implementation")
    if "codebase/main/infrastructure/persistence/database.js" not in exact["current_paths"] or "codebase/tests/unit/persistence/localDataDatabase.test.js" not in exact["current_paths"]:
        errors.append("CAP-SEARCH-EXACT lacks SQLite exact-query implementation/tests")
    notes = by_id["CAP-NOTES"]
    notes_payload = json.dumps({"current_paths": notes["current_paths"], "runtime_chain": notes.get("runtime_chain", {})}).lower()
    if any(term in notes_payload for term in ("tokenizer", "diarization-model", "/resources/bin/")):
        errors.append("CAP-NOTES contains unrelated tokenizer/diarization/binary assets")
    if not {"codebase/renderer/features/notes/components/RichTextEditor.tsx", "codebase/main/infrastructure/persistence/database.js", "codebase/preload/index.js"}.issubset(notes["current_paths"]):
        errors.append("CAP-NOTES lacks editor, persistence, or preload boundary")
    semantic_contracts = {
        "CAP-PLAYBACK": {
            "required_paths": {"codebase/renderer/features/notes/components/MeetingRecordingPill.tsx"},
            "forbidden_terms": ("audioActivityDetector", "audioTapManager", "systemAudioAccess"),
            "target_contains": "MeetingRecordingPill.tsx",
        },
        "CAP-HOTKEY": {
            "required_paths": {"codebase/main/features/dictation/hotkeyManager.js"},
            "forbidden_terms": ("correctionLearner", "dictionaryEchoFilter", "audioActivityDetector"),
            "target_contains": "hotkeyManager.js",
        },
        "CAP-MEETING-NOTES": {
            "required_paths": {"codebase/renderer/features/notes/components/NoteEditor.tsx", "codebase/renderer/features/notes/components/MeetingTranscriptView.tsx"},
            "forbidden_terms": ("audioActivityDetector", "audioTapManager", "meetingEchoLeakDetector"),
            "target_contains": "NoteEditor.tsx",
        },
        "CAP-IPC": {"required_paths": {"codebase/main/ipc/ipcHandlers.js"}, "forbidden_terms": (), "target_contains": "ipcHandlers.js"},
        "CAP-PACKAGING": {"required_paths": {"codebase/electron-builder.json"}, "forbidden_terms": ("windowsKeyManager",), "target_contains": "electron-builder.json"},
        "CAP-RENDERER": {"required_paths": {"codebase/renderer/app/AppRouter.jsx"}, "forbidden_terms": (".prettierignore",), "target_contains": "AppRouter.jsx"},
        "CAP-LEGAL": {"required_paths": {"codebase/LICENSE"}, "forbidden_terms": (), "target_contains": "LICENSE"},
        "CAP-SHERPA-ONNX": {"required_paths": {"codebase/main/features/meetings/diarization.js", "codebase/resources/bin/sherpa-onnx-diarize-win32-x64.exe"}, "forbidden_terms": (), "target_contains": "diarization.js"},
        "CAP-MACOS-LINUX": {"required_paths": {"codebase/native/helpers/macos", "codebase/native/helpers/linux"}, "forbidden_terms": (), "target_contains": "native/helpers"},
        "CAP-IMPORT-AUDIO": {"required_paths": {"codebase/renderer/features/notes/components/UploadAudioView.tsx"}, "forbidden_terms": ("audioActivityDetector",), "target_contains": "UploadAudioView.tsx"},
        "CAP-RECOVERY": {"required_paths": {"codebase/renderer/features/meetings/meetingRecordingStore.ts"}, "forbidden_terms": ("discardedRecording.test.js",), "target_contains": "recordingRecovery.js"},
        "CAP-TRANSCRIPT-EDIT": {"required_paths": {"codebase/main/infrastructure/persistence/database.js"}, "forbidden_terms": ("downloadUtils",), "target_contains": "database.js"},
        "CAP-TRANSCRIPT-HISTORY": {"required_paths": {"codebase/main/infrastructure/persistence/database.js"}, "forbidden_terms": ("downloadUtils",), "target_contains": "database.js"},
    }
    for capability_id, contract in semantic_contracts.items():
        cap = by_id[capability_id]
        paths = set(cap.get("current_paths", []))
        payload = json.dumps({"current_paths": cap.get("current_paths", []), "runtime_chain": cap.get("runtime_chain", {})})
        missing = contract["required_paths"] - paths
        if missing:
            errors.append(f"{capability_id} lacks reviewed boundary paths: {sorted(missing)}")
        contaminated = [term for term in contract["forbidden_terms"] if term in payload]
        if contaminated:
            errors.append(f"{capability_id} contains unrelated implementation: {contaminated}")
        targets = " ".join(cap.get("target_paths", []))
        if contract["target_contains"] not in targets:
            errors.append(f"{capability_id} target is not its reviewed owned boundary: {targets}")
    return errors


def exact_location_errors(entries: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for entry in entries:
        if entry.get("location_class") not in LOCATION_CLASSES:
            errors.append(f"{entry['id']}: invalid location class {entry.get('location_class')}")
        path = entry.get("current_path")
        if not path:
            if "PLANNED" not in entry.get("status", "") and "NO ACTIVE PATH" not in entry.get("status", ""):
                errors.append(f"{entry['id']}: null current path lacks planned/absence status")
            continue
        absolute = ROOT / path
        if not absolute.exists():
            errors.append(f"{entry['id']}: current path does not exist: {path}")
            continue
        anchor = entry.get("current_anchor")
        if not anchor:
            errors.append(f"{entry['id']}: current path lacks symbol/anchor")
            continue
        if "::sha256:" in anchor:
            expected = anchor.rsplit("::sha256:", 1)[1]
            if not absolute.is_file() or sha256(absolute) != expected:
                errors.append(f"{entry['id']}: content anchor hash mismatch")
        elif "::json-key:" in anchor:
            key = anchor.rsplit("::json-key:", 1)[1]
            if not absolute.is_file():
                errors.append(f"{entry['id']}: JSON structural anchor points to a non-file")
            else:
                try:
                    if key not in json.loads(absolute.read_text(encoding="utf-8")):
                        errors.append(f"{entry['id']}: JSON structural anchor missing: {key}")
                except (OSError, json.JSONDecodeError):
                    errors.append(f"{entry['id']}: JSON structural anchor file is unreadable")
        elif "::heading:" in anchor:
            heading = anchor.rsplit("::heading:", 1)[1]
            if not absolute.is_file() or heading not in absolute.read_text(encoding="utf-8", errors="replace").splitlines():
                errors.append(f"{entry['id']}: Markdown heading anchor missing: {heading}")
        elif anchor.endswith("::directory-anchor"):
            if not absolute.is_dir(): errors.append(f"{entry['id']}: directory anchor points to a file")
        elif "::line:" in anchor:
            match = re.search(r"::line:(\d+):", anchor)
            if not match or not absolute.is_file():
                errors.append(f"{entry['id']}: invalid deletion line anchor")
            else:
                lines = absolute.read_text(encoding="utf-8", errors="replace").splitlines()
                number = int(match.group(1))
                if number < 1 or number > len(lines):
                    errors.append(f"{entry['id']}: deletion line anchor out of range")
                else:
                    stored = anchor.split(f"::line:{number}:", 1)[1]
                    actual_line = lines[number - 1].strip()[:220]
                    if stored != actual_line:
                        errors.append(f"{entry['id']}: deletion line anchor content mismatch")
        else:
            symbol = entry.get("current_symbol") or anchor.split("::", 1)[-1]
            if absolute.is_file() and symbol not in absolute.read_text(encoding="utf-8", errors="replace"):
                errors.append(f"{entry['id']}: symbol not found: {symbol}")
        target = str(entry.get("intended_target_path", "")).replace("\\", "/").lower()
        if entry.get("editable_target") and any(marker in "/" + target for marker in VENDOR_OR_GENERATED_MARKERS):
            errors.append(f"{entry['id']}: editable target is vendor/generated: {target}")
    return errors


def deletion_errors(tasks: list[dict[str, Any]]) -> tuple[list[str], list[str], list[str]]:
    disposition_errors: list[str] = []
    false_positive_errors: list[str] = []
    interlock_errors: list[str] = []
    for task in (item for item in tasks if item.get("task_kind") == "DELETION"):
        candidates = task.get("static_analysis_candidates", [])
        for candidate in candidates:
            disposition = candidate.get("reviewed_disposition")
            if disposition not in DISPOSITIONS:
                disposition_errors.append(f"{task['stable_task_id']}: invalid/missing disposition at {candidate.get('path')}:{candidate.get('line')}")
            value = f"{candidate.get('path')} {candidate.get('anchor')}".lower()
            if disposition == "ACTIVE REMOVAL CANDIDATE" and ("tokenizer" in value or "all-minilm" in value):
                false_positive_errors.append(f"{task['stable_task_id']}: tokenizer asset is active deletion")
            if task["capability_id"] == "CAP-REMOVE-AUTHENTICATION" and disposition == "ACTIVE REMOVAL CANDIDATE" and any(term in value for term in ("getloginitemsettings", "setloginitemsettings", "login item", "no account")):
                false_positive_errors.append(f"{task['stable_task_id']}: OS login-item/offline message is authentication deletion")
            if task["capability_id"] == "CAP-REMOVE-AUTHENTICATION" and disposition == "ACTIVE REMOVAL CANDIDATE" and any(term in value for term in ("auto-start at login", "logout/login", "login to take effect")):
                false_positive_errors.append(f"{task['stable_task_id']}: OS startup/help text is authentication deletion")
            if task["capability_id"] == "CAP-REMOVE-AUTHENTICATION" and disposition == "ACTIVE REMOVAL CANDIDATE" and any(term in value for term in ("input group", "group changes", "re-login", "new login session", "ydotoold", "runs on every login")):
                false_positive_errors.append(f"{task['stable_task_id']}: OS permission/session text is authentication deletion")
            if task["capability_id"] == "CAP-REMOVE-WORKSPACES" and disposition == "ACTIVE REMOVAL CANDIDATE" and any(term in value for term in ("nsworkspace", "workspace.activewindow", "workspace app launched", "workspace app terminated", "visibleonallworkspaces")):
                false_positive_errors.append(f"{task['stable_task_id']}: OS workspace API is product-workspace deletion")
            if task["capability_id"] == "CAP-REMOVE-UPGRADE-SYSTEMS" and disposition == "ACTIVE REMOVAL CANDIDATE" and "premium" in value and not any(term in value for term in ("premium plan", "upgrade", "subscription", "paid plan", "billing")):
                false_positive_errors.append(f"{task['stable_task_id']}: visual-style adjective is upgrade-system deletion")
            if task["capability_id"] == "CAP-REMOVE-UPGRADE-SYSTEMS" and disposition == "ACTIVE REMOVAL CANDIDATE" and "pip upgrade" in value:
                false_positive_errors.append(f"{task['stable_task_id']}: Python package maintenance timeout is product-upgrade deletion")
            if disposition == "ACTIVE REMOVAL CANDIDATE" and any(term in value for term in ("no login or api key", "no account or api key")):
                false_positive_errors.append(f"{task['stable_task_id']}: positive local/offline message is active deletion")
            if task["capability_id"] == "CAP-REMOVE-HOSTED-AI" and disposition == "ACTIVE REMOVAL CANDIDATE" and "local network" in value:
                false_positive_errors.append(f"{task['stable_task_id']}: local-network provider text is hosted-AI deletion")
            if task["capability_id"] == "CAP-REMOVE-SHARING" and disposition == "ACTIVE REMOVAL CANDIDATE" and "sharing anonymous performance metrics" in value:
                false_positive_errors.append(f"{task['stable_task_id']}: analytics wording is product-sharing deletion")
            if task["capability_id"] == "CAP-REMOVE-ACTIVE-OPENWHISPR-IDENTITY" and disposition == "ACTIVE REMOVAL CANDIDATE" and (
                any(term in value for term in ("legacy", "any old \"openwhispr\"", ".cache/openwhispr", "openwhispr-binds.conf"))
                or ('".cache"' in value and '"openwhispr"' in value)
            ):
                false_positive_errors.append(f"{task['stable_task_id']}: legacy compatibility evidence is active identity deletion")
        interlocks = task.get("binding_deletion_interlocks", [])
        if {item.get("gate") for item in interlocks} != BDI_IDS or len(interlocks) != 7:
            interlock_errors.append(f"{task['stable_task_id']}: seven exact Binding Deletion Interlock gates are absent")
        coverage = task.get("deletion_architectural_layer_coverage", {})
        if set(coverage) != DELETION_LAYERS:
            interlock_errors.append(f"{task['stable_task_id']}: full deletion layer set is absent")
        for layer, contract in coverage.items():
            if not contract.get("status") or not contract.get("absence_rule") or "IMPLEMENTATION-TIME PROOF" not in contract.get("status", ""):
                interlock_errors.append(f"{task['stable_task_id']}: incomplete {layer} absence contract")
    all_candidates = [candidate for task in tasks if task.get("task_kind") == "DELETION" for candidate in task.get("static_analysis_candidates", [])]
    migration_identity = [candidate for candidate in all_candidates if "datamigration" in candidate.get("path", "").lower() and "openwhispr" in candidate.get("anchor", "").lower()]
    if not migration_identity or any(candidate.get("reviewed_disposition") != "HISTORICAL MIGRATION - PRESERVE" for candidate in migration_identity):
        false_positive_errors.append("Historical OpenWhispr data-migration identity is absent or not preserved as historical migration evidence")
    legal_identity = [candidate for candidate in all_candidates if candidate.get("path") == "codebase/LICENSE" and "openwhispr" in candidate.get("anchor", "").lower()]
    if not legal_identity or any(candidate.get("reviewed_disposition") != "LEGAL/ATTRIBUTION - PRESERVE" for candidate in legal_identity):
        false_positive_errors.append("OpenWhispr LICENSE attribution is absent or not preserved as legal evidence")
    active_identity_env = [candidate for candidate in all_candidates if set(candidate.get("matched_terms", [])) & {"openwhispr_dev_server_port", "openwhispr_log_level"}]
    if len(active_identity_env) < 2 or any(candidate.get("reviewed_disposition") != "ACTIVE REMOVAL CANDIDATE" for candidate in active_identity_env):
        false_positive_errors.append("Active OpenWhispr environment-variable identity is absent or lacks active-removal disposition")
    return disposition_errors, false_positive_errors, interlock_errors


def dependency_analysis(tasks: list[dict[str, Any]]) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    by_id = {item["stable_task_id"]: item for item in tasks}
    indegree = {task_id: 0 for task_id in by_id}
    adjacency: dict[str, list[str]] = collections.defaultdict(list)
    for task_id, task in by_id.items():
        if task.get("dependencies") != task.get("semantic_dependencies"):
            errors.append(f"{task_id}: compatibility dependencies differ from semantic_dependencies")
        for dependency in task.get("semantic_dependencies", []):
            if dependency not in by_id:
                errors.append(f"{task_id}: unknown dependency {dependency}")
                continue
            indegree[task_id] += 1
            adjacency[dependency].append(task_id)
    ready = sorted(task_id for task_id, degree in indegree.items() if degree == 0)
    topo: list[str] = []
    depth: dict[str, int] = {}
    while ready:
        task_id = ready.pop(0)
        topo.append(task_id)
        dependencies = by_id[task_id].get("semantic_dependencies", [])
        depth[task_id] = 0 if not dependencies else 1 + max(depth[dependency] for dependency in dependencies)
        for dependent in sorted(adjacency[task_id]):
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                ready.append(dependent); ready.sort()
    cycle_count = 0 if len(topo) == len(tasks) else len(tasks) - len(topo)
    roots = sorted(task_id for task_id, task in by_id.items() if not task.get("semantic_dependencies"))
    leaves = sorted(task_id for task_id in by_id if not adjacency[task_id])
    metrics = {
        "task_nodes": len(tasks), "dependency_edges": sum(len(task.get("semantic_dependencies", [])) for task in tasks),
        "root_tasks": roots, "leaf_tasks": leaves, "maximum_dependency_depth": max(depth.values(), default=0),
        "cycle_count": cycle_count, "topological_order_result": "PASS" if cycle_count == 0 else "FAIL",
    }
    if roots != ["TASK-GOV-001-PROVENANCE-BASELINE"]: errors.append(f"Unexpected dependency roots: {roots}")
    if cycle_count: errors.append(f"Dependency graph contains {cycle_count} cyclic/unreachable nodes")
    ordered = sorted(tasks, key=lambda item: item.get("execution_order", -1))
    if [item.get("execution_order") for item in ordered] != list(range(1, len(tasks) + 1)):
        errors.append("Execution order is not contiguous")
    position = {task["stable_task_id"]: task.get("execution_order", -1) for task in tasks}
    for task in tasks:
        for dependency in task.get("semantic_dependencies", []):
            if dependency in position and position[dependency] >= position[task["stable_task_id"]]:
                errors.append(f"{task['stable_task_id']}: dependency is not earlier in execution order")
    return errors, metrics


def test_errors(test_doc: dict[str, Any], tasks: list[dict[str, Any]], package_scripts: dict[str, str]) -> tuple[list[str], list[str], list[str]]:
    command_errors: list[str] = []
    reference_errors: list[str] = []
    appropriateness_errors: list[str] = []
    contracts = test_doc["tests"]
    task_by_id = {item["stable_task_id"]: item for item in tasks}
    if {item["task_id"] for item in contracts} != set(task_by_id):
        reference_errors.append("Test matrix does not contain exactly one contract per task")
    for contract in contracts:
        task = task_by_id.get(contract["task_id"])
        if not task: continue
        proofs = [item for field in ("characterisation_before_change", "targeted_verification", "real_integration_verification", "broader_regression_verification") for item in contract.get(field, [])]
        for proof in proofs:
            command = proof.get("command", "")
            working = proof.get("working_directory")
            status = proof.get("reference_status")
            path = proof.get("test_path")
            if working not in {".", "codebase"}: command_errors.append(f"{contract['test_contract_id']}: invalid working directory {working}")
            if "--test-name-pattern" in command: command_errors.append(f"{contract['test_contract_id']}: unsupported synthetic test-name command")
            if command.startswith("npm test --"):
                command_errors.append(f"{contract['test_contract_id']}: appends an unreliable positional selector to the verified glob-based test script")
            match = re.match(r"npm run ([^\s]+)", command)
            if match and match.group(1) not in package_scripts: command_errors.append(f"{contract['test_contract_id']}: nonexistent package script {match.group(1)}")
            if command.startswith("npm test") and "test" not in package_scripts: command_errors.append(f"{contract['test_contract_id']}: package has no test script")
            if status == "EXISTING TEST" and (not path or not (ROOT / path).is_file()): reference_errors.append(f"{contract['test_contract_id']}: claimed existing test is absent: {path}")
            if status == "TEST TO CREATE" and path and (ROOT / path).exists(): reference_errors.append(f"{contract['test_contract_id']}: existing path is mislabeled TEST TO CREATE: {path}")
            if status not in {"EXISTING TEST", "TEST TO CREATE", "COMMAND TO ADD DURING IMPLEMENTATION", "MANUAL/EXTERNAL EVIDENCE", "STATIC VALIDATOR", "PACKAGE SCRIPT"}:
                reference_errors.append(f"{contract['test_contract_id']}: invalid reference status {status}")
        types = set(contract.get("evidence_types", []))
        if task["capability_id"] in {"CAP-PROVENANCE", "CAP-PLANNING-GOVERNANCE", "CAP-EXACT-LOCATION", "CAP-IMPLEMENTATION-GOVERNANCE", "CAP-DELETION-GOVERNANCE", "CAP-RELEASE", "CAP-SIMPLIFICATION"} and any(item.get("reference_status") == "TEST TO CREATE" for item in proofs):
            appropriateness_errors.append(f"{contract['test_contract_id']}: governance task uses a synthetic application test")
        if task.get("task_kind") == "DELETION" and "STATIC/GRAPH AUDIT" not in types:
            appropriateness_errors.append(f"{contract['test_contract_id']}: deletion lacks static/graph evidence")
        if task["capability_id"] == "CAP-AEC" and not {"NATIVE/PROCESS TEST", "AUDIO/HARDWARE TEST"}.issubset(types):
            appropriateness_errors.append("AEC lacks native/process and audio/hardware proof types")
        if task["capability_id"] == "CAP-SEARCH-EXACT" and not any("localDataDatabase.test.js" == Path(item.get("test_path", "")).name for item in proofs):
            appropriateness_errors.append("Exact search lacks the existing SQLite exact-query test")
    signatures: dict[str, list[tuple[str, str]]] = collections.defaultdict(list)
    for contract in contracts:
        signature = json.dumps({
            field: contract.get(field)
            for field in ("characterisation_before_change", "targeted_verification", "real_integration_verification", "broader_regression_verification", "required_evidence_artifacts")
        }, sort_keys=True, ensure_ascii=False)
        signatures[signature].append((contract["task_id"], contract["capability_id"]))
    for duplicate_group in signatures.values():
        if len({capability_id for _, capability_id in duplicate_group}) > 1:
            appropriateness_errors.append(f"Unrelated capabilities share an identical generic evidence contract: {duplicate_group[:5]}")
    return command_errors, reference_errors, appropriateness_errors


def internal_link_errors() -> list[str]:
    errors: list[str] = []
    pattern = re.compile(r"`((?:Graphify/)?[A-Za-z0-9 _./-]+\.(?:md|json))`")
    for path in G.iterdir():
        if not path.is_file() or path.suffix.lower() != ".md": continue
        for reference in pattern.findall(path.read_text(encoding="utf-8", errors="replace")):
            normalized = reference.replace("\\", "/")
            if normalized.startswith(("Graphify/", "codebase/")):
                target = ROOT / normalized
            elif normalized.endswith("/SKILL.md"):
                # Installed skill references are provenance, not internal
                # Graphify links and are validated in the tool log.
                continue
            else:
                target = G / normalized
            if not target.exists() and not normalized.startswith("Graphify/evidence/"):
                errors.append(f"{path.name}: broken internal reference {reference}")
    current_reference_pattern = re.compile(r"`((?:codebase|Graphify)/[^`]+?)(?:::([^`]+))?`")
    for name in ("CURRENT_ARCHITECTURE.md", "REPOSITORY_INVENTORY.md"):
        document = (G / name).read_text(encoding="utf-8", errors="replace")
        for raw_path, _symbol in current_reference_pattern.findall(document):
            if any(marker in raw_path for marker in ("{", "}", "<", ">")):
                continue
            if not (ROOT / raw_path.rstrip("/")).exists():
                errors.append(f"{name}: nonexistent current path {raw_path}")
    return errors


def third_party_register_errors() -> list[str]:
    errors: list[str] = []
    package_document = json.loads((CB / "package.json").read_text(encoding="utf-8"))
    expected = set(package_document.get("dependencies", {})) | set(package_document.get("devDependencies", {}))
    register = (G / "THIRD_PARTY_CODE_REGISTER.md").read_text(encoding="utf-8", errors="replace")
    rows: dict[str, list[str]] = {}
    for line in register.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) >= 7 and cells[0] in expected:
            rows[cells[0]] = cells
    missing = sorted(expected - set(rows))
    if missing: errors.append(f"Third-party register missing top-level packages: {missing}")
    suspicious_owners = {"Repository infrastructure", "Meeting recording", "Windows packaging"}
    for package, cells in rows.items():
        if cells[3] in suspicious_owners:
            errors.append(f"{package}: nonspecific or contaminated third-party owner {cells[3]}")
        if "codebase/node_modules/" in cells[4]:
            errors.append(f"{package}: installed vendor path used as owned reference")
    for package in {"tar", "unbzip2-stream", "unzipper"}:
        if package in rows and "OFFLINE LOCAL MODEL-PACK IMPORT" not in rows[package][5]:
            errors.append(f"{package}: archive dependency is not owned by file-only offline model-pack import")
    if "codebase/LICENSE" not in register or "legal provenance" not in register:
        errors.append("Third-party register omits the source LICENSE legal-provenance disposition")
    return errors


def inventory_integrity(inventory: dict[str, Any], full_hash: bool) -> tuple[list[str], dict[str, Any]]:
    """Canonical tracked-codebase parity plus a separately labeled local-only full-tree audit.

    Tracked parity uses git blob content (line-ending independent and reproducible
    from any clean clone). The full local tree audit (node_modules, build-output,
    caches) runs only when the complete local dependency tree is present and is
    explicitly reported as LOCAL ONLY - NOT GITHUB-VERIFIED.
    """
    errors: list[str] = []
    baseline_manifest = G / "TRACKED_CODEBASE_BASELINE_SHA256.txt"
    final_manifest = G / "TRACKED_CODEBASE_FINAL_SHA256.txt"
    baseline_map, baseline_errors = parse_manifest(baseline_manifest)
    final_map, final_errors = parse_manifest(final_manifest)
    current_map, current_errors = current_tracked_codebase_mapping()
    errors.extend(baseline_errors + final_errors + current_errors)
    added = sorted((set(final_map) | set(current_map)) - set(baseline_map))
    removed = sorted(set(baseline_map) - (set(final_map) & set(current_map)))
    changed = sorted(path for path in set(baseline_map) & set(final_map) & set(current_map) if not (baseline_map[path] == final_map[path] == current_map[path]))
    if added: errors.append(f"Tracked codebase manifest added paths: {added[:20]}")
    if removed: errors.append(f"Tracked codebase manifest missing paths: {removed[:20]}")
    if changed: errors.append(f"Tracked codebase manifest changed hashes: {changed[:20]}")
    evidence = {
        "tracked_codebase_file_count": len(current_map),
        "tracked_baseline_entries": len(baseline_map),
        "tracked_final_entries": len(final_map),
        "tracked_unchanged": sum(1 for path, digest in baseline_map.items() if final_map.get(path) == digest == current_map.get(path)),
        "tracked_added": len(added),
        "tracked_removed": len(removed),
        "tracked_changed": len(changed),
        "tracked_manifest_errors": len(baseline_errors) + len(final_errors) + len(current_errors),
        "claim": "Tracked codebase parity is verified from git blob content and is reproducible from any clean clone.",
    }
    local_full_tree = (CB / "node_modules").is_dir()
    if local_full_tree:
        baseline = {item["path"]: item for item in inventory["files"] if item["path"].startswith("codebase/")}
        actual_paths = sorted(path for path in CB.rglob("*") if path.is_file())
        actual = {path.relative_to(ROOT).as_posix(): path for path in actual_paths}
        if set(actual) != set(baseline):
            for path in sorted(set(actual) - set(baseline))[:100]: errors.append(f"LOCAL ONLY - unexpected codebase file: {path}")
            for path in sorted(set(baseline) - set(actual))[:100]: errors.append(f"LOCAL ONLY - missing codebase file: {path}")
        comparable = 0
        path_size_only = 0
        full_manifest: list[str] = []
        for path, absolute in actual.items():
            entry = baseline.get(path)
            if not entry: continue
            size = absolute.stat().st_size
            if size != entry.get("size_bytes"): errors.append(f"LOCAL ONLY - codebase size changed: {path}")
            current_hash = None
            if entry.get("sha256") or full_hash:
                current_hash = sha256(absolute)
            if entry.get("sha256"):
                comparable += 1
                if current_hash != entry["sha256"]: errors.append(f"LOCAL ONLY - comparable codebase SHA-256 changed: {path}")
            else:
                path_size_only += 1
            if full_hash:
                full_manifest.append(f"{path}\0{current_hash}")
        full_fingerprint = hashlib.sha256("\n".join(full_manifest).encode("utf-8")).hexdigest().upper() if full_hash else None
        evidence.update({
            "local_full_tree_audit": "RUN - LOCAL ONLY (ignored dependencies/build output are not GitHub-verified)",
            "local_baseline_codebase_files": len(baseline),
            "local_current_codebase_files": len(actual),
            "local_comparable_pre_and_post_sha256_files": comparable,
            "local_path_and_size_only_files": path_size_only,
            "local_post_run_full_sha256_fingerprint": full_fingerprint,
            "local_claim_limit": "Only comparable-hash files are proven byte-identical. Path/size-only files are not cryptographic equality proof. A post-run full fingerprint without an equivalent pre-run full fingerprint is a current-state checkpoint, not full before/after proof.",
        })
    else:
        evidence["local_full_tree_audit"] = "SKIPPED - clean clone (full local dependency tree absent); tracked parity above is the GitHub-verifiable claim"
    return errors, evidence


def negative_fixture_errors() -> list[str]:
    """Known corrupt examples must be rejected by the validator's semantic rules."""
    failures: list[str] = []
    scope = {"stable_requirement_id": "NEG-SCOPE", "source_master_plan_code": "MP2", "source_line_start": 11, "requirement_summary": "retained product scope", "requirement_type": "Deletion requirement", "retained_or_removed_scope": "REMOVED SCOPE", "capability_ids": ["CAP-SEARCH-SEMANTIC"]}
    if scope["requirement_type"] == "Product requirement" or set(scope["capability_ids"]) == set(PRODUCT_SCOPE_CAPS): failures.append("Scope-lock negative fixture was not rejected")
    aec_paths = ["codebase/renderer/features/dictation/dictionaryEchoFilter.js"]
    if not any("dictionaryEchoFilter" in path for path in aec_paths): failures.append("AEC contamination fixture was not rejected")
    exact_paths = ["codebase/main/features/search/localEmbeddings.js", "codebase/main/features/search/vectorIndex.js"]
    if not any(any(term in path for term in ("localEmbeddings", "vectorIndex", "qdrant")) for path in exact_paths): failures.append("Exact-search contamination fixture was not rejected")
    vendor_target = "codebase/node_modules/pkg/index.js"
    if not any(marker in "/" + vendor_target for marker in VENDOR_OR_GENERATED_MARKERS): failures.append("Vendor-target fixture was not rejected")
    tokenizer = {"reviewed_disposition": "ACTIVE REMOVAL CANDIDATE", "path": "codebase/resources/bin/all-MiniLM-L6-v2/tokenizer.json"}
    if not (tokenizer["reviewed_disposition"] == "ACTIVE REMOVAL CANDIDATE" and "tokenizer" in tokenizer["path"]): failures.append("Tokenizer false-positive fixture was not rejected")
    login_item = "app.setLoginItemSettings({ openAtLogin: true })"
    if "setloginitemsettings" not in login_item.lower(): failures.append("OS login-item fixture was not rejected")
    startup_help = "requires logout/login to take effect; Auto-start at login"
    if not any(term in startup_help.lower() for term in ("logout/login", "auto-start at login")): failures.append("OS startup/help fixture was not rejected")
    os_workspace = "NSWorkspace notification: Workspace app launched"
    if not any(term in os_workspace.lower() for term in ("nsworkspace", "workspace app launched")): failures.append("OS workspace fixture was not rejected")
    premium_style = "Primary CTA — ultra-premium with subtle depth"
    if not ("premium" in premium_style.lower() and not any(term in premium_style.lower() for term in ("premium plan", "upgrade", "subscription", "paid plan", "billing"))): failures.append("Premium visual-style fixture was not rejected")
    legacy_identity = 'const LEGACY_STORAGE_DIR = path.join(home, ".cache", "openwhispr")'
    if not any(term in legacy_identity.lower() for term in ("legacy", ".cache/openwhispr")): failures.append("Legacy identity fixture was not rejected")
    playback_pollution = ["codebase/main/features/meetings/audioActivityDetector.js"]
    if not any("audioActivityDetector" in path for path in playback_pollution): failures.append("Playback contamination fixture was not rejected")
    ipc_target = "codebase/electron-builder.json"
    if "ipcHandlers.js" in ipc_target: failures.append("IPC packaging-target fixture was not rejected")
    sequential = [{"id": f"T{i}", "dependencies": [] if i == 1 else [f"T{i-1}"]} for i in range(1, 5)]
    if not all(item["dependencies"] == [f"T{index-1}"] for index, item in enumerate(sequential, 1) if index > 1): failures.append("Sequential-chain fixture was not rejected")
    governance_test = {"capability_id": "CAP-PROVENANCE", "reference_status": "TEST TO CREATE", "test_path": "codebase/tests/integration/git.test.js"}
    if not (governance_test["capability_id"] == "CAP-PROVENANCE" and governance_test["reference_status"] == "TEST TO CREATE"): failures.append("Governance synthetic-test fixture was not rejected")
    return failures


def manifest_pair_stats(baseline: Path, final: Path) -> dict[str, Any]:
    baseline_map, baseline_errors = parse_manifest(baseline)
    final_map, final_errors = parse_manifest(final)
    combined_errors = baseline_errors + final_errors
    duplicates = sum(1 for error in combined_errors if "duplicate" in error or "collision" in error)
    return {
        "baseline_entries": len(baseline_map),
        "final_entries": len(final_map),
        "unchanged": sum(1 for path, digest in baseline_map.items() if final_map.get(path) == digest),
        "added": len(set(final_map) - set(baseline_map)),
        "missing": len(set(baseline_map) - set(final_map)),
        "changed": sum(1 for path in set(baseline_map) & set(final_map) if baseline_map[path] != final_map[path]),
        "duplicates": duplicates,
        "malformed": len(combined_errors) - duplicates,
        "mappings_identical": baseline_map == final_map and not combined_errors,
    }


def reconciliation_fields(integrity_evidence: dict[str, Any], checks: list[dict[str, Any]], verdict: str, pre_run_status: str, manifest_entries: list[dict[str, Any]]) -> dict[str, Any]:
    historical_base = G / "AUDIT_CODEBASE_BASELINE_SHA256.txt"
    historical_final = G / "AUDIT_CODEBASE_FINAL_SHA256.txt"
    canonical_base = G / "TRACKED_CODEBASE_BASELINE_SHA256.txt"
    canonical_final = G / "TRACKED_CODEBASE_FINAL_SHA256.txt"

    def raw_sha(path: Path) -> str | None:
        return sha256(path) if path.is_file() else None

    historical = manifest_pair_stats(historical_base, historical_final)
    canonical = manifest_pair_stats(canonical_base, canonical_final)
    current_map, current_errors = current_tracked_codebase_mapping()
    canonical_final_map, _ = parse_manifest(canonical_final)
    tracked_files = [line for line in git(["ls-files"]).splitlines() if line]
    lfs_lines = [line for line in git(["lfs", "ls-files", "-l"]).splitlines() if line]
    return {
        "schema_version": 1,
        "scope": "FINAL REPOSITORY RECONCILIATION - tracked Git parity, Git LFS verification and separate local-only inventory claims",
        "repository_url": git(["remote", "get-url", "origin"]) or "unknown",
        "default_branch": git(["symbolic-ref", "--short", "refs/remotes/origin/HEAD"]).removeprefix("origin/") or "main",
        "branch": git(["branch", "--show-current"]) or "",
        "verified_commit_sha": git(["rev-parse", "HEAD"]),
        "verified_tree_sha": git(["rev-parse", "HEAD^{tree}"]),
        "tracked_file_count": len(tracked_files),
        "tracked_codebase_file_count": len(current_map),
        "lfs_file_count": len(lfs_lines),
        "master_plan_sha256": {name: git_blob_sha256(f"Graphify/Master Plan/{name}") for name in MASTER_HASHES},
        "historical_manifests": {
            "raw_baseline_sha256": raw_sha(historical_base),
            "raw_final_sha256": raw_sha(historical_final),
            "raw_files_byte_identical": raw_sha(historical_base) == raw_sha(historical_final),
            **historical,
        },
        "canonical_manifests": {
            "raw_baseline_sha256": raw_sha(canonical_base),
            "raw_final_sha256": raw_sha(canonical_final),
            "raw_files_byte_identical": raw_sha(canonical_base) == raw_sha(canonical_final),
            **canonical,
            "current_mapping_identical_to_final": current_map == canonical_final_map and not current_errors,
        },
        "transient_exclusions": sorted(TRANSIENT_MANIFEST_PARTS | set(TRANSIENT_MANIFEST_SUFFIXES)),
        "output_manifest_entries": len(manifest_entries),
        "validator": {
            "gate_count": len(checks),
            "passed": sum(1 for item in checks if item["status"] == "PASS"),
            "failed": sum(1 for item in checks if item["status"] == "FAIL"),
            "verdict": verdict,
            "commands": [
                "python -B Graphify/tools/semantic_validator.py --self-test-only",
                "python -B Graphify/tools/validate_planning.py",
                "python -B Graphify/tools/validate_planning.py --full-codebase",
            ],
        },
        "local_full_tree_audit": integrity_evidence.get("local_full_tree_audit"),
        "pre_run_working_tree": "CLEAN" if not pre_run_status else "DIRTY",
        "implementation_status": "NOT STARTED",
        "release_status": "NOT EVALUATED",
    }


def render_reconciliation_md(computed: dict[str, Any]) -> str:
    lines = [
        "# Final Repository Reconciliation",
        "",
        "This report is machine-generated from the reconciliation validator. Tracked Git parity, Git LFS verification and local-only inventory claims are reported separately; GitHub parity applies only to tracked and Git LFS-managed content.",
        "",
        "## Repository identity",
        "",
        f"- Repository URL: `{computed['repository_url']}`",
        f"- Default branch: `{computed['default_branch']}`",
        f"- Branch at verification: `{computed['branch']}`",
        f"- Verified commit: `{computed['verified_commit_sha']}`",
        f"- Verified tree: `{computed['verified_tree_sha']}`",
        f"- Tracked file count: {computed['tracked_file_count']}",
        f"- Tracked codebase file count: {computed['tracked_codebase_file_count']}",
        f"- Git LFS file count: {computed['lfs_file_count']}",
        "",
        "## Protected content",
        "",
    ]
    for name, digest in computed["master_plan_sha256"].items():
        lines.append(f"- `Master Plan/{name}`: `{digest}` (canonical git blob content)")
    lines += [
        "",
        "## Historical full-tree manifests (LOCAL ONLY - NOT GITHUB-VERIFIED)",
        "",
        f"- Raw baseline SHA-256: `{computed['historical_manifests']['raw_baseline_sha256']}`",
        f"- Raw final SHA-256: `{computed['historical_manifests']['raw_final_sha256']}`",
        f"- Raw files byte-identical: {computed['historical_manifests']['raw_files_byte_identical']}",
        f"- Normalized baseline entries: {computed['historical_manifests']['baseline_entries']}",
        f"- Normalized final entries: {computed['historical_manifests']['final_entries']}",
        f"- Added: {computed['historical_manifests']['added']}; missing: {computed['historical_manifests']['missing']}; changed: {computed['historical_manifests']['changed']}; duplicates: {computed['historical_manifests']['duplicates']}; malformed: {computed['historical_manifests']['malformed']}",
        f"- Normalized path-to-SHA-256 mappings identical: {computed['historical_manifests']['mappings_identical']}",
        "",
        "## Canonical tracked manifests (GitHub-verifiable)",
        "",
        f"- Raw baseline SHA-256: `{computed['canonical_manifests']['raw_baseline_sha256']}`",
        f"- Raw final SHA-256: `{computed['canonical_manifests']['raw_final_sha256']}`",
        f"- Raw files byte-identical: {computed['canonical_manifests']['raw_files_byte_identical']}",
        f"- Normalized baseline entries: {computed['canonical_manifests']['baseline_entries']}",
        f"- Normalized final entries: {computed['canonical_manifests']['final_entries']}",
        f"- Added: {computed['canonical_manifests']['added']}; missing: {computed['canonical_manifests']['missing']}; changed: {computed['canonical_manifests']['changed']}; duplicates: {computed['canonical_manifests']['duplicates']}; malformed: {computed['canonical_manifests']['malformed']}",
        f"- Normalized path-to-SHA-256 mappings identical: {computed['canonical_manifests']['mappings_identical']}",
        f"- Current git mapping identical to final manifest: {computed['canonical_manifests']['current_mapping_identical_to_final']}",
        "",
        "## Transient exclusions",
        "",
        f"- Excluded categories: {', '.join(computed['transient_exclusions'])}",
        f"- Graphify output-manifest entries: {computed['output_manifest_entries']}",
        "",
        "## Validation",
        "",
        f"- Gate count: {computed['validator']['gate_count']}; passed: {computed['validator']['passed']}; failed: {computed['validator']['failed']}; verdict: {computed['validator']['verdict']}",
        f"- Commands: {', '.join(computed['validator']['commands'])}",
        "",
        "## Local-only inventory audit",
        "",
        f"- {computed['local_full_tree_audit']}",
        "",
        "## Working tree",
        "",
        f"- Pre-run working tree: {computed['pre_run_working_tree']}",
        "",
        "## Status",
        "",
        f"- Implementation: {computed['implementation_status']}; release: {computed['release_status']}",
    ]
    return "\n".join(lines)


def write_reconciliation_report(computed: dict[str, Any]) -> None:
    """Write the reconciliation report, preserving a valid report that already describes HEAD^ (report-only delivery commit)."""
    json_path = G / "FINAL-REPOSITORY-RECONCILIATION.json"
    committed: dict[str, Any] | None = None
    if json_path.is_file():
        try:
            committed = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            committed = None
    preserve = False
    if committed:
        head = computed.get("verified_commit_sha", "")
        parent = git(["rev-parse", "HEAD^"])
        sha_ok = committed.get("verified_commit_sha") == head
        if not sha_ok and parent and committed.get("verified_commit_sha") == parent:
            sha_ok = True
        stable_keys = [key for key in computed if key not in {"verified_commit_sha", "verified_tree_sha"}]
        if sha_ok and all(committed.get(key) == computed[key] for key in stable_keys):
            preserve = True
    if not preserve:
        dump("FINAL-REPOSITORY-RECONCILIATION.json", computed)
        write("FINAL-REPOSITORY-RECONCILIATION.md", render_reconciliation_md(computed))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-codebase", action="store_true", help="Hash every current codebase file for a post-run fingerprint; only baseline-hashed files are comparable.")
    parser.add_argument("--skip-reproducibility", action="store_true")
    parser.add_argument("--self-test-only", action="store_true")
    parser.add_argument("--allow-dirty", action="store_true", help="Skip the pre-run clean-working-tree gate (development runs before committing).")
    args = parser.parse_args()
    if args.self_test_only:
        errors = negative_fixture_errors()
        print(json.dumps({"negative_fixture_count": 14, "status": "PASS" if not errors else "FAIL", "errors": errors}, indent=2))
        return 0 if not errors else 1

    pre_run_status = git(["status", "--porcelain"])
    reproducibility_errors: list[str] = []
    before_fingerprint = semantic_authority_fingerprint()
    generator_stdout = "SKIPPED"
    if not args.skip_reproducibility:
        result = subprocess.run([sys.executable, "-B", str(G / "tools" / "complete_planning.py")], cwd=ROOT, text=True, capture_output=True)
        generator_stdout = result.stdout.strip()
        if result.returncode != 0:
            reproducibility_errors.append(f"Generator exited {result.returncode}: {result.stderr[-2000:]}")
        after_fingerprint = semantic_authority_fingerprint()
        if before_fingerprint != after_fingerprint:
            reproducibility_errors.append(f"Semantic authority fingerprint changed on regeneration: {before_fingerprint} -> {after_fingerprint}")
    else:
        after_fingerprint = before_fingerprint

    req_doc = load("MASTER_REQUIREMENT_REGISTER.json"); requirements = req_doc["requirements"]
    cap_doc = load("CAPABILITY_REGISTRY.json"); capabilities = cap_doc["capabilities"]
    loc_doc = load("EXACT_LOCATION_REGISTRY.json"); locations = loc_doc["entries"]
    task_doc = load("IMPLEMENTATION_QUEUE.json"); tasks = task_doc["tasks"]
    test_doc = load("TEST_MATRIX.json")
    conditional_doc = load("CONDITIONAL_DECISION_PACKAGES.json"); packages = conditional_doc["packages"]
    release_doc = load("RELEASE_GATE_PLAN.json"); release_gates = release_doc["gates"]
    interpretation_doc = load("INTERPRETATION_REGISTER.json"); interpretations = interpretation_doc["interpretations"]
    inventory = load("REPOSITORY_FILE_INVENTORY.json")
    package_scripts = json.loads((CB / "package.json").read_text(encoding="utf-8"))["scripts"]
    req_ids = {item["stable_requirement_id"] for item in requirements}
    cap_ids = {item["id"] for item in capabilities}
    task_ids = {item["stable_task_id"] for item in tasks}
    location_ids = {item["id"] for item in locations}
    checks = Checks()

    manifest_entries, manifest_scan_errors = build_graphify_output_manifest()
    hash_errors = [f"{name}: expected {expected}, got {git_blob_sha256(f'Graphify/Master Plan/{name}')}" for name, expected in MASTER_HASHES.items() if git_blob_sha256(f"Graphify/Master Plan/{name}") != expected]
    checks.add("SEM-001-MASTER-HASH", "Master Plan hash integrity (canonical git blob content)", hash_errors, {name: git_blob_sha256(f"Graphify/Master Plan/{name}") for name in MASTER_HASHES})
    checks.add("SEM-002-REQUIREMENT-SOURCE", "Requirement source and line reconciliation", requirement_source_errors(requirements), {"requirements": len(requirements)})
    classification_errors = []
    valid_types = {"Product requirement", "Preservation requirement", "Deletion requirement", "Architecture requirement", "Data-safety requirement", "Migration requirement", "Offline requirement", "Platform requirement", "Packaging requirement", "Testing requirement", "Planning-governance requirement", "Git/provenance requirement", "Legal/licensing requirement", "Conditional decision requirement", "Final release requirement"}
    for requirement in requirements:
        if requirement.get("requirement_type") not in valid_types: classification_errors.append(f"{requirement['stable_requirement_id']}: invalid type")
        if not requirement.get("semantic_mapping_basis"): classification_errors.append(f"{requirement['stable_requirement_id']}: missing reviewed mapping basis")
        if requirement.get("mandatory_or_conditional") == "CONDITIONAL" and requirement.get("requirement_type") != "Conditional decision requirement":
            classification_errors.append(f"{requirement['stable_requirement_id']}: conditional contract is not classified as a Conditional decision requirement")
    checks.add("SEM-003-REQUIREMENT-CLASSIFICATION", "Semantic requirement classifications", classification_errors)
    scope_errors = scope_lock_errors(requirements)
    checks.add("SEM-004-NAMED-CAPABILITIES", "Named product-scope capability completeness", scope_errors)
    protected_errors = [f"{item['stable_requirement_id']}: protected retained scope classified as deletion" for item in requirements if item.get("retained_or_removed_scope") == "PROTECTED RETAINED SCOPE" and item.get("requirement_type") == "Deletion requirement"]
    checks.add("SEM-005-PROTECTED-SEPARATION", "Protected retained scope is separated from deletion", protected_errors)
    runtime_errors = capability_runtime_errors(capabilities)
    checks.add("SEM-006-CAPABILITY-OWNERSHIP", "Capability-domain ownership", [error for error in runtime_errors if "owner" in error.lower()] + third_party_register_errors())
    checks.add("SEM-007-RUNTIME-CHAIN", "Capability runtime-chain correctness", [error for error in runtime_errors if "owner" not in error.lower()])
    location_errors = exact_location_errors(locations)
    checks.add("SEM-008-EXACT-SYMBOLS", "Exact-location path, symbol and anchor reconciliation", [error for error in location_errors if "vendor/generated" not in error])
    vendor_errors = [error for error in location_errors if "vendor/generated" in error]
    vendor_errors += [f"{entry['id']}: vendor/generated implementation target" for entry in locations if entry.get("editable_target") and any(marker in "/" + str(entry.get("intended_target_path", "")).replace("\\", "/").lower() for marker in VENDOR_OR_GENERATED_MARKERS)]
    checks.add("SEM-009-VENDOR-TARGETS", "Vendor/generated target restrictions", vendor_errors)
    target_errors = []
    for entry in locations:
        if not entry.get("target_owner") or not entry.get("intended_target_path") or not entry.get("intended_target_symbol"): target_errors.append(f"{entry['id']}: unowned/incomplete target")
    target_keys = [(entry["stable_capability_id"], str(entry.get("intended_target_path")), str(entry.get("intended_target_symbol")), entry.get("current_line_start")) for entry in locations]
    target_errors.extend(f"Duplicate exact target record: {key}" for key in duplicates(repr(key) for key in target_keys))
    checks.add("SEM-010-TARGET-OWNERSHIP", "Target ownership and collision rules", target_errors)
    disposition_errors, false_positive_errors, interlock_errors = deletion_errors(tasks)
    checks.add("SEM-011-DELETION-DISPOSITIONS", "Deletion candidates have reviewed dispositions", disposition_errors)
    checks.add("SEM-012-KNOWN-FALSE-POSITIVES", "Tokenizer, login-item, historical, legal and offline-message exclusions", false_positive_errors)
    checks.add("SEM-013-DELETION-INTERLOCKS", "Seven Binding Deletion Interlock gates", [error for error in interlock_errors if "seven exact" in error])
    checks.add("SEM-014-DELETION-LAYERS", "Deletion architectural-layer coverage", [error for error in interlock_errors if "seven exact" not in error])
    task_contract_errors = []
    for task in tasks:
        missing = sorted(TASK_FIELDS - set(task))
        if missing: task_contract_errors.append(f"{task['stable_task_id']}: missing {missing}")
        for field in ("master_requirement_ids", "preconditions", "files_expected_to_change", "files_forbidden_from_changing", "exact_implementation_actions", "characterisation_tests_required_before_change", "targeted_verification", "real_integration_verification", "broader_regression_verification", "required_evidence_artifacts", "acceptance_criteria", "completion_criteria", "stop_conditions"):
            if not task.get(field): task_contract_errors.append(f"{task['stable_task_id']}: empty {field}")
        if any(str(action).startswith("At the reviewed ") for action in task.get("exact_implementation_actions", [])):
            task_contract_errors.append(f"{task['stable_task_id']}: generic capability action remains instead of an exact implementation contract")
        if any(reference not in location_ids for reference in task.get("exact_location_registry_refs", [])): task_contract_errors.append(f"{task['stable_task_id']}: invalid exact-location reference")
    checks.add("SEM-015-TASK-CONTRACTS", "Implementation-ready task contracts", task_contract_errors)
    dependency_errors, graph_metrics = dependency_analysis(tasks)
    sequential = all(tasks[index].get("semantic_dependencies") == [tasks[index - 1]["stable_task_id"]] for index in range(1, len(tasks)))
    semantic_dependency_errors = [error for error in dependency_errors if "cycle" not in error.lower() and "Execution order" not in error and "not earlier" not in error]
    if sequential: semantic_dependency_errors.append("Task graph is an artificial immediate-predecessor chain")
    checks.add("SEM-016-SEMANTIC-DEPENDENCIES", "Real semantic task dependencies", semantic_dependency_errors, graph_metrics)
    checks.add("SEM-017-DAG", "Dependency graph acyclicity", [error for error in dependency_errors if "cycle" in error.lower()], graph_metrics)
    topo_errors = [error for error in dependency_errors if "Execution order" in error or "not earlier" in error]
    if task_doc.get("dependency_graph_metrics") != graph_metrics: topo_errors.append("Stored dependency graph metrics do not reconcile")
    checks.add("SEM-018-TOPOLOGICAL-ORDER", "Topological execution order", topo_errors, graph_metrics)
    phase_errors = []
    ordered = sorted(tasks, key=lambda item: item["execution_order"])
    if [item["phase"] for item in ordered] != sorted(item["phase"] for item in ordered): phase_errors.append("Execution order regresses to an earlier phase")
    for task in tasks:
        if not re.fullmatch(r"PHASE-0[1-7]-[A-Z0-9-]+", task["phase"]) or not re.fullmatch(r"WAVE-0[1-7][A-Z]?", task["wave"]): phase_errors.append(f"{task['stable_task_id']}: invalid phase/wave")
    checks.add("SEM-019-PHASE-WAVE", "Phase, wave and order agreement", phase_errors)
    command_errors, reference_errors, evidence_errors = test_errors(test_doc, tasks, package_scripts)
    checks.add("SEM-020-TEST-COMMANDS", "Test-command and package-script validity", command_errors, {"verified_scripts": test_doc.get("verified_package_scripts")})
    checks.add("SEM-021-TEST-REFERENCE-STATUS", "Existing-versus-planned test distinction", reference_errors, test_doc.get("unique_test_path_totals", {}))
    checks.add("SEM-022-EVIDENCE-APPROPRIATENESS", "Evidence type appropriateness", evidence_errors, test_doc.get("evidence_type_totals", {}))
    conditional_errors = []
    required_conditional_fields = {"master_plan_sources", "mandatory_default", "deviation_condition", "evidence_to_collect", "exact_current_implementation_locations", "decision_phase", "comparison_dimensions", "decision_owner", "allowed_outcomes", "downstream_tasks_by_outcome", "fallback", "threshold_rule", "conditional_preservation_rule", "decision_task_id"}
    for package in packages:
        missing = sorted(required_conditional_fields - set(package))
        if missing: conditional_errors.append(f"{package['decision_package_id']}: missing {missing}")
        for location in package.get("exact_current_implementation_locations", []):
            current_path = str(location).split("::", 1)[0].rstrip("/").replace("\\", "/")
            if current_path.startswith("codebase/") and not (ROOT / current_path).exists():
                conditional_errors.append(f"{package['decision_package_id']}: exact current location is absent: {current_path}")
        outcomes = package.get("downstream_tasks_by_outcome", {})
        if set(outcomes) != {"DEFAULT", "DEVIATION"} or any(task_id not in task_ids for task_id in outcomes.values()): conditional_errors.append(f"{package['decision_package_id']}: invalid outcome tasks")
        if package.get("decision_task_id") not in task_ids: conditional_errors.append(f"{package['decision_package_id']}: missing decision task")
    checks.add("SEM-023-CONDITIONAL-PACKAGES", "Conditional decision package completeness", conditional_errors, {"packages": len(packages)})
    release_errors = []
    required_gate_fields = {"master_requirement_ids", "capability_ids", "applicable_task_ids", "required_evidence", "evidence_producers", "verification_method", "failure_condition", "not_applicable_rule", "final_decision_authority", "proof_task_ids"}
    for gate in release_gates:
        missing = sorted(required_gate_fields - set(gate))
        if missing: release_errors.append(f"{gate['release_gate_id']}: missing {missing}")
        if any(req_id not in req_ids for req_id in gate.get("master_requirement_ids", [])): release_errors.append(f"{gate['release_gate_id']}: unknown requirement")
        if any(cap_id not in cap_ids for cap_id in gate.get("capability_ids", [])): release_errors.append(f"{gate['release_gate_id']}: unknown capability")
        if any(task_id not in task_ids for task_id in gate.get("applicable_task_ids", [])): release_errors.append(f"{gate['release_gate_id']}: unknown task")
    checks.add("SEM-024-RELEASE-GATES", "Strict Release Conjunction traceability", release_errors, {"gates": len(release_gates)})
    interpretation_errors = []
    for item in interpretations:
        for field in ("source_documents", "relevant_headings", "apparent_ambiguity", "adopted_interpretation", "preservation_rationale", "affected_capability_ids", "affected_task_ids", "user_clarification_required"):
            if field not in item or item[field] in (None, "", []): interpretation_errors.append(f"{item.get('interpretation_id')}: missing {field}")
    required_interpretations = {f"INT-{index:03}" for index in range(1, 8)}
    if not required_interpretations.issubset({item["interpretation_id"].split("-")[0] + "-" + item["interpretation_id"].split("-")[1] for item in interpretations}): interpretation_errors.append("One or more seven mandated interpretations is absent")
    checks.add("SEM-025-INTERPRETATIONS", "Master Plan interpretation register", interpretation_errors)
    vague_errors = []
    vague_pattern = re.compile(r"\b(?:TODO|TBD|FIXME|later determine|implement as needed|fix relevant files|clean up everything|verify functionality|handle edge cases|remove unused code|repair IPC|test everything)\b", re.I)
    for task in tasks:
        payload = json.dumps({field: task.get(field) for field in ("exact_purpose", "exact_implementation_actions", "acceptance_criteria", "completion_criteria")}, ensure_ascii=False)
        if vague_pattern.search(payload): vague_errors.append(f"{task['stable_task_id']}: vague/placeholder task language")
    raw_evidence_files = {"REPOSITORY_FILE_INVENTORY.json", "REPOSITORY_FINGERPRINT.json", "CODEBASE_KNOWLEDGE_LAYER.json", "PONYTAIL_FINDINGS.json", "VERIFICATION_AUDIT.json"}
    for path in G.iterdir():
        if path.is_file() and path.suffix.lower() in {".md", ".json"} and path.name not in {"PLANNING_VALIDATION_REPORT.json", *raw_evidence_files}:
            if re.search(r"\b(?:TODO|TBD|FIXME|later determine)\b", path.read_text(encoding="utf-8", errors="replace"), re.I): vague_errors.append(f"{path.name}: unresolved placeholder")
    checks.add("SEM-026-PLACEHOLDERS", "Placeholder and vague-language detection", vague_errors)
    req_caps = collections.defaultdict(list); cap_tasks = collections.defaultdict(list)
    for requirement in requirements:
        for cap_id in requirement.get("capability_ids", []): req_caps[cap_id].append(requirement["stable_requirement_id"])
    for task in tasks: cap_tasks[task["capability_id"]].append(task["stable_task_id"])
    orphan_counts = {
        "requirements_without_capability": sum(not item.get("capability_ids") for item in requirements),
        "capabilities_without_requirement": sum(not req_caps[item["id"]] for item in capabilities),
        "capabilities_without_task": sum(not cap_tasks[item["id"]] for item in capabilities),
        "tasks_without_requirement": sum(not item.get("master_requirement_ids") for item in tasks),
        "tasks_without_capability": sum(item.get("capability_id") not in cap_ids for item in tasks),
    }
    checks.add("SEM-027-ORPHANS", "Orphan requirement/capability/task detection", [f"{key}: {value}" for key, value in orphan_counts.items() if value], orphan_counts)
    duplicate_errors = [f"Duplicate requirement ID {value}" for value in duplicates(item["stable_requirement_id"] for item in requirements)] + [f"Duplicate capability ID {value}" for value in duplicates(item["id"] for item in capabilities)] + [f"Duplicate task ID {value}" for value in duplicates(item["stable_task_id"] for item in tasks)] + [f"Duplicate exact ID {value}" for value in duplicates(item["id"] for item in locations)]
    suspicious_files = [path.name for path in G.iterdir() if path.is_file() and re.search(r"(?:final-final|\.bak$|\.old$|(?:^|[-_])v2(?:[-_.]|$)|copy of)", path.name, re.I)]
    duplicate_errors.extend(f"Suspicious parallel authority: {name}" for name in suspicious_files)
    checks.add("SEM-028-DUPLICATE-AUTHORITY", "Duplicate IDs and authority detection", duplicate_errors)
    checks.add("SEM-029-INTERNAL-LINKS", "Internal Graphify link integrity", internal_link_errors())
    count_errors = []
    expected_counts = {"total": len(requirements), "by_master_plan_file": count_by(requirements, "source_master_plan"), "by_section": count_by(requirements, "source_heading"), "by_classification": count_by(requirements, "requirement_type"), "by_capability": count_by(requirements, "capability_ids"), "by_architectural_layer": count_by(requirements, "applicable_architectural_layers"), "by_release_gate": count_by(requirements, "release_gate_ids")}
    if req_doc.get("counts") != expected_counts: count_errors.append("Requirement counts do not derive from requirements")
    for label, stored, actual in (("capabilities", cap_doc.get("capability_count"), len(capabilities)), ("locations", loc_doc.get("entry_count"), len(locations)), ("tasks", task_doc.get("task_count"), len(tasks)), ("tests", test_doc.get("test_contract_count"), len(test_doc["tests"])), ("packages", conditional_doc.get("package_count"), len(packages)), ("gates", release_doc.get("gate_count"), len(release_gates))):
        if stored != actual: count_errors.append(f"{label}: stored {stored}, actual {actual}")
    checks.add("SEM-030-COUNTS", "Cross-authority count reconciliation", count_errors, expected_counts)
    checks.add("SEM-031-GENERATOR-REPRODUCIBILITY", "Generator semantic reproducibility", reproducibility_errors, {"before": before_fingerprint, "after": after_fingerprint, "generator_stdout": generator_stdout})
    wording_errors = []
    for name in ("RUN_STATE.md", "COMPLETION_TRACKER.md", "REPOSITORY_INVENTORY.md", "START-HERE.md", "PLANNING_BASELINE.md"):
        text = (G / name).read_text(encoding="utf-8", errors="replace")
        if re.search(r"all\s+[\d,]+\s+codebase files.*(?:byte|sha).*(?:identical|unchanged)", text, re.I | re.S): wording_errors.append(f"{name}: overstates full cryptographic equality")
    checks.add("SEM-032-INTEGRITY-WORDING", "Codebase-integrity wording accuracy", wording_errors)
    inventory_errors, integrity_evidence = inventory_integrity(inventory, args.full_codebase)
    checks.add("SEM-033-NO-CODEBASE-MUTATION", "No forbidden codebase mutation within available baseline evidence", inventory_errors, integrity_evidence)
    handoff_errors = []
    start = (G / "START-HERE.md").read_text(encoding="utf-8")
    if task_doc.get("exact_first_task_id") != "TASK-GOV-001-PROVENANCE-BASELINE" or tasks[0]["stable_task_id"] != "TASK-GOV-001-PROVENANCE-BASELINE": handoff_errors.append("First task authority mismatch")
    for phase in sorted({task["phase"] for task in tasks}):
        if phase not in start: handoff_errors.append(f"START-HERE omits {phase}")
    for phrase in (
        "implementation has not started", "codebase", "semantic_dependencies", "RELEASE_GATE_PLAN.json",
        "CONDITIONAL_DECISION_PACKAGES.json", "files_expected_to_change", "files_forbidden_from_changing",
        "State-inspection commands", "Conditional decisions and task completion", "Git/hash checkpoint",
        "false-completion", "NOT APPLICABLE", "HARDWARE UNAVAILABLE",
    ):
        if phrase.lower() not in start.lower(): handoff_errors.append(f"START-HERE omits {phrase}")
    checks.add("SEM-034-HANDOFF", "Authoritative implementation handoff consistency", handoff_errors)
    final_domain_errors = []
    data_tasks = {"TASK-CAP-DATA-SAFETY", "TASK-CAP-DATABASE", "TASK-CAP-BACKUP", "TASK-CAP-RESTORE", "TASK-CAP-LEGACY-MIGRATION"}
    if not data_tasks.issubset(task_ids): final_domain_errors.append("Data-safety/migration/backup/recovery task set incomplete")
    if not {"TASK-CAP-NETWORK-POLICY", "TASK-CAP-OFFLINE-FIRST-LAUNCH", "TASK-REL-09-OFFLINE"}.issubset(task_ids): final_domain_errors.append("Offline implementation/proof task set incomplete")
    if not {"TASK-CAP-PACKAGING", "TASK-CAP-WINDOWS-INSTALLER", "TASK-REL-10-WINDOWS-RELEASE"}.issubset(task_ids): final_domain_errors.append("Windows build/package/install/launch task set incomplete")
    checks.add("SEM-035-DATA-OFFLINE-WINDOWS", "Data safety, offline, and Windows release planning", final_domain_errors)
    checks.add("SEM-036-KNOWN-NEGATIVES", "Known-negative validator fixtures", negative_fixture_errors(), {"fixture_count": 14})

    # SEM-037: transient and non-tracked Graphify output-manifest detection
    transient_errors = list(manifest_scan_errors)
    committed_out = load("GRAPHIFY_OUTPUT_MANIFEST.json")
    tracked_graphify = graphify_tracked_set()
    for entry in committed_out.get("files", []):
        rel = str(entry.get("path", ""))
        if set(rel.split("/")) & TRANSIENT_MANIFEST_PARTS or rel.endswith(TRANSIENT_MANIFEST_SUFFIXES):
            transient_errors.append(f"committed output manifest contains transient entry: {rel}")
        if rel and f"Graphify/{rel}" not in tracked_graphify:
            transient_errors.append(f"committed output manifest contains non-tracked entry: {rel}")
    checks.add("SEM-037-TRANSIENT-OUTPUT-MANIFEST", "Transient and non-tracked Graphify output-manifest detection", transient_errors, {"committed_output_manifest_entries": len(committed_out.get("files", [])), "regenerated_output_manifest_entries": len(manifest_entries), "tracked_graphify_files": len(tracked_graphify)})

    # SEM-038: canonical tracked manifest structure and equality
    canonical_base_map, canonical_base_errors = parse_manifest(G / "TRACKED_CODEBASE_BASELINE_SHA256.txt")
    canonical_final_map, canonical_final_errors = parse_manifest(G / "TRACKED_CODEBASE_FINAL_SHA256.txt")
    canonical_current_map, canonical_current_errors = current_tracked_codebase_mapping()
    canonical_struct_errors = list(canonical_base_errors + canonical_final_errors + canonical_current_errors)
    canonical_added = sorted((set(canonical_final_map) | set(canonical_current_map)) - set(canonical_base_map))
    canonical_missing = sorted(set(canonical_base_map) - (set(canonical_final_map) & set(canonical_current_map)))
    canonical_changed = sorted(path for path in set(canonical_base_map) & set(canonical_final_map) & set(canonical_current_map) if not (canonical_base_map[path] == canonical_final_map[path] == canonical_current_map[path]))
    if canonical_added: canonical_struct_errors.append(f"canonical manifest added paths: {canonical_added[:20]}")
    if canonical_missing: canonical_struct_errors.append(f"canonical manifest missing paths: {canonical_missing[:20]}")
    if canonical_changed: canonical_struct_errors.append(f"canonical manifest changed hashes: {canonical_changed[:20]}")
    canonical_stats = manifest_pair_stats(G / "TRACKED_CODEBASE_BASELINE_SHA256.txt", G / "TRACKED_CODEBASE_FINAL_SHA256.txt")
    checks.add("SEM-038-CANONICAL-MANIFEST-COMPARISON", "Canonical tracked manifest structure and equality", canonical_struct_errors, {"canonical_stats": canonical_stats, "current_mapping_identical_to_final": canonical_current_map == canonical_final_map and not canonical_current_errors})

    # SEM-039: manifest honesty (raw-file vs normalized-mapping claims)
    honesty_errors = []
    historical_stats = manifest_pair_stats(G / "AUDIT_CODEBASE_BASELINE_SHA256.txt", G / "AUDIT_CODEBASE_FINAL_SHA256.txt")
    hist_raw_base = sha256(G / "AUDIT_CODEBASE_BASELINE_SHA256.txt")
    hist_raw_final = sha256(G / "AUDIT_CODEBASE_FINAL_SHA256.txt")
    if not historical_stats["mappings_identical"]:
        honesty_errors.append("historical full-tree manifests differ after normalization")
    rec_doc = load("FINAL-REPOSITORY-RECONCILIATION.json") if (G / "FINAL-REPOSITORY-RECONCILIATION.json").is_file() else {}
    canonical_raw_base = sha256(G / "TRACKED_CODEBASE_BASELINE_SHA256.txt")
    canonical_raw_final = sha256(G / "TRACKED_CODEBASE_FINAL_SHA256.txt")
    historical_expected = {"raw_baseline_sha256": hist_raw_base, "raw_final_sha256": hist_raw_final, "raw_files_byte_identical": hist_raw_base == hist_raw_final, **historical_stats}
    if rec_doc.get("historical_manifests") != historical_expected:
        honesty_errors.append("FINAL-REPOSITORY-RECONCILIATION.json historical-manifest fields disagree with computed values")
    canonical_expected = {"raw_baseline_sha256": canonical_raw_base, "raw_final_sha256": canonical_raw_final, "raw_files_byte_identical": canonical_raw_base == canonical_raw_final, **canonical_stats, "current_mapping_identical_to_final": canonical_current_map == canonical_final_map and not canonical_current_errors}
    if rec_doc.get("canonical_manifests") != canonical_expected:
        honesty_errors.append("FINAL-REPOSITORY-RECONCILIATION.json canonical-manifest fields disagree with computed values")
    checks.add("SEM-039-MANIFEST-HONESTY", "Raw-file versus normalized-mapping honesty", honesty_errors, {"historical": {"raw_baseline_sha256": hist_raw_base, "raw_final_sha256": hist_raw_final, "raw_files_byte_identical": hist_raw_base == hist_raw_final, **historical_stats}, "canonical": canonical_expected})

    # SEM-040: protected Master Plan and tracked codebase content
    protected_errors = []
    for name, expected in MASTER_HASHES.items():
        actual = git_blob_sha256(f"Graphify/Master Plan/{name}")
        if actual != expected:
            protected_errors.append(f"Master Plan {name}: canonical blob hash changed ({actual} != {expected})")
    if canonical_added or canonical_missing or canonical_changed:
        protected_errors.append("tracked codebase canonical manifests changed")
    checks.add("SEM-040-PROTECTED-CONTENT", "Protected Master Plan and tracked codebase content unchanged", protected_errors, {"master_plan_sha256": {name: git_blob_sha256(f"Graphify/Master Plan/{name}") for name in MASTER_HASHES}, "tracked_codebase_manifest_unchanged": not (canonical_added or canonical_missing or canonical_changed)})

    # SEM-041: final repository reconciliation report consistency
    reconciliation_errors = []
    rec_path = G / "FINAL-REPOSITORY-RECONCILIATION.json"
    if not rec_path.is_file():
        reconciliation_errors.append("FINAL-REPOSITORY-RECONCILIATION.json is absent")
        committed_rec: dict[str, Any] = {}
    else:
        committed_rec = json.loads(rec_path.read_text(encoding="utf-8"))
    computed_rec = reconciliation_fields(integrity_evidence, checks.items, "PENDING", pre_run_status, manifest_entries)
    stable_keys = [key for key in computed_rec if key not in {"verified_commit_sha", "verified_tree_sha", "validator"}]
    for key in stable_keys:
        if committed_rec.get(key) != computed_rec[key]:
            reconciliation_errors.append(f"FINAL-REPOSITORY-RECONCILIATION.json {key} disagrees with computed value")
    rec_sha = str(committed_rec.get("verified_commit_sha", ""))
    head_sha = computed_rec["verified_commit_sha"]
    parent_sha = git(["rev-parse", "HEAD^"])
    sha_ok = (rec_sha == parent_sha) if parent_sha else (rec_sha == head_sha)
    if not sha_ok:
        reconciliation_errors.append("FINAL-REPOSITORY-RECONCILIATION.json verified commit does not equal the parent commit (or HEAD when HEAD has no parent)")
    if rec_sha and git(["rev-parse", f"{rec_sha}^{{tree}}"]) != str(committed_rec.get("verified_tree_sha", "")):
        reconciliation_errors.append("FINAL-REPOSITORY-RECONCILIATION.json verified tree SHA does not match the verified commit")
    checks.add("SEM-041-RECONCILIATION-REPORT", "Final repository reconciliation report consistency", reconciliation_errors, {"report_present": rec_path.is_file(), "verified_commit_reconciles": bool(sha_ok), "stable_fields_match": not any("disagrees" in error for error in reconciliation_errors)})

    # SEM-042: pre-run tracked working tree cleanliness
    clean_errors = []
    if pre_run_status and not args.allow_dirty:
        clean_errors.append(f"pre-run working tree is not clean:\n{pre_run_status[:800]}")
    checks.add("SEM-042-REPO-CLEAN-PRERUN", "Pre-run tracked working tree cleanliness", clean_errors, {"pre_run_clean": not bool(pre_run_status), "gate_skipped_by_allow_dirty": bool(args.allow_dirty)})

    failed = [item for item in checks.items if item["status"] == "FAIL"]
    verdict = "PASS" if not failed else "FAIL"
    statement = "SEMANTIC GRAPHIFY PLANNING COMPLETE — IMPLEMENTATION NOT STARTED" if verdict == "PASS" else "SEMANTIC GRAPHIFY PLANNING INCOMPLETE — CONTINUE WORKING"
    disposition_counts = collections.Counter(candidate["reviewed_disposition"] for task in tasks if task.get("task_kind") == "DELETION" for candidate in task.get("static_analysis_candidates", []))
    placeholder_count = len(vague_errors)
    contradiction_count = sum(
        item["error_count"] for item in checks.items
        if item["check_id"] in {"SEM-005-PROTECTED-SEPARATION", "SEM-018-TOPOLOGICAL-ORDER", "SEM-019-PHASE-WAVE", "SEM-028-DUPLICATE-AUTHORITY", "SEM-030-COUNTS", "SEM-034-HANDOFF"}
    )
    report = {
        "schema_version": 5, "scope": "DERIVED GRAPHIFY PLANNING ONLY - IMPLEMENTATION NOT STARTED",
        "verdict": verdict, "completion_statement": statement, "total_checks": len(checks.items),
        "passed_checks": len(checks.items) - len(failed), "failed_checks": len(failed), "checks": checks.items,
        "counts": {"requirements": len(requirements), "requirements_by_master_plan": expected_counts["by_master_plan_file"], "requirements_by_classification": expected_counts["by_classification"], "capabilities": len(capabilities), "exact_locations": len(locations), "tasks": len(tasks), "deletion_tasks": sum(task.get("task_kind") == "DELETION" for task in tasks), "conditional_packages": len(packages), "release_gates": len(release_gates)},
        "dependency_graph": graph_metrics, "deletion_dispositions": dict(sorted(disposition_counts.items())),
        "deletion_candidate_count": sum(disposition_counts.values()),
        "known_false_positive_active_count": len(false_positive_errors),
        "unmapped_requirement_count": orphan_counts["requirements_without_capability"],
        "placeholder_count": placeholder_count, "contradiction_count": contradiction_count,
        "orphans": orphan_counts, "codebase_integrity_evidence": integrity_evidence,
        "master_plan_hashes": {name: git_blob_sha256(f"Graphify/Master Plan/{name}") for name in MASTER_HASHES},
        "implementation_status": "NOT STARTED", "release_status": "NOT EVALUATED",
    }
    dump("PLANNING_VALIDATION_REPORT.json", report)
    lines = ["# Semantic Planning Validation Report", "", statement, "", f"Checks: **{report['passed_checks']}/{report['total_checks']} passed**. Implementation: **NOT STARTED**. Release: **NOT EVALUATED**.", "", "| Gate | Result | Errors |", "| --- | --- | ---: |"]
    lines.extend(f"| {item['check_id']} - {item['name']} | {item['status']} | {item['error_count']} |" for item in checks.items)
    if failed:
        lines.extend(["", "## Failures", ""] + [f"- `{item['check_id']}`: {error}" for item in failed for error in item["errors"][:20]])
    write("PLANNING_VALIDATION_REPORT.md", "\n".join(lines))
    dump("VERIFICATION_AUDIT.json", {"schema_version": 4, "scope": report["scope"], "verdict": verdict, "checks": checks.items, "codebase_integrity_evidence": integrity_evidence, "implementation_status": "NOT STARTED", "release_status": "NOT EVALUATED"})
    readiness = {"schema_version": 4, "planning_verdict": verdict, "completion_statement": statement, "implementation_status": "NOT STARTED", "release_status": "NOT EVALUATED", "failed_planning_checks": [item["check_id"] for item in failed], "exact_first_task_id": "TASK-GOV-001-PROVENANCE-BASELINE"}
    dump("READINESS_GATE.json", readiness)
    write("READINESS_GATE.md", f"# Readiness Gate\n\n{statement}\n\nSemantic planning validator: **{verdict}**. Implementation: **NOT STARTED**. Release: **NOT EVALUATED**. Exact first task: `TASK-GOV-001-PROVENANCE-BASELINE`.\n")
    consistency = {"schema_version": 4, "verdict": verdict, "requirements": len(requirements), "capabilities": len(capabilities), "tasks": len(tasks), "exact_locations": len(locations), "dependency_graph": graph_metrics, "orphan_counts": orphan_counts, "duplicate_requirement_ids": duplicates(item["stable_requirement_id"] for item in requirements), "duplicate_capability_ids": duplicates(item["id"] for item in capabilities), "duplicate_task_ids": duplicates(item["stable_task_id"] for item in tasks)}
    dump("GRAPH_CONSISTENCY_REPORT.json", consistency)
    write("GRAPH_CONSISTENCY_REPORT.md", f"# Graph Consistency Report\n\nSemantic planning graph verdict: **{verdict}**. Requirements: {len(requirements)}; capabilities: {len(capabilities)}; tasks: {len(tasks)}; dependency edges: {graph_metrics['dependency_edges']}; cycles: {graph_metrics['cycle_count']}; orphans: {sum(orphan_counts.values())}. This is planning consistency, not application execution proof.\n")
    write("GRAPHIFY_READINESS_REPORT.md", f"# Graphify Readiness Report\n\n{statement}\n\nThe deterministic structural and semantic planning validator reports **{verdict}**. No implementation, application test, build, package, installer, offline launch, hardware workflow, final Graphify rescan, Ponytail pass, or release approval is claimed.\n")
    dump("GRAPHIFY_OUTPUT_MANIFEST.json", {"schema_version": 4, "scope": "Tracked Graphify authorities, reports, tools and immutable Master Plan; genuine graphify-out evidence excluded and separately preserved; transient and non-tracked entries excluded; deterministic (no timestamps)", "self_excluded": True, "file_count": len(manifest_entries), "files": manifest_entries})
    write_reconciliation_report(reconciliation_fields(integrity_evidence, checks.items, verdict, pre_run_status, manifest_entries))
    print(json.dumps({"verdict": verdict, "checks": f"{report['passed_checks']}/{report['total_checks']}", "requirements": len(requirements), "capabilities": len(capabilities), "tasks": len(tasks), "exact_locations": len(locations), "dependency_graph": graph_metrics, "failed": [item["check_id"] for item in failed]}, indent=2, ensure_ascii=False))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
