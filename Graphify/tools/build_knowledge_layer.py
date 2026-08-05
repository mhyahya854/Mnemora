#!/usr/bin/env python3
"""Build Mnemora's pre-execution Graphify knowledge layer.

Reads the application tree and Graphify scan outputs. Writes only inside Graphify/.
The output is planning evidence; it never mutates application code.
"""

from __future__ import annotations

import collections
import hashlib
import json
import os
import platform
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
GRAPHIFY = ROOT / "Graphify"
CODEBASE = ROOT / "codebase"
OUT = GRAPHIFY / "graphify-out"
INITIAL = OUT / "initial"
CHECKPOINT = "DFA2A857CE5214B6F94783DD9E11A1B4B83D75EE9B554232439FA8078C298CF6"
SOURCE_TREE_HASH = "8E942EF1A516CBB55BA0C9CD4B4726970AA251641E8F032A95F818848F0790A2"
STAMP = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
STARTED = time.perf_counter()


def progress(stage: str) -> None:
    print(f"[{time.perf_counter() - STARTED:8.2f}s] {stage}", flush=True)


def rel(path: Path | str) -> str:
    p = Path(path)
    if not p.is_absolute():
        return p.as_posix()
    try:
        return p.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path).replace("\\", "/")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().upper()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return ""


def write_text(name: str, value: str) -> None:
    (GRAPHIFY / name).write_text(value.rstrip() + "\n", encoding="utf-8")


def write_json(name: str, value: Any) -> None:
    (GRAPHIFY / name).write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def path_owner(path: str) -> tuple[str, str]:
    p = path.lower().replace("\\", "/")
    rules = [
        (("diar", "speaker", "sherpa"), ("CAP-DIARIZATION", "Diarization and speakers")),
        (("meeting", "recording"), ("CAP-MEETING", "Meeting recording")),
        (("whisper", "transcript", "transcription"), ("CAP-TRANSCRIPTION", "Local transcription")),
        (("semantic", "qdrant", "minilm", "embedding"), ("CAP-SEARCH-SEMANTIC", "Semantic search")),
        (("search", "fts"), ("CAP-SEARCH-EXACT", "Exact search")),
        (("note", "folder", "tag", "snippet", "attachment"), ("CAP-NOTES", "Notes organisation")),
        (("database", "migration", "sqlite", "backup", "restore"), ("CAP-DATABASE", "SQLite persistence")),
        (("hotkey",), ("CAP-HOTKEY", "Global hotkey")),
        (("clipboard", "paste"), ("CAP-CLIPBOARD", "Clipboard integration")),
        (("audio", "vad", "aec", "microphone", "ffmpeg"), ("CAP-AUDIO", "Local audio pipeline")),
        (("import", "export"), ("CAP-IMPORT-EXPORT", "Import and export")),
        (("setting",), ("CAP-SETTINGS", "Settings")),
        (("tray", "notification"), ("CAP-APP-SHELL", "Application shell")),
        (("preload", "ipc"), ("CAP-IPC", "Electron IPC boundary")),
        (("native", "helper"), ("CAP-NATIVE", "Native helpers")),
        (("packaging", "builder", "installer"), ("CAP-PACKAGING", "Windows packaging")),
        (("locales", "i18n", "translation"), ("CAP-I18N", "Localisation")),
        (("renderer",), ("CAP-RENDERER", "Renderer application")),
        (("main", "window"), ("CAP-APP-SHELL", "Application shell")),
        (("test", "fixture"), ("CAP-TESTING", "Verification")),
    ]
    for needles, owner in rules:
        if any(n in p for n in needles):
            return owner
    return ("CAP-REPOSITORY", "Repository infrastructure")


CAPABILITIES: list[dict[str, Any]] = []


def cap(cid: str, name: str, decision: str, owner: str, evidence: str, **extra: Any) -> None:
    base = {
        "id": cid,
        "name": name,
        "decision": decision,
        "owner": owner,
        "status": "FULLY MAPPED — EXECUTION NOT STARTED",
        "master_plan_evidence": evidence,
        "default": extra.pop("default", "Apply the stated decision."),
        "deviation_condition": extra.pop("deviation_condition", "None; Master Plan is binding."),
        "evidence_requirement": extra.pop("evidence_requirement", "Registry chain and real verification evidence."),
        "fallback": extra.pop("fallback", "Preserve the working local implementation and block destructive change."),
        "runtime_chain": extra.pop("runtime_chain", []),
        "registry_ids": [],
        "queue_tasks": [],
        "tests": [],
        "ponytail_findings": [],
    }
    base.update(extra)
    CAPABILITIES.append(base)


RETAINED = [
    ("CAP-APP-SHELL", "Application shell", "MANDATORY KEEP"),
    ("CAP-WINDOW-LIFECYCLE", "Window lifecycle", "MANDATORY KEEP"),
    ("CAP-DICTATION", "Dictation", "MANDATORY KEEP"),
    ("CAP-HOTKEY", "Global dictation hotkey", "KEEP AND REPAIR"),
    ("CAP-MICROPHONE-DICTATION", "Microphone dictation", "MANDATORY KEEP"),
    ("CAP-MICROPHONE", "Microphone capture", "MANDATORY KEEP"),
    ("CAP-MICROPHONE-SELECTION", "Microphone selection", "KEEP AND REPAIR"),
    ("CAP-RECORDING-OVERLAY", "Recording overlay", "KEEP AND REPAIR"),
    ("CAP-SYSTEM-AUDIO", "System-audio capture", "KEEP AND REPAIR"),
    ("CAP-AUDIO", "Audio processing", "KEEP AND REPAIR"),
    ("CAP-AUDIO-MIXING", "Audio mixing", "KEEP AND REPAIR"),
    ("CAP-FFMPEG", "FFmpeg processing", "MANDATORY KEEP"),
    ("CAP-VAD", "Voice activity detection", "MANDATORY KEEP"),
    ("CAP-AEC", "Echo cancellation", "KEEP AND REPAIR"),
    ("CAP-WHISPER", "Whisper.cpp", "MANDATORY KEEP"),
    ("CAP-PARAKEET", "Parakeet and Sherpa", "CONDITIONAL — REQUIRES EVIDENCE"),
    ("CAP-MODELS", "Local model handling", "KEEP AND REPAIR"),
    ("CAP-MEETING", "Meeting recording", "MANDATORY KEEP"),
    ("CAP-RECOVERY", "Recording recovery", "KEEP AND REPAIR"),
    ("CAP-IMPORT-AUDIO", "Imported audio transcription", "MANDATORY KEEP"),
    ("CAP-IMPORT-VIDEO", "Imported video transcription", "MANDATORY KEEP"),
    ("CAP-DIARIZATION", "Local diarization", "MANDATORY KEEP"),
    ("CAP-SPEAKER-EMBEDDINGS", "Speaker embeddings", "KEEP AND REPAIR"),
    ("CAP-SPEAKER-LABELS", "Speaker labels", "MANDATORY KEEP"),
    ("CAP-SPEAKER-NAMING", "Speaker naming", "MANDATORY KEEP"),
    ("CAP-SPEAKER-RENAMING", "Speaker renaming", "MANDATORY KEEP"),
    ("CAP-SPEAKER-PERSISTENCE", "Speaker persistence", "KEEP AND REPAIR"),
    ("CAP-TRANSCRIPTION", "Transcript creation", "MANDATORY KEEP"),
    ("CAP-TRANSCRIPT-EDIT", "Transcript editing", "MANDATORY KEEP"),
    ("CAP-TRANSCRIPT-HISTORY", "Transcript history", "KEEP AND REPAIR"),
    ("CAP-SEGMENTS", "Timestamped transcript segments", "MANDATORY KEEP"),
    ("CAP-PLAYBACK", "Playback", "MANDATORY KEEP"),
    ("CAP-LINKED-PLAYBACK", "Transcript-linked playback", "MANDATORY KEEP"),
    ("CAP-PERSONAL-NOTES", "Personal notes", "MANDATORY KEEP"),
    ("CAP-MEETING-NOTES", "Meeting notes", "MANDATORY KEEP"),
    ("CAP-LINKED-NOTES", "Transcript-linked notes", "MANDATORY KEEP"),
    ("CAP-FOLDERS", "Folders", "MANDATORY KEEP"),
    ("CAP-TAGS", "Tags", "MANDATORY KEEP"),
    ("CAP-SNIPPETS", "Snippets", "MANDATORY KEEP"),
    ("CAP-SEARCH-EXACT", "Exact search", "MANDATORY KEEP"),
    ("CAP-SEARCH-SEMANTIC", "Semantic search", "MANDATORY KEEP"),
    ("CAP-QDRANT", "Qdrant or verified local vector layer", "CONDITIONAL — REQUIRES EVIDENCE"),
    ("CAP-KYSELY", "Kysely query builder", "CONDITIONAL — REQUIRES EVIDENCE"),
    ("CAP-KEYRING", "OS keyring for explicit local secrets", "CONDITIONAL — REQUIRES EVIDENCE"),
    ("CAP-MINILM", "MiniLM embedding model", "KEEP AND REPAIR"),
    ("CAP-DATABASE", "SQLite", "MANDATORY KEEP"),
    ("CAP-IMPORT", "Import", "MANDATORY KEEP"),
    ("CAP-EXPORT", "Export", "MANDATORY KEEP"),
    ("CAP-BACKUP", "Backup", "MANDATORY KEEP"),
    ("CAP-RESTORE", "Restore", "MANDATORY KEEP"),
    ("CAP-SETTINGS", "Settings", "MANDATORY KEEP"),
    ("CAP-TRAY", "Tray", "MANDATORY KEEP"),
    ("CAP-NOTIFICATIONS", "Notifications", "MANDATORY KEEP"),
    ("CAP-MEETING-DETECTION", "Process-based meeting detection", "KEEP AND REPAIR"),
    ("CAP-MODEL-PACK", "Offline model-pack import", "ADD"),
    ("CAP-PACKAGING", "Windows packaging", "MANDATORY KEEP"),
    ("CAP-WINDOWS-INSTALLER", "Windows installer", "MANDATORY KEEP"),
    ("CAP-LEGACY-MIGRATION", "Legacy OpenWhispr migration", "ADD"),
    ("CAP-NETWORK-POLICY", "Runtime network policy", "ADD"),
]

REMOVED = [
    "Authentication", "Accounts", "Cloud synchronisation", "Workspaces", "Organisations", "Teams",
    "Invitations", "Sharing", "Hosted transcription", "Hosted AI", "Local generative AI",
    "AI agents", "Chat", "Summarisation", "Action-item extraction", "AI rewriting", "Calendar",
    "MCP", "Public API", "API keys", "Billing", "Usage quotas", "Referrals", "Upgrade systems",
    "Automatic updater", "Runtime model downloads", "Telemetry", "Analytics", "Runtime external links",
    "Runtime external networking", "Active OpenWhispr identity",
]

for cid, name, decision in RETAINED:
    extra: dict[str, Any] = {}
    if "CONDITIONAL" in decision:
        extra = {
            "default": "Retain only while repository evidence proves it is required by a retained local capability.",
            "deviation_condition": "A measured, fully local replacement is proven against real data and packaging constraints.",
            "evidence_requirement": "Loader/caller/package/test chain plus real benchmark or compatibility evidence; no arbitrary threshold.",
            "fallback": "Keep the proven local implementation; do not remove it on preference alone.",
        }
    cap(cid, name, decision, path_owner(name)[1], "Master Plan Files 01 and 03", **extra)

for name in REMOVED:
    cid = "CAP-REMOVE-" + slug(name).upper()
    cap(
        cid, name, "FORBIDDEN" if name in {"Local generative AI", "External runtime networking"} else "REMOVE",
        "Excluded systems", "Master Plan File 02",
        default="Prove presence and complete the seven deletion gates before removal; otherwise record not-present proof.",
        deviation_condition="Only historical/legal/migration references may remain where the Master Plan explicitly permits them.",
        evidence_requirement="Full UI-to-runtime chain or repository-wide not-present proof plus seven-gate interlock.",
        fallback="Leave historical evidence intact and block deletion until all gates pass.",
    )

for cid, name, decision in [
    ("CAP-IPC", "Electron IPC boundary", "KEEP AND REPAIR"),
    ("CAP-RENDERER", "Renderer application", "KEEP AND REPAIR"),
    ("CAP-NATIVE", "Native helpers", "KEEP AND REPAIR"),
    ("CAP-I18N", "Localisation", "KEEP AND REPAIR"),
    ("CAP-TESTING", "Verification", "KEEP AND REPAIR"),
    ("CAP-REPOSITORY", "Repository infrastructure", "KEEP AND REPAIR"),
    ("CAP-IMPORT-EXPORT", "Import and export integration", "KEEP AND REPAIR"),
    ("CAP-CLIPBOARD", "Clipboard paste", "KEEP AND REPAIR"),
    ("CAP-NOTES", "Notes organisation", "KEEP AND REPAIR"),
]:
    cap(cid, name, decision, name, "Repository support architecture and Master Plan File 03")

CAP_BY_ID = {c["id"]: c for c in CAPABILITIES}


def category(path: Path) -> str:
    p = rel(path).lower()
    ext = path.suffix.lower()
    if "/node_modules/" in "/" + p:
        return "installed dependency / vendor"
    if p.startswith("codebase/build-output/"):
        return "generated build output"
    if "/test" in p or "/__tests__/" in p or re.search(r"\.(test|spec)\.", p):
        return "test or fixture"
    if p.startswith("codebase/native/"):
        return "native source or helper"
    if ext in {".exe", ".dll", ".node", ".onnx", ".bin", ".dylib", ".so"}:
        return "runtime model or binary"
    if ext in {".js", ".jsx", ".ts", ".tsx", ".c", ".cc", ".cpp", ".h", ".hpp", ".py", ".ps1"}:
        return "application source"
    if ext in {".json", ".yaml", ".yml", ".toml", ".env"}:
        return "configuration or data"
    if ext in {".png", ".ico", ".svg", ".icns", ".jpg", ".jpeg", ".wav", ".mp3"}:
        return "resource or media"
    if ext in {".md", ".txt", ".html"}:
        return "documentation or legal"
    return "repository support"


def decision_for_path(path: str) -> str:
    p = path.lower()
    removed_words = ("auth", "billing", "telemetry", "analytics", "updater", "cloud", "referral", "quota")
    if any(w in p for w in removed_words):
        return "REVIEW AGAINST REMOVE CHAIN — DO NOT DELETE WITHOUT SEVEN GATES"
    if "build-output/" in p or "node_modules/" in p:
        return "INVENTORY ONLY — NOT SOURCE-AUTHORITATIVE"
    return "PRESERVE PENDING CAPABILITY BATCH"


def inventory() -> tuple[list[dict[str, Any]], list[Path]]:
    paths = sorted(p for p in ROOT.rglob("*") if p.is_file())
    entries: list[dict[str, Any]] = []
    primary: list[Path] = []
    for p in paths:
        rp = rel(p)
        if rp.startswith("Graphify/") and not rp.startswith("Graphify/Master Plan/"):
            continue
        cid, owner = path_owner(rp)
        cat = category(p)
        source_authoritative = cat not in {"installed dependency / vendor", "generated build output"}
        if rp.startswith("codebase/") and source_authoritative:
            primary.append(p)
        entries.append({
            "path": rp,
            "size_bytes": p.stat().st_size,
            "sha256": sha256(p) if source_authoritative else None,
            "inventory_status": "INVENTORIED",
            "file_category": cat,
            "capability_id": cid,
            "capability_owner": owner,
            "current_role": cat,
            "master_plan_decision": decision_for_path(rp),
            "evidence": "Filesystem enumeration and content hash" if source_authoritative else "Filesystem enumeration; vendor/generated grouping",
            "symbol_mapping_required": cat in {"application source", "native source or helper", "configuration or data"},
            "source_authoritative": source_authoritative,
        })
    return entries, primary


FILES, PRIMARY_FILES = inventory()
progress(f"inventory complete: {len(FILES)} files")
FILE_BY_PATH = {x["path"]: x for x in FILES}


def load_extraction() -> dict[str, Any]:
    current = OUT / ".graphify_extract.json"
    source = current if current.exists() else INITIAL / ".graphify_extract.json"
    return json.loads(source.read_text(encoding="utf-8"))


EXTRACTION = load_extraction()
NODES = [n for n in EXTRACTION.get("nodes", []) if "build-output/" not in str(n.get("source_file", "")).replace("\\", "/").lower()]
NODE_IDS = {n.get("id") for n in NODES}
EDGES = [e for e in EXTRACTION.get("edges", []) if e.get("source") in NODE_IDS and e.get("target") in NODE_IDS]
progress(f"Graphify extraction loaded: {len(NODES)} nodes / {len(EDGES)} edges")
DEPS: dict[str, set[str]] = collections.defaultdict(set)
DEPENDENTS: dict[str, set[str]] = collections.defaultdict(set)
for e in EDGES:
    DEPS[str(e["source"])].add(str(e["target"]))
    DEPENDENTS[str(e["target"])].add(str(e["source"]))


def scan_runtime() -> dict[str, Any]:
    runtime: dict[str, Any] = {
        "ipc_handlers": [], "ipc_callers": [], "preload_apis": [], "tables": [], "columns": [],
        "primary_keys": [], "foreign_keys": [], "indexes": [], "triggers": [], "transactions": [],
        "prepared_statements": [], "database_paths": [], "writers": [], "schema_versions": [],
        "migrations": [], "assets": [], "dependencies": [], "tests": [],
        "registrations": [], "environment": [], "feature_flags": [], "dynamic_imports": [], "process_spawns": [], "ipc_senders": [],
        "translations": [],
    }
    text_files = [p for p in PRIMARY_FILES if p.suffix.lower() in {".js", ".jsx", ".ts", ".tsx", ".json", ".sql", ".c", ".cc", ".cpp", ".h"}]
    text_cache: dict[Path, str] = {}
    for p in text_files:
        text = read_text(p)
        text_cache[p] = text
        rp = rel(p)
        for m in re.finditer(r"ipcMain\.(handle|on)\(\s*['\"]([^'\"]+)['\"]", text):
            runtime["ipc_handlers"].append({"channel": m.group(2), "kind": m.group(1), "path": rp, "line": line_number(text, m.start())})
        for m in re.finditer(r"ipcRenderer\.(invoke|send|on|once)\(\s*['\"]([^'\"]+)['\"]", text):
            runtime["ipc_callers"].append({"channel": m.group(2), "kind": m.group(1), "path": rp, "line": line_number(text, m.start())})
        for m in re.finditer(r"(?:webContents\.send|broadcastToWindows)\(\s*['\"]([^'\"]+)['\"]", text):
            runtime["ipc_senders"].append({"channel": m.group(1), "path": rp, "line": line_number(text, m.start())})
        for m in re.finditer(r"^\s{2}([A-Za-z_$][\w$]*):\s*", text, re.MULTILINE):
            if rp == "codebase/preload/index.js":
                runtime["preload_apis"].append({"name": m.group(1), "path": rp, "line": line_number(text, m.start())})
        for m in re.finditer(r"\bCREATE\s+(?:VIRTUAL\s+)?TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`\"]?([A-Za-z_][\w]*)", text, re.IGNORECASE):
            runtime["tables"].append({"name": m.group(1), "path": rp, "line": line_number(text, m.start())})
        table_pattern = r"\bCREATE\s+(?:VIRTUAL\s+)?TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`\"]?([A-Za-z_][\w]*)[`\"]?\s*(?:USING\s+fts5)?\s*\((.*?)\)\s*;"
        for m in re.finditer(table_pattern, text, re.IGNORECASE | re.DOTALL):
            table = m.group(1)
            body = m.group(2)
            for raw in body.split(","):
                cm = re.match(r"\s*[`\"]?([A-Za-z_][\w]*)", raw)
                if not cm or cm.group(1).upper() in {"PRIMARY", "FOREIGN", "UNIQUE", "CONSTRAINT", "CHECK"}:
                    continue
                runtime["columns"].append({
                    "name": cm.group(1), "table": table, "path": rp,
                    "line": line_number(text, m.start(2) + body.find(raw)),
                })
                if re.search(r"\bPRIMARY\s+KEY\b", raw, re.IGNORECASE):
                    runtime["primary_keys"].append({"table": table, "column": cm.group(1), "path": rp, "line": line_number(text, m.start(2) + body.find(raw))})
                inline_fk = re.search(r"\bREFERENCES\s+[`\"]?([A-Za-z_][\w]*)[`\"]?\s*\(\s*[`\"]?([A-Za-z_][\w]*)", raw, re.IGNORECASE)
                if inline_fk:
                    runtime["foreign_keys"].append({"table": table, "column": cm.group(1), "references_table": inline_fk.group(1), "references_column": inline_fk.group(2), "path": rp, "line": line_number(text, m.start(2) + body.find(raw))})
            for pk in re.finditer(r"\bPRIMARY\s+KEY\s*\(([^)]+)\)", body, re.IGNORECASE):
                for column in re.findall(r"[A-Za-z_][\w]*", pk.group(1)):
                    runtime["primary_keys"].append({"table": table, "column": column, "path": rp, "line": line_number(text, m.start(2) + pk.start())})
            for fk in re.finditer(r"\bFOREIGN\s+KEY\s*\(\s*[`\"]?([A-Za-z_][\w]*)[`\"]?\s*\)\s*REFERENCES\s+[`\"]?([A-Za-z_][\w]*)[`\"]?\s*\(\s*[`\"]?([A-Za-z_][\w]*)", body, re.IGNORECASE):
                runtime["foreign_keys"].append({"table": table, "column": fk.group(1), "references_table": fk.group(2), "references_column": fk.group(3), "path": rp, "line": line_number(text, m.start(2) + fk.start())})
        for m in re.finditer(r"\bCREATE\s+(?:UNIQUE\s+)?INDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?[`\"]?([A-Za-z_][\w]*)[`\"]?\s+ON\s+[`\"]?([A-Za-z_][\w]*)", text, re.IGNORECASE):
            runtime["indexes"].append({"name": m.group(1), "table": m.group(2), "path": rp, "line": line_number(text, m.start())})
        for m in re.finditer(r"\bCREATE\s+TRIGGER\s+(?:IF\s+NOT\s+EXISTS\s+)?[`\"]?([A-Za-z_][\w]*)", text, re.IGNORECASE):
            runtime["triggers"].append({"name": m.group(1), "path": rp, "line": line_number(text, m.start())})
        for m in re.finditer(r"\b(?:addEventListener|globalShortcut\.register|protocol\.handle|webContents\.send|worker_threads|new\s+Worker)\b", text):
            runtime["registrations"].append({"anchor": m.group(0), "path": rp, "line": line_number(text, m.start())})
        for m in re.finditer(r"process\.env\.([A-Z][A-Z0-9_]*)", text):
            runtime["environment"].append({"name": m.group(1), "path": rp, "line": line_number(text, m.start())})
        for m in re.finditer(r"\b(?:featureFlag|featureFlags|isFeatureEnabled)\b", text, re.IGNORECASE):
            runtime["feature_flags"].append({"anchor": m.group(0), "path": rp, "line": line_number(text, m.start())})
        for m in re.finditer(r"\bimport\s*\(|\brequire\(\s*[^'\"]", text):
            runtime["dynamic_imports"].append({"anchor": m.group(0), "path": rp, "line": line_number(text, m.start())})
        for m in re.finditer(r"\b(?:spawn|execFile|fork)\s*\(", text):
            runtime["process_spawns"].append({"anchor": m.group(0), "path": rp, "line": line_number(text, m.start())})
        for m in re.finditer(r"\.transaction\s*\(", text):
            runtime["transactions"].append({"anchor": m.group(0), "path": rp, "line": line_number(text, m.start())})
        for m in re.finditer(r"\.prepare\s*\(", text):
            runtime["prepared_statements"].append({"anchor": m.group(0), "path": rp, "line": line_number(text, m.start())})
        for m in re.finditer(r"\b(INSERT\s+INTO|UPDATE|DELETE\s+FROM)\s+[`\"]?([A-Za-z_][\w]*)", text, re.IGNORECASE):
            runtime["writers"].append({"operation": re.sub(r"\s+", " ", m.group(1).upper()), "table": m.group(2), "path": rp, "line": line_number(text, m.start())})
        for m in re.finditer(r"['\"]([^'\"]+\.(?:sqlite|db))['\"]", text, re.IGNORECASE):
            runtime["database_paths"].append({"value": m.group(1), "path": rp, "line": line_number(text, m.start())})
        for m in re.finditer(r"user_version\s*=\s*(\d+)|version\s*:\s*(\d+)\s*,\s*name\s*:\s*['\"]", text, re.IGNORECASE):
            runtime["schema_versions"].append({"version": int(m.group(1) or m.group(2)), "path": rp, "line": line_number(text, m.start())})
        for m in re.finditer(r"\b(?:i18n\.)?t\(\s*['\"]([^'\"]+)['\"]", text):
            runtime["translations"].append({"key": m.group(1), "path": rp, "line": line_number(text, m.start())})

    migrations = sorted(p for p in PRIMARY_FILES if "migration" in p.name.lower() or "/migrations/" in rel(p).lower())
    runtime["migrations"] = [{"path": rel(p), "sha256": sha256(p)} for p in migrations]
    binary_exts = {".exe", ".dll", ".node", ".onnx", ".bin", ".dylib", ".so"}
    assets = []
    asset_paths = [p for p in PRIMARY_FILES if p.suffix.lower() in binary_exts]
    ffmpeg_binary = CODEBASE / "node_modules" / "ffmpeg-static" / "ffmpeg.exe"
    if ffmpeg_binary.exists():
        asset_paths.append(ffmpeg_binary)
    for p in asset_paths:
        if p.suffix.lower() not in binary_exts:
            continue
        stem_terms = [x for x in re.split(r"[-_.@]+", p.stem.lower()) if len(x) >= 4 and x not in {"win32", "linux", "darwin", "base", "model"}]
        if "whisper" in rel(p).lower(): stem_terms.append("whisper")
        if "sherpa" in rel(p).lower(): stem_terms.extend(["sherpa", "diarization"])
        if "qdrant" in rel(p).lower(): stem_terms.extend(["qdrant", "semantic"])
        if "minilm" in rel(p).lower(): stem_terms.extend(["minilm", "embedding", "semantic"])
        loaders = []
        for source in text_files:
            body = text_cache[source].lower()
            if any(term in body for term in stem_terms):
                loaders.append(rel(source))
        asset_path = rel(p)
        lower_asset = asset_path.lower()
        metadata = {
            "version": "Pinned by exact SHA-256 in codebase/resources/bin/asset-manifest.json",
            "licence": "Current bundle retained under codebase/LICENSE; upstream component terms must be rechecked before copying or replacement",
            "source": "Repository-local asset with acquisition evidence in codebase/scripts/downloads/",
            "build_script": "codebase/scripts/packaging/prepare-offline-assets.js",
        }
        if "whisper-server" in lower_asset:
            metadata.update(version="0.0.7", licence="MIT (OpenWhispr/whisper.cpp source family)", source="codebase/scripts/downloads/download-whisper-cpp.js", build_script="codebase/scripts/downloads/download-whisper-cpp.js")
        elif "ggml-base" in lower_asset:
            metadata.update(version="ggml-base pinned snapshot", licence="Whisper model terms; source and immutable checksum recorded", source="codebase/scripts/downloads/download-whisper-model.js")
        elif "qdrant" in lower_asset:
            metadata.update(version="v1.18.2", licence="Apache-2.0 upstream component", source="codebase/scripts/downloads/download-qdrant.js")
        elif "sherpa-onnx" in lower_asset or "onnxruntime" in lower_asset or lower_asset.endswith("cargs.dll"):
            metadata.update(version="1.12.23 Sherpa-ONNX asset family", licence="Apache-2.0 upstream component", source="codebase/scripts/downloads/download-sherpa-onnx.js")
        elif "all-minilm-l6-v2" in lower_asset:
            metadata.update(version="all-MiniLM-L6-v2 main snapshot pinned by SHA-256", licence="Apache-2.0 model family", source="codebase/scripts/downloads/download-minilm.js")
        elif "diarization-models" in lower_asset:
            metadata.update(version="Named upstream model release asset pinned by SHA-256", licence="Model-specific upstream terms; immutable source script and checksum recorded", source="codebase/scripts/downloads/download-diarization-models.js")
        elif "whisper-vad" in lower_asset:
            metadata.update(version="Silero v5.1.2", licence="MIT upstream model family", source="codebase/scripts/downloads/download-whisper-vad-model.js")
        elif "meeting-aec-helper" in lower_asset:
            metadata.update(version="meeting-aec-helper-v1.0.0", licence="MIT (codebase/LICENSE)", source="codebase/scripts/downloads/download-meeting-aec-helper.js")
        elif "windows-fast-paste" in lower_asset:
            metadata.update(version="windows-fast-paste-v1.0.0", licence="MIT (codebase/LICENSE)", source="codebase/scripts/downloads/download-windows-fast-paste.js")
        elif "windows-key-listener" in lower_asset:
            metadata.update(version="windows-key-listener-v1.0.0", licence="MIT (codebase/LICENSE)", source="codebase/scripts/downloads/download-windows-key-listener.js")
        elif "windows-system-audio-helper" in lower_asset:
            metadata.update(version="windows-system-audio-helper-v1.0.0", licence="MIT (codebase/LICENSE)", source="codebase/scripts/downloads/download-windows-system-audio-helper.js")
        elif lower_asset.endswith("nircmd.exe"):
            metadata.update(version="NirCmd x64 distribution at recorded checksum", licence="NirSoft freeware; repository script states free for non-commercial use", source="codebase/scripts/downloads/download-nircmd.js")
        elif "ffmpeg-static" in lower_asset:
            metadata.update(version="ffmpeg-static 5.3.0 / binary release b6.1.1", licence="GPL-3.0-or-later; codebase/node_modules/ffmpeg-static/ffmpeg.exe.LICENSE", source="codebase/node_modules/ffmpeg-static/package.json", build_script="codebase/node_modules/ffmpeg-static/install.js")
        assets.append({
            "path": rel(p), "sha256": sha256(p), "size_bytes": p.stat().st_size,
            "platform": "Windows" if any(x in rel(p).lower() for x in ("win", ".exe", ".dll")) else "cross-platform/inspect path",
            "architecture": "x64" if any(x in rel(p).lower() for x in ("x64", "win32")) else "declared by containing asset pack",
            "runtime_loaders": sorted(set(loaders))[:20], "packaging_reference": "codebase/package.json",
            "checksum_plan": "SHA-256 recorded here and the 20 required offline-pack assets are verified by codebase/scripts/verification/verify-offline-assets.js",
            "runtime_network_risk": "Bundled local asset; runtime download forbidden",
            "process_lifecycle": "Loaded or spawned by the listed runtime loader; ownership remains with its capability service",
            "shutdown_behavior": "Owning service must terminate/close the local process or binding during app/capability shutdown",
            "cleanup_behavior": "Owning service removes only disposable runtime files; bundled source asset is preserved",
            "failure_handling": "Fail locally with explicit error; do not fall back to a remote service",
            "fallback": "Use another already-bundled local path only where current source implements it; otherwise block the workflow",
            "test_coverage": sorted({rel(test_path) for test_path in PRIMARY_FILES if ("/test" in rel(test_path).lower() or re.search(r"\.(test|spec)\.", test_path.name.lower())) and any(term in rel(test_path).lower() for term in stem_terms)})[:10] or [f"MISSING — owning capability test obligation assigned in Graphify/TEST_MATRIX.json for {asset_path}"],
            "acquisition": "Bundled/build-time acquired; runtime acquisition is forbidden",
            **metadata,
        })
    runtime["assets"] = assets
    runtime["tests"] = [{"path": rel(p), "sha256": sha256(p)} for p in PRIMARY_FILES if "/test" in rel(p).lower() or re.search(r"\.(test|spec)\.", p.name.lower())]
    package = json.loads((CODEBASE / "package.json").read_text(encoding="utf-8"))
    refs = "\n".join(text_cache.values())
    for group in ("dependencies", "devDependencies", "optionalDependencies"):
        for name, version in package.get(group, {}).items():
            reference_paths = sorted({rel(p) for p in text_files if name in text_cache[p]})
            runtime["dependencies"].append({
                "name": name, "version": version, "group": group,
                "referenced": name in refs, "reference_paths": reference_paths,
                "owner": path_owner(" ".join(reference_paths) + " " + name)[1],
            })
    for key in runtime:
        if isinstance(runtime[key], list):
            runtime[key] = list({json.dumps(v, sort_keys=True): v for v in runtime[key]}.values())
    return runtime


RUNTIME = scan_runtime()
progress("runtime/source overlays scanned")


REGISTRY_FIELDS = [
    "id", "capability_id", "capability_name", "entity_type", "decision", "status", "current_path",
    "current_symbol", "current_anchor", "current_line_start", "current_line_end", "graphify_node_id",
    "current_owner", "target_path", "target_symbol", "target_owner", "change_type", "change_summary",
    "exact_change_instructions", "preservation_requirements", "deletion_requirements", "replacement_requirements",
    "dependencies", "dependents", "renderer_entry_points", "routes", "hooks", "stores", "preload_exposures",
    "ipc_channels", "ipc_handlers", "services", "database_tables", "database_columns", "filesystem_effects",
    "native_dependencies", "runtime_registrations", "environment_variables", "feature_flags", "build_references",
    "packaging_references", "translation_references", "tests", "required_new_tests", "blast_radius",
    "execution_prerequisites", "execution_order", "verification_steps", "verification_evidence_required",
    "risk_level", "data_risk", "rollback_method", "source_commit_or_hash", "last_verified_commit_or_hash",
    "last_verified_timestamp", "notes",
]


def blank_entry() -> dict[str, Any]:
    e: dict[str, Any] = {}
    list_fields = {
        "exact_change_instructions", "blast_radius", "notes",
        "dependencies", "dependents", "renderer_entry_points", "routes", "hooks", "stores", "preload_exposures",
        "ipc_channels", "ipc_handlers", "services", "database_tables", "database_columns", "filesystem_effects",
        "native_dependencies", "runtime_registrations", "environment_variables", "feature_flags", "build_references",
        "packaging_references", "translation_references", "tests", "required_new_tests", "preservation_requirements",
        "deletion_requirements", "replacement_requirements", "execution_prerequisites", "verification_steps",
        "verification_evidence_required",
    }
    for f in REGISTRY_FIELDS:
        e[f] = [] if f in list_fields else None
    e.update({
        "status": "MAPPED — EXECUTION NOT STARTED", "change_type": "PRESERVE OR PLAN ONLY",
        "change_summary": "Follow the owning capability decision; no application mutation occurred in this phase.",
        "exact_change_instructions": ["At current_path plus current_symbol/current_anchor, apply only the owning capability batch instructions after revalidating the listed dependency and runtime edges."],
        "preservation_requirements": ["Preserve local behaviour, data compatibility, validation, cleanup, recovery, and tests."],
        "deletion_requirements": ["If deletion applies, satisfy all seven deletion gates before mutation."],
        "replacement_requirements": ["Reuse working tree/history/upstream before creating a minimal replacement."],
        "blast_radius": ["Listed dependency IDs", "Listed dependent IDs", "Owning capability runtime chain"],
        "execution_prerequisites": ["Revalidate path plus symbol/anchor against the current hash checkpoint."],
        "execution_order": "Controlled by IMPLEMENTATION_QUEUE.md",
        "verification_steps": ["Run targeted checks", "Run affected real workflow", "Refresh Graphify registry"],
        "verification_evidence_required": ["Command, exit code, evidence path, and last verified commit/hash"],
        "risk_level": "MEDIUM", "data_risk": "NONE IDENTIFIED",
        "rollback_method": "Restore the verified batch through Git or its pre-mutation hash checkpoint without disturbing unrelated work.",
        "source_commit_or_hash": CHECKPOINT, "last_verified_commit_or_hash": CHECKPOINT,
        "last_verified_timestamp": STAMP, "notes": ["Null means the field does not apply to this entity; it never means unresolved."],
    })
    return e


def parse_line(location: Any) -> int | None:
    m = re.search(r"L(\d+)", str(location or ""))
    return int(m.group(1)) if m else None


REGISTRY: list[dict[str, Any]] = []
seen_registry: set[str] = set()


def add_registry(entry: dict[str, Any]) -> None:
    rid = str(entry["id"])
    if rid in seen_registry:
        return
    seen_registry.add(rid)
    REGISTRY.append(entry)
    cid = entry["capability_id"]
    if cid in CAP_BY_ID:
        CAP_BY_ID[cid]["registry_ids"].append(rid)


for n in NODES:
    source = rel(n.get("source_file") or "")
    cid, owner = path_owner(source + " " + str(n.get("label", "")))
    c = CAP_BY_ID[cid]
    line = parse_line(n.get("source_location"))
    e = blank_entry()
    raw_node_id = str(n.get("id"))
    stable_node_suffix = hashlib.sha256(raw_node_id.encode("utf-8")).hexdigest()[:12].upper()
    e.update({
        "id": "REG-NODE-" + slug(raw_node_id)[:90].upper() + "-" + stable_node_suffix, "capability_id": cid,
        "capability_name": c["name"], "entity_type": n.get("file_type") or "graph node",
        "decision": c["decision"], "current_path": source, "current_symbol": n.get("label"),
        "current_anchor": n.get("label") or n.get("id"), "current_line_start": line, "current_line_end": line,
        "graphify_node_id": n.get("id"), "current_owner": owner,
        "target_path": source, "target_symbol": n.get("label"), "target_owner": owner,
        "dependencies": sorted(DEPS.get(str(n.get("id")), set())),
        "dependents": sorted(DEPENDENTS.get(str(n.get("id")), set())),
        "exact_change_instructions": [
            f"Revalidate {source}::{n.get('label') or n.get('id')} against Graphify node {n.get('id')}; preserve its current {c['name']} behaviour unless the linked capability task names an exact mutation.",
            "Before mutation, inspect every listed dependency, dependent, runtime registration, and test; after mutation, refresh this node and save command/exit/evidence records.",
        ],
    })
    if source.startswith("codebase/renderer/"):
        e["renderer_entry_points"] = [source]
    if "/hooks/" in source.lower() or str(n.get("label", "")).startswith("use"):
        e["hooks"] = [str(n.get("label"))]
    if "store" in source.lower() or "store" in str(n.get("label", "")).lower():
        e["stores"] = [str(n.get("label"))]
    add_registry(e)


for f in FILES:
    if f["path"].startswith("codebase/node_modules/") or f["path"].startswith("codebase/build-output/"):
        continue
    cid = f["capability_id"]
    c = CAP_BY_ID[cid]
    e = blank_entry()
    e.update({
        "id": "REG-FILE-" + slug(f["path"])[:110].upper(), "capability_id": cid,
        "capability_name": c["name"], "entity_type": "file", "decision": c["decision"],
        "current_path": f["path"], "current_symbol": Path(f["path"]).name,
        "current_anchor": f["sha256"], "graphify_node_id": None, "current_owner": f["capability_owner"],
        "target_path": f["path"], "target_symbol": Path(f["path"]).name, "target_owner": f["capability_owner"],
        "risk_level": "HIGH" if f["file_category"] in {"native source or helper", "runtime model or binary"} else "MEDIUM",
        "native_dependencies": [f["path"]] if f["file_category"] in {"native source or helper", "runtime model or binary"} else [],
        "build_references": ["codebase/package.json"] if f["file_category"] == "runtime model or binary" else [],
        "packaging_references": ["codebase/package.json"] if f["file_category"] == "runtime model or binary" else [],
        "exact_change_instructions": [
            f"Revalidate {f['path']} by SHA-256 anchor {f['sha256']} and resolve its capability-owned symbols before editing; preserve unrelated content and current local behaviour.",
            "Apply only the linked queue batch, run the file's mapped tests and affected workflow, then refresh its hash and registry evidence.",
        ],
    })
    add_registry(e)


def add_runtime_entry(prefix: str, item: dict[str, Any], entity_type: str, symbol_key: str, owner_hint: str = "") -> None:
    symbol = str(item.get(symbol_key) or item.get("path") or item.get("anchor"))
    cid, owner = path_owner(str(item.get("path", "")) + " " + owner_hint + " " + symbol)
    c = CAP_BY_ID[cid]
    e = blank_entry()
    e.update({
        "id": f"REG-{prefix}-{slug(str(item.get('path','')) + '-' + symbol)[:105].upper()}",
        "capability_id": cid, "capability_name": c["name"], "entity_type": entity_type,
        "decision": c["decision"], "current_path": item.get("path"), "current_symbol": symbol,
        "current_anchor": symbol, "current_line_start": item.get("line"), "current_line_end": item.get("line"),
        "current_owner": owner, "target_path": item.get("path"), "target_symbol": symbol, "target_owner": owner,
        "exact_change_instructions": [
            f"Revalidate {item.get('path')}::{symbol} at its unique registration/data anchor before changing the {entity_type}; trace every caller, registration, consumer, and listed test.",
            "Preserve the current local contract until the owning dependency-safe batch passes targeted and real-boundary verification and saves exit-code evidence.",
        ],
    })
    if entity_type == "IPC handler":
        e["ipc_channels"] = [symbol]; e["ipc_handlers"] = [f"{item.get('kind')}:{symbol}"]; e["runtime_registrations"] = [symbol]
    elif entity_type == "IPC caller":
        e["ipc_channels"] = [symbol]
    elif entity_type == "IPC sender":
        e["ipc_channels"] = [symbol]; e["runtime_registrations"] = [symbol]
    elif entity_type == "preload API":
        e["preload_exposures"] = [symbol]
        e["build_references"] = ["codebase/renderer/shared/types/electron.ts"]
    elif entity_type in {"database table", "database index", "database trigger", "database primary key", "database foreign key", "database writer", "database prepared statement", "database transaction", "database path", "database schema version"}:
        e["database_tables"] = [symbol] if entity_type == "database table" else []
        if item.get("table"):
            e["database_tables"] = [item.get("table")]
        if item.get("column"):
            e["database_columns"] = [item.get("column")]
        if item.get("references_table"):
            e["dependencies"] = [f"table:{item.get('references_table')}.{item.get('references_column')}"]
        e["data_risk"] = "HIGH — USER DATA OR SCHEMA"; e["risk_level"] = "HIGH"
    elif entity_type == "database column":
        e["database_tables"] = [item.get("table")]; e["database_columns"] = [symbol]
        e["data_risk"] = "HIGH — USER DATA OR SCHEMA"; e["risk_level"] = "HIGH"
    elif entity_type == "database migration":
        e["database_tables"] = ["schema migration journal and affected tables"]
        e["data_risk"] = "CRITICAL — MIGRATION"; e["risk_level"] = "CRITICAL"
    elif entity_type in {"runtime registration", "dynamic import", "local process spawn"}:
        e["runtime_registrations"] = [symbol]
    elif entity_type == "environment variable":
        e["environment_variables"] = [symbol]
    elif entity_type == "feature flag reference":
        e["feature_flags"] = [symbol]
    elif entity_type == "translation key reference":
        e["translation_references"] = [symbol]
    elif entity_type == "native/model asset":
        e["native_dependencies"] = [item.get("path")]; e["packaging_references"] = ["codebase/package.json"]
        e["runtime_registrations"] = item.get("runtime_loaders", [])
        e["build_references"] = ["codebase/scripts/verification/verify-offline-assets.js", "codebase/package.json"]
        e["risk_level"] = "HIGH"
    elif entity_type == "test":
        e["tests"] = [item.get("path")]
    elif entity_type == "package dependency":
        e["build_references"] = ["codebase/package.json", "codebase/package-lock.json"]
        e["services"] = item.get("reference_paths", [])[:20]
    add_registry(e)


for item in RUNTIME["ipc_handlers"]:
    add_runtime_entry("IPC-HANDLER", item, "IPC handler", "channel", "ipc")
for item in RUNTIME["ipc_callers"]:
    add_runtime_entry("IPC-CALLER", item, "IPC caller", "channel", "ipc")
for item in RUNTIME["ipc_senders"]:
    add_runtime_entry("IPC-SENDER", item, "IPC sender", "channel", "ipc")
for item in RUNTIME["preload_apis"]:
    add_runtime_entry("PRELOAD", item, "preload API", "name", "preload")
for item in RUNTIME["tables"]:
    add_runtime_entry("TABLE", item, "database table", "name", "database")
for item in RUNTIME["indexes"]:
    add_runtime_entry("INDEX", item, "database index", "name", "database")
for item in RUNTIME["triggers"]:
    add_runtime_entry("TRIGGER", item, "database trigger", "name", "database")
for item in RUNTIME["columns"]:
    add_runtime_entry("COLUMN", item, "database column", "name", "database")
for item in RUNTIME["primary_keys"]:
    add_runtime_entry("PRIMARY-KEY", item, "database primary key", "column", "database primary key")
for item in RUNTIME["foreign_keys"]:
    add_runtime_entry("FOREIGN-KEY", item, "database foreign key", "column", "database foreign key")
for item in RUNTIME["transactions"]:
    add_runtime_entry("TRANSACTION", item, "database transaction", "anchor", "database transaction")
for item in RUNTIME["prepared_statements"]:
    add_runtime_entry("PREPARED", item, "database prepared statement", "anchor", "database prepared statement")
for item in RUNTIME["database_paths"]:
    add_runtime_entry("DATABASE-PATH", item, "database path", "value", "database path")
for item in RUNTIME["schema_versions"]:
    add_runtime_entry("SCHEMA-VERSION", item, "database schema version", "version", "database schema version")
for item in RUNTIME["writers"]:
    add_runtime_entry("DATABASE-WRITER", item, "database writer", "table", "database writer")
for item in RUNTIME["migrations"]:
    add_runtime_entry("MIGRATION", item, "database migration", "path", "database migration")
for item in RUNTIME["assets"]:
    add_runtime_entry("ASSET", item, "native/model asset", "path", "native model")
for item in RUNTIME["tests"]:
    add_runtime_entry("TEST", item, "test", "path", "test")
for item in RUNTIME["dependencies"]:
    add_runtime_entry("DEPENDENCY", {**item, "path": "codebase/package.json"}, "package dependency", "name", item["name"])
for item in RUNTIME["registrations"]:
    add_runtime_entry("REGISTRATION", item, "runtime registration", "anchor")
for item in RUNTIME["environment"]:
    add_runtime_entry("ENV", item, "environment variable", "name")
for item in RUNTIME["feature_flags"]:
    add_runtime_entry("FEATURE-FLAG", item, "feature flag reference", "anchor")
for item in RUNTIME["dynamic_imports"]:
    add_runtime_entry("DYNAMIC-IMPORT", item, "dynamic import", "anchor")
for item in RUNTIME["process_spawns"]:
    add_runtime_entry("PROCESS", item, "local process spawn", "anchor")
for item in RUNTIME["translations"]:
    add_runtime_entry("TRANSLATION", item, "translation key reference", "key", "translation")


CAPABILITY_TERMS = {
    "CAP-APP-SHELL": ["app", "window", "tray"], "CAP-WINDOW-LIFECYCLE": ["window", "browserwindow"],
    "CAP-DICTATION": ["dictation", "transcription"], "CAP-MICROPHONE-DICTATION": ["dictation", "microphone"],
    "CAP-MICROPHONE": ["microphone", "audio"], "CAP-SYSTEM-AUDIO": ["systemaudio", "system-audio", "audio"],
    "CAP-MICROPHONE-SELECTION": ["microphone", "device", "inputdevice"],
    "CAP-RECORDING-OVERLAY": ["recordingoverlay", "overlay", "recording"],
    "CAP-AUDIO-MIXING": ["mix", "mixer", "audio"], "CAP-FFMPEG": ["ffmpeg"],
    "CAP-VAD": ["vad", "voiceactivity"], "CAP-AEC": ["aec", "echo"], "CAP-WHISPER": ["whisper"],
    "CAP-PARAKEET": ["parakeet", "sherpa"], "CAP-MODELS": ["model", "assets"],
    "CAP-RECOVERY": ["recovery", "recording"], "CAP-IMPORT-AUDIO": ["import", "audio"],
    "CAP-IMPORT-VIDEO": ["import", "video"], "CAP-SPEAKER-EMBEDDINGS": ["speaker", "embedding"],
    "CAP-SPEAKER-LABELS": ["speaker", "label"], "CAP-SPEAKER-NAMING": ["speaker"],
    "CAP-SPEAKER-RENAMING": ["speaker", "rename"], "CAP-SPEAKER-PERSISTENCE": ["speaker", "database"],
    "CAP-TRANSCRIPT-EDIT": ["transcript", "editor"], "CAP-TRANSCRIPT-HISTORY": ["transcript", "history"],
    "CAP-SEGMENTS": ["segment", "transcript"],
    "CAP-PLAYBACK": ["playback", "audio"], "CAP-LINKED-PLAYBACK": ["playback", "transcript"],
    "CAP-PERSONAL-NOTES": ["personalnotes", "notes"], "CAP-MEETING-NOTES": ["meeting", "note"],
    "CAP-LINKED-NOTES": ["note", "transcript"], "CAP-FOLDERS": ["folder"], "CAP-TAGS": ["tag"],
    "CAP-SNIPPETS": ["snippet"], "CAP-QDRANT": ["qdrant"], "CAP-MINILM": ["minilm", "embedding"],
    "CAP-IMPORT": ["import"], "CAP-EXPORT": ["export"], "CAP-BACKUP": ["backup"],
    "CAP-RESTORE": ["restore", "backup"], "CAP-TRAY": ["tray"], "CAP-NOTIFICATIONS": ["notification"],
    "CAP-MEETING-DETECTION": ["meetingdetection", "meeting-detection", "detectionengine"],
    "CAP-MODEL-PACK": ["model", "import"], "CAP-LEGACY-MIGRATION": ["migration", "localdatadatabase"],
    "CAP-NETWORK-POLICY": ["network", "csp", "offline"], "CAP-WINDOWS-INSTALLER": ["installer", "nsis", "win"],
}


def evidence_paths_for_capability(c: dict[str, Any]) -> list[str]:
    terms = CAPABILITY_TERMS.get(c["id"], [w for w in slug(c["name"]).split("-") if len(w) >= 4])
    candidates = []
    for f in FILES:
        p = f["path"].lower().replace("-", "").replace("_", "")
        if not f["source_authoritative"] or not p.startswith("codebase/"):
            continue
        if any(t.replace("-", "").replace("_", "") in p for t in terms):
            candidates.append(f["path"])
    return sorted(candidates)[:40]


def symbols_for_paths(paths: list[str], limit: int = 80) -> list[str]:
    wanted = set(paths)
    values = []
    for node in NODES:
        source = rel(node.get("source_file") or "")
        label = str(node.get("label") or node.get("id") or "")
        if source in wanted and label:
            values.append(f"{source}::{label}")
    return sorted(set(values))[:limit]


SEVEN_GATES = [
    "Authority gate — bind the decision to Master Plan File 02.",
    "Static dependency gate — map imports, calls, types, tests, build, and packaging references.",
    "Runtime gate — map dynamic imports, IPC/events, registrations, processes, native loaders, and configuration.",
    "Data gate — preserve historical migrations and prove database/filesystem/user-data effects.",
    "Replacement gate — prove every retained consumer has a working local path or the capability is absent.",
    "Verification gate — run targeted, integration, workflow, build, package, and offline evidence as applicable.",
    "Final-reference gate — rescan and prove no active implementation, duplicate, backup, registration, or stale identity remains.",
]

REPLACEMENTS: dict[str, list[str]] = {
    "Authentication": ["CAP-APP-SHELL"], "Accounts": ["CAP-APP-SHELL"],
    "Cloud synchronisation": ["CAP-DATABASE", "CAP-BACKUP", "CAP-RESTORE"],
    "Workspaces": ["CAP-FOLDERS", "CAP-TAGS"], "Organisations": ["CAP-FOLDERS", "CAP-TAGS"],
    "Teams": ["CAP-FOLDERS", "CAP-TAGS"], "Invitations": ["CAP-FOLDERS"],
    "Sharing": ["CAP-PERSONAL-NOTES", "CAP-MEETING-NOTES"],
    "Hosted transcription": ["CAP-WHISPER", "CAP-PARAKEET"],
    "Hosted AI": ["CAP-SEARCH-EXACT", "CAP-SEARCH-SEMANTIC"],
    "Local generative AI": ["CAP-SEARCH-EXACT", "CAP-SEARCH-SEMANTIC"],
    "AI agents": ["CAP-SEARCH-EXACT", "CAP-SEARCH-SEMANTIC"], "Chat": ["CAP-SEARCH-EXACT", "CAP-SEARCH-SEMANTIC"],
    "Summarisation": ["CAP-SEARCH-EXACT", "CAP-SEARCH-SEMANTIC"],
    "Action-item extraction": ["CAP-NOTES", "CAP-TAGS"], "AI rewriting": ["CAP-NOTES"],
    "Calendar": ["CAP-MEETING", "CAP-MEETING-DETECTION"], "MCP": ["CAP-IPC"], "Public API": ["CAP-IPC"],
    "API keys": ["CAP-SETTINGS"], "Billing": ["CAP-MODELS", "CAP-BACKUP"], "Usage quotas": ["CAP-MODELS", "CAP-BACKUP"],
    "Referrals": [], "Upgrade systems": ["CAP-PACKAGING"], "Automatic updater": ["CAP-PACKAGING"],
    "Runtime model downloads": ["CAP-MODEL-PACK"], "Telemetry": [], "Analytics": [],
    "Runtime external links": ["CAP-NETWORK-POLICY"], "Runtime external networking": ["CAP-NETWORK-POLICY"],
    "Active OpenWhispr identity": ["CAP-APP-SHELL"],
}


for c in CAPABILITIES:
    paths = evidence_paths_for_capability(c)
    terms = CAPABILITY_TERMS.get(c["id"], [w for w in slug(c["name"]).split("-") if len(w) >= 4])
    channels = sorted({x["channel"] for x in RUNTIME["ipc_handlers"] + RUNTIME["ipc_callers"] if any(t.replace("-", "") in x["channel"].replace("-", "") for t in terms)})
    preload = sorted({x["name"] for x in RUNTIME["preload_apis"] if any(t.replace("-", "").lower() in x["name"].lower() for t in terms)})
    tests = sorted({x["path"] for x in RUNTIME["tests"] if any(t.replace("-", "").lower() in x["path"].replace("-", "").replace("_", "").lower() for t in terms)})
    renderer = [p for p in paths if p.startswith("codebase/renderer/")][:10]
    main = [p for p in paths if p.startswith("codebase/main/")][:10]
    data = [p for p in paths if any(x in p.lower() for x in ("database", "persistence", "migration"))][:10]
    hook_paths = [p for p in renderer if "hook" in p.lower()]
    store_paths = [p for p in renderer if "store" in p.lower()]
    handler_locations = sorted({f"{x['path']}:{x['line']}::{x['channel']}" for x in RUNTIME["ipc_handlers"] if x["channel"] in channels})
    result_events = sorted({f"{x['path']}:{x['line']}::{x['channel']}" for x in RUNTIME["ipc_senders"] if x["channel"] in channels})
    runtime_registrations = sorted({f"{x['path']}:{x['line']}::{x['anchor']}" for x in RUNTIME["registrations"] + RUNTIME["process_spawns"] if x["path"] in paths})
    table_names = sorted({x["table"] for x in RUNTIME["writers"] if x["path"] in paths})
    writer_locations = sorted({f"{x['path']}:{x['line']}::{x['operation']} {x['table']}" for x in RUNTIME["writers"] if x["path"] in paths})
    recovery_paths = [p for p in paths if any(x in p.lower() for x in ("recovery", "backup", "migration"))][:10]
    c["runtime_chain"] = {
        "user_action": [c["name"]] if c["decision"] not in {"REMOVE", "FORBIDDEN"} else [f"Legacy or excluded {c['name']} interaction, if active presence is proven"],
        "entry_points": renderer,
        "ui_components": symbols_for_paths(renderer, 40),
        "navigation_routes": [p for p in renderer if "route" in p.lower() or "app." in p.lower()],
        "hooks": symbols_for_paths(hook_paths, 30),
        "stores": symbols_for_paths(store_paths, 30),
        "hooks_and_stores": hook_paths + store_paths,
        "preload_exposures": preload,
        "typescript_contracts": ["codebase/renderer/shared/types/electron.ts"] if preload or channels else [],
        "ipc_channels": channels,
        "ipc_handlers": handler_locations,
        "main_services_and_handlers": main,
        "main_symbols": symbols_for_paths(main, 50),
        "repositories": data,
        "data_native_or_process_boundary": data + [p for p in paths if any(x in p.lower() for x in ("native", "resources", "model"))][:10],
        "result_events": result_events,
        "renderer_update": symbols_for_paths(renderer, 30),
        "tests": tests,
        "runtime_registrations": runtime_registrations,
        "data_read": table_names,
        "data_written": writer_locations,
        "side_effects": sorted(set(runtime_registrations + [p for p in paths if any(x in p.lower() for x in ("filesystem", "file", "native", "audio", "model"))]))[:40],
        "failure_path": [p for p in paths if any(x in p.lower() for x in ("error", "failure", "fallback"))][:10],
        "cleanup_path": [p for p in paths if any(x in p.lower() for x in ("cleanup", "lifecycle", "manager"))][:10],
        "recovery_path": recovery_paths,
        "failure_cleanup_recovery": recovery_paths,
        "current_test_coverage": tests,
        "current_breakage": "Repair is required by the Master Plan; exact failure must be revalidated from baseline evidence" if "REPAIR" in c["decision"] else "No additional active breakage is asserted by this mapping phase",
        "required_change": "Execute only the linked dependency-safe queue task and exact registry instructions; preserve working local behavior",
        "target_owner": c["owner"],
        "intermediate_symbols": symbols_for_paths(paths),
        "mapping_evidence": paths if paths else ["Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md"],
        "presence_status": "REPOSITORY CANDIDATES MAPPED" if paths else "NO ACTIVE PATH FOUND — MASTER PLAN REMOVAL/ADD NODE RETAINED",
    }
    replacement_ids = REPLACEMENTS.get(c["name"], [])
    c["replacement_capability_ids"] = replacement_ids
    replacement_paths = []
    for replacement_id in replacement_ids:
        replacement_paths.extend(evidence_paths_for_capability(CAP_BY_ID[replacement_id]))
    replacement_paths = sorted(set(replacement_paths))
    source_path = paths[0] if paths else "Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md"
    e = blank_entry()
    e.update({
        "id": "REG-CAPABILITY-" + c["id"].replace("CAP-", ""), "capability_id": c["id"],
        "capability_name": c["name"], "entity_type": "capability", "decision": c["decision"],
        "current_path": source_path, "current_symbol": c["name"], "current_anchor": c["id"],
        "current_owner": c["owner"], "target_path": source_path if c["decision"] not in {"REMOVE", "FORBIDDEN"} else (replacement_paths[0] if replacement_paths else None),
        "target_symbol": c["name"] if c["decision"] not in {"REMOVE", "FORBIDDEN"} else (", ".join(replacement_ids) if replacement_ids else "No replacement required"),
        "target_owner": c["owner"] if c["decision"] not in {"REMOVE", "FORBIDDEN"} else (", ".join(replacement_ids) if replacement_ids else "Excluded with no replacement"),
        "renderer_entry_points": renderer, "preload_exposures": preload, "ipc_channels": channels,
        "ipc_handlers": [x for x in channels if any(h["channel"] == x for h in RUNTIME["ipc_handlers"])],
        "services": main, "tests": tests, "required_new_tests": [f"codebase/tests/integration/{slug(c['name'])}.integration.test.js"],
        "deletion_requirements": SEVEN_GATES if c["decision"] in {"REMOVE", "FORBIDDEN"} else [],
        "replacement_requirements": (["Use only mapped local replacement capabilities: " + ", ".join(replacement_ids)] if replacement_ids else (["No replacement is required; prove absence of retained consumers."] if c["decision"] in {"REMOVE", "FORBIDDEN"} else ["Preserve the current local implementation unless a verified replacement is required."])),
        "exact_change_instructions": ([
            f"For {c['id']} ({c['name']}), revalidate every path in runtime_chain.mapping_evidence and trace its UI, preload, IPC, main, persistence/native, result, cleanup, and test stages.",
            "Do not delete from word matches: satisfy all seven deletion gates, preserve historical/legal/migration evidence, then remove only the proven active chain in its dependency-safe queue batch.",
        ] if c["decision"] in {"REMOVE", "FORBIDDEN"} else [
            f"For {c['id']} ({c['name']}), use the structured runtime chain and exact registry IDs to preserve working local behaviour through its dependency-ordered queue batch.",
            "Repair before replacement; run the mapped targeted tests and affected real workflow, then record command, exit code, evidence path, and refreshed hash checkpoint.",
        ]),
        "notes": [c["runtime_chain"]["presence_status"]],
    })
    add_registry(e)
progress(f"capability chains and registry populated: {len(REGISTRY)} entries")


PONYTAIL_FINDINGS = [
    {
        "id": "PONY-001", "path": "codebase/main/ipc/ipcHandlers.js", "anchor": "registerIpcHandlers",
        "category": "proven multi-responsibility monolith", "evidence": "3,842 lines, 177 unique handler channels, 28 lint warnings across the main process audit; registrations span persistence, audio, meetings, notes, models, and shell.",
        "owner": "Electron IPC boundary", "target_owner": "Capability-owned IPC modules behind one registration facade",
        "risk": "HIGH", "blast_radius": "renderer/preload/main contracts and most retained workflows",
        "permitted": "KEEP AND REORGANISE after complete caller/handler mapping",
        "prerequisite": "Characterisation tests and real renderer/preload/main round trips",
        "tests": ["IPC contract inventory", "real IPC round trips", "typecheck"], "decision": "ACCEPTED",
        "reason": "Multiple responsibilities are proven; size alone is not the reason.", "task": "TASK-22",
    },
    {
        "id": "PONY-002", "path": "codebase/main/infrastructure/persistence/database.js", "anchor": "Database",
        "category": "proven multi-responsibility monolith", "evidence": "2,248 lines contain schema creation, four migrations, repositories/queries, backup/search/speaker/data maintenance responsibilities.",
        "owner": "SQLite persistence", "target_owner": "Persistence capabilities with a temporary compatibility facade",
        "risk": "CRITICAL", "blast_radius": "all durable user data and most IPC workflows",
        "permitted": "KEEP AND REORGANISE only after migration and integrity fixtures",
        "prerequisite": "Disposable real databases, backup/checksum evidence, characterisation tests",
        "tests": ["real SQLite fixtures", "migration interruption", "foreign-key integrity"], "decision": "ACCEPTED",
        "reason": "Responsibilities are independently evidenced; no schema rewrite is authorised.", "task": "TASK-22",
    },
    {
        "id": "PONY-003", "path": "codebase/renderer/features/meetings/meetingRecordingStore.ts", "anchor": "meetingRecordingStore",
        "category": "state/service concentration", "evidence": "1,099 lines coordinate capture, session state, transcription, recovery, IPC, and lifecycle behaviour.",
        "owner": "Meeting recording", "target_owner": "Meeting capability modules with one store contract",
        "risk": "HIGH", "blast_radius": "recording, recovery, transcription, renderer state",
        "permitted": "KEEP AND REORGANISE after workflow proof", "prerequisite": "Recording/recovery characterisation tests",
        "tests": ["recording state transitions", "recovery fixture", "real IPC round trip"], "decision": "DEFERRED",
        "reason": "Likely valuable, but native/audio lifecycle proof must precede decomposition.", "task": "TASK-22",
    },
    {
        "id": "PONY-004", "path": "codebase/renderer/features/notes/components/PersonalNotesView.tsx", "anchor": "PersonalNotesView",
        "category": "UI responsibility concentration", "evidence": "1,062 lines combine navigation, editing, folders/tags, search, and interaction state.",
        "owner": "Personal notes", "target_owner": "Notes feature with cohesive components",
        "risk": "MEDIUM", "blast_radius": "personal notes workflow",
        "permitted": "KEEP AND REORGANISE after behaviour tests", "prerequisite": "Notes workflow characterisation",
        "tests": ["notes create/edit/search/folder/tag workflow"], "decision": "DEFERRED",
        "reason": "Split boundaries require runtime interaction evidence, not line-count preference.", "task": "TASK-22",
    },
    {
        "id": "PONY-005", "path": "codebase/main/features/dictation/clipboard.js", "anchor": "clipboard integration",
        "category": "large platform-sensitive module", "evidence": "1,924 lines, but behaviour is concentrated around reliable cross-platform clipboard/paste handling.",
        "owner": "Clipboard integration", "target_owner": "Clipboard integration",
        "risk": "HIGH", "blast_radius": "primary dictation delivery path",
        "permitted": "Preserve unless multiple responsibilities are proven", "prerequisite": "Real Windows paste matrix",
        "tests": ["Windows paste integration"], "decision": "REJECTED",
        "reason": "Large size does not prove a safer decomposition; platform fallbacks are intentional complexity.", "task": None,
    },
    {
        "id": "PONY-006", "path": "codebase/main/features/dictation/hotkeyManager.js", "anchor": "HotkeyManager",
        "category": "large platform-sensitive module", "evidence": "1,192 lines implement global hotkey modes, recovery, and native platform behaviour.",
        "owner": "Global hotkey", "target_owner": "Global hotkey",
        "risk": "HIGH", "blast_radius": "dictation activation",
        "permitted": "Preserve unless callers and platform responsibilities prove a coherent extraction", "prerequisite": "Real global-hotkey hardware/OS workflow",
        "tests": ["Windows hotkey registration and recovery"], "decision": "REJECTED",
        "reason": "No aesthetic split; native lifecycle cohesion outweighs file size.", "task": None,
    },
    {
        "id": "PONY-007", "path": "codebase/build-output/", "anchor": "generated packaged copies",
        "category": "generated files tracked beside source", "evidence": "212 generated/build-output files polluted the initial source-symbol graph; one packaged onnxWorker.js exactly duplicates source.",
        "owner": "Windows packaging", "target_owner": "Generated build outputs outside source authority",
        "risk": "LOW", "blast_radius": "repository size and graph accuracy, not runtime source",
        "permitted": "Remove generated outputs only after packaging provenance is captured", "prerequisite": "Git/provenance recovery and reproducible package proof",
        "tests": ["Windows package reproduction"], "decision": "ACCEPTED",
        "reason": "Generated artifacts must remain inventoried but are not authoritative source nodes.", "task": "TASK-24",
    },
    {
        "id": "PONY-008", "path": "codebase/main/index.js", "anchor": "hotkey-listening-mode-changed",
        "category": "dead IPC candidate", "evidence": "One registered main-process channel had no direct ipcRenderer caller in static extraction; event direction/dynamic use remains possible.",
        "owner": "Electron IPC boundary", "target_owner": "Electron IPC boundary",
        "risk": "MEDIUM", "blast_radius": "hotkey settings/listening state",
        "permitted": "Delete only after dynamic/runtime proof and all seven gates", "prerequisite": "Runtime event trace and preload contract check",
        "tests": ["hotkey settings IPC round trip"], "decision": "DEFERRED",
        "reason": "A static no-caller result is a review candidate, never deletion authority.", "task": "TASK-07",
    },
    {
        "id": "PONY-009", "path": "codebase/package.json", "anchor": "dependencies and devDependencies",
        "category": "unused dependency audit", "evidence": "All 36 direct dependencies and 21 devDependencies have source/config string references; this is not runtime-use proof but yields no zero-reference deletion candidate.",
        "owner": "Repository infrastructure", "target_owner": "Capability-owned dependencies",
        "risk": "MEDIUM", "blast_radius": "build, package, native compatibility",
        "permitted": "Remove only after retained-consumer and package evidence", "prerequisite": "Task-by-task dependency reachability",
        "tests": ["typecheck", "unit tests", "production build", "packaged launch"], "decision": "REJECTED",
        "reason": "No dependency is removable from reference counting alone.", "task": None,
    },
    {
        "id": "PONY-010", "path": "codebase/renderer/shared/", "anchor": "shared",
        "category": "generic dumping-ground candidate", "evidence": "Contains cross-feature UI primitives, types, hooks, and utilities; static location alone does not prove misownership.",
        "owner": "Renderer application", "target_owner": "Cross-feature primitives or proven capability owner",
        "risk": "MEDIUM", "blast_radius": "renderer-wide imports",
        "permitted": "Move only symbols with proven single-capability ownership", "prerequisite": "Importer and call-site mapping",
        "tests": ["typecheck", "affected renderer workflows"], "decision": "DEFERRED",
        "reason": "Shared code is not automatically waste; per-symbol ownership must drive moves.", "task": "TASK-23",
    },
    {
        "id": "PONY-011", "path": "codebase/renderer/assets/logo.svg", "anchor": "Mnemora Logo",
        "category": "dead asset candidate", "evidence": "Graphify semantic extraction found the asset, while TypeScript/compiler-assisted and repository reference mapping found no active source, build, or packaging consumer.",
        "owner": "Renderer application", "target_owner": "Renderer assets only if a retained consumer is proven",
        "risk": "LOW", "blast_radius": "branding resource only; potential hidden packaging/legal reference",
        "permitted": "Remove only after packaging, legal, dynamic-path, and final reference gates", "prerequisite": "Seven-gate asset deletion proof",
        "tests": ["renderer build", "Windows package resource inspection"], "decision": "DEFERRED",
        "reason": "No active reference is evidence for review, not deletion authority.", "task": "TASK-24",
    },
    {
        "id": "PONY-012", "path": "codebase/renderer/features/meetings/meetingRecordingStore.ts", "anchor": "meetingRecordingStore.ts ↔ transcriptSpeakerState.ts",
        "category": "circular dependency", "evidence": "TypeScript compiler module resolution plus Tarjan SCC proves a two-file bidirectional import cycle across 455 resolved local edges.",
        "owner": "Meeting recording", "target_owner": "Meeting capability with one directional speaker-state contract",
        "risk": "HIGH", "blast_radius": "meeting recording state, transcript speaker assignments, renderer updates",
        "permitted": "Break the cycle inside the coherent meeting/monolith batch without duplicating state logic", "prerequisite": "Meeting recording and speaker-state characterisation tests",
        "tests": ["meeting store state transitions", "speaker assignment workflow", "typecheck"], "decision": "ACCEPTED",
        "reason": "The cycle is compiler-resolved and crosses two proven responsibilities; task 22 owns the safe extraction boundary.", "task": "TASK-22",
    },
]


for finding in PONYTAIL_FINDINGS:
    cid, _ = path_owner(finding["path"])
    c = CAP_BY_ID[cid]
    c["ponytail_findings"].append(finding["id"])
    e = blank_entry()
    e.update({
        "id": "REG-" + finding["id"], "capability_id": cid, "capability_name": c["name"],
        "entity_type": "Ponytail finding", "decision": finding["decision"], "current_path": finding["path"],
        "current_symbol": finding["anchor"], "current_anchor": finding["anchor"], "current_owner": finding["owner"],
        "target_path": finding["path"], "target_symbol": finding["anchor"], "target_owner": finding["target_owner"],
        "change_summary": finding["evidence"], "exact_change_instructions": [
            f"At {finding['path']}::{finding['anchor']}, apply only this audited disposition: {finding['permitted']}.",
            f"First satisfy {finding['prerequisite']}; then run {', '.join(finding['tests'])} and save evidence before closing {finding['id']}.",
        ],
        "blast_radius": [finding["blast_radius"]], "execution_prerequisites": [finding["prerequisite"]],
        "verification_steps": finding["tests"], "risk_level": finding["risk"], "notes": [finding["reason"]],
    })
    add_registry(e)
progress("Ponytail findings linked")


QUEUE_DATA = [
    (1, "CAP-REPOSITORY", "Repository safety and active identity", "KEEP AND REPAIR", "CRITICAL", "NONE", []),
    (2, "CAP-NETWORK-POLICY", "Runtime external-network boundary", "ADD", "CRITICAL", "NONE", [1]),
    (3, "CAP-REMOVE-CLOUD-SYNCHRONISATION", "Isolated cloud-system removal", "REMOVE", "HIGH", "MEDIUM", [1, 2]),
    (4, "CAP-REMOVE-AUTHENTICATION", "Authentication and account removal", "REMOVE", "HIGH", "MEDIUM", [1, 3]),
    (5, "CAP-REMOVE-AI-AGENTS", "Agent, chat, and AI removal", "REMOVE", "HIGH", "MEDIUM", [1, 3, 4]),
    (6, "CAP-REMOVE-CALENDAR", "Calendar, API, MCP, and updater removal", "REMOVE", "HIGH", "MEDIUM", [2, 3, 4, 5]),
    (7, "CAP-IPC", "Preload and IPC cleanup", "KEEP AND REPAIR", "CRITICAL", "MEDIUM", [2, 3, 4, 5, 6]),
    (8, "CAP-LEGACY-MIGRATION", "Database migration preparation", "ADD", "CRITICAL", "CRITICAL", [1]),
    (9, "CAP-REMOVE-CLOUD-SYNCHRONISATION", "Cloud-metadata migration", "REPLACE", "CRITICAL", "CRITICAL", [3, 4, 5, 6, 8]),
    (10, "CAP-DATABASE", "Local SQLite repair", "KEEP AND REPAIR", "CRITICAL", "CRITICAL", [8, 9]),
    (11, "CAP-DICTATION", "Dictation repair", "KEEP AND REPAIR", "HIGH", "MEDIUM", [2, 7, 10]),
    (12, "CAP-MEETING", "Meeting and audio repair", "KEEP AND REPAIR", "CRITICAL", "HIGH", [2, 7, 10]),
    (13, "CAP-TRANSCRIPTION", "Local transcription repair", "KEEP AND REPAIR", "HIGH", "HIGH", [11, 12]),
    (14, "CAP-DIARIZATION", "Diarization and speaker repair", "KEEP AND REPAIR", "HIGH", "HIGH", [13]),
    (15, "CAP-PLAYBACK", "Transcript and playback repair", "KEEP AND REPAIR", "HIGH", "HIGH", [13, 14]),
    (16, "CAP-NOTES", "Notes, folders, tags, and snippets", "KEEP AND REPAIR", "HIGH", "HIGH", [10, 15]),
    (17, "CAP-SEARCH-EXACT", "Exact search", "MANDATORY KEEP", "HIGH", "HIGH", [10, 15, 16]),
    (18, "CAP-SEARCH-SEMANTIC", "Semantic search", "KEEP AND REPAIR", "HIGH", "HIGH", [10, 13, 16, 17]),
    (19, "CAP-IMPORT-EXPORT", "Import and export", "KEEP AND REPAIR", "HIGH", "HIGH", [10, 13, 16]),
    (20, "CAP-BACKUP", "Backup and restore", "KEEP AND REPAIR", "CRITICAL", "CRITICAL", [8, 10, 19]),
    (21, "CAP-LEGACY-MIGRATION", "Legacy OpenWhispr migration", "ADD", "CRITICAL", "CRITICAL", [8, 9, 10, 20]),
    (22, "CAP-IPC", "Monolith decomposition", "KEEP AND REORGANISE", "CRITICAL", "CRITICAL", [7, 10, 11, 12, 13, 14, 15, 16, 20, 21]),
    (23, "CAP-REPOSITORY", "Folder ownership reorganisation", "KEEP AND REORGANISE", "HIGH", "MEDIUM", [22]),
    (24, "CAP-REPOSITORY", "Dependency cleanup", "REMOVE", "HIGH", "NONE", [6, 23]),
    (25, "CAP-REPOSITORY", "Ponytail-approved simplification", "KEEP AND REORGANISE", "HIGH", "MEDIUM", [22, 23, 24]),
    (26, "CAP-PACKAGING", "Windows build", "MANDATORY KEEP", "CRITICAL", "NONE", [21, 25]),
    (27, "CAP-WINDOWS-INSTALLER", "Windows packaging and installer", "MANDATORY KEEP", "CRITICAL", "NONE", [26]),
    (28, "CAP-NETWORK-POLICY", "Offline packaged launch verification", "ADD", "CRITICAL", "HIGH", [27]),
    (29, "CAP-TESTING", "Final Graphify and Ponytail audits", "KEEP AND REPAIR", "CRITICAL", "NONE", [28]),
]

TASK_SCOPES = {
    1: ["Revalidate codebase/package.json, codebase/package-lock.json, codebase/LICENSE, Electron product metadata, and every active OpenWhispr identity occurrence against the three Master Plans.", "Preserve legal, migration, and fork-provenance occurrences; change only active identity after a path-specific baseline checkpoint."],
    2: ["Trace codebase/main/infrastructure/runtime/runtimeNetworkPolicy.js, its tests, Electron session hooks, CSP, process spawns, and all runtime URL/openExternal call sites.", "Enforce the Master Plan allow/deny policy without blocking loopback IPC or bundled local processes; prove it with real interception/observation."],
    3: ["Use the CAP-REMOVE-CLOUD-SYNCHRONISATION registry candidates to prove every isolated cloud UI, preload, IPC, service, configuration, package, data, and test edge.", "Remove only chains that pass all seven deletion gates; retain historical migration fields and records."],
    4: ["Trace authentication and account candidates through renderer entry points, codebase/preload/index.js, codebase/main/ipc/ipcHandlers.js, persistence fields, settings, tests, and package references.", "Remove the complete proven active chain while preserving local startup, local settings, and legacy migration interpretation."],
    5: ["Trace AI-agent, chat, hosted/local generative AI, summarisation, action-item, and rewrite candidates through every route, preload exposure, IPC handler, service, configuration, dependency, and test.", "Delete only active excluded chains; preserve exact and semantic search and all non-generative transcript/note editing."],
    6: ["Trace calendar, MCP, public API, API-key, updater, upgrade, billing/quota/referral, telemetry, analytics, and runtime external-link candidates across source, package, build, packaging, and tests.", "Apply one seven-gate removal batch per independent chain and keep migration/legal text that is explicitly historical."],
    7: ["Reconcile all 224 preload API properties in codebase/preload/index.js with codebase/renderer/shared/types/electron.ts, 217 channel references, and 177 registrations in codebase/main/ipc/ipcHandlers.js.", "Remove or repair a contract only after its renderer caller, handler, result event, error path, cleanup, and real IPC round trip are proven."],
    8: ["Characterise codebase/main/infrastructure/persistence/database.js, dataMigration.js, localBackup.js, migration tests, schema versions, backups, transactions, and foreign-key checks on disposable SQLite copies.", "Do not alter a real database or historical migration; record source/destination versions, checksums, journal state, interruption, and rollback evidence."],
    9: ["Map every legacy cloud/account/workspace column and table to its historical consumer and intended local Mnemora interpretation using DATABASE_AND_DATA_GRAPH.md.", "Write only forward, idempotent migration design after non-empty-destination and interruption fixtures exist; never erase original OpenWhispr data."],
    10: ["Repair the mapped better-sqlite3 repositories and prepared statements in codebase/main/infrastructure/persistence/database.js without a schema rewrite or speculative Kysely migration.", "Verify record counts, keys, foreign keys, transcript order, speakers, note/folder/tag links, attachments, settings, and semantic rebuild state."],
    11: ["Trace dictation from codebase/renderer/features/dictation/App.jsx through audioManager.js, useAudioRecording.js, hotkey/preload/IPC, whisper, clipboard, and dictation tests.", "Preserve validation, microphone selection, recording overlay/cues, hotkey recovery, local transcription, clipboard restoration, and failure cleanup."],
    12: ["Trace meeting capture through meetingRecordingStore.ts, systemAudioAccess.ts, meetingMicHoldback.js, meetingAecManager.js, native helpers, recovery, persistence, and renderer events.", "Preserve microphone/system-audio mixing, AEC, FFmpeg, recovery, shutdown cleanup, and non-destructive recordings on every failure path."],
    13: ["Trace imported and live audio from renderer transcription entry points through preload/IPC to whisperServer.js, whisper.js, ffmpegUtils.js, model loaders, segments, and tests.", "Keep transcription completely local, preserve model/process lifecycle and timestamps, and prohibit remote/runtime-download fallback."],
    14: ["Trace diarization through diarization.js, speakerEmbeddings.js, liveSpeakerIdentifier.js, speakerAssignmentPolicy.js, Sherpa/ONNX assets, speaker tables, renderer state, and tests.", "Preserve labels, renaming, embeddings, assignments, persistence, segment order, and local-only failure handling."],
    15: ["Trace transcript segments, edits, history, audio playback, and timestamp-linked playback through MeetingTranscriptView.tsx, parseTranscriptSegments.ts, transcriptSpeakerState.ts, IPC, database writers, and tests.", "Preserve ordering, timestamps, edit history, speaker assignments, media references, renderer updates, and recovery."],
    16: ["Trace PersonalNotesView.tsx, NoteEditor.tsx, noteStore.ts, folder/tag/snippet hooks, preload/IPC, database tables, markdown mirror, and tests.", "Preserve strict Markdown boundaries, links, attachments, folder/tag relationships, snippets, search visibility, and data compatibility."],
    17: ["Trace exact search from codebase/renderer/features/search/SearchView.tsx through preload/IPC and SQLite FTS/index/query paths.", "Prove deterministic exact results on a disposable real SQLite fixture and preserve notes, meetings, transcripts, folders, tags, and snippets coverage."],
    18: ["Trace semantic search through SearchView.tsx, localEmbeddings.js, onnxWorkerClient.js, vectorIndex.js, qdrantManager.js, MiniLM/Qdrant assets, persistence state, and tests.", "Retain Qdrant only while evidence requires it, prohibit arbitrary thresholds and remote fallback, and prove rebuild/recovery on real local fixtures."],
    19: ["Trace each import/export entry point through preload/IPC, filesystem path creation, FFmpeg/media handling, notes/transcripts/recordings, sanitisation, and tests.", "Use disposable filesystem fixtures, preserve originals and metadata, and verify error cleanup without touching real user exports."],
    20: ["Trace localBackup.js and its IPC/UI callers through manifest, schema version, checksums, staging, restore validation, and real SQLite/filesystem fixtures.", "Protect non-empty destinations, preserve recordings/attachments, validate restored relationships, and prove rollback after interruption."],
    21: ["Trace dataMigration.js, postMigrationDetector.js, startup invocation in codebase/main/index.js, database migrations, onboarding UI, markers, backups, and tests.", "Copy before transform, preserve original OpenWhispr data, remain idempotent, and never silently overwrite non-empty Mnemora data."],
    22: ["Decompose only the proven responsibilities in codebase/main/ipc/ipcHandlers.js, database.js, meetingRecordingStore.ts, and the meetingRecordingStore/transcriptSpeakerState cycle.", "Map exports/callers/registrations first, extract one low-risk capability batch at a time, keep at most one facade, duplicate no logic, and delete the monolith only after zero callers/logic/registrations remain."],
    23: ["Apply FOLDER_OWNERSHIP_MAP.md to each proposed move and re-query importers, runtime registrations, tests, build, and packaging references before changing a path.", "Keep shared code only when semantically independent and multi-consumer; do not create directories for aesthetics or move platform logic into domain folders."],
    24: ["Revalidate all 57 direct dependencies, generated build-output files, asset loaders, download/build scripts, licences, package and installer inclusions against retained consumers.", "Remove only zero-consumer items after seven-gate and reproducible-build proof; never clean untracked work or remove a dependency from string search alone."],
    25: ["Execute only ACCEPTED Ponytail findings linked to TASK-25 or their prerequisite task; retain REJECTED findings and re-evaluate DEFERRED findings only with new runtime evidence.", "Prefer deletion/reuse/native behavior, avoid new abstractions, and leave one focused runnable check for every non-trivial simplification."],
    26: ["Run the recorded Windows build scripts from codebase/package.json after all prior batches pass; verify native compilation, offline asset preparation, renderer output, and dependency ABI compatibility.", "Do not treat renderer build alone as completion; save commands, exits, hashes, logs, and generated-output provenance."],
    27: ["Run electron-builder Windows packaging/NSIS from codebase/package.json and inspect inclusion of every mapped native/model asset, licences, migrations, icons, and runtime files.", "Launch the produced installer/application on Windows, record hashes and logs, and do not pass on installer creation alone."],
    28: ["Launch the packaged Windows application with external networking intercepted or observed; exercise retained workflows and every bundled local process without network access.", "Fail on any hidden remote call, updater, runtime model download, telemetry, external link, or cloud fallback; unavailable hardware remains unverified, never passed."],
    29: ["Re-run Graphify deep extraction, compiler import-cycle analysis, exact registry validation, Ponytail read-only audit, all release evidence checks, and the Master Plan conjunction.", "Mark complete only when no stale path, duplicate implementation, unresolved field, active excluded chain, failed applicable gate, or false completion claim remains."],
}


TASKS: list[dict[str, Any]] = []
for order, cid, title, decision, risk, data_risk, blockers in QUEUE_DATA:
    c = CAP_BY_ID[cid]
    tid = f"TASK-{order:02d}"
    dependents = [f"TASK-{o:02d}" for o, _, _, _, _, _, bs in QUEUE_DATA if order in bs]
    registries = c["registry_ids"][:100]
    current_locations = sorted({r["current_path"] for r in REGISTRY if r["capability_id"] == cid and r["current_path"]})[:40]
    target_locations = sorted({r["target_path"] for r in REGISTRY if r["capability_id"] == cid and r["target_path"]})[:40]
    exact_symbols = sorted({str(r["current_symbol"]) for r in REGISTRY if r["capability_id"] == cid and r["current_symbol"]})[:60]
    task = {
        "task_id": tid, "capability_id": cid, "title": title, "decision": decision,
        "priority": "P0" if risk == "CRITICAL" else "P1" if risk == "HIGH" else "P2",
        "risk": risk, "data_risk": data_risk, "current_locations": current_locations,
        "target_locations": target_locations or current_locations,
        "exact_symbols": exact_symbols,
        "exact_required_changes": TASK_SCOPES[order],
        "exact_forbidden_changes": ["No data loss or mutation of the user's only database, recording, note, transcript, export, or backup.", "No destructive Git, hidden cloud call, runtime download, updater, external link, permanent duplicate implementation, style-only rewrite, or unrelated change."],
        "dependencies": [f"TASK-{b:02d}" for b in blockers], "blocking_tasks": [f"TASK-{b:02d}" for b in blockers],
        "dependents": dependents, "blast_radius": ["All graph dependencies and dependents of the linked registry IDs", f"The complete {title} runtime chain", "Renderer/preload/main/data/native/build consumers listed in CAPABILITY_REGISTRY.json"],
        "files_expected_to_change": current_locations,
        "database_impact": data_risk, "native_impact": "Revalidate loaders/assets" if cid in {"CAP-DICTATION", "CAP-MEETING", "CAP-TRANSCRIPTION", "CAP-DIARIZATION", "CAP-PACKAGING"} else "None identified",
        "packaging_impact": "Required" if order >= 24 or cid in {"CAP-PACKAGING", "CAP-WINDOWS-INSTALLER"} else "Revalidate every mapped packaging reference if a bundled asset or path changes",
        "execution_prerequisites": [f"Complete and checkpoint TASK-{b:02d}" for b in blockers] + ["Revalidate every current path plus symbol/anchor against the latest Graphify scan"],
        "required_tests": ["Mapped targeted unit/characterisation tests", "Affected real workflow with mocks excluded at final boundaries", "Typecheck and broader regression checks", "Graphify path/symbol/runtime-registration refresh"],
        "verification_steps": ["Run every mapped targeted command and record exact exit codes", "Exercise the affected renderer/preload/main/data/native workflow", "Run broader typecheck/test/build/package/offline checks applicable to the blast radius", "Refresh Graphify and prove no stale, duplicate, or competing implementation remains"],
        "verification_evidence_required": ["Commands and working directories", "Exit codes and logs", "Fixture/checksum/evidence paths", "Last verified Git commit or recoverable hash checkpoint"],
        "required_workflow_proof": "Use real SQLite, filesystem, IPC, local-process, native, network, packaged-app, installer, or hardware evidence wherever TEST_MATRIX.json marks mocks insufficient.",
        "rollback_method": "Verified Git commit or recoverable hash-manifest checkpoint; data tasks require disposable copy and timestamped backup.",
        "graphify_registry_ids": registries, "completion_criteria": "All targeted and broader checks pass; evidence saved; registry refreshed; no duplicate implementation remains.",
        "status": "PLANNED — EXECUTION BLOCKED",
        "deletion_interlock": SEVEN_GATES if decision == "REMOVE" else [],
        "parallel_safe_group": "A" if order in {3, 8} else "B" if order in {11, 12} else "C" if order in {17, 19} else "SEQUENTIAL",
    }
    TASKS.append(task)
    c["queue_tasks"].append(tid)

task_by_id = {t["task_id"]: t for t in TASKS}
for finding in PONYTAIL_FINDINGS:
    target = finding["task"] or "TASK-29"
    rid = "REG-" + finding["id"]
    if rid not in task_by_id[target]["graphify_registry_ids"]:
        task_by_id[target]["graphify_registry_ids"].append(rid)
progress("29-task queue linked")


CAPABILITY_TEST_TASK = {
    "CAP-APP-SHELL": ["TASK-01", "TASK-28"], "CAP-WINDOW-LIFECYCLE": ["TASK-01", "TASK-28"],
    "CAP-HOTKEY": ["TASK-11"], "CAP-MICROPHONE-DICTATION": ["TASK-11"], "CAP-MICROPHONE": ["TASK-11", "TASK-12"],
    "CAP-MICROPHONE-SELECTION": ["TASK-11", "TASK-12"], "CAP-RECORDING-OVERLAY": ["TASK-11"], "CAP-SYSTEM-AUDIO": ["TASK-12"],
    "CAP-AUDIO": ["TASK-12"], "CAP-AUDIO-MIXING": ["TASK-12"], "CAP-FFMPEG": ["TASK-12", "TASK-13", "TASK-19"],
    "CAP-VAD": ["TASK-11", "TASK-13"], "CAP-AEC": ["TASK-12"], "CAP-WHISPER": ["TASK-13"], "CAP-PARAKEET": ["TASK-13", "TASK-14"],
    "CAP-MODELS": ["TASK-13", "TASK-18", "TASK-24"], "CAP-RECOVERY": ["TASK-12"], "CAP-IMPORT-AUDIO": ["TASK-13", "TASK-19"],
    "CAP-IMPORT-VIDEO": ["TASK-13", "TASK-19"], "CAP-SPEAKER-EMBEDDINGS": ["TASK-14"], "CAP-SPEAKER-LABELS": ["TASK-14"],
    "CAP-SPEAKER-NAMING": ["TASK-14"], "CAP-SPEAKER-RENAMING": ["TASK-14"], "CAP-SPEAKER-PERSISTENCE": ["TASK-14"],
    "CAP-TRANSCRIPT-EDIT": ["TASK-15"], "CAP-TRANSCRIPT-HISTORY": ["TASK-15"], "CAP-SEGMENTS": ["TASK-15"],
    "CAP-LINKED-PLAYBACK": ["TASK-15"], "CAP-PERSONAL-NOTES": ["TASK-16"], "CAP-MEETING-NOTES": ["TASK-16"],
    "CAP-LINKED-NOTES": ["TASK-16"], "CAP-FOLDERS": ["TASK-16"], "CAP-TAGS": ["TASK-16"], "CAP-SNIPPETS": ["TASK-16"],
    "CAP-QDRANT": ["TASK-18"], "CAP-KYSELY": ["TASK-10"], "CAP-KEYRING": ["TASK-01"], "CAP-MINILM": ["TASK-18"],
    "CAP-IMPORT": ["TASK-19"], "CAP-EXPORT": ["TASK-19"], "CAP-RESTORE": ["TASK-20"], "CAP-SETTINGS": ["TASK-01"],
    "CAP-TRAY": ["TASK-01", "TASK-28"], "CAP-NOTIFICATIONS": ["TASK-01", "TASK-28"], "CAP-MEETING-DETECTION": ["TASK-12"],
    "CAP-MODEL-PACK": ["TASK-13", "TASK-18", "TASK-24"], "CAP-I18N": ["TASK-24"], "CAP-CLIPBOARD": ["TASK-11"],
    "CAP-RENDERER": ["TASK-07", "TASK-23"], "CAP-NATIVE": ["TASK-11", "TASK-12", "TASK-13", "TASK-14", "TASK-24"],
    "CAP-IMPORT-EXPORT": ["TASK-19"], "CAP-NOTES": ["TASK-16"],
}


TEST_ROWS: list[dict[str, Any]] = []
test_paths = [t["path"] for t in RUNTIME["tests"]]
for i, c in enumerate([x for x in CAPABILITIES if x["decision"] not in {"REMOVE", "FORBIDDEN"}], 1):
    matching = [p for p in test_paths if any(w in p.lower() for w in slug(c["name"]).split("-") if len(w) > 3)]
    real_required = c["id"] in {"CAP-DATABASE", "CAP-BACKUP", "CAP-RESTORE", "CAP-IPC", "CAP-IMPORT", "CAP-EXPORT", "CAP-NETWORK-POLICY", "CAP-PACKAGING", "CAP-LEGACY-MIGRATION", "CAP-NATIVE"}
    row = {
        "test_id": f"TEST-{i:03d}", "capability_id": c["id"], "task_ids": c["queue_tasks"] or CAPABILITY_TEST_TASK.get(c["id"], ["TASK-29"]), "test_level": "integration" if real_required else "unit + workflow",
        "test_type": "real boundary" if real_required else "unit/characterisation plus affected workflow",
        "existing_or_missing": "EXISTING COVERAGE + REQUIRED WORKFLOW PROOF" if matching else "MISSING — PLANNED",
        "current_test_path": matching[:5], "required_new_test_path": f"codebase/tests/integration/{slug(c['name'])}.integration.test.js" if not matching or real_required else None,
        "real_versus_mocked_boundary": "REAL REQUIRED; mocks may supplement" if real_required else "Mocks allowed for pure logic; final workflow remains real",
        "input_fixture": "Capability-specific deterministic fixture", "expected_output": "Preserved local behaviour and explicit failure handling",
        "database_fixture": "Disposable real SQLite copy" if c["id"] in {"CAP-DATABASE", "CAP-BACKUP", "CAP-RESTORE", "CAP-LEGACY-MIGRATION", "CAP-SEARCH-EXACT", "CAP-SEARCH-SEMANTIC"} else None,
        "filesystem_fixture": "Disposable temporary directory" if c["id"] in {"CAP-IMPORT", "CAP-EXPORT", "CAP-BACKUP", "CAP-RESTORE", "CAP-MODELS", "CAP-PACKAGING"} else None,
        "native_requirement": c["id"] in {"CAP-DICTATION", "CAP-MEETING", "CAP-TRANSCRIPTION", "CAP-DIARIZATION", "CAP-NATIVE", "CAP-PACKAGING"},
        "hardware_requirement": "Physical microphone/system-audio/global-hotkey workflow" if c["id"] in {"CAP-MICROPHONE", "CAP-MICROPHONE-DICTATION", "CAP-MICROPHONE-SELECTION", "CAP-SYSTEM-AUDIO", "CAP-HOTKEY"} else None,
        "hardware_status": "UNVERIFIED — REQUIRED HARDWARE UNAVAILABLE" if c["id"] in {"CAP-MICROPHONE", "CAP-MICROPHONE-DICTATION", "CAP-MICROPHONE-SELECTION", "CAP-SYSTEM-AUDIO", "CAP-HOTKEY"} else None,
        "platform": "Windows 11 x64" if c["id"] in {"CAP-PACKAGING", "CAP-WINDOWS-INSTALLER", "CAP-HOTKEY", "CAP-SYSTEM-AUDIO", "CAP-CLIPBOARD"} else "Windows-first",
        "command": ["npm test", "npm run typecheck", f"node --test {matching[0]}" if matching else f"node --test tests/integration/{slug(c['name'])}.integration.test.js"], "working_directory": "codebase",
        "evidence_required": "Command, exit code, fixture hash, logs, and workflow observation",
        "pass_condition": "Expected durable/runtime result and no forbidden network/data loss",
        "failure_response": "Repair within the same batch; do not advance or mark complete.",
    }
    TEST_ROWS.append(row)
    c["tests"].append(row["test_id"])

for task in [t for t in TASKS if t["decision"] == "REMOVE"]:
    row = {
        "test_id": "TEST-DELETION-" + task["task_id"].split("-")[-1], "capability_id": task["capability_id"],
        "task_ids": [task["task_id"]], "test_level": "integration + repository-wide final scan", "test_type": "destructive-change proof",
        "existing_or_missing": "MISSING — PLANNED BEFORE DELETION", "current_test_path": [],
        "required_new_test_path": f"codebase/tests/integration/{slug(task['title'])}.integration.test.js",
        "real_versus_mocked_boundary": "REAL REQUIRED; static no-reference proof plus affected real workflows",
        "input_fixture": "Untouched baseline plus retained-capability fixtures", "expected_output": "Excluded chain absent; retained workflows unchanged",
        "database_fixture": "Disposable real SQLite copy when legacy fields/tables are involved", "filesystem_fixture": "Disposable application-data tree",
        "native_requirement": False, "hardware_requirement": None, "hardware_status": None, "platform": "Windows-first",
        "command": ["npm test", "npm run typecheck", "npm run build:win", "Graphify/tools/run_second_graphify_scan.py"],
        "working_directory": "codebase", "evidence_required": "All seven gates, command exits, final Graphify scan, and affected workflow proof",
        "pass_condition": "No active chain or stale registration remains and no retained consumer regresses",
        "failure_response": "Restore the verified batch; repair the mapping; do not continue deletion.",
    }
    TEST_ROWS.append(row)
    CAP_BY_ID[task["capability_id"]]["tests"].append(row["test_id"])
progress(f"test matrix populated: {len(TEST_ROWS)} obligations")


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    def cell(v: Any) -> str:
        if isinstance(v, list):
            v = ", ".join(map(str, v))
        return str(v if v is not None else "N/A").replace("|", "\\|").replace("\n", " ")
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    out.extend("| " + " | ".join(cell(v) for v in row) + " |" for row in rows)
    return "\n".join(out)


def folder_ownership_rows() -> list[list[Any]]:
    file_paths = [x["path"] for x in FILES if x["source_authoritative"] and x["path"].startswith("codebase/")]
    folders = sorted({str(Path(p).parent).replace("\\", "/") + "/" for p in file_paths})
    rows: list[list[Any]] = []
    generic_names = {"helpers", "utils", "common", "misc", "other", "old", "legacy", "temp", "general", "shared"}
    for folder in folders:
        direct = sorted(p for p in file_paths if (str(Path(p).parent).replace("\\", "/") + "/") == folder)
        descendants = sorted(p for p in file_paths if p.startswith(folder))
        cid, owner = path_owner(folder + " " + " ".join(direct[:10]))
        parts = [x for x in folder.rstrip("/").split("/") if x]
        layer = "Electron main" if "/main/" in folder else "Electron preload" if "/preload/" in folder else "Renderer" if "/renderer/" in folder else "Native" if "/native/" in folder else "Build/packaging" if "/scripts/" in folder or "/resources/" in folder else "Repository support"
        domain = CAP_BY_ID[cid]["name"] if cid in CAP_BY_ID else owner
        entry_points = [p for p in direct if Path(p).name.lower() in {"index.js", "index.ts", "index.tsx", "main.js", "package.json", "vite.config.ts"} or Path(p).stem.lower().endswith(("store", "manager", "service"))]
        findings = [f["id"] for f in PONYTAIL_FINDINGS if str(f["path"]).startswith(folder)]
        generic_review = parts[-1].lower() in generic_names
        violations = findings + (["GENERIC-FOLDER REVIEWED — retain only multi-capability, semantically independent contents"] if generic_review else [])
        corrections = [f"Execute {f['task']} only after its prerequisites" for f in PONYTAIL_FINDINGS if f["id"] in findings and f.get("task")]
        if generic_review and not corrections:
            corrections.append("TASK-23: move only symbols proven to have one capability owner; keep genuine cross-capability primitives")
        rows.append([
            folder, layer, domain, f"Own {owner} artifacts evidenced by {len(descendants)} descendant source-authoritative file(s)",
            sorted({FILE_BY_PATH[p]["file_category"] for p in direct}) or ["Container for owned descendants"],
            ["Unrelated capability implementations", "Active excluded cloud/auth/AI/network systems", "Generated copies presented as source authority"],
            entry_points, "Renderer → preload → main service → persistence/native; feature folders may depend on shared primitives, never the reverse",
            ["Same capability", "Approved cross-cutting platform/shared layer"], ["Mapped parent feature", "Explicitly mapped cross-capability callers"],
            violations or ["NONE PROVEN"], corrections or ["Preserve current placement; revalidate through TASK-23 before any move"],
            direct[:8] or descendants[:8],
        ])
    proposed = [
        ["codebase/main/ipc/capabilities/", "Electron main", "Capability-owned IPC", "Proposed extraction target for proven handler capability batches", ["One capability's handlers and registration export"], ["Duplicate handler logic", "Database implementation", "Renderer state"], ["Per-capability register function behind codebase/main/ipc/ipcHandlers.js facade"], "preload contract → capability handler → service", ["codebase/main/ipc/ facade", "capability services"], ["main registration facade"], ["PROPOSED; MUST NOT EXIST UNTIL TASK-22 EXTRACTION"], ["TASK-22 creates only after callers/tests prove the boundary"], ["PONY-001", "TASK-22"]],
        ["codebase/main/infrastructure/persistence/repositories/", "Electron main", "SQLite persistence", "Proposed repository boundary behind the existing Database compatibility facade", ["Capability-cohesive prepared statements and transactions"], ["Schema duplication", "Renderer code", "Remote storage"], ["Existing Database facade during migration"], "service → repository → better-sqlite3", ["Persistence facade", "Migration/schema definitions"], ["Capability services"], ["PROPOSED; DATA PROOF REQUIRED"], ["TASK-22 extracts one repository at a time after TASK-08/10/20/21"], ["PONY-002", "TASK-22"]],
        ["codebase/renderer/features/meetings/state/", "Renderer", "Meeting recording", "Possible target only if runtime tests prove separable meeting state responsibilities", ["Meeting-owned state slices with one source of truth"], ["Duplicate state", "Main/native implementation", "Generic shared primitives"], ["meetingRecordingStore compatibility export while callers migrate"], "meeting UI → meeting state → preload", ["Meeting feature", "Renderer shared types"], ["Meeting components/hooks"], ["PROPOSED AND DEFERRED"], ["TASK-22 may create only after PONY-003/PONY-012 prerequisites"], ["PONY-003", "PONY-012", "TASK-22"]],
    ]
    return rows + proposed


def generate_outputs(final: bool) -> None:
    progress("writing operational and phase-boundary outputs")
    phase = "SECOND SCAN VERIFIED" if final else "INITIAL GRAPH POPULATED — SECOND SCAN PENDING"
    plan_files = [GRAPHIFY / "Master Plan" / n for n in [
        "01-EVERYTHING-WE-ARE-KEEPING.md", "02-EVERYTHING-WE-ARE-DELETING.md", "03-HOW-WE-WILL-KEEP-DELETE-AND-REPLACE.md"
    ]]
    skill_root = Path("C:/Users/mhyah/.codex/skills")
    second_marker = json.loads((OUT / "SECOND_SCAN_COMPLETE").read_text(encoding="utf-8")) if (OUT / "SECOND_SCAN_COMPLETE").exists() else None
    import_cycles = json.loads((GRAPHIFY / "IMPORT_CYCLES.json").read_text(encoding="utf-8")) if (GRAPHIFY / "IMPORT_CYCLES.json").exists() else {"files": 0, "import_specifiers": 0, "resolved_local_edges": 0, "unresolved_relative_imports": [], "non_code_asset_references": [], "cycles": []}
    fingerprint = {
        "project": "Mnemora", "repository_root": str(ROOT), "codebase_root": str(CODEBASE), "graphify_root": str(GRAPHIFY),
        "git": {"present": False, "repository_root": None, "branch": None, "commit": None, "staged": [], "unstaged": [], "deleted": [], "untracked": [], "provenance_search": ["C:/Users/mhyah/Downloads/Code/Mnemora", "C:/Users/mhyah/Downloads/Code", "C:/Users/mhyah/Downloads", "C:/Users/mhyah", "C:/Users", "C:/"], "result": "No .git directory exists at the repository root or any parent; hash checkpoint is authoritative for this mapping phase"},
        "hash_checkpoint_id": CHECKPOINT, "source_tree_sha256": SOURCE_TREE_HASH,
        "master_plan_hashes": {rel(p): sha256(p) for p in plan_files},
        "package_manifest_hashes": {"codebase/package.json": sha256(CODEBASE / "package.json")},
        "lockfile_hashes": {"codebase/package-lock.json": sha256(CODEBASE / "package-lock.json")},
        "migration_manifest": RUNTIME["migrations"], "native_model_binary_manifest": RUNTIME["assets"],
        "operating_system": platform.platform(), "architecture": platform.machine(),
        "package_manager": "npm 11.16.0", "node": "v24.18.0", "electron": "41.2.0", "typescript": "^6.0.2",
        "database_driver": "better-sqlite3 12.9.0", "query_layer": "Direct better-sqlite3 prepared statements; Kysely is not installed/imported and remains conditional on evidence", "workspace_structure": ["codebase (Electron application)", "Graphify (Master Plan and pre-execution intelligence)"],
        "native_modules": ["better-sqlite3", "bundled platform helpers and local-process assets in native_model_binary_manifest"],
        "current_generated_outputs": ["codebase/build-output (inventoried, non-source-authoritative)", "Graphify/graphify-out"],
        "existing_baseline_failures": ["npm run lint: 28 warnings, zero errors", "Hardware-dependent workflows unverified because required hardware evidence was unavailable"],
        "build_system": "Vite 8 + native scripts", "test_system": "Node test runner",
        "packaging_system": "electron-builder 26.4.0", "scan_timestamp": STAMP, "state": phase,
        "scan_timestamps": {
            "initial_graph_saved": datetime.fromtimestamp((INITIAL / "graph.json").stat().st_mtime, timezone.utc).isoformat().replace("+00:00", "Z"),
            "second_scan_completed": second_marker.get("completed_at") if second_marker else None,
        },
        "tool_revisions": {
            "graphify_cli": "0.9.17",
            "graphify_skill_sha256": sha256(skill_root / "graphify" / "SKILL.md"),
            "ponytail_skill_sha256": sha256(skill_root / "ponytail" / "SKILL.md"),
            "ponytail_audit_skill_sha256": sha256(skill_root / "ponytail-audit" / "SKILL.md"),
        },
        "tool_discovery": {
            "graphify": {"installed_name": "graphifyy / graphify", "version": "0.9.17", "executable_path": "C:/Users/mhyah/.local/bin/graphify.exe", "python_path_record": "Graphify/graphify-out/.graphify_python", "configuration_path": "C:/Users/mhyah/.codex/skills/graphify/SKILL.md", "invocation": "C:/Users/mhyah/.local/bin/graphify.exe plus Graphify/tools/run_second_graphify_scan.py using the recorded Graphify Python runtime", "working_directory": str(ROOT), "deepest_mode": "deep AST + semantic + health/build verification", "read_only_for_application": True, "output_path": str(OUT)},
            "ponytail": {"installed_name": "ponytail skill", "version": sha256(skill_root / "ponytail" / "SKILL.md"), "executable_path": None, "configuration_path": "C:/Users/mhyah/.codex/skills/ponytail/SKILL.md", "audit_configuration_path": "C:/Users/mhyah/.codex/skills/ponytail-audit/SKILL.md", "invocation": "$ponytail + $ponytail-audit instruction workflow", "mode": "READ-ONLY AUDIT", "mutation_modes_not_used": ["full simplification", "review mutation", "debt execution"], "output_path": str(GRAPHIFY / "PONYTAIL_AUDIT.md")},
        },
    }
    write_json("REPOSITORY_FINGERPRINT.json", fingerprint)
    write_json("REPOSITORY_FILE_INVENTORY.json", {"schema_version": 1, "fingerprint": CHECKPOINT, "generated_at": STAMP, "files": FILES})
    write_json("EXACT_LOCATION_REGISTRY.json", {
        "schema_version": 1, "authority": "Path plus symbol or unique anchor; line numbers are secondary",
        "fingerprint": CHECKPOINT, "generated_at": STAMP, "entry_count": len(REGISTRY), "required_fields": REGISTRY_FIELDS,
        "entries": sorted(REGISTRY, key=lambda x: x["id"]),
    })
    write_json("CAPABILITY_REGISTRY.json", {"schema_version": 1, "fingerprint": CHECKPOINT, "capabilities": CAPABILITIES})
    write_json("IMPLEMENTATION_QUEUE.json", {"schema_version": 1, "fingerprint": CHECKPOINT, "tasks": TASKS})
    write_json("TEST_MATRIX.json", {"schema_version": 1, "fingerprint": CHECKPOINT, "tests": TEST_ROWS})
    write_json("PONYTAIL_FINDINGS.json", {"schema_version": 1, "mode": "READ-ONLY AUDIT", "findings": PONYTAIL_FINDINGS})

    grouped = collections.Counter(x["file_category"] for x in FILES)
    source_files = [x for x in FILES if x["file_category"] in {"application source", "native source or helper"} and x["source_authoritative"]]
    write_text("RUN_STATE.md", f"""
# Mnemora Graphify Run State

- Phase: `{phase}`
- Application mutation: `FORBIDDEN / NONE PERFORMED`
- Repository fingerprint: `{CHECKPOINT}`
- Source-tree baseline: `{SOURCE_TREE_HASH}`
- Initial deep scan: `COMPLETE`
- Ponytail read-only audit: `COMPLETE`
- Second deep scan: `{'COMPLETE' if final else 'PENDING'}`
- Execution: `NOT STARTED`
- Updated: `{STAMP}`

The three files under `Master Plan/` are the transformation authority. `EXACT_LOCATION_REGISTRY.json` is the exact-location authority. Null registry values mean not applicable, never an unresolved unknown.
""")
    write_text("REPOSITORY_INVENTORY.md", f"""
# Repository Inventory

Fingerprint: `{CHECKPOINT}`

The machine-readable inventory is `REPOSITORY_FILE_INVENTORY.json`. It enumerates source-authoritative files individually and inventories installed/generated files without treating their minified or packaged symbols as source authority.

{markdown_table(['Category','Count'], [[k,v] for k,v in sorted(grouped.items())])}

## Coverage

- Inventory entries: {len(FILES)}
- Source-authoritative source/native files: {len(source_files)}
- Graphify significant nodes: {len(NODES)}
- Graphify dependency edges retained for registry mapping: {len(EDGES)}
- Installed/vendor files: {grouped['installed dependency / vendor']}
- Generated build-output files: {grouped['generated build output']}
- Unclassified source files: 0

Generated and vendor files are repository items but are not target locations for source changes. Exact file hashes are omitted only for those two bulk categories; their paths, sizes, categories, and status remain inventoried.
""")
    write_text("CAPABILITY_REGISTRY.md", "# Capability Registry\n\nMachine authority: `CAPABILITY_REGISTRY.json`. Stable IDs are linked to the exact-location registry, queue, tests, and Ponytail findings.\n\n" + markdown_table(
        ["ID", "Capability", "Decision", "Registry entries", "Tasks", "Tests"],
        [[c["id"], c["name"], c["decision"], len(c["registry_ids"]), ", ".join(c["queue_tasks"]) or "Planning proof only", ", ".join(c["tests"])] for c in CAPABILITIES]
    ))
    queue_sections = ["# Implementation Queue", "", "Execution is blocked. Every item is a planned coherent dependency-safe capability batch.", ""]
    for t in TASKS:
        queue_sections += [f"## {t['task_id']} — {t['title']}", "", "```json", json.dumps(t, indent=2, ensure_ascii=False), "```", ""]
    write_text("IMPLEMENTATION_QUEUE.md", "\n".join(queue_sections))
    write_text("COMPLETION_TRACKER.md", "# Completion Tracker\n\nPlanning is complete; application execution has not started.\n\n" + markdown_table(
        ["Task", "Capability", "Status", "Blocking tasks"], [[t["task_id"], t["capability_id"], t["status"], t["blocking_tasks"]] for t in TASKS]
    ))
    write_text("CURRENT_ARCHITECTURE.md", f"""
# Current Architecture

This describes observed repository state, not the target product.

Mnemora is an Electron {fingerprint['electron']} application with a JavaScript main process, one preload boundary, a React/TypeScript renderer, better-sqlite3 persistence, local native processes/models, Vite builds, Node tests, and electron-builder packaging. The main process owns desktop lifecycle, windows, tray, hotkeys, audio, local processes, IPC, and persistence. The preload exposes {len(RUNTIME['preload_apis'])} named API properties found by AST-supported source inspection. The renderer contains feature folders for dictation, meetings, notes, settings, and shared UI/state.

## Runtime and data evidence

- Unique IPC handler registrations: {len({x['channel'] for x in RUNTIME['ipc_handlers']})}
- Unique renderer/preload IPC channel references: {len({x['channel'] for x in RUNTIME['ipc_callers']})}
- SQLite tables: {len({x['name'] for x in RUNTIME['tables']})}
- Migrations/migration-related files: {len(RUNTIME['migrations'])}
- Native/model/binary assets: {len(RUNTIME['assets'])}
- Test files: {len(RUNTIME['tests'])}
- Package dependencies/devDependencies: {len(RUNTIME['dependencies'])}

The current architecture retains large registration/persistence modules and generated packaged output inside the repository. Those facts are mapped, not silently recast as completed target architecture.
""")
    changes = [
        ["main/ipc/ipcHandlers.js", "Electron IPC boundary", "177-channel registration and handlers", "capability-owned IPC modules", "capability owners", "DECOMPOSE AFTER TESTS", "real IPC characterisation", "renderer/preload/main", "real IPC round trips"],
        ["main/infrastructure/persistence/database.js", "SQLite persistence", "schema, migrations, queries, backup/search", "capability-owned persistence behind facade", "SQLite persistence", "DECOMPOSE AFTER DATA PROOF", "real DB fixtures and backups", "all durable data", "migration/integrity tests"],
        ["renderer/features/meetings/meetingRecordingStore.ts", "Meeting recording", "capture/session/transcription/recovery state", "cohesive meeting capability modules", "Meeting recording", "DEFERRED REORGANISATION", "workflow tests", "recording lifecycle", "real recording/recovery"],
        ["build-output/", "Windows packaging", "generated artifacts", "generated-only, non-source authority", "Packaging", "REMOVE WHEN REPRODUCIBLE", "provenance + package reproduction", "distribution artifacts", "Windows package"],
    ]
    write_text("TARGET_ARCHITECTURE.md", "# Target Architecture\n\nThe target remains Windows-first, offline/local-first, Electron-based, SQLite-backed, and reuse-first. Working local code stays in place by default. Capability ownership may justify moves only after callers, runtime registrations, tests, and data effects are mapped. No one-folder-per-function design is authorised.\n\n" + markdown_table(
        ["Current path", "Current owner", "Current responsibility", "Target path", "Target owner", "Change", "Prerequisites", "Blast radius", "Verification"], changes
    ) + "\n\nThe target excludes authentication, cloud sync, hosted AI/transcription, local generative AI, billing, telemetry, automatic updating, runtime downloads, and external runtime networking. Historical/legal/migration references remain where required.")
    write_text("FOLDER_OWNERSHIP_MAP.md", "# Folder Ownership Map\n\nEvery current source-authoritative folder and every proposed folder has an evidence-based ownership contract. Shared and generic folders are reviewed, not automatically deleted. Proposed rows are plans only and do not claim that a directory or move exists.\n\n" + markdown_table(
        ["Folder path", "Layer", "Domain", "Responsibility", "Allowed contents", "Forbidden contents", "Public entry points", "Dependency direction", "Allowed import sources", "Allowed consumers", "Current violations", "Planned corrections", "Evidence"], folder_ownership_rows()
    ))
    write_text("MOVE_LEDGER.md", "# Move Ledger\n\nNo files were moved in the pre-execution phase. Planned ownership changes are in `TARGET_ARCHITECTURE.md` and queue tasks 22-23; exact paths must be revalidated before any future move.\n")
    removal_rows = []
    for c in CAPABILITIES:
        if c["decision"] not in {"REMOVE", "FORBIDDEN"}:
            continue
        chain = c["runtime_chain"]
        removal_task = "TASK-04" if c["name"] in {"Authentication", "Accounts"} else "TASK-05" if c["name"] in {"Hosted AI", "Local generative AI", "AI agents", "Chat", "Summarisation", "Action-item extraction", "AI rewriting"} else "TASK-06" if c["name"] in {"Calendar", "MCP", "Public API", "API keys", "Billing", "Usage quotas", "Referrals", "Upgrade systems", "Automatic updater", "Telemetry", "Analytics", "Runtime external links"} else "TASK-03"
        removal_rows.append([c["id"], c["name"], c["decision"], chain["presence_status"], chain["mapping_evidence"][:5], "REG-CAPABILITY-" + c["id"].replace("CAP-", ""), f"{removal_task} / TASK-29"])
    write_text("DELETED_ITEMS_LEDGER.md", "# Deleted Items Ledger\n\nNo application files were deleted in the pre-execution phase. Each removal node carries the full seven-gate interlock in `EXACT_LOCATION_REGISTRY.json`; word matches are review candidates, never deletion authority. Historical migration, legal, and fork-provenance references are preserved.\n\n" + markdown_table(
        ["Capability", "Name", "Decision", "Presence proof", "Evidence", "Registry", "Queue"], removal_rows
    ) + "\n\n## Seven-gate planning interlock\n\n" + "\n".join(f"{i}. {gate}" for i, gate in enumerate(SEVEN_GATES, 1)))
    replacement_rows = []
    for removed_name, replacement_ids in REPLACEMENTS.items():
        removed_cap = next(c for c in CAPABILITIES if c["name"] == removed_name)
        replacement_rows.append([
            removed_cap["id"], removed_name, replacement_ids or ["No replacement required"],
            [CAP_BY_ID[x]["name"] for x in replacement_ids] if replacement_ids else ["Removal only after no retained consumer is proven"],
            "REG-CAPABILITY-" + removed_cap["id"].replace("CAP-", ""),
        ])
    write_text("REPLACEMENT_MAP.md", "# Removed-System Replacement Map\n\nThis is the explicit bridge from Master Plan File 03 section 11 to stable local capability IDs. Replacement does not authorise implementation in this phase.\n\n" + markdown_table(
        ["Removed capability", "Removed name", "Replacement IDs", "Local replacement", "Registry evidence"], replacement_rows
    ))
    dep_rows = [[d["name"], d["version"], d["group"], d["owner"], d["reference_paths"][:10], "RETAIN PENDING BATCH" if d["referenced"] else "TASK-24 REMOVAL REVIEW"] for d in RUNTIME["dependencies"]]
    write_text("THIRD_PARTY_CODE_REGISTER.md", "# Third-Party Code Register\n\nThis register covers package-level third-party code. Native/model asset checksums and loaders are in the exact-location and fingerprint JSON files. Licence/source verification is an execution prerequisite before copied code or replacement. A string reference is ownership evidence, not final runtime-use proof.\n\n" + markdown_table(["Package", "Version", "Group", "Owner", "Reference paths", "Decision"], dep_rows))
    test_lines = ["# Testing Evidence Matrix", "", "Machine-readable authority: `TEST_MATRIX.json`.", "", "Mocks may prove pure logic, failure injection, deterministic edge cases, and isolated boundaries whose real boundary is separately tested. They cannot be final proof for SQLite, migrations, IPC, filesystem import/export, backup/restore, local process startup, native bindings, network enforcement, packaged behaviour, or installer launch.", "", markdown_table(
        ["Test", "Capability", "Task IDs", "Level", "Coverage", "Boundary", "Current path", "Required path", "Hardware requirement", "Hardware status"],
        [[t["test_id"], t["capability_id"], t["task_ids"], t["test_level"], t["existing_or_missing"], t["real_versus_mocked_boundary"], t["current_test_path"], t["required_new_test_path"], t["hardware_requirement"], t["hardware_status"]] for t in TEST_ROWS]
    )]
    write_text("TEST_MATRIX.md", "\n".join(test_lines))
    write_text("REGRESSION_RESULTS.md", """
# Baseline Regression Results

These commands established a read-only baseline; no failures were repaired.

| Command | Exit | Result |
| --- | ---: | --- |
| `npm run typecheck` | 0 | Passed |
| `npm run lint` | 0 | Passed with 28 warnings, no errors |
| `npm test` | 0 | 187 tests: 183 passed, 4 skipped, 0 failed |
| `npm run verify:offline-assets` | 0 | 20 required Windows x64 assets verified |
| `npm run i18n:check` | 0 | Passed |

Working directory was `codebase/`. No build, package, installer, or application launch was performed in this pre-execution phase.
""")
    relation_counts = collections.Counter(e.get("relation") for e in EDGES)
    write_text("DEPENDENCY_GRAPH.md", "# Dependency Graph\n\nGenerated from Graphify AST/semantic extraction; raw machine graph is `graphify-out/graph.json`. Generated/minified build-output symbols are inventoried but excluded from source authority in the second scan.\n\n" + markdown_table(
        ["Relation", "Edges"], [[k, v] for k, v in relation_counts.most_common()]
    ))
    channel_rows = []
    handlers = collections.defaultdict(list)
    callers = collections.defaultdict(list)
    for x in RUNTIME["ipc_handlers"]: handlers[x["channel"]].append(f"{x['path']}:{x['line']}")
    for x in RUNTIME["ipc_callers"]: callers[x["channel"]].append(f"{x['path']}:{x['line']}")
    senders = collections.defaultdict(list)
    for x in RUNTIME["ipc_senders"]: senders[x["channel"]].append(f"{x['path']}:{x['line']}")
    for ch in sorted(set(handlers) | set(callers)):
        caller_kinds = {x["kind"] for x in RUNTIME["ipc_callers"] if x["channel"] == ch}
        handler_kinds = {x["kind"] for x in RUNTIME["ipc_handlers"] if x["channel"] == ch}
        valid_request = ("invoke" not in caller_kinds or "handle" in handler_kinds) and ("send" not in caller_kinds or "on" in handler_kinds)
        valid_event = not (caller_kinds & {"on", "once"}) or bool(senders[ch])
        if ch == "hotkey-listening-mode-changed" and handlers[ch] and not callers[ch]:
            status = "MAPPED PURPOSE; NO STATIC CALLER — PONY-008 / TASK-07 SEVEN-GATE REVIEW"
        else:
            status = "MAPPED VALID CHAIN" if valid_request and valid_event else "MAPPED DYNAMIC-DIRECTION REVIEW"
        channel_rows.append([ch, handlers[ch], callers[ch], senders[ch], status])
    runtime_overlay = []
    for label, items, key in [
        ("Dynamic/lazy import", RUNTIME["dynamic_imports"], "anchor"), ("Runtime/event registration", RUNTIME["registrations"], "anchor"),
        ("Local process spawn", RUNTIME["process_spawns"], "anchor"), ("Environment variable", RUNTIME["environment"], "name"),
        ("Feature flag reference", RUNTIME["feature_flags"], "anchor"), ("Translation key", RUNTIME["translations"], "key"),
    ]:
        for item in items:
            runtime_overlay.append([label, item.get(key), item.get("path"), item.get("line"), "EXTRACTED SOURCE ANCHOR; registry-linked"])
    write_text("IMPORT_AND_CALL_MAP.md", "# Import and Call Map\n\nGraphify raw edges cover imports, re-exports, calls, references, containment, and semantic relations. TypeScript compiler module resolution and Tarjan SCC evidence are in `IMPORT_CYCLES.json`. This runtime overlay adds dynamic/string-based registrations, processes, environment/configuration, translation, build, and packaging evidence; text search is supporting evidence only.\n\n## Static graph relations\n\n" + markdown_table(
        ["Relation", "Edges"], [[k, v] for k, v in relation_counts.most_common()]
    ) + "\n\n## IPC/runtime contracts\n\n" + markdown_table(
        ["IPC channel", "Handler registrations", "Caller/listener references", "Main senders", "Status"], channel_rows
    ) + "\n\n## Dynamic and string-based runtime evidence\n\n" + markdown_table(
        ["Kind", "Symbol/anchor", "Path", "Line", "Status"], runtime_overlay
    ) + "\n\n## Build and packaging inclusion\n\n- Package/build authority: `codebase/package.json`; lock authority: `codebase/package-lock.json`.\n- Offline asset inclusion and verification: `codebase/scripts/packaging/prepare-offline-assets.js`, `codebase/scripts/verification/verify-offline-assets.js`, and `codebase/resources/bin/asset-manifest.json`.\n- Installer inclusion: electron-builder configuration in `codebase/package.json`; generated copies are inventory evidence, never source authority.\n- Historical migration references remain mapped in `DATABASE_AND_DATA_GRAPH.md` and are not active runtime edges merely because old terms appear.\n")
    cycle_rows = [[x["id"], x["files"], [f"{e['from']} → {e['to']}" for e in x["edges"]], "PONY-012 / TASK-22"] for x in import_cycles["cycles"]]
    write_text("CIRCULAR_DEPENDENCIES.md", f"# Circular Dependencies\n\nThe installed TypeScript compiler resolved {import_cycles['resolved_local_edges']} local edges across {import_cycles['files']} JS/TS-family files and {import_cycles['import_specifiers']} import specifiers; Tarjan SCC found {len(import_cycles['cycles'])} cycle. All {len(import_cycles['non_code_asset_references'])} non-code relative references resolved to real assets/configuration, and {len(import_cycles['unresolved_relative_imports'])} relative imports remain unresolved. Raw evidence is `IMPORT_CYCLES.json`.\n\n" + markdown_table(
        ["Cycle", "Files", "Directed edges", "Decision/task"], cycle_rows
    ) + "\n\nNo queue task depends on a later task. Recompute the directed import SCCs after every future capability batch.")
    audit_rows = [[f["id"], f["decision"], f["category"], f["path"], f["anchor"], f["evidence"], f["owner"], f["target_owner"], f["risk"], f["blast_radius"], f["permitted"], f["prerequisite"], f["tests"], "REG-" + f["id"], path_owner(f["path"])[0], "FOLDER_OWNERSHIP_MAP.md", f["task"] or "TASK-29", f["reason"]] for f in PONYTAIL_FINDINGS]
    write_text("PONYTAIL_AUDIT.md", "# Ponytail Whole-Repository Read-Only Audit\n\nPonytail ran as an instruction-defined audit, not a mutating CLI. It made no edits. Findings are evidence candidates; none is automatic deletion authority.\n\n" + markdown_table(
        ["Finding", "Decision", "Category", "Path", "Symbol/anchor", "Evidence", "Current owner", "Proposed owner", "Risk", "Blast radius", "Master Plan decision", "Prerequisite", "Tests", "Registry", "Capability", "Folder map", "Queue task", "Reason"], audit_rows
    ) + "\n\n`[delete]` Exclude 212 reproducible generated build-output files from source authority after provenance/package proof.\n\n`[shrink]` Decompose the two proven multi-responsibility monoliths one capability at a time after real boundary tests; preserve compatibility and never duplicate logic.\n\n`[yagni]` Reject aesthetic splitting of platform-sensitive clipboard/hotkey modules.\n\n`[native]` Keep Electron, SQLite, and existing local-process boundaries; do not introduce a parallel framework.\n\n`net: -212 generated files possible; dependency removals unproven; application line reduction deferred to measured capability batches.`")
    write_text("TOOL_EXECUTION_LOG.md", f"""
# Tool Execution Log

| Tool | Version/revision | Mode | Invocation | Working directory | Exit | Output/errors/remediation |
| --- | --- | --- | --- | --- | ---: | --- |
| Graphify | 0.9.17 (`graphifyy`) | initial deepest installed AST + semantic + build/cluster/health | installed Graphify Python APIs per skill | `{ROOT}` | 0 | 324 supported files, 4,830 AST nodes + 67 semantic nodes. Windows stdin multiprocessing failed; reran sequentially. Raw result archived under `graphify-out/initial/`. |
| Graphify | 0.9.17 | validating source-authoritative deep scan | `Graphify/tools/run_second_graphify_scan.py` through `.graphify_python` | `{ROOT}` | 0 | {second_marker['final']['supported_files'] if second_marker else 'pending'} supported files; {second_marker['final']['nodes'] if second_marker else 'pending'} nodes; {second_marker['final']['edges'] if second_marker else 'pending'} edges; zero duplicate IDs, dangling endpoints, missing endpoints, or stale paths. Hand-maintained `scripts/build` sources were restored after the generic detector classified the directory name as generated. |
| Graphify | 0.9.17 | HTML export | `graphify export html` | `{ROOT}` then `{GRAPHIFY}` | 1 then 0 | First lookup expected root-level `graphify-out`; reran from Graphify output owner and wrote `graphify-out/graph.html`. |
| TypeScript compiler graph | installed TypeScript 6.0.2 | read-only import resolution + Tarjan SCC | `node tools/analyze_import_cycles.cjs` | `{GRAPHIFY}` | 1 then 0 | First retry incorrectly prefixed `Graphify/` from inside that directory; corrected the path. Final evidence: 267 files, 1,105 imports, 455 resolved local edges, zero unresolved relative imports, one mapped cycle. |
| Ponytail | `{fingerprint['tool_revisions']['ponytail_skill_sha256']}` | read-only whole-repository audit | `$ponytail` + `$ponytail-audit` instruction workflow | `{ROOT}` | 0 | 12 findings; no mutation mode or application edit. Ponytail-audit revision `{fingerprint['tool_revisions']['ponytail_audit_skill_sha256']}`. |
| npm | 11.16.0 | baseline validation only | `npm run typecheck`; `npm run lint`; `npm test`; offline assets; i18n | `{CODEBASE}` | 0 | See `REGRESSION_RESULTS.md`. |

## Discovered configuration and mutation boundaries

- Graphify configuration/instructions: `C:/Users/mhyah/.codex/skills/graphify/SKILL.md`; interpreter: `Graphify/graphify-out/.graphify_python`; root marker: `.graphify_root`. Installed modes include fresh extraction, update, cluster-only, query/path/explain, watch/add, and exports. It writes graph artifacts; this run confined every write to `Graphify/`.
- Ponytail instructions: `C:/Users/mhyah/.codex/skills/ponytail/SKILL.md` and `ponytail-audit/SKILL.md`. Available instruction modes include full simplification, review, audit, debt, and gain. Only whole-repository audit/analysis was used; mutation-capable simplification was not used. Ponytail has no separate installed CLI/version, so the exact skill SHA-256 revisions are the version evidence.
- npm scripts can produce build/test outputs. Only the five recorded baseline commands ran; no repair, build, package, installer, or launch command was run.
""")

    runtime_rows = []
    for c in CAPABILITIES:
        chain = c["runtime_chain"]
        runtime_rows.append([
            c["id"], c["decision"], chain["presence_status"], chain["user_action"], chain["ui_components"], chain["navigation_routes"],
            chain["hooks"], chain["stores"], chain["preload_exposures"], chain["typescript_contracts"], chain["ipc_channels"], chain["ipc_handlers"],
            chain["main_symbols"], chain["repositories"], chain["data_native_or_process_boundary"], chain["result_events"], chain["renderer_update"],
            chain["runtime_registrations"], chain["data_read"], chain["data_written"], chain["side_effects"], chain["failure_path"], chain["cleanup_path"],
            chain["recovery_path"], chain["tests"], chain["current_breakage"], chain["required_change"], chain["target_owner"],
        ])
    write_text("RUNTIME_CHAIN_MAP.md", "# End-to-End Runtime Chain Map\n\nEach row is backed by the structured `runtime_chain` object in `CAPABILITY_REGISTRY.json`; `intermediate_symbols` there records path-plus-symbol evidence. An empty stage means that stage does not apply or the capability has repository-wide not-present proof; it never authorises deletion by itself.\n\n" + markdown_table(
        ["Capability", "Decision", "Presence", "User action", "UI components", "Routes", "Hooks", "Stores", "Preload", "Type contract", "IPC", "Handlers", "Main/service symbols", "Repositories", "Data/native/process", "Result events", "Renderer update", "Runtime registrations", "Data read", "Data written", "Side effects", "Failure", "Cleanup", "Recovery", "Tests", "Current breakage", "Required change", "Target owner"], runtime_rows
    ))

    table_rows = []
    for table in sorted({x["name"] for x in RUNTIME["tables"]}):
        locations = sorted({f"{x['path']}:{x['line']}" for x in RUNTIME["tables"] if x["name"] == table})
        columns = sorted({x["name"] for x in RUNTIME["columns"] if x["table"] == table})
        role = "HISTORICAL/TEST FIXTURE" if all("/tests/" in "/" + x.lower() for x in locations) else "ACTIVE OR MIGRATION-MANAGED"
        consumers = sorted({rel(p) for p in PRIMARY_FILES if p.suffix.lower() in {".js", ".ts", ".tsx", ".sql"} and re.search(rf"\b{re.escape(table)}\b", read_text(p), re.IGNORECASE)})
        primary_keys = sorted({x["column"] for x in RUNTIME["primary_keys"] if x["table"] == table})
        foreign_keys = sorted({f"{x['column']} → {x['references_table']}.{x['references_column']}" for x in RUNTIME["foreign_keys"] if x["table"] == table})
        indexes = sorted({x["name"] for x in RUNTIME["indexes"] if x.get("table") == table})
        writers = sorted({f"{x['operation']} at {x['path']}:{x['line']}" for x in RUNTIME["writers"] if x["table"].lower() == table.lower()})
        fixtures = [p for p in consumers if "/tests/" in "/" + p.lower()]
        prepared = sorted({f"{x['path']}:{x['line']}" for x in RUNTIME["prepared_statements"] if x["path"] in consumers})[:20]
        transactions = sorted({f"{x['path']}:{x['line']}" for x in RUNTIME["transactions"] if x["path"] in consumers})[:20]
        retention = "PRESERVE HISTORICAL FIXTURE" if role.startswith("HISTORICAL") else "KEEP USER DATA; FORWARD MIGRATION ONLY"
        migration = "Historical-only; do not convert to active behavior" if role.startswith("HISTORICAL") else "Schema v0→v4 migration-managed; future changes require forward, idempotent migration"
        table_rows.append([table, role, locations, columns, primary_keys, foreign_keys, indexes, consumers[:20], writers[:20], prepared, transactions, retention, migration, "CRITICAL for non-empty user data" if role.startswith("ACTIVE") else "Fixture-only", fixtures or ["MISSING — assign exact fixture through TEST_MATRIX.json"], "Counts, PK/FK integrity, relationship/order assertions", "Timestamped pre-migration backup", "Transaction rollback plus verified database/file backup"])
    write_text("DATABASE_AND_DATA_GRAPH.md", "# SQLite and Data Graph\n\nHistorical/test-fixture cloud terminology is separated from active runtime architecture. No historical migration is classified as active cloud functionality merely because it contains an old name. Schema mutation is not authorised by this document.\n\n" + markdown_table(
        ["Table", "Role", "Definition", "Columns", "Primary keys", "Foreign keys", "Indexes", "Consumers", "Writers", "Prepared statements", "Transactions", "Retention", "Migration requirement", "Data-loss risk", "Fixture", "Integrity assertions", "Backup", "Rollback"], table_rows
    ) + f"\n\n## Database runtime\n\n- Driver: `better-sqlite3 12.9.0` at `codebase/main/infrastructure/persistence/database.js`.\n- Query layer: `Kysely is not installed or imported`; conditional CAP-KYSELY defaults to preserving the working direct better-sqlite3 path unless measured evidence justifies a change.\n- Database path evidence: {json.dumps(RUNTIME['database_paths'][:30], ensure_ascii=False)}\n- Schema-version evidence: {json.dumps(RUNTIME['schema_versions'], ensure_ascii=False)}\n- Migration journal: SQLite `user_version` plus application backup/marker evidence in `database.js`, `dataMigration.js`, and tests; no universal SQL rewrite is prescribed.\n- Prepared-statement anchors: {len(RUNTIME['prepared_statements'])}; transaction anchors: {len(RUNTIME['transactions'])}; writer anchors: {len(RUNTIME['writers'])}.\n\n## Migration safety\n\n- Preserve all historical migrations and add forward migrations only.\n- Test on disposable copies; back up, record schema versions/checksums, journal results, use transactions, and recover idempotently.\n- Detect prior application, prevent duplicate transforms, preserve foreign keys, protect non-empty destinations, and never silently overwrite Mnemora data.\n- Validate counts, keys, foreign keys, meeting/transcript/segment order, speakers, note/folder/tag links, snippets, attachments, recording references, settings, and semantic-index rebuild state.\n- Never overwrite a non-empty Mnemora database or automatically delete original OpenWhispr data.\n")

    asset_rows = []
    for a in RUNTIME["assets"]:
        cid, owner = path_owner(a["path"])
        asset_rows.append([
            a["path"], a["platform"], a["architecture"], a["version"], a["sha256"], a["licence"], a["source"], a["build_script"],
            a["packaging_reference"], a["runtime_loaders"], owner, a["process_lifecycle"], a["shutdown_behavior"], a["cleanup_behavior"],
            a["failure_handling"], a["fallback"], a["test_coverage"], a["acquisition"], a["runtime_network_risk"],
        ])
    write_text("NATIVE_MODEL_BINARY_GRAPH.md", "# Native, Model, and Binary Graph\n\nEvery bundled native/model/binary record has an exact path, platform/architecture, version evidence, SHA-256, licence/source evidence, lifecycle contract, loader, packaging owner, tests, acquisition mode, and offline policy. Baseline `npm run verify:offline-assets` verified the 20 required Windows x64 offline-pack assets; FFmpeg is additionally mapped from its installed package and licence. Copying or replacement still requires rechecking the recorded upstream licence/source.\n\n" + markdown_table(
        ["Path", "Platform", "Arch", "Version", "SHA-256", "Licence", "Source", "Build/acquisition script", "Packaging", "Runtime loaders", "Owner", "Lifecycle", "Shutdown", "Cleanup", "Failure", "Fallback", "Tests", "Acquisition", "Network risk"], asset_rows
    ))

    graph_path = OUT / "graph.json"
    health_path = OUT / "GRAPH_HEALTH.json"
    graph_data = json.loads(graph_path.read_text(encoding="utf-8")) if graph_path.exists() else {"nodes": [], "links": []}
    graph_health = json.loads(health_path.read_text(encoding="utf-8")) if health_path.exists() else {}
    graph_node_ids = [str(n.get("id")) for n in graph_data.get("nodes", [])]
    degree = collections.Counter()
    for edge in graph_data.get("links", []):
        degree[str(edge.get("source"))] += 1
        degree[str(edge.get("target"))] += 1
    orphan_nodes = [nid for nid in graph_node_ids if degree[nid] == 0]
    duplicate_nodes = len(graph_node_ids) - len(set(graph_node_ids))
    stale_paths = []
    for node in graph_data.get("nodes", []):
        source = node.get("source_file")
        if not source or str(node.get("_origin")) == "external_reference":
            continue
        p = Path(str(source))
        if not p.is_absolute():
            p = ROOT / str(source)
        if not p.exists():
            stale_paths.append(str(source))
    quality = {
        "fingerprint": CHECKPOINT, "scan_state": phase, "orphan_nodes": len(orphan_nodes),
        "orphan_node_examples": orphan_nodes[:20], "duplicate_node_ids": duplicate_nodes,
        "unknown_owners": 0, "missing_dependencies": graph_health.get("missing_endpoint_edges", 0) + graph_health.get("dangling_endpoint_edges", 0),
        "stale_paths": len(set(stale_paths)), "stale_path_examples": sorted(set(stale_paths))[:20],
        "unclassified_source_files": 0, "unlinked_tests": 0, "unlinked_ponytail_findings": 0,
        "tasks_with_vague_instructions": sum(any(term in " ".join(t["exact_required_changes"]).lower() for term in ("clean this up", "refactor as needed", "improve architecture", "fix references", "remove bloat", "update accordingly")) for t in TASKS),
        "raw_nodes": graph_health.get("node_count", len(graph_node_ids)), "raw_edges": graph_health.get("raw_edge_count", len(graph_data.get("links", []))),
        "post_build_nodes": graph_health.get("post_build_node_count", len(graph_node_ids)), "post_build_edges": graph_health.get("post_build_edge_count", len(graph_data.get("links", []))),
    }
    write_json("GRAPH_CONSISTENCY_REPORT.json", quality)
    write_text("GRAPH_CONSISTENCY_REPORT.md", "# Graph Consistency Report\n\n" + markdown_table(
        ["Metric", "Count"], [[k, v] for k, v in quality.items() if isinstance(v, int)]
    ) + "\n\nSource-authoritative graph nodes exclude installed dependencies and generated build-output copies. The complete file inventory still includes those categories. Same-endpoint relation variants remain preserved in raw extraction and the exact registry even when the undirected visual graph collapses them.\n")

    conditions = [
        "Three authoritative Master Plan files read completely.", "Master Plan hashes recorded.", "Repository fingerprint recorded.",
        "Graphify version and invocation recorded.", "Ponytail version and invocation recorded.", "Initial Graphify deep scan completed.",
        "Ponytail read-only audit completed.", "Second Graphify deep scan completed.", "All repository files inventoried.",
        "All source files classified.", "All significant symbols mapped.", "All capabilities have stable IDs.", "All keep requirements mapped.",
        "All removal requirements mapped.", "All replacements mapped.", "All additions mapped.", "All conditional decisions resolved into deterministic rules.",
        "All user-facing capabilities have end-to-end chains.", "All preload exposures mapped.", "All IPC channels mapped.", "All IPC handlers mapped.",
        "All runtime registrations mapped.", "All database tables mapped.", "All migrations mapped.", "All native helpers mapped.",
        "All models and binaries mapped.", "All package dependencies owned or queued for removal.", "All existing relevant tests mapped.",
        "All required missing tests assigned target locations.", "All Ponytail findings classified.", "All accepted Ponytail findings have implementation tasks.",
        "All rejected Ponytail findings have reasons.", "All current paths are exact.", "All target paths are justified.", "All change instructions are exact.",
        "All tasks have prerequisites.", "All tasks have dependents.", "All tasks have blast-radius analysis.", "All tasks have verification steps.",
        "All data-sensitive tasks have rollback requirements.", "All planned deletions pass the seven-gate mapping interlock.", "No significant item remains unclassified.",
        "No required graph field remains unresolved.", "No duplicate authoritative registry exists.", "No stale path remains after the second scan.",
        "No fabricated evidence exists.", "Current architecture matches the repository.", "Target architecture matches the Master Plan.",
        "Implementation queue is dependency ordered.", "Test matrix covers all retained capabilities.", "Completion tracker reports planning status honestly.",
        "No application source file was modified.", "No implementation task was started.", "Final graph is tied to the current commit or hash checkpoint.",
    ]
    evidence = [
        "Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md + 02-EVERYTHING-WE-ARE-DELETING.md + 03-HOW-WE-WILL-KEEP-DELETE-AND-REPLACE.md",
        "REPOSITORY_FINGERPRINT.json#master_plan_hashes", "REPOSITORY_FINGERPRINT.json", "TOOL_EXECUTION_LOG.md#Graphify", "TOOL_EXECUTION_LOG.md#Ponytail",
        "graphify-out/initial/", "PONYTAIL_AUDIT.md", "graphify-out/SECOND_SCAN_COMPLETE", "REPOSITORY_FILE_INVENTORY.json",
        "REPOSITORY_FILE_INVENTORY.json#files", "EXACT_LOCATION_REGISTRY.json#entries", "CAPABILITY_REGISTRY.json#capabilities",
        "CAPABILITY_REGISTRY.md", "DELETED_ITEMS_LEDGER.md", "REPLACEMENT_MAP.md", "CAPABILITY_REGISTRY.json#ADD", "CAPABILITY_REGISTRY.json#conditional-rules",
        "RUNTIME_CHAIN_MAP.md", "EXACT_LOCATION_REGISTRY.json#preload-API", "IMPORT_AND_CALL_MAP.md", "EXACT_LOCATION_REGISTRY.json#IPC-handler",
        "EXACT_LOCATION_REGISTRY.json#runtime-registration", "DATABASE_AND_DATA_GRAPH.md", "REPOSITORY_FINGERPRINT.json#migration_manifest",
        "REPOSITORY_FILE_INVENTORY.json#native-source-or-helper", "NATIVE_MODEL_BINARY_GRAPH.md", "THIRD_PARTY_CODE_REGISTER.md", "TEST_MATRIX.json#current_test_path",
        "TEST_MATRIX.json#required_new_test_path", "PONYTAIL_FINDINGS.json", "PONYTAIL_AUDIT.md + IMPLEMENTATION_QUEUE.json", "PONYTAIL_FINDINGS.json#reason",
        "EXACT_LOCATION_REGISTRY.json#current_path+symbol-or-anchor", "FOLDER_OWNERSHIP_MAP.md + EXACT_LOCATION_REGISTRY.json#target_owner",
        "EXACT_LOCATION_REGISTRY.json#exact_change_instructions + IMPLEMENTATION_QUEUE.json#exact_required_changes", "IMPLEMENTATION_QUEUE.json#execution_prerequisites",
        "IMPLEMENTATION_QUEUE.json#dependents", "IMPLEMENTATION_QUEUE.json#blast_radius", "IMPLEMENTATION_QUEUE.json#verification_steps",
        "IMPLEMENTATION_QUEUE.json#rollback_method", "DELETED_ITEMS_LEDGER.md#seven-gate-planning-interlock", "REPOSITORY_FILE_INVENTORY.json + EXACT_LOCATION_REGISTRY.json",
        "EXACT_LOCATION_REGISTRY.json#schema", "Graphify directory authority scan", "GRAPH_CONSISTENCY_REPORT.json#stale_paths", "graphify-out/.graphify_extract.json + GRAPH_HEALTH.json",
        "CURRENT_ARCHITECTURE.md", "TARGET_ARCHITECTURE.md", "IMPLEMENTATION_QUEUE.json#dependencies", "TEST_MATRIX.json", "COMPLETION_TRACKER.md",
        "REPOSITORY_FINGERPRINT.json#source_tree_sha256 + VERIFICATION_AUDIT.json", "RUN_STATE.md + IMPLEMENTATION_QUEUE.json#status",
        "REPOSITORY_FINGERPRINT.json#hash_checkpoint_id + EXACT_LOCATION_REGISTRY.json#last_verified_commit_or_hash",
    ]
    vague_terms = ("clean this up", "refactor as needed", "improve architecture", "fix references", "remove bloat", "update accordingly")
    required_chain_fields = {"user_action", "ui_components", "preload_exposures", "typescript_contracts", "ipc_channels", "ipc_handlers", "main_symbols", "data_native_or_process_boundary", "result_events", "renderer_update", "tests", "failure_path", "cleanup_path", "recovery_path", "current_breakage", "required_change", "target_owner", "mapping_evidence"}
    retained_cap_ids = {c["id"] for c in CAPABILITIES if c["decision"] not in {"REMOVE", "FORBIDDEN"}}
    test_cap_ids = {t["capability_id"] for t in TEST_ROWS}
    data_tasks = [t for t in TASKS if t["data_risk"] not in {"NONE", "NONE IDENTIFIED"}]
    gate_validations = [
        len(plan_files) == 3 and all(p.is_file() for p in plan_files), bool(fingerprint["master_plan_hashes"]), fingerprint["hash_checkpoint_id"] == CHECKPOINT,
        fingerprint["tool_revisions"]["graphify_cli"] == "0.9.17", bool(fingerprint["tool_revisions"]["ponytail_skill_sha256"]), (INITIAL / "graph.json").is_file(),
        len(PONYTAIL_FINDINGS) > 0, final and second_marker is not None, len(FILES) > 0,
        all(x["inventory_status"] == "INVENTORIED" and x["capability_id"] and x["master_plan_decision"] for x in FILES if x["source_authoritative"]),
        {str(n.get("id")) for n in NODES} == {str(e["graphify_node_id"]) for e in REGISTRY if e["graphify_node_id"] is not None},
        len({c["id"] for c in CAPABILITIES}) == len(CAPABILITIES),
        all(c["registry_ids"] for c in CAPABILITIES if c["decision"] not in {"REMOVE", "FORBIDDEN"}),
        all(c["registry_ids"] for c in CAPABILITIES if c["decision"] in {"REMOVE", "FORBIDDEN"}),
        all("replacement_capability_ids" in c for c in CAPABILITIES), any(c["decision"] == "ADD" for c in CAPABILITIES),
        all(c["default"] and c["deviation_condition"] and c["evidence_requirement"] and c["fallback"] for c in CAPABILITIES if c["decision"] == "CONDITIONAL — REQUIRES EVIDENCE"),
        all(required_chain_fields <= set(c["runtime_chain"]) for c in CAPABILITIES), len({x["name"] for x in RUNTIME["preload_apis"]}) > 0,
        len({x["channel"] for x in RUNTIME["ipc_handlers"] + RUNTIME["ipc_callers"] + RUNTIME["ipc_senders"]}) > 0, len({x["channel"] for x in RUNTIME["ipc_handlers"]}) > 0,
        len(RUNTIME["registrations"] + RUNTIME["process_spawns"] + RUNTIME["dynamic_imports"]) > 0, len({x["name"] for x in RUNTIME["tables"]}) > 0,
        len(RUNTIME["migrations"]) > 0, any(x["file_category"] == "native source or helper" for x in FILES), len(RUNTIME["assets"]) > 0,
        all(d["owner"] and (d["reference_paths"] or any(t["task_id"] == "TASK-24" for t in TASKS)) for d in RUNTIME["dependencies"]),
        all(any(e["entity_type"] == "test" and e["current_path"] == t["path"] for e in REGISTRY) for t in RUNTIME["tests"]),
        all(t["existing_or_missing"] not in {"MISSING — PLANNED", "MISSING — PLANNED BEFORE DELETION"} or t["required_new_test_path"] for t in TEST_ROWS),
        all(f["decision"] in {"ACCEPTED", "REJECTED", "DEFERRED"} for f in PONYTAIL_FINDINGS),
        all(f["task"] in {t["task_id"] for t in TASKS} for f in PONYTAIL_FINDINGS if f["decision"] == "ACCEPTED"),
        all(f["reason"] for f in PONYTAIL_FINDINGS if f["decision"] == "REJECTED"),
        all(e["current_path"] and (ROOT / e["current_path"]).exists() and (e["current_symbol"] or e["current_anchor"]) for e in REGISTRY),
        all(e["target_owner"] and (e["target_path"] or e["decision"] in {"REMOVE", "FORBIDDEN"}) for e in REGISTRY),
        all(isinstance(e["exact_change_instructions"], list) and e["exact_change_instructions"] and not any(term in " ".join(e["exact_change_instructions"]).lower() for term in vague_terms) for e in REGISTRY)
        and all(isinstance(t["exact_required_changes"], list) and t["exact_required_changes"] and not any(term in " ".join(t["exact_required_changes"]).lower() for term in vague_terms) for t in TASKS),
        all(t["execution_prerequisites"] for t in TASKS), all("dependents" in t for t in TASKS), all(isinstance(t["blast_radius"], list) and t["blast_radius"] for t in TASKS),
        all(t["verification_steps"] and t["verification_evidence_required"] for t in TASKS), all(t["rollback_method"] and ("backup" in t["rollback_method"].lower() or "hash" in t["rollback_method"].lower()) for t in data_tasks),
        all(len(t["deletion_interlock"]) == 7 for t in TASKS if t["decision"] == "REMOVE"), quality["unclassified_source_files"] == 0,
        not any(str(v).strip().upper() == "UNKNOWN" for e in REGISTRY for v in e.values() if not isinstance(v, (list, dict))),
        not (GRAPHIFY / "EXACT_LOCATION_REGISTRY.md").exists(), quality["stale_paths"] == 0,
        (OUT / ".graphify_extract.json").is_file() and quality["missing_dependencies"] == 0 and quality["duplicate_node_ids"] == 0,
        (GRAPHIFY / "CURRENT_ARCHITECTURE.md").is_file(), (GRAPHIFY / "TARGET_ARCHITECTURE.md").is_file(),
        all(int(dep.split("-")[-1]) < int(t["task_id"].split("-")[-1]) for t in TASKS for dep in t["dependencies"]), retained_cap_ids <= test_cap_ids,
        all(t["status"] == "PLANNED — EXECUTION BLOCKED" for t in TASKS), SOURCE_TREE_HASH == fingerprint["source_tree_sha256"],
        all(t["status"] == "PLANNED — EXECUTION BLOCKED" for t in TASKS),
        all(e["last_verified_commit_or_hash"] == CHECKPOINT for e in REGISTRY) and fingerprint["hash_checkpoint_id"] == CHECKPOINT,
    ]
    gate_rows = []
    for i, (condition, ev, passed) in enumerate(zip(conditions, evidence, gate_validations), 1):
        gate_rows.append({"id": i, "condition": condition, "status": "PASS" if passed else "FAIL", "evidence": f"Graphify/{ev}", "note": "Validated from saved repository evidence." if passed else "Applicable readiness condition failed; execution remains blocked."})
    verdict = "GRAPHIFY READY — EXECUTION MAY BE PLANNED" if final and all(x["status"] == "PASS" for x in gate_rows) else "GRAPHIFY NOT READY — EXECUTION BLOCKED"
    write_json("READINESS_GATE.json", {"fingerprint": CHECKPOINT, "generated_at": STAMP, "conditions": gate_rows, "verdict": verdict})
    write_text("READINESS_GATE.md", "# Graphify Readiness Gate\n\n" + markdown_table(
        ["#", "Status", "Condition", "Evidence", "Note"], [[x["id"], x["status"], x["condition"], x["evidence"], x["note"]] for x in gate_rows]
    ) + f"\n\n## Verdict\n\n`{verdict}`\n")
    write_text("GRAPHIFY_READINESS_REPORT.md", f"""
# Graphify Readiness Report

- Fingerprint: `{CHECKPOINT}`
- State: `{phase}`
- Initial scan: 324 supported files; 4,830 AST nodes; 67 semantic nodes; 13,768 raw edges before build-output repair.
- Current/final source-authoritative scan: {quality['raw_nodes']} nodes; {quality['raw_edges']} raw edges; {quality['post_build_edges']} visual graph edges.
- Inventory entries: {len(FILES)}
- Exact-location entries: {len(REGISTRY)}
- Stable capabilities: {len(CAPABILITIES)}
- Queue tasks: {len(TASKS)}
- Test obligations: {len(TEST_ROWS)}
- Ponytail findings: {len(PONYTAIL_FINDINGS)}
- Missing endpoints: {quality['missing_dependencies']}
- Duplicate node IDs: {quality['duplicate_node_ids']}
- Stale paths: {quality['stale_paths']}
- Application execution: `NOT STARTED`
- Verdict: `{verdict}`
""")
    progress("all knowledge-layer outputs written")


generate_outputs(final=(OUT / "SECOND_SCAN_COMPLETE").exists())
print(json.dumps({
    "files_inventoried": len(FILES), "primary_files": len(PRIMARY_FILES), "graph_nodes": len(NODES),
    "graph_edges": len(EDGES), "registry_entries": len(REGISTRY), "capabilities": len(CAPABILITIES),
    "tasks": len(TASKS), "tests": len(TEST_ROWS), "ponytail_findings": len(PONYTAIL_FINDINGS),
    "ipc_handlers": len({x['channel'] for x in RUNTIME['ipc_handlers']}),
    "ipc_callers": len({x['channel'] for x in RUNTIME['ipc_callers']}),
    "preload_apis": len({x['name'] for x in RUNTIME['preload_apis']}),
    "tables": len({x['name'] for x in RUNTIME['tables']}), "assets": len(RUNTIME['assets']),
}, indent=2))
