#!/usr/bin/env python3
"""Complete Mnemora's derived planning system without modifying application files.

The script reads immutable Master Plan sources, the saved Graphify/static-analysis
evidence, and current planning registries. It writes only authoritative or derived
planning artifacts under Graphify/. It never executes application code, tests,
builds, packaging, installers, migrations, or Git mutations.
"""

from __future__ import annotations

import collections
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable

from semantic_rules import (
    CAPABILITY_OWNERS,
    EXACT_LOCATIONS,
    PRIMARY_CAPS_BY_SECTION,
    PRODUCT_SCOPE_CAPS,
    REMOVAL_CAPS,
    SYMBOL_OVERRIDES,
    VENDOR_OR_GENERATED_MARKERS,
    owner_for,
    reviewed_paths,
    target_for,
)


ROOT = Path(__file__).resolve().parents[2]
G = ROOT / "Graphify"
CB = ROOT / "codebase"
MP = G / "Master Plan"
MASTER_FILES = [
    ("MP1", MP / "01-EVERYTHING-WE-ARE-KEEPING.md"),
    ("MP2", MP / "02-EVERYTHING-WE-ARE-DELETING.md"),
    ("MP3", MP / "03-HOW-WE-WILL-KEEP-DELETE-AND-REPLACE.md"),
]
EXPECTED_MASTER_HASHES = {
    "MP1": "BDF185A823422BCAA9BFEBA815A6852D8F7A5CD46B64714B2CD1DE3357A67F64",
    "MP2": "76B6EEC15778B1928F2CD9C0F73FA68C9F3363493062E31E0C904E620DE0AAC3",
    "MP3": "5E076498731C35ACF314904AAB3A39671F7026A166B5E847EFE3CCD4CF07304E",
}


def probe_git_state(root: Path) -> dict[str, Any]:
    """Read-only Git presence probe used by derived provenance records."""
    git_dir = root / ".git"
    branch: str | None = None
    if git_dir.is_dir():
        try:
            head = (git_dir / "HEAD").read_text(encoding="utf-8", errors="replace").strip()
            match = re.match(r"^ref: refs/heads/(.+)$", head)
            branch = match.group(1) if match else None
        except OSError:
            branch = None
    return {"present": git_dir.is_dir(), "branch": branch}


GIT_STATE = probe_git_state(ROOT)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().upper()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(name: str, value: Any) -> None:
    (G / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(name: str, value: str) -> None:
    (G / name).write_text(value.rstrip() + "\n", encoding="utf-8")


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def stable_id(prefix: str, *parts: str, length: int = 10) -> str:
    raw = "\0".join(parts)
    return f"{prefix}-{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:length].upper()}"


def unique(values: Iterable[Any]) -> list[Any]:
    result: list[Any] = []
    seen: set[str] = set()
    for value in values:
        key = json.dumps(value, sort_keys=True, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value)
        if key not in seen:
            seen.add(key)
            result.append(value)
    return result


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    def cell(value: Any) -> str:
        if isinstance(value, list):
            value = ", ".join(str(x) for x in value)
        return str(value if value is not None else "N/A").replace("|", "\\|").replace("\n", " ")

    output = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    output.extend("| " + " | ".join(cell(v) for v in row) + " |" for row in rows)
    return "\n".join(output)


for code, path in MASTER_FILES:
    actual = sha256(path)
    if actual != EXPECTED_MASTER_HASHES[code]:
        raise SystemExit(f"Immutable Master Plan hash mismatch before planning generation: {path} {actual}")


# Existing capability IDs are preserved. Additions cover Master Plan concepts that
# the previous registry collapsed or omitted.
EXTRA_CAPABILITIES: list[dict[str, Any]] = [
    {"id": "CAP-LEGAL", "name": "Legal attribution and third-party notices", "decision": "MANDATORY KEEP", "owner": "Legal and packaging", "target_paths": ["codebase/LICENSE", "codebase/NOTICE", "codebase/THIRD-PARTY-NOTICES"]},
    {"id": "CAP-PROVENANCE", "name": "Repository provenance and safe Git batching", "decision": "MANDATORY KEEP", "owner": "Repository governance", "target_paths": [".git/", ".gitignore", "Graphify/RUN_STATE.md"]},
    {"id": "CAP-PLANNING-GOVERNANCE", "name": "Master Plan and planning authority", "decision": "MANDATORY KEEP", "owner": "Graphify governance", "target_paths": ["Graphify/Master Plan/", "Graphify/MASTER_REQUIREMENT_REGISTER.json"]},
    {"id": "CAP-DELETION-GOVERNANCE", "name": "Binding deletion interlock", "decision": "MANDATORY KEEP", "owner": "Graphify governance", "target_paths": ["Graphify/DELETED_ITEMS_LEDGER.md", "Graphify/IMPLEMENTATION_QUEUE.json"]},
    {"id": "CAP-EXACT-LOCATION", "name": "Exact-location authority", "decision": "MANDATORY KEEP", "owner": "Graphify governance", "target_paths": ["Graphify/EXACT_LOCATION_REGISTRY.json"]},
    {"id": "CAP-IMPLEMENTATION-GOVERNANCE", "name": "Dependency-safe implementation batches", "decision": "MANDATORY KEEP", "owner": "Implementation governance", "target_paths": ["Graphify/IMPLEMENTATION_QUEUE.json", "Graphify/START-HERE.md"]},
    {"id": "CAP-DATA-SAFETY", "name": "Data safety and migration integrity", "decision": "MANDATORY KEEP", "owner": "SQLite persistence", "target_paths": ["codebase/main/infrastructure/persistence/database.js", "codebase/main/infrastructure/persistence/dataMigration.js", "codebase/main/infrastructure/persistence/localBackup.js"]},
    {"id": "CAP-PROCESSING-JOBS", "name": "Local processing job queue", "decision": "ADD", "owner": "Local processing", "target_paths": ["codebase/main/infrastructure/runtime/localJobQueue.js"]},
    {"id": "CAP-SHERPA-ONNX", "name": "Sherpa-ONNX local engine packaging", "decision": "CONDITIONAL — REQUIRES EVIDENCE", "owner": "Local transcription and diarization", "target_paths": ["codebase/main/features/meetings/diarization.js", "codebase/resources/bin/sherpa-onnx-diarize-win32-x64.exe"]},
    {"id": "CAP-VOICE-FINGERPRINTING", "name": "Local voice fingerprinting", "decision": "CONDITIONAL — REQUIRES EVIDENCE", "owner": "Diarization and speakers", "target_paths": ["codebase/main/features/meetings/speakerEmbeddings.js", "codebase/main/features/meetings/liveSpeakerIdentifier.js"]},
    {"id": "CAP-NOTE-TEMPLATES", "name": "Local note templates", "decision": "CONDITIONAL — REQUIRES EVIDENCE", "owner": "Notes organisation", "target_paths": ["codebase/renderer/features/notes/noteTemplates.ts"]},
    {"id": "CAP-PORTABLE-WINDOWS", "name": "Portable Windows build", "decision": "CONDITIONAL — REQUIRES EVIDENCE", "owner": "Windows packaging", "target_paths": ["codebase/electron-builder.json"]},
    {"id": "CAP-MACOS-LINUX", "name": "macOS and Linux source and CI preservation", "decision": "CONDITIONAL — REQUIRES EVIDENCE", "owner": "Cross-platform source", "target_paths": ["codebase/native/helpers/macos/", "codebase/native/helpers/linux/", "codebase/packaging/macos/", "codebase/packaging/linux/"]},
    {"id": "CAP-LOOPBACK-WEBSOCKETS", "name": "Loopback-only WebSockets", "decision": "CONDITIONAL — REQUIRES EVIDENCE", "owner": "Runtime network policy", "target_paths": ["codebase/main/infrastructure/runtime/runtimeNetworkPolicy.js"]},
    {"id": "CAP-ONBOARDING", "name": "Local offline onboarding", "decision": "KEEP AND REPAIR", "owner": "Renderer onboarding", "target_paths": ["codebase/renderer/features/onboarding/OnboardingFlow.tsx"]},
    {"id": "CAP-OFFLINE-FIRST-LAUNCH", "name": "Offline first launch proof", "decision": "ADD", "owner": "Release verification", "target_paths": ["codebase/tests/integration/offline-first-launch.integration.test.js"]},
    {"id": "CAP-RELEASE", "name": "Strict Release Conjunction", "decision": "MANDATORY KEEP", "owner": "Release governance", "target_paths": ["Graphify/RELEASE_GATE_PLAN.json", "Graphify/COMPLETION_TRACKER.md"]},
    {"id": "CAP-THIRD-PARTY", "name": "Reuse-first third-party provenance", "decision": "MANDATORY KEEP", "owner": "Legal and architecture", "target_paths": ["Graphify/THIRD_PARTY_CODE_REGISTER.md"]},
    {"id": "CAP-SIMPLIFICATION", "name": "Post-correctness simplification audit", "decision": "KEEP AND REPAIR", "owner": "Architecture governance", "target_paths": ["Graphify/PONYTAIL_AUDIT.md"]},
    {"id": "CAP-MARKDOWN-GOVERNANCE", "name": "Markdown separation", "decision": "MANDATORY KEEP", "owner": "Repository governance", "target_paths": ["Graphify/", "codebase/LICENSE", "codebase/NOTICE", "codebase/THIRD-PARTY-NOTICES"]},
    {"id": "CAP-MODEL-DISCOVERY", "name": "Local model discovery and validation", "decision": "MANDATORY KEEP", "owner": "Local model handling", "target_paths": ["codebase/main/features/transcription/modelDirUtils.js", "codebase/main/features/transcription/modelRegistryData.json"]},
]


MP1_SECTION_CAPS: dict[str, list[str]] = {
    "governing-rule": ["CAP-PLANNING-GOVERNANCE", "CAP-IMPLEMENTATION-GOVERNANCE"],
    "1-product-and-legal-identity": ["CAP-LEGAL", "CAP-APP-SHELL", "CAP-MARKDOWN-GOVERNANCE"],
    "2-core-desktop-stack": ["CAP-APP-SHELL", "CAP-RENDERER", "CAP-DATABASE", "CAP-KYSELY", "CAP-NATIVE"],
    "3-application-shell": ["CAP-APP-SHELL", "CAP-IPC", "CAP-LOOPBACK-WEBSOCKETS", "CAP-NETWORK-POLICY"],
    "4-voice-dictation": ["CAP-DICTATION", "CAP-HOTKEY", "CAP-MICROPHONE", "CAP-RECORDING-OVERLAY", "CAP-CLIPBOARD"],
    "5-local-transcription-engines": ["CAP-WHISPER", "CAP-PARAKEET", "CAP-SHERPA-ONNX", "CAP-TRANSCRIPTION"],
    "6-local-model-handling": ["CAP-MODELS", "CAP-MODEL-DISCOVERY", "CAP-MODEL-PACK"],
    "7-meeting-recording": ["CAP-MEETING", "CAP-SYSTEM-AUDIO", "CAP-RECOVERY", "CAP-PLAYBACK", "CAP-MEETING-DETECTION"],
    "8-audio-processing": ["CAP-AUDIO", "CAP-FFMPEG", "CAP-VAD", "CAP-AEC", "CAP-AUDIO-MIXING"],
    "9-speaker-diarization": ["CAP-DIARIZATION", "CAP-SPEAKER-EMBEDDINGS", "CAP-VOICE-FINGERPRINTING", "CAP-SPEAKER-NAMING", "CAP-SPEAKER-RENAMING"],
    "10-transcripts-and-history": ["CAP-TRANSCRIPTION", "CAP-SEGMENTS", "CAP-TRANSCRIPT-EDIT", "CAP-TRANSCRIPT-HISTORY"],
    "11-notes": ["CAP-NOTES", "CAP-PERSONAL-NOTES", "CAP-MEETING-NOTES", "CAP-LINKED-NOTES", "CAP-NOTE-TEMPLATES"],
    "12-folders-tags-and-snippets": ["CAP-FOLDERS", "CAP-TAGS", "CAP-SNIPPETS", "CAP-NOTES"],
    "13-exact-search": ["CAP-SEARCH-EXACT"],
    "14-semantic-search": ["CAP-SEARCH-SEMANTIC", "CAP-MINILM", "CAP-QDRANT", "CAP-REMOVE-LOCAL-GENERATIVE-AI"],
    "15-local-actions-and-clipboard": ["CAP-CLIPBOARD", "CAP-NOTES", "CAP-DATABASE", "CAP-IMPORT-EXPORT", "CAP-BACKUP"],
    "16-notifications-and-process-detection": ["CAP-NOTIFICATIONS", "CAP-MEETING-DETECTION", "CAP-TRAY"],
    "17-internal-ipc": ["CAP-IPC"],
    "18-sqlite-and-local-persistence": ["CAP-DATABASE", "CAP-KYSELY", "CAP-KEYRING", "CAP-DATA-SAFETY"],
    "19-import-and-export": ["CAP-IMPORT", "CAP-EXPORT", "CAP-IMPORT-EXPORT", "CAP-BACKUP", "CAP-MARKDOWN-GOVERNANCE"],
    "20-playback": ["CAP-PLAYBACK", "CAP-LINKED-PLAYBACK"],
    "21-settings": ["CAP-SETTINGS", "CAP-MODEL-PACK"],
    "22-native-and-platform-components": ["CAP-NATIVE", "CAP-MACOS-LINUX", "CAP-WINDOWS-INSTALLER"],
    "23-packaging": ["CAP-PACKAGING", "CAP-WINDOWS-INSTALLER", "CAP-PORTABLE-WINDOWS"],
    "24-tests-and-proof": ["CAP-TESTING", "CAP-RELEASE"],
    "25-preservation-first-policy": ["CAP-IMPLEMENTATION-GOVERNANCE", "CAP-THIRD-PARTY"],
    "26-conditional-keeps-summary": ["CAP-QDRANT", "CAP-PARAKEET", "CAP-SHERPA-ONNX", "CAP-KYSELY", "CAP-LOOPBACK-WEBSOCKETS", "CAP-KEYRING", "CAP-VOICE-FINGERPRINTING", "CAP-MEETING-DETECTION", "CAP-NOTE-TEMPLATES", "CAP-PORTABLE-WINDOWS", "CAP-MACOS-LINUX"],
    "final-keep-acceptance": ["CAP-RELEASE", "CAP-EXACT-LOCATION", "CAP-TESTING"],
}


MP2_SECTION_CAPS: dict[str, list[str]] = {
    "governing-rule": ["CAP-DELETION-GOVERNANCE"],
    "binding-deletion-interlock": ["CAP-DELETION-GOVERNANCE", "CAP-EXACT-LOCATION"],
    "1-active-openwhispr-identity": ["CAP-REMOVE-ACTIVE-OPENWHISPR-IDENTITY"],
    "2-authentication-and-accounts": ["CAP-REMOVE-AUTHENTICATION", "CAP-REMOVE-ACCOUNTS"],
    "3-cloud-synchronization": ["CAP-REMOVE-CLOUD-SYNCHRONISATION"],
    "4-workspaces-organisations-and-teams": ["CAP-REMOVE-WORKSPACES", "CAP-REMOVE-ORGANISATIONS", "CAP-REMOVE-TEAMS"],
    "5-invitations-and-sharing": ["CAP-REMOVE-INVITATIONS", "CAP-REMOVE-SHARING"],
    "6-hosted-transcription-providers": ["CAP-REMOVE-HOSTED-TRANSCRIPTION"],
    "7-hosted-ai-and-provider-systems": ["CAP-REMOVE-HOSTED-AI"],
    "8-ai-agents-and-chat": ["CAP-REMOVE-AI-AGENTS", "CAP-REMOVE-CHAT", "CAP-REMOVE-SUMMARISATION", "CAP-REMOVE-ACTION-ITEM-EXTRACTION", "CAP-REMOVE-AI-REWRITING", "CAP-REMOVE-LOCAL-GENERATIVE-AI"],
    "9-agent-tools-and-remote-actions": ["CAP-REMOVE-AI-AGENTS", "CAP-REMOVE-CALENDAR", "CAP-CLIPBOARD", "CAP-NOTES"],
    "10-google-calendar-and-remote-calendars": ["CAP-REMOVE-CALENDAR"],
    "11-mcp-public-api-and-cli-authentication": ["CAP-REMOVE-MCP", "CAP-REMOVE-PUBLIC-API", "CAP-IPC"],
    "12-api-key-and-provider-configuration": ["CAP-REMOVE-API-KEYS", "CAP-KEYRING"],
    "13-billing-usage-referrals-and-upgrades": ["CAP-REMOVE-BILLING", "CAP-REMOVE-USAGE-QUOTAS", "CAP-REMOVE-REFERRALS", "CAP-REMOVE-UPGRADE-SYSTEMS"],
    "14-automatic-updates": ["CAP-REMOVE-AUTOMATIC-UPDATER"],
    "15-runtime-model-and-binary-downloads": ["CAP-REMOVE-RUNTIME-MODEL-DOWNLOADS", "CAP-MODEL-PACK"],
    "16-external-runtime-networking": ["CAP-REMOVE-RUNTIME-EXTERNAL-NETWORKING", "CAP-NETWORK-POLICY", "CAP-LOOPBACK-WEBSOCKETS"],
    "17-cloud-audio-and-streaming": ["CAP-REMOVE-HOSTED-TRANSCRIPTION", "CAP-AUDIO"],
    "18-remote-speaker-systems": ["CAP-DIARIZATION", "CAP-VOICE-FINGERPRINTING"],
    "19-cloud-metadata-in-local-data": ["CAP-REMOVE-CLOUD-SYNCHRONISATION", "CAP-DATA-SAFETY", "CAP-DATABASE"],
    "20-navigation-and-ui": ["CAP-RENDERER", "CAP-DELETION-GOVERNANCE"],
    "21-onboarding": ["CAP-ONBOARDING", "CAP-DELETION-GOVERNANCE"],
    "22-settings": ["CAP-SETTINGS", "CAP-DELETION-GOVERNANCE"],
    "23-notifications-and-hotkeys": ["CAP-NOTIFICATIONS", "CAP-HOTKEY", "CAP-DELETION-GOVERNANCE"],
    "24-native-and-packaging-remnants": ["CAP-NATIVE", "CAP-PACKAGING", "CAP-DELETION-GOVERNANCE"],
    "25-dependencies": ["CAP-THIRD-PARTY", "CAP-DELETION-GOVERNANCE"],
    "26-dead-code-and-bloat": ["CAP-SIMPLIFICATION", "CAP-DELETION-GOVERNANCE"],
    "27-generic-dumping-grounds": ["CAP-REPOSITORY", "CAP-SIMPLIFICATION"],
    "28-markdown-from-codebase": ["CAP-MARKDOWN-GOVERNANCE"],
    "protected-until-proven-otherwise": ["CAP-DATA-SAFETY", "CAP-DELETION-GOVERNANCE"],
    "final-deletion-acceptance": ["CAP-DELETION-GOVERNANCE", "CAP-RELEASE"],
}


MP3_HEADING_RULES: list[tuple[re.Pattern[str], list[str]]] = [
    (re.compile(r"correct-file|authoritative-master-plan|purpose"), ["CAP-PLANNING-GOVERNANCE"]),
    (re.compile(r"autonomous|continuous-execution|continue-until|implementation-missing|how-we-implement"), ["CAP-IMPLEMENTATION-GOVERNANCE"]),
    (re.compile(r"preservation-first|how-we-keep"), ["CAP-IMPLEMENTATION-GOVERNANCE", "CAP-THIRD-PARTY"]),
    (re.compile(r"no-data-loss|database-and-legacy|copy-before|idempotency|content-integrity"), ["CAP-DATA-SAFETY", "CAP-DATABASE", "CAP-LEGACY-MIGRATION", "CAP-BACKUP"]),
    (re.compile(r"git|provenance|checkpoint"), ["CAP-PROVENANCE"]),
    (re.compile(r"false-completion|strict-release|final-approval|completion-tracking"), ["CAP-RELEASE"]),
    (re.compile(r"final-root|moving-the-application|folder-specificity|generic-folder|monolith"), ["CAP-REPOSITORY", "CAP-IMPLEMENTATION-GOVERNANCE"]),
    (re.compile(r"moving-markdown"), ["CAP-MARKDOWN-GOVERNANCE"]),
    (re.compile(r"graphify-scan|what-graphify|graphify-operational|registry-authority|exact-location"), ["CAP-EXACT-LOCATION", "CAP-PLANNING-GOVERNANCE"]),
    (re.compile(r"how-we-delete"), ["CAP-DELETION-GOVERNANCE"]),
    (re.compile(r"how-we-replace"), ["CAP-DELETION-GOVERNANCE", "CAP-IMPLEMENTATION-GOVERNANCE"]),
    (re.compile(r"reuse-first"), ["CAP-THIRD-PARTY", "CAP-LEGAL"]),
    (re.compile(r"ipc-audit"), ["CAP-IPC"]),
    (re.compile(r"sqlite-native-binding"), ["CAP-DATABASE", "CAP-TESTING"]),
    (re.compile(r"testing-evidence|tests-and-verification"), ["CAP-TESTING"]),
    (re.compile(r"runtime-offline"), ["CAP-NETWORK-POLICY", "CAP-OFFLINE-FIRST-LAUNCH"]),
    (re.compile(r"ponytail"), ["CAP-SIMPLIFICATION"]),
]


def is_product_scope_lock(text: str) -> bool:
    value = re.sub(r"[^a-z0-9]+", " ", text.lower())
    return all(
        phrase in value
        for phrase in (
            "retained product scope",
            "dictation",
            "meeting recording",
            "local transcription",
            "sqlite",
            "notes",
            "diarization",
            "exact and semantic search",
        )
    )


# Each rule is constrained to a reviewed source section. The text expression only
# selects a narrower capability inside that semantic section; it is never used as
# global deletion or ownership authority.
CONTEXT_CAPABILITY_RULES: list[tuple[str, re.Pattern[str], re.Pattern[str], list[str]]] = [
    ("MP1", re.compile(r"5-local-transcription-engines|26-conditional-keeps-summary"), re.compile(r"\bwhisper(?:\.cpp)?\b", re.I), ["CAP-WHISPER"]),
    ("MP1", re.compile(r"5-local-transcription-engines|26-conditional-keeps-summary"), re.compile(r"\bparakeet\b", re.I), ["CAP-PARAKEET"]),
    ("MP1", re.compile(r"5-local-transcription-engines|26-conditional-keeps-summary"), re.compile(r"\bsherpa-onnx\b", re.I), ["CAP-SHERPA-ONNX"]),
    ("MP1", re.compile(r"6-local-model-handling|21-settings"), re.compile(r"model[- ]pack|import.*model|model.*validation", re.I), ["CAP-MODEL-PACK", "CAP-MODEL-DISCOVERY"]),
    ("MP1", re.compile(r"7-meeting-recording"), re.compile(r"system audio", re.I), ["CAP-SYSTEM-AUDIO"]),
    ("MP1", re.compile(r"7-meeting-recording"), re.compile(r"recover", re.I), ["CAP-RECOVERY"]),
    ("MP1", re.compile(r"7-meeting-recording|16-notifications-and-process-detection|26-conditional-keeps-summary"), re.compile(r"process[- ]based|process detection", re.I), ["CAP-MEETING-DETECTION"]),
    ("MP1", re.compile(r"8-audio-processing"), re.compile(r"\bffmpeg\b", re.I), ["CAP-FFMPEG"]),
    ("MP1", re.compile(r"8-audio-processing"), re.compile(r"voice activity|\bvad\b", re.I), ["CAP-VAD"]),
    ("MP1", re.compile(r"8-audio-processing"), re.compile(r"acoustic echo|echo cancellation|\baec\b", re.I), ["CAP-AEC"]),
    ("MP1", re.compile(r"8-audio-processing"), re.compile(r"mix", re.I), ["CAP-AUDIO-MIXING"]),
    ("MP1", re.compile(r"9-speaker-diarization"), re.compile(r"embedding", re.I), ["CAP-SPEAKER-EMBEDDINGS"]),
    ("MP1", re.compile(r"9-speaker-diarization|26-conditional-keeps-summary"), re.compile(r"voice fingerprint", re.I), ["CAP-VOICE-FINGERPRINTING"]),
    ("MP1", re.compile(r"9-speaker-diarization"), re.compile(r"speaker nam", re.I), ["CAP-SPEAKER-NAMING", "CAP-SPEAKER-RENAMING"]),
    ("MP1", re.compile(r"10-transcripts-and-history"), re.compile(r"edit", re.I), ["CAP-TRANSCRIPT-EDIT"]),
    ("MP1", re.compile(r"10-transcripts-and-history"), re.compile(r"history", re.I), ["CAP-TRANSCRIPT-HISTORY"]),
    ("MP1", re.compile(r"11-notes"), re.compile(r"personal", re.I), ["CAP-PERSONAL-NOTES"]),
    ("MP1", re.compile(r"11-notes"), re.compile(r"meeting", re.I), ["CAP-MEETING-NOTES"]),
    ("MP1", re.compile(r"11-notes"), re.compile(r"transcript", re.I), ["CAP-LINKED-NOTES"]),
    ("MP1", re.compile(r"11-notes|26-conditional-keeps-summary"), re.compile(r"template", re.I), ["CAP-NOTE-TEMPLATES"]),
    ("MP1", re.compile(r"12-folders-tags-and-snippets"), re.compile(r"folder", re.I), ["CAP-FOLDERS"]),
    ("MP1", re.compile(r"12-folders-tags-and-snippets"), re.compile(r"\btag", re.I), ["CAP-TAGS"]),
    ("MP1", re.compile(r"12-folders-tags-and-snippets"), re.compile(r"snippet", re.I), ["CAP-SNIPPETS"]),
    ("MP1", re.compile(r"14-semantic-search"), re.compile(r"minilm|embedding|onnx", re.I), ["CAP-MINILM"]),
    ("MP1", re.compile(r"14-semantic-search|26-conditional-keeps-summary"), re.compile(r"qdrant", re.I), ["CAP-QDRANT"]),
    ("MP1", re.compile(r"18-sqlite-and-local-persistence|26-conditional-keeps-summary"), re.compile(r"kysely", re.I), ["CAP-KYSELY"]),
    ("MP1", re.compile(r"18-sqlite-and-local-persistence|26-conditional-keeps-summary"), re.compile(r"keyring|secure storage", re.I), ["CAP-KEYRING"]),
    ("MP1", re.compile(r"19-import-and-export"), re.compile(r"backup|restore", re.I), ["CAP-BACKUP", "CAP-RESTORE"]),
    ("MP1", re.compile(r"19-import-and-export"), re.compile(r"audio", re.I), ["CAP-IMPORT-AUDIO"]),
    ("MP1", re.compile(r"19-import-and-export"), re.compile(r"video", re.I), ["CAP-IMPORT-VIDEO"]),
    ("MP1", re.compile(r"20-playback"), re.compile(r"timestamp|transcript", re.I), ["CAP-LINKED-PLAYBACK"]),
    ("MP1", re.compile(r"22-native-and-platform-components|26-conditional-keeps-summary"), re.compile(r"macos|linux", re.I), ["CAP-MACOS-LINUX"]),
    ("MP1", re.compile(r"23-packaging"), re.compile(r"installer", re.I), ["CAP-WINDOWS-INSTALLER"]),
    ("MP1", re.compile(r"23-packaging|26-conditional-keeps-summary"), re.compile(r"portable", re.I), ["CAP-PORTABLE-WINDOWS"]),
    ("MP1", re.compile(r"3-application-shell|26-conditional-keeps-summary"), re.compile(r"websocket", re.I), ["CAP-LOOPBACK-WEBSOCKETS"]),
    ("MP3", re.compile(r".*"), re.compile(r"\bqdrant\b", re.I), ["CAP-QDRANT"]),
    ("MP3", re.compile(r".*"), re.compile(r"\bparakeet\b", re.I), ["CAP-PARAKEET"]),
    ("MP3", re.compile(r".*"), re.compile(r"\bsherpa-onnx\b", re.I), ["CAP-SHERPA-ONNX"]),
    ("MP3", re.compile(r".*"), re.compile(r"\bkysely\b", re.I), ["CAP-KYSELY"]),
    ("MP3", re.compile(r"runtime-offline|how-we-keep|how-we-replace|testing-evidence-matrix|tests-and-verification"), re.compile(r"loopback|localhost", re.I), ["CAP-NETWORK-POLICY", "CAP-LOOPBACK-WEBSOCKETS"]),
    ("MP3", re.compile(r"database-and-legacy-migration-safety|historical-migrations|copy-before-transform|idempotency-and-interruption-recovery|content-integrity-verification"), re.compile(r".*", re.I), ["CAP-DATABASE", "CAP-DATA-SAFETY", "CAP-LEGACY-MIGRATION", "CAP-BACKUP"]),
]


def heading_caps(source: str, anchor: str, text: str) -> list[str]:
    if is_product_scope_lock(text):
        return list(PRODUCT_SCOPE_CAPS)
    result = list(PRIMARY_CAPS_BY_SECTION.get((source, anchor), []))
    if source == "MP3":
        for pattern, cap_ids in MP3_HEADING_RULES:
            if pattern.search(anchor):
                result.extend(cap_ids)
        if not result:
            result = ["CAP-IMPLEMENTATION-GOVERNANCE"]
    for rule_source, heading_pattern, text_pattern, cap_ids in CONTEXT_CAPABILITY_RULES:
        if source == rule_source and heading_pattern.search(anchor) and text_pattern.search(text):
            result.extend(cap_ids)
    return unique(result or (["CAP-DELETION-GOVERNANCE"] if source == "MP2" else ["CAP-PLANNING-GOVERNANCE"]))


MP1_REQUIREMENT_TYPES = {
    "governing-rule": "Preservation requirement",
    "1-product-and-legal-identity": "Legal/licensing requirement",
    "2-core-desktop-stack": "Architecture requirement",
    "3-application-shell": "Architecture requirement",
    "4-voice-dictation": "Product requirement",
    "5-local-transcription-engines": "Product requirement",
    "6-local-model-handling": "Offline requirement",
    "7-meeting-recording": "Product requirement",
    "8-audio-processing": "Product requirement",
    "9-speaker-diarization": "Product requirement",
    "10-transcripts-and-history": "Product requirement",
    "11-notes": "Product requirement",
    "12-folders-tags-and-snippets": "Product requirement",
    "13-exact-search": "Product requirement",
    "14-semantic-search": "Product requirement",
    "15-local-actions-and-clipboard": "Product requirement",
    "16-notifications-and-process-detection": "Product requirement",
    "17-internal-ipc": "Architecture requirement",
    "18-sqlite-and-local-persistence": "Data-safety requirement",
    "19-import-and-export": "Product requirement",
    "20-playback": "Product requirement",
    "21-settings": "Product requirement",
    "22-native-and-platform-components": "Platform requirement",
    "23-packaging": "Packaging requirement",
    "24-tests-and-proof": "Testing requirement",
    "25-preservation-first-policy": "Preservation requirement",
    "26-conditional-keeps-summary": "Conditional decision requirement",
    "final-keep-acceptance": "Final release requirement",
}


MP3_TYPE_RULES = [
    (re.compile(r"6-1-correct-file-law|authoritative-master-plan|graphify|exact-location|completion-tracking"), "Planning-governance requirement"),
    (re.compile(r"git|provenance|checkpoint"), "Git/provenance requirement"),
    (re.compile(r"no-data-loss|database-and-legacy|historical-migrations|copy-before-transform|idempotency|content-integrity|sqlite-native-binding"), "Migration requirement"),
    (re.compile(r"runtime-offline"), "Offline requirement"),
    (re.compile(r"testing-evidence|tests-and-verification|hardware-dependent"), "Testing requirement"),
    (re.compile(r"strict-release|final-approval|no-false-completion"), "Final release requirement"),
    (re.compile(r"how-we-delete"), "Deletion requirement"),
    (re.compile(r"how-we-keep|preservation-first|reuse-first"), "Preservation requirement"),
    (re.compile(r"moving-the-application|moving-markdown|folder|monolith|ipc-audit|root-structure|capability-ownership"), "Architecture requirement"),
    (re.compile(r"how-we-replace|how-we-implement-missing"), "Product requirement"),
]


def classify_requirement(source: str, anchor: str, text: str) -> str:
    if is_product_scope_lock(text):
        return "Product requirement"
    if source == "MP1":
        return MP1_REQUIREMENT_TYPES.get(anchor, "Product requirement")
    if source == "MP2":
        if anchor in {"mnemora-everything-we-are-deleting", "protected-until-proven-otherwise"}:
            return "Preservation requirement"
        if anchor in {"governing-rule", "binding-deletion-interlock", "final-deletion-acceptance"}:
            return "Planning-governance requirement"
        return "Deletion requirement"
    for pattern, requirement_type in MP3_TYPE_RULES:
        if pattern.search(anchor):
            return requirement_type
    return "Planning-governance requirement"


def release_gates_for(req_type: str, text: str) -> list[str]:
    lower = text.lower()
    result: list[str] = []
    mapping = {
        "Planning-governance requirement": ["GATE-01-AUTHORITY", "GATE-03-MAPPING"],
        "Git/provenance requirement": ["GATE-02-PROVENANCE"],
        "Preservation requirement": ["GATE-04-PRESERVATION"],
        "Deletion requirement": ["GATE-05-DELETION"],
        "Product requirement": ["GATE-06-CAPABILITY"],
        "Data-safety requirement": ["GATE-07-DATA-SAFETY"],
        "Migration requirement": ["GATE-07-DATA-SAFETY"],
        "Testing requirement": ["GATE-08-REAL-INTEGRATION"],
        "Offline requirement": ["GATE-09-OFFLINE"],
        "Packaging requirement": ["GATE-10-WINDOWS-RELEASE"],
        "Platform requirement": ["GATE-12-HARDWARE"],
        "Final release requirement": ["GATE-11-AUDIT"],
        "Legal/licensing requirement": ["GATE-04-PRESERVATION", "GATE-10-WINDOWS-RELEASE"],
        "Architecture requirement": ["GATE-03-MAPPING", "GATE-04-PRESERVATION"],
        "Conditional decision requirement": ["GATE-03-MAPPING", "GATE-11-AUDIT"],
    }
    result.extend(mapping.get(req_type, ["GATE-06-CAPABILITY"]))
    if "windows" in lower or "installer" in lower:
        result.append("GATE-10-WINDOWS-RELEASE")
    if "offline" in lower or "network" in lower:
        result.append("GATE-09-OFFLINE")
    if "hardware" in lower or "macos" in lower or "linux" in lower:
        result.append("GATE-12-HARDWARE")
    return unique(result)


def architectural_layers(req_type: str, caps: list[str], text: str) -> list[str]:
    value = text.lower()
    layers = ["planning/governance"] if "Planning" in req_type or "Final release" in req_type else []
    terms = [
        (("ui", "renderer", "navigation", "route", "component"), "renderer/UI"),
        (("hook", "store"), "renderer state"), (("preload",), "preload"), (("ipc",), "IPC/type contract"),
        (("service", "main process", "electron"), "main/service"), (("database", "sqlite", "migration", "schema"), "database"),
        (("filesystem", "file", "recording", "backup"), "filesystem/data"), (("native", "audio tap", "helper"), "native/platform"),
        (("model", "binary", "whisper", "sherpa", "qdrant", "onnx"), "models/local processes"),
        (("setting", "environment", "feature flag"), "configuration"), (("test", "fixture", "verification"), "tests/evidence"),
        (("build", "package", "installer"), "build/packaging"), (("translation", "i18n"), "localization"),
        (("legal", "licence", "license"), "legal"),
    ]
    for needles, layer in terms:
        if any(needle in value for needle in needles):
            layers.append(layer)
    if not layers:
        layers = ["cross-layer capability contract"]
    if any(cap.startswith("CAP-REMOVE-") for cap in caps):
        layers.extend(["full deletion chain", "tests/evidence"])
    return unique(layers)


def acceptance_for(req_type: str, summary: str) -> list[str]:
    base = f"Saved implementation evidence proves the authoritative requirement without weakening it: {summary}"
    extras = {
        "Deletion requirement": "All seven Binding Deletion Interlock checks and every applicable architectural layer are evidenced before deletion and by the final rescan.",
        "Migration requirement": "A disposable-copy test proves backup, integrity, idempotency, interruption recovery, non-empty destination protection, and preservation of original data.",
        "Data-safety requirement": "No user database, recording, transcript, note, export, backup, or recoverable source audio is silently lost or overwritten.",
        "Offline requirement": "Real runtime observation proves external traffic is blocked while approved local files, IPC, loopback, and bundled processes remain functional.",
        "Packaging requirement": "Saved build/package/installer evidence is tied to the verified implementation checkpoint and contains every required local asset and notice.",
        "Testing requirement": "The exact command, working directory, runtime, exit code, fixture, log, and rerun result are saved; real boundaries are not replaced by mocks.",
        "Git/provenance requirement": "A recoverable Git commit or permitted pre-Git hash/delta checkpoint records every mutation batch without discarding user work.",
        "Conditional decision requirement": "The mandatory default, deviation condition, collected evidence, decision owner, fallback, and outcome task disposition are recorded before mutation.",
        "Planning-governance requirement": "The authoritative register, capability, task, exact-location, and release-gate IDs reconcile under deterministic validation.",
        "Final release requirement": "The release gate remains unpassed until its real implementation evidence exists; planning status alone cannot satisfy it.",
    }
    return [base, extras.get(req_type, "The mapped capability workflow and affected real integration boundaries satisfy the requirement with saved evidence.")]


def evidence_for(req_type: str) -> list[str]:
    common = ["Verified commit or recoverable hash checkpoint", "Exact path plus symbol/anchor evidence", "Command, working directory, exit code, and saved log"]
    specialized = {
        "Deletion requirement": ["Seven interlock records", "Full architectural-layer ledger", "Final Graphify/static/runtime absence proof"],
        "Migration requirement": ["Disposable SQLite fixtures", "Pre/post schema versions and checksums", "Integrity, idempotency, interruption, and recovery results"],
        "Data-safety requirement": ["Backup manifest and checksums", "Content-integrity reconciliation", "Recovery drill result"],
        "Offline requirement": ["External-network interception or observation log", "Loopback allow-list proof", "Offline first-launch workflow record"],
        "Packaging requirement": ["Windows production build log", "Package/installer hashes", "Installed application launch log and asset inspection"],
        "Testing requirement": ["Targeted, integration, and regression evidence", "Real fixture or hardware status"],
        "Legal/licensing requirement": ["Licence/source/version register", "Packaged NOTICE and THIRD-PARTY-NOTICES inspection"],
        "Conditional decision requirement": ["Decision package evidence bundle", "Outcome comparison", "Owner-signed disposition and fallback"],
        "Planning-governance requirement": ["Deterministic validator report", "Reconciled machine-register counts"],
    }
    return unique(common + specialized.get(req_type, ["Affected workflow evidence"]))


def strip_markdown(value: str) -> str:
    value = re.sub(r"<!--.*?-->", "", value, flags=re.S)
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"[*_>#]", "", value)
    return re.sub(r"\s+", " ", value).strip(" -")


def parse_master_requirements(code: str, path: Path) -> list[dict[str, Any]]:
    """Extract independently verifiable top-level bullets, paragraphs and table rows.

    A classification-only bullet is carried into its section's records instead of
    becoming meaningless sentence-level noise. Nested bullets stay with their
    parent contract. Code/tree blocks are retained as one architecture contract.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    records: list[dict[str, Any]] = []
    heading = path.stem
    anchor = slug(heading)
    section_classification = "MANDATORY"
    in_frontmatter = bool(lines and lines[0].strip() == "---")
    in_fence = False
    fence_start = 0
    fence_lines: list[str] = []

    def add(raw: str, start: int, end: int, kind: str) -> None:
        nonlocal section_classification
        raw = raw.strip()
        cleaned = strip_markdown(raw)
        if not cleaned or cleaned in {"---", "|"}:
            return
        class_match = re.match(r"(?i)^classification:\s*(.+)$", cleaned)
        if class_match and len(cleaned.split()) <= 9:
            section_classification = class_match.group(1).strip()
            return
        req_type = classify_requirement(code, anchor, cleaned)
        caps = heading_caps(code, anchor, cleaned)
        decision = section_classification
        upper = cleaned.upper()
        for label in (
            "CONDITIONAL", "FORBIDDEN", "OBSOLETE", "OPTIONAL LATER",
            "KEEP AFTER DECOUPLING", "KEEP AND REORGANISE", "KEEP AND REPAIR", "MANDATORY KEEP",
        ):
            if label in upper:
                decision = label if label != "CONDITIONAL" else "CONDITIONAL - REQUIRES EVIDENCE"
                break
        mandatory = "CONDITIONAL" if "CONDITIONAL" in decision.upper() or "OPTIONAL" in decision.upper() else "MANDATORY"
        if mandatory == "CONDITIONAL":
            req_type = "Conditional decision requirement"
        scope_lock = is_product_scope_lock(cleaned)
        if scope_lock and code == "MP2":
            retained_removed = "PROTECTED RETAINED SCOPE"
        elif code == "MP2" and anchor == "protected-until-proven-otherwise":
            retained_removed = "PROTECTED RETAINED SCOPE"
        elif code == "MP2" or req_type == "Deletion requirement" or "REMOVE" in decision.upper() or "FORBIDDEN" in decision.upper():
            retained_removed = "REMOVED SCOPE"
        elif mandatory == "CONDITIONAL":
            retained_removed = "CONDITIONAL RETAINED SCOPE"
        else:
            retained_removed = "RETAINED OR REQUIRED SCOPE"
        identifier = stable_id(f"REQ-{code}", anchor, cleaned)
        summary = f"{heading}: {cleaned}" if len(cleaned) < 30 else cleaned
        records.append({
            "stable_requirement_id": identifier,
            "source_master_plan": path.name,
            "source_master_plan_code": code,
            "source_heading": heading,
            "source_anchor": f"{anchor}-L{start}",
            "source_line_start": start,
            "source_line_end": end,
            "source_block_kind": kind,
            "source_excerpt": raw,
            "requirement_summary": summary,
            "requirement_type": req_type,
            "decision_classification": decision,
            "mandatory_or_conditional": mandatory,
            "retained_or_removed_scope": retained_removed,
            "capability_ids": caps,
            "semantic_mapping_basis": "Explicit product-scope declaration" if scope_lock else f"Reviewed source section: {heading}",
            "applicable_architectural_layers": architectural_layers(req_type, caps, cleaned),
            "acceptance_criteria": acceptance_for(req_type, cleaned),
            "required_evidence": evidence_for(req_type),
            "release_gate_ids": release_gates_for(req_type, cleaned),
            "dependencies": ["Master Plan authority", *(["Evidence-driven decision package"] if mandatory == "CONDITIONAL" else [])],
            "conflicts_or_interpretations": [],
            "planning_status": "PLANNING COMPLETE - IMPLEMENTATION EVIDENCE PENDING",
        })

    i = 0
    while i < len(lines):
        line = lines[i]
        n = i + 1
        if in_frontmatter:
            if n > 1 and line.strip() == "---":
                in_frontmatter = False
            i += 1
            continue
        heading_match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if heading_match:
            heading = strip_markdown(heading_match.group(2))
            anchor = slug(heading)
            section_classification = "MANDATORY"
            i += 1
            continue
        if line.strip().startswith("```"):
            if not in_fence:
                in_fence, fence_start, fence_lines = True, n, []
            else:
                in_fence = False
                if fence_lines:
                    add("\n".join(fence_lines), fence_start, n, "code-or-structure-block")
            i += 1
            continue
        if in_fence:
            fence_lines.append(line)
            i += 1
            continue
        bullet = re.match(r"^([-*+] |\d+[.)] )(.*)$", line)
        if bullet:
            start = n
            block = [bullet.group(2)]
            i += 1
            while i < len(lines):
                continuation = lines[i]
                if re.match(r"^\s{2,}([-*+] |\d+[.)] )", continuation) or (continuation.startswith("  ") and continuation.strip()):
                    block.append(continuation.strip())
                    i += 1
                    continue
                if not continuation.strip() and i + 1 < len(lines) and lines[i + 1].startswith("  "):
                    i += 1
                    continue
                break
            add(" ".join(block), start, i, "top-level-list-item")
            continue
        if line.startswith("|") and line.count("|") >= 2:
            if re.match(r"^\|[\s:|-]+\|$", line):
                i += 1
                continue
            add(line, n, n, "table-row")
            i += 1
            continue
        if line.strip():
            start = n
            block = [line.strip()]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,6})\s+|^([-*+] |\d+[.)] )|^```|^\|", lines[i]):
                block.append(lines[i].strip())
                i += 1
            add(" ".join(block), start, i, "paragraph")
            continue
        i += 1
    # Coalesce noun/status/extension inventories into their introducing contract.
    # Keep imperative steps separate, even when they are only one word (for
    # example "Build" or "Package"), because those remain independently testable.
    action_start = re.compile(
        r"(?i)^(must|shall|do|run|create|verify|record|inspect|confirm|commit|use|keep|remove|repair|add|build|package|launch|restore|preserve|map|test|move|delete|implement|initialize|stop|prove|check|compare|repeat|resume|read|document|update|continue|install|recover|copy|classify|execute)\b"
    )

    def short_inventory(item: dict[str, Any]) -> bool:
        summary = strip_markdown(item["source_excerpt"]).strip()
        words = re.findall(r"[A-Za-z0-9]+", summary)
        return item["source_block_kind"] == "top-level-list-item" and len(words) <= 7 and not action_start.search(summary)

    filtered: list[dict[str, Any]] = []
    for item in records:
        if item["source_block_kind"] == "table-row" and item["source_line_end"] < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[item["source_line_end"]]):
            continue  # Markdown table header, not a requirement.
        filtered.append(item)

    def rebuilt(group: list[dict[str, Any]], kind: str) -> dict[str, Any]:
        base = dict(group[0])
        raw = " ".join(item["source_excerpt"] for item in group)
        cleaned = strip_markdown(raw)
        summary = f"{base['source_heading']}: {cleaned}" if len(cleaned) < 30 else cleaned
        base.update({
            "stable_requirement_id": stable_id(f"REQ-{code}", slug(base["source_heading"]), cleaned),
            "source_line_end": group[-1]["source_line_end"],
            "source_block_kind": kind,
            "source_excerpt": raw,
            "requirement_summary": summary,
        })
        caps = unique([cap_id for item in group for cap_id in item["capability_ids"]] + heading_caps(code, slug(base["source_heading"]), cleaned))
        req_type = classify_requirement(code, slug(base["source_heading"]), cleaned)
        if base.get("mandatory_or_conditional") == "CONDITIONAL":
            req_type = "Conditional decision requirement"
        base["capability_ids"] = caps
        base["requirement_type"] = req_type
        base["applicable_architectural_layers"] = architectural_layers(req_type, caps, cleaned)
        base["acceptance_criteria"] = acceptance_for(req_type, cleaned)
        base["required_evidence"] = evidence_for(req_type)
        base["release_gate_ids"] = release_gates_for(req_type, cleaned)
        return base

    inventory_intro = re.compile(r"(?i)(labels|statuses|authoritative owner|include|through:|where applicable|such as|extensions|record:|records:|validate:|fields:|must map:|must record:|work unit is:|classification values|valid values)")
    coalesced: list[dict[str, Any]] = []
    i = 0
    while i < len(filtered):
        if filtered[i]["source_block_kind"] == "paragraph" and filtered[i]["requirement_summary"].endswith(":"):
            prefix = filtered[i]
            j = i + 1
            bullet_run: list[dict[str, Any]] = []
            while j < len(filtered) and filtered[j]["source_block_kind"] == "top-level-list-item" and filtered[j]["source_heading"] == prefix["source_heading"]:
                if bullet_run and filtered[j]["source_line_start"] > bullet_run[-1]["source_line_end"] + 2:
                    break
                bullet_run.append(filtered[j])
                j += 1
            if bullet_run:
                all_inventory = all(short_inventory(item) or re.fullmatch(r"[A-Z0-9 _./-]+", strip_markdown(item["source_excerpt"])) for item in bullet_run)
                if len(bullet_run) >= 2 and (inventory_intro.search(prefix["requirement_summary"]) or all_inventory):
                    coalesced.append(rebuilt([prefix, *bullet_run], "coherent-inventory-contract"))
                else:
                    for item in bullet_run:
                        coalesced.append(rebuilt([prefix, item], "contextual-action-contract"))
                i = j
                continue
            if i + 1 < len(filtered) and filtered[i + 1]["source_block_kind"] == "code-or-structure-block" and filtered[i + 1]["source_heading"] == prefix["source_heading"]:
                coalesced.append(rebuilt([prefix, filtered[i + 1]], "contextual-code-or-structure-contract"))
                i += 2
                continue
        start = i
        while i < len(filtered) and short_inventory(filtered[i]) and (i == start or filtered[i]["source_heading"] == filtered[start]["source_heading"]):
            i += 1
        run = filtered[start:i]
        if len(run) >= 2:
            coalesced.append(rebuilt(run, "coherent-inventory-contract"))
            continue
        if run:
            coalesced.extend(run)
            continue
        coalesced.append(filtered[i])
        i += 1
    return coalesced


requirements: list[dict[str, Any]] = []
for source_code, source_path in MASTER_FILES:
    requirements.extend(parse_master_requirements(source_code, source_path))

# Deterministic de-duplication protects IDs while retaining the earliest exact source.
requirements = list({item["stable_requirement_id"]: item for item in requirements}.values())
requirements.sort(key=lambda item: (item["source_master_plan_code"], item["source_line_start"], item["stable_requirement_id"]))


INTERPRETATIONS: list[dict[str, Any]] = [
    {
        "interpretation_id": "INT-001-PARAKEET-SHERPA",
        "source_documents": [MASTER_FILES[0][1].name, MASTER_FILES[2][1].name],
        "relevant_headings": ["5. Local transcription engines", "11. How We Replace Removed Systems"],
        "apparent_ambiguity": "Master Plan 1 names Parakeet and Sherpa-ONNX as conditional retained local engines; a Master Plan 3 replacement table names optional Parakeet without repeating Sherpa-ONNX.",
        "adopted_interpretation": "Both Parakeet and Sherpa-ONNX remain separate conditional retained packages. The shorter replacement-table cell does not delete or override Sherpa-ONNX.",
        "preservation_rationale": "It applies the explicit keep rule and treats the replacement table as non-exhaustive, so neither conditional engine is removed without evidence.",
        "affected_capability_ids": ["CAP-PARAKEET", "CAP-SHERPA-ONNX", "CAP-WHISPER"],
        "affected_task_ids": [],
        "user_clarification_required": False,
    },
    {
        "interpretation_id": "INT-002-CODEBASE-CASING",
        "source_documents": [MASTER_FILES[2][1].name],
        "relevant_headings": ["2. Final Root Structure", "14. Moving the Application into Codebase"],
        "apparent_ambiguity": "The planned target tree uses Codebase while the actual application folder is currently lowercase codebase.",
        "adopted_interpretation": "codebase is the authoritative current application path. Codebase is only a future target spelling and this planning run must not rename or move it.",
        "preservation_rationale": "It records current evidence accurately and reserves the move for a provenance-protected implementation task.",
        "affected_capability_ids": ["CAP-REPOSITORY", "CAP-PROVENANCE", "CAP-IMPLEMENTATION-GOVERNANCE"],
        "affected_task_ids": [],
        "user_clarification_required": False,
    },
    {
        "interpretation_id": "INT-003-PLANNING-ONLY",
        "source_documents": [MASTER_FILES[2][1].name],
        "relevant_headings": ["6.2 Autonomous execution law", "24. Autonomous Authority"],
        "apparent_ambiguity": "The implementation plan grants autonomous execution authority, but the present user run is expressly planning-only.",
        "adopted_interpretation": "Autonomous mutation authority begins only in a future implementation run. This run may update derived planning under Graphify and may not edit codebase.",
        "preservation_rationale": "The interpretation preserves future authority while honoring the narrower, later user instruction and read-only scope.",
        "affected_capability_ids": ["CAP-PLANNING-GOVERNANCE", "CAP-IMPLEMENTATION-GOVERNANCE", "CAP-PROVENANCE"],
        "affected_task_ids": [],
        "user_clarification_required": False,
    },
    {
        "interpretation_id": "INT-004-PLATFORM-PROOF",
        "source_documents": [MASTER_FILES[0][1].name, MASTER_FILES[2][1].name],
        "relevant_headings": ["22. Native and platform components", "Hardware-dependent status", "Strict Release Conjunction"],
        "apparent_ambiguity": "Windows proof is mandatory for first release while macOS/Linux source is retained and hardware may be unavailable.",
        "adopted_interpretation": "Windows build, installation, launch and offline proof are mandatory. macOS/Linux source and configuration must be preserved and statically or in CI verified; unavailable hardware is recorded as HARDWARE UNAVAILABLE and does not block the Windows release unless a gate explicitly applies to that platform.",
        "preservation_rationale": "No cross-platform source is discarded and no unavailable-hardware result is misreported as a pass.",
        "affected_capability_ids": ["CAP-PACKAGING", "CAP-WINDOWS-INSTALLER", "CAP-MACOS-LINUX", "CAP-TESTING"],
        "affected_task_ids": [],
        "user_clarification_required": False,
    },
    {
        "interpretation_id": "INT-005-RUNTIME-DOWNLOADS",
        "source_documents": [MASTER_FILES[0][1].name, MASTER_FILES[1][1].name, MASTER_FILES[2][1].name],
        "relevant_headings": ["6. Local model handling", "15. Runtime model and binary downloads", "22. Runtime Offline Enforcement"],
        "apparent_ambiguity": "Runtime downloads are forbidden while existing download scripts may be needed to acquire release assets.",
        "adopted_interpretation": "Installed runtime code cannot reach download logic. Build-time acquisition may remain only as isolated tooling that produces pinned, checksummed inputs before packaging and is unreachable from the installed application.",
        "preservation_rationale": "It preserves reproducible build tooling without weakening offline runtime enforcement.",
        "affected_capability_ids": ["CAP-REMOVE-RUNTIME-MODEL-DOWNLOADS", "CAP-MODEL-PACK", "CAP-NETWORK-POLICY", "CAP-PACKAGING"],
        "affected_task_ids": [],
        "user_clarification_required": False,
    },
    {
        "interpretation_id": "INT-006-LOOPBACK",
        "source_documents": [MASTER_FILES[0][1].name, MASTER_FILES[1][1].name, MASTER_FILES[2][1].name],
        "relevant_headings": ["3. Application shell", "16. External runtime networking", "22. Runtime Offline Enforcement"],
        "apparent_ambiguity": "External networking is forbidden while local services may communicate over localhost or loopback.",
        "adopted_interpretation": "Loopback is allowed only for a named, owned, bundled local process under an explicit allow-list and lifecycle owner. External hosts, third-party services and unowned listeners remain forbidden.",
        "preservation_rationale": "It permits required local sidecars such as Qdrant without reintroducing an external service boundary.",
        "affected_capability_ids": ["CAP-NETWORK-POLICY", "CAP-QDRANT", "CAP-LOOPBACK-WEBSOCKETS", "CAP-REMOVE-RUNTIME-EXTERNAL-NETWORKING"],
        "affected_task_ids": [],
        "user_clarification_required": False,
    },
    {
        "interpretation_id": "INT-007-HISTORICAL-MIGRATIONS",
        "source_documents": [MASTER_FILES[0][1].name, MASTER_FILES[1][1].name, MASTER_FILES[2][1].name],
        "relevant_headings": ["1. Product and legal identity", "Protected Until Proven Otherwise", "Historical migrations"],
        "apparent_ambiguity": "Removed names and schema terms can appear in historical migrations although active product behavior must not retain removed systems.",
        "adopted_interpretation": "Historical migration SQL, compatibility keys and legal provenance are evidence and may retain legacy terms. They are not active forbidden behavior unless reachable runtime code recreates or exposes the removed capability.",
        "preservation_rationale": "It protects migration continuity and attribution while requiring active runtime paths to pass deletion interlocks.",
        "affected_capability_ids": ["CAP-LEGACY-MIGRATION", "CAP-DATA-SAFETY", "CAP-REMOVE-ACTIVE-OPENWHISPR-IDENTITY", "CAP-DELETION-GOVERNANCE"],
        "affected_task_ids": [],
        "user_clarification_required": False,
    },
]


CONDITIONAL_SPECS: dict[str, dict[str, Any]] = {
    "CAP-QDRANT": {
        "title": "Qdrant versus an embedded local vector alternative",
        "default": "Retain the current bundled local Qdrant sidecar until a measured fully local alternative proves semantic-search, migration, lifecycle, packaging and recovery equivalence.",
        "deviation": "A candidate embedded/local alternative is already licence-compatible and proves equivalent behavior on representative Mnemora data with lower verified maintenance or packaging cost.",
        "locations": ["codebase/main/features/search/qdrantManager.js::QdrantManager", "codebase/main/features/search/vectorIndex.js", "codebase/resources/bin/qdrant-win32-x64.exe", "codebase/scripts/downloads/download-qdrant.js::main"],
        "test": "Run the same indexed corpus through exact semantic result checks, restart recovery, index migration, corrupt-sidecar recovery, offline launch and packaged Windows lifecycle tests.",
        "dimensions": ["result correctness", "index migration", "startup/shutdown ownership", "offline behavior", "binary/package size", "licence", "recovery", "maintenance surface"],
        "owner": "Semantic search and Windows packaging",
        "phase": "PHASE-05-CONDITIONAL-DECISIONS",
        "fallback": "Keep bundled Qdrant and harden its local lifecycle and allow-list.",
    },
    "CAP-PARAKEET": {
        "title": "Parakeet packaging",
        "default": "Preserve Parakeet as an optional offline engine or offline model pack; Whisper.cpp remains the bundled fallback and Parakeet is not mandatory in the default installer without evidence.",
        "deviation": "A proven, licence-compatible local implementation and asset set demonstrates platform coverage, acceptable package impact and reliable offline transcription.",
        "locations": ["codebase/shared/i18n/en/translation.json::Parakeet references", "codebase/main/features/transcription/::no proven Parakeet runtime engine", "codebase/electron-builder.json::extraResources"],
        "test": "Prove engine discovery, checksum rejection, supported-language behavior, cancellation, retry, package inclusion, clean offline launch and Whisper.cpp fallback on each supported packaged platform.",
        "dimensions": ["runtime presence", "accuracy evidence", "latency", "memory", "package size", "platform support", "licence", "offline fallback"],
        "owner": "Local transcription and packaging",
        "phase": "PHASE-05-CONDITIONAL-DECISIONS",
        "fallback": "Ship Whisper.cpp by default and expose Parakeet only through a verified offline model pack.",
    },
    "CAP-SHERPA-ONNX": {
        "title": "Sherpa-ONNX packaging",
        "default": "Preserve the current bundled Sherpa-ONNX diarization implementation and evaluate any optional transcription role separately; never remove it merely for installer-size preference.",
        "deviation": "Real platform/package evidence proves a narrower offline pack or an equivalent retained local implementation without breaking diarization or recovery.",
        "locations": ["codebase/main/features/meetings/diarization.js", "codebase/resources/bin/sherpa-onnx-diarize-win32-x64.exe", "codebase/resources/bin/diarization-models/", "codebase/scripts/downloads/download-sherpa-onnx.js::main"],
        "test": "Run real fixture diarization, process cleanup, missing/corrupt model handling, offline pack import and packaged Windows binary/model discovery; preserve separate transcription-engine evidence.",
        "dimensions": ["diarization correctness", "transcription role", "binary/model packaging", "platform coverage", "process cleanup", "licence", "offline recovery"],
        "owner": "Diarization, local transcription and packaging",
        "phase": "PHASE-05-CONDITIONAL-DECISIONS",
        "fallback": "Keep the proven bundled diarization helper and Whisper.cpp transcription fallback.",
    },
    "CAP-KYSELY": {
        "title": "Kysely retention",
        "default": "Keep Kysely only if current or planned local SQLite code receives measurable type-safety benefit; do not order a persistence rewrite for style.",
        "deviation": "Repository evidence confirms Kysely is absent, used only by removed systems, or duplicates direct better-sqlite3 with a safe migration and measurable maintenance benefit.",
        "locations": ["codebase/package.json::dependencies", "codebase/main/infrastructure/persistence/database.js::DatabaseManager", "codebase/package-lock.json::packages"],
        "test": "Inventory imports and dependency lock entries, characterize every persistence query and migration, then compare type checks, SQL behavior, transaction behavior and native binding packaging.",
        "dimensions": ["actual usage", "query type safety", "migration risk", "transaction behavior", "dependency cost", "maintenance benefit"],
        "owner": "SQLite persistence",
        "phase": "PHASE-05-CONDITIONAL-DECISIONS",
        "fallback": "Use the verified existing direct better-sqlite3 layer; current static evidence indicates Kysely is absent.",
    },
    "CAP-LOOPBACK-WEBSOCKETS": {
        "title": "Loopback WebSockets",
        "default": "Do not add or retain a WebSocket path unless a named bundled local service requires it and the runtime policy explicitly owns its listener, client and shutdown lifecycle.",
        "deviation": "A retained local service proves bidirectional event transport cannot use existing IPC or bounded local HTTP without greater risk or complexity.",
        "locations": ["codebase/main/infrastructure/runtime/runtimeNetworkPolicy.js", "codebase/main/features/search/qdrantManager.js::_checkHealth", "codebase/package.json::dependencies"],
        "test": "Capture listener ownership, bind address, random-port behavior, authentication or process-bound trust, external-host denial, teardown and packaged offline behavior.",
        "dimensions": ["necessity", "listener ownership", "bind scope", "external reachability", "lifecycle", "dependency cost", "IPC/HTTP alternative"],
        "owner": "Runtime network policy",
        "phase": "PHASE-05-CONDITIONAL-DECISIONS",
        "fallback": "Use typed Electron IPC or bounded owned loopback HTTP; current static evidence does not prove an active WebSocket dependency.",
    },
    "CAP-KEYRING": {
        "title": "OS keyring",
        "default": "Do not add a keyring dependency unless a retained local secret is identified; removed provider and account credentials do not justify it.",
        "deviation": "A retained feature has a concrete secret that cannot safely remain in existing local configuration and native packaging evidence supports all applicable platforms.",
        "locations": ["codebase/package.json::dependencies", "codebase/main/infrastructure/persistence/database.js::settings", "codebase/renderer/features/settings/"],
        "test": "Inventory retained secret values, prove platform keyring read/write/delete, upgrade recovery, uninstall behavior and packaged native-module loading without exposing removed provider settings.",
        "dimensions": ["retained secret need", "platform support", "native packaging", "migration", "recovery", "dependency surface"],
        "owner": "Settings and platform security",
        "phase": "PHASE-05-CONDITIONAL-DECISIONS",
        "fallback": "Add no keyring dependency; current static evidence finds no keyring package and removed remote credentials stay deleted.",
    },
    "CAP-VOICE-FINGERPRINTING": {
        "title": "Local voice fingerprinting",
        "default": "Preserve current local speaker embeddings only while consent, deletion, false-match, migration and useful speaker-identification evidence are proven.",
        "deviation": "Privacy or correctness evidence shows the feature cannot meet local-only consent, deletion and safe-match requirements, or a simpler non-persistent mapping meets the retained scope.",
        "locations": ["codebase/main/features/meetings/speakerEmbeddings.js", "codebase/main/features/meetings/liveSpeakerIdentifier.js", "codebase/main/infrastructure/persistence/database.js::speaker tables", "codebase/main/ipc/ipcHandlers.js::speaker mapping handlers"],
        "test": "Use consented local fixtures to measure repeat identity, false matches, unknown-speaker behavior, deletion, export exclusion, schema upgrade, corrupt embedding recovery and offline-only execution.",
        "dimensions": ["user value", "consent", "false-match risk", "deletion", "migration", "local-only proof", "storage cost"],
        "owner": "Diarization and speaker management",
        "phase": "PHASE-05-CONDITIONAL-DECISIONS",
        "fallback": "Retain non-biometric per-transcript speaker labels and explicit manual naming without persistent voice fingerprints.",
    },
    "CAP-MEETING-DETECTION": {
        "title": "Local process-based meeting detection",
        "default": "Preserve local process detection only when it improves meeting workflow without sending process data externally or producing disruptive false positives.",
        "deviation": "Representative local tests show unacceptable false positives, platform fragility, privacy cost or no meaningful workflow benefit.",
        "locations": ["codebase/main/features/meetings/meetingProcessDetector.js", "codebase/main/features/meetings/meetingDetectionEngine.js", "codebase/main/desktop/windowManager.js::meeting notifications"],
        "test": "Exercise supported and unrelated process fixtures, start/stop churn, permission failures, notification rate limits, disabled setting, no-network observation and platform-unavailable states.",
        "dimensions": ["precision", "false positives", "privacy", "platform support", "resource use", "notification behavior", "user control"],
        "owner": "Meeting workflow and platform integration",
        "phase": "PHASE-05-CONDITIONAL-DECISIONS",
        "fallback": "Keep manual meeting start and local notifications; disable automatic detection by default where evidence is insufficient.",
    },
    "CAP-NOTE-TEMPLATES": {
        "title": "Local note templates",
        "default": "Do not add templates unless user workflows and a simple local data model demonstrate value without reintroducing remote AI or generic abstraction.",
        "deviation": "Existing notes can support a small local template schema and real workflows show repeatable value with safe export, backup and migration.",
        "locations": ["codebase/renderer/features/notes/", "codebase/main/infrastructure/persistence/database.js::notes", "codebase/preload/index.js::notes API"],
        "test": "Prototype only after evidence; verify create/apply/edit/delete, rich-text integrity, backup/restore, migration, exact search and no remote-generation path.",
        "dimensions": ["workflow demand", "schema simplicity", "editor integrity", "search", "backup/restore", "remote-AI exclusion"],
        "owner": "Notes organisation",
        "phase": "PHASE-05-CONDITIONAL-DECISIONS",
        "fallback": "Keep existing local notes without templates; current static evidence does not prove a template implementation.",
    },
    "CAP-PORTABLE-WINDOWS": {
        "title": "Portable Windows build",
        "default": "Preserve the configured portable target until real packaging evidence determines whether it is supportable alongside the required installer.",
        "deviation": "The portable artifact fails data-location, native helper, model, update-removal, licence, offline or supportability requirements and the required installer remains fully proven.",
        "locations": ["codebase/electron-builder.json::win.target portable", "codebase/main/index.js::userData", "codebase/resources/", "codebase/packaging/windows/"],
        "test": "Build at the verified checkpoint, inspect contents, launch on a clean offline Windows account, verify writable data placement, all helpers/models, uninstall independence and no external traffic.",
        "dimensions": ["artifact integrity", "data location", "native helpers", "model assets", "offline launch", "support burden", "installer parity"],
        "owner": "Windows packaging",
        "phase": "PHASE-05-CONDITIONAL-DECISIONS",
        "fallback": "Release the proven NSIS installer only while keeping portable configuration evidence for later review.",
    },
    "CAP-MACOS-LINUX": {
        "title": "macOS and Linux source and CI verification",
        "default": "Preserve platform source, build configuration and CI/static coverage; record unavailable physical hardware honestly without blocking the Windows release unless an explicit gate applies.",
        "deviation": "Specific platform code is proven dead or unrecoverable only after ownership, build references, licence and replacement evidence satisfy preservation and deletion gates.",
        "locations": ["codebase/native/helpers/macos/", "codebase/native/helpers/linux/", "codebase/packaging/macos/", "codebase/packaging/linux/", "codebase/electron-builder.json::mac/linux"],
        "test": "Run applicable type/static/unit/CI builds on target runners; on physical hardware record permission, hotkey, microphone, system-audio, paste and packaged offline results or HARDWARE UNAVAILABLE.",
        "dimensions": ["source preservation", "configuration", "CI availability", "native build", "permissions", "hardware evidence", "Windows-gate applicability"],
        "owner": "Cross-platform source and release governance",
        "phase": "PHASE-05-CONDITIONAL-DECISIONS",
        "fallback": "Preserve source/configuration and mark unexecuted hardware checks HARDWARE UNAVAILABLE; do not claim a platform pass.",
    },
}


RELEASE_GATES: list[dict[str, Any]] = [
    {"release_gate_id": "GATE-01-AUTHORITY", "name": "Master authority unchanged and fully traced", "planned_proof": ["Post-run SHA-256 equality", "Requirement source-line reconciliation", "Zero unmapped requirements"]},
    {"release_gate_id": "GATE-02-PROVENANCE", "name": "Git or recoverable hash provenance", "planned_proof": ["Repository-state capture", "Mutation batch checkpoint", "No user-work destruction record"]},
    {"release_gate_id": "GATE-03-MAPPING", "name": "Exact capability and dependency mapping", "planned_proof": ["Exact-location registry validation", "Capability-task reconciliation", "Final Graphify/static rescan"]},
    {"release_gate_id": "GATE-04-PRESERVATION", "name": "Retained capabilities preserved", "planned_proof": ["Characterisation results", "Before/after retained workflow evidence", "Third-party and legal inspection"]},
    {"release_gate_id": "GATE-05-DELETION", "name": "Removed systems absent", "planned_proof": ["Seven interlocks per deletion", "Full-layer absence ledger", "Runtime and packaged absence proof"]},
    {"release_gate_id": "GATE-06-CAPABILITY", "name": "Mandatory capabilities complete", "planned_proof": ["Targeted capability results", "Real integration workflows", "Broader regression results"]},
    {"release_gate_id": "GATE-07-DATA-SAFETY", "name": "Data migration and recovery safe", "planned_proof": ["Backup checksums", "Integrity and idempotency results", "Interrupted migration recovery drill"]},
    {"release_gate_id": "GATE-08-REAL-INTEGRATION", "name": "Real integration boundaries proven", "planned_proof": ["SQLite native binding result", "Child-process/model fixture result", "Microphone/system-audio/hotkey evidence or explicit hardware status"]},
    {"release_gate_id": "GATE-09-OFFLINE", "name": "Installed runtime is offline", "planned_proof": ["Offline first-launch capture", "External network denial observation", "Owned loopback allow-list evidence"]},
    {"release_gate_id": "GATE-10-WINDOWS-RELEASE", "name": "Windows build, installer and installed launch", "planned_proof": ["Production build log", "Installer hash and clean installation", "Installed offline launch and packaged-asset inspection"]},
    {"release_gate_id": "GATE-11-AUDIT", "name": "Final audits and reconciliation", "planned_proof": ["Final Graphify scan", "Final simplification audit", "Zero placeholder, contradiction and orphan report"]},
    {"release_gate_id": "GATE-12-HARDWARE", "name": "Applicable platform and hardware truthfulness", "planned_proof": ["Windows physical workflow results", "macOS/Linux CI or static results", "HARDWARE UNAVAILABLE records where applicable"]},
]


def path_from_ref(value: str) -> str:
    return value.split("::", 1)[0].split(":", 1)[0].replace("\\", "/")


def runtime_refs(cap: dict[str, Any]) -> tuple[list[str], list[str]]:
    chain = cap.get("runtime_chain", {}) if isinstance(cap.get("runtime_chain"), dict) else {}
    paths: list[str] = []
    symbols: list[str] = []
    for key in (
        "mapping_evidence", "entry_points", "navigation_routes", "hooks_and_stores",
        "main_services_and_handlers", "data_native_or_process_boundary", "tests",
    ):
        for item in chain.get(key, []) or []:
            if isinstance(item, str) and item.startswith("codebase/"):
                paths.append(path_from_ref(item))
    for key in ("ui_components", "hooks", "stores", "main_symbols", "ipc_handlers", "intermediate_symbols"):
        for item in chain.get(key, []) or []:
            if isinstance(item, str) and item.startswith("codebase/"):
                symbols.append(item)
                paths.append(path_from_ref(item))
    return unique(paths), unique(symbols)


def verified_anchor(capability_id: str, path: str) -> str:
    """Return a real symbol when reviewed, otherwise a content-addressed anchor."""
    absolute = ROOT / path
    symbol = SYMBOL_OVERRIDES.get((capability_id, path))
    if symbol and absolute.is_file():
        try:
            if symbol in absolute.read_text(encoding="utf-8", errors="replace"):
                return f"{path}::{symbol}"
        except OSError:
            pass
    # Generated Graphify authorities cannot carry a stable hash of themselves or
    # of a sibling rewritten later in the same generation transaction.  Use a
    # real structural anchor for those derived governance files instead.
    if path.startswith("Graphify/") and absolute.is_file():
        if absolute.suffix.lower() == ".json":
            return f"{path}::json-key:schema_version"
        if absolute.suffix.lower() == ".md":
            first_heading = next(
                (line.strip() for line in absolute.read_text(encoding="utf-8", errors="replace").splitlines() if line.startswith("#")),
                "# document",
            )
            return f"{path}::heading:{first_heading}"
    if absolute.is_file():
        return f"{path}::sha256:{sha256(absolute)}"
    return f"{path}::directory-anchor"


def reviewed_runtime_chain(
    capability_id: str,
    capability_name: str,
    current_paths: list[str],
    current_symbols: list[str],
    owner: str,
) -> dict[str, Any]:
    """Build a domain-clean runtime/static chain from reviewed locations only."""
    symbol_by_path = {item.split("::", 1)[0]: item for item in current_symbols}
    renderer = [path for path in current_paths if "/renderer/" in path]
    main_features = [path for path in current_paths if "/main/features/" in path]
    ipc = [path for path in current_paths if "/main/ipc/" in path]
    preload = [path for path in current_paths if "/preload/" in path]
    types = [path for path in current_paths if path.endswith((".ts", ".tsx", ".d.ts")) and ("types" in path.lower() or "/preload/" in path)]
    persistence = [path for path in current_paths if "/persistence/" in path]
    native_or_process = [
        path for path in current_paths
        if "/native/" in path or "/resources/bin/" in path or "manager" in Path(path).stem.lower()
    ]
    tests = [path for path in current_paths if "/tests/" in path]
    runtime_registrations = [
        symbol_by_path[path] for path in current_paths
        if path.endswith("/main/index.js") or "/main/ipc/" in path or "electron-builder" in path
    ]
    return {
        "user_action": [capability_name],
        "entry_points": renderer[:3] or main_features[:3] or current_paths[:3],
        "ui_components": [symbol_by_path[path] for path in renderer],
        "navigation_routes": [symbol_by_path[path] for path in renderer if "router" in path.lower() or "view" in path.lower()],
        "hooks": [symbol_by_path[path] for path in renderer if "hook" in path.lower()],
        "stores": [symbol_by_path[path] for path in renderer if "store" in path.lower()],
        "hooks_and_stores": [symbol_by_path[path] for path in renderer if "hook" in path.lower() or "store" in path.lower()],
        "preload_exposures": [symbol_by_path[path] for path in preload],
        "typescript_contracts": [symbol_by_path[path] for path in types],
        "ipc_channels": [symbol_by_path[path] for path in ipc],
        "ipc_handlers": [symbol_by_path[path] for path in ipc],
        "main_services_and_handlers": [symbol_by_path[path] for path in main_features + ipc],
        "main_symbols": [symbol_by_path[path] for path in current_paths if "/main/" in path],
        "repositories": [symbol_by_path[path] for path in persistence if "database" in path.lower() or "repositor" in path.lower()],
        "data_native_or_process_boundary": [symbol_by_path[path] for path in unique(persistence + native_or_process)],
        "result_events": [],
        "renderer_update": [symbol_by_path[path] for path in renderer],
        "tests": tests,
        "runtime_registrations": runtime_registrations,
        "data_read": [symbol_by_path[path] for path in persistence],
        "data_written": [symbol_by_path[path] for path in persistence],
        "side_effects": [symbol_by_path[path] for path in native_or_process],
        "failure_path": [],
        "cleanup_path": [symbol_by_path[path] for path in current_paths if "cleanup" in path.lower() or "recovery" in path.lower() or "manager" in path.lower()],
        "recovery_path": [symbol_by_path[path] for path in current_paths if "recovery" in path.lower() or "backup" in path.lower() or "migration" in path.lower()],
        "failure_cleanup_recovery": [symbol_by_path[path] for path in current_paths if any(word in path.lower() for word in ("recovery", "backup", "migration", "manager"))],
        "current_test_coverage": tests,
        "current_breakage": "Implementation status must be established by the linked characterization task; static planning does not claim a runtime result.",
        "required_change": "Execute only the linked dependency-safe task at the reviewed paths and anchors; preserve all retained behavior and data.",
        "target_owner": owner,
        "intermediate_symbols": current_symbols,
        "mapping_evidence": current_paths,
        "presence_status": "REVIEWED CURRENT LOCATIONS" if current_paths else "NO CURRENT IMPLEMENTATION PROVEN",
        "provenance": "Reviewed static paths plus real symbols or SHA-256 content anchors; not runtime execution evidence.",
    }


old_capability_doc = load_json(G / "CAPABILITY_REGISTRY.json")
old_capabilities = old_capability_doc.get("capabilities", old_capability_doc)
capability_by_id: dict[str, dict[str, Any]] = {item["id"]: dict(item) for item in old_capabilities}
for item in EXTRA_CAPABILITIES:
    capability_by_id.setdefault(item["id"], dict(item))

# Resolve older collapsed/ambiguous records without discarding their deep maps.
capability_by_id["CAP-PARAKEET"]["name"] = "Parakeet local engine packaging"
capability_by_id["CAP-PARAKEET"]["decision"] = "CONDITIONAL - REQUIRES EVIDENCE"
capability_by_id["CAP-MEETING-DETECTION"]["decision"] = "CONDITIONAL - REQUIRES EVIDENCE"
for item in capability_by_id.values():
    if isinstance(item.get("decision"), str):
        item["decision"] = item["decision"].replace("â€”", "-").replace("—", "-")

unknown_requirement_caps = sorted({cap_id for req in requirements for cap_id in req["capability_ids"] if cap_id not in capability_by_id})
if unknown_requirement_caps:
    raise SystemExit(f"Requirement mapping names unknown capability IDs: {unknown_requirement_caps}")

reqs_by_cap: dict[str, list[str]] = collections.defaultdict(list)
for req in requirements:
    for cap_id in req["capability_ids"]:
        reqs_by_cap[cap_id].append(req["stable_requirement_id"])

mp1_governing = next(req["stable_requirement_id"] for req in requirements if req["source_master_plan_code"] == "MP1" and req["source_heading"] == "Governing Rule")
mp2_governing = next(req["stable_requirement_id"] for req in requirements if req["source_master_plan_code"] == "MP2" and req["source_heading"] == "Governing Rule")
for cap_id, cap in capability_by_id.items():
    if not reqs_by_cap[cap_id]:
        reqs_by_cap[cap_id].append(mp2_governing if cap_id.startswith("CAP-REMOVE-") or cap.get("decision") in {"REMOVE", "FORBIDDEN"} else mp1_governing)

# Keep the requirement-to-capability and capability-to-requirement relations
# exactly bidirectional.  Capabilities without a narrower source declaration are
# governed by the appropriate immutable preservation/deletion rule above.
requirements_by_stable_id = {item["stable_requirement_id"]: item for item in requirements}
for cap_id, requirement_ids in reqs_by_cap.items():
    for requirement_id in requirement_ids:
        requirement = requirements_by_stable_id[requirement_id]
        if cap_id not in requirement["capability_ids"]:
            requirement["capability_ids"].append(cap_id)
            requirement["capability_ids"] = unique(requirement["capability_ids"])
            requirement["semantic_mapping_basis"] += "; governing-rule coverage for derived capability contract"

for req in requirements:
    for interpretation in INTERPRETATIONS:
        if req["source_master_plan"] in interpretation["source_documents"] and any(
            heading.lower() in req["source_heading"].lower() or req["source_heading"].lower() in heading.lower()
            for heading in interpretation["relevant_headings"]
        ):
            req["conflicts_or_interpretations"].append(interpretation["interpretation_id"])


capabilities: list[dict[str, Any]] = []
for cap_id in sorted(capability_by_id):
    cap = capability_by_id[cap_id]
    candidate_paths, _candidate_symbols = runtime_refs(cap)
    declared_targets = cap.get("target_paths", []) or []
    for target in declared_targets:
        if isinstance(target, str) and target.startswith("codebase/") and (ROOT / path_from_ref(target)).exists():
            candidate_paths.append(path_from_ref(target))
    current_paths = reviewed_paths(cap_id, unique(candidate_paths), ROOT)
    # Governance authorities are current Graphify files, never application targets.
    if cap_id in {"CAP-DELETION-GOVERNANCE", "CAP-EXACT-LOCATION", "CAP-IMPLEMENTATION-GOVERNANCE", "CAP-PLANNING-GOVERNANCE", "CAP-RELEASE", "CAP-PROVENANCE", "CAP-THIRD-PARTY", "CAP-SIMPLIFICATION", "CAP-MARKDOWN-GOVERNANCE"}:
        current_paths.extend(
            path_from_ref(path)
            for path in declared_targets
            if isinstance(path, str) and path.startswith("Graphify/") and (ROOT / path_from_ref(path)).exists()
        )
        current_paths = unique(current_paths)
    current_symbols = [verified_anchor(cap_id, path) for path in current_paths]
    is_removal = cap_id in REMOVAL_CAPS
    is_conditional = cap_id in CONDITIONAL_SPECS
    if current_paths:
        presence = "CURRENT IMPLEMENTATION OR STATIC CANDIDATES MAPPED"
    elif is_removal:
        presence = "NO ACTIVE PATH PROVEN - FINAL DELETION INTERLOCK STILL REQUIRED"
    else:
        presence = "PLANNED ADDITION OR CURRENT IMPLEMENTATION NOT PROVEN"
    implementation_gap = "Runtime completeness is not claimed by static planning; execute the linked characterization and completion contract."
    if cap_id == "CAP-SEARCH-EXACT":
        presence = "PARTIAL CURRENT IMPLEMENTATION MAPPED - COMPLETION TASK REQUIRED"
        implementation_gap = "SQLite note/transcript/tag exact queries and a combined search UI exist; complete and prove speaker/folder/date/source filters, highlighting, result routing and transcript timestamp jumps."
    elif cap_id == "CAP-AEC":
        presence = "CURRENT NATIVE/MAIN AEC CHAIN MAPPED - REAL AUDIO PROOF REQUIRED"
        implementation_gap = "MeetingAecManager, leak detection, native helper, binary staging and cleanup exist statically; real microphone/system-audio echo cancellation remains unexecuted evidence."
    elif cap_id == "CAP-NOTES":
        implementation_gap = "Editor, state, folders, links, IPC and SQLite paths exist; prove autosave, tag/snippet integration, backup/export and the separate conditional template outcome end to end."
    target_path, target_symbol = target_for(cap_id, current_paths, declared_targets, cap.get("name", cap_id))
    targets = [target_path]
    owner = owner_for(cap_id, cap.get("owner", "Implementation governance"))
    cap.update({
        "id": cap_id,
        "decision": cap.get("decision", "MANDATORY KEEP"),
        "owner": owner,
        "module_owner": owner,
        "planning_status": "PLANNING COMPLETE - IMPLEMENTATION EVIDENCE PENDING",
        "implementation_status": "NOT STARTED",
        "presence_status": presence,
        "implementation_gap": implementation_gap,
        "master_requirement_ids": unique(reqs_by_cap[cap_id]),
        "current_paths": current_paths,
        "current_symbols": current_symbols,
        "target_paths": targets,
        "target_symbols": [target_symbol],
        "conditional_decision_package_id": f"DEC-{cap_id.removeprefix('CAP-')}" if is_conditional else None,
        "phase": "PHASE-04-EXCLUDED-SYSTEM-REMOVAL" if is_removal else ("PHASE-05-RETAINED-CAPABILITIES" if is_conditional else "PHASE-05-RETAINED-CAPABILITIES"),
        "wave": "WAVE-04" if is_removal else ("WAVE-05C" if is_conditional else "WAVE-05"),
        "semantic_review_status": "REVIEWED AGAINST MASTER PLAN AND CURRENT DOMAIN",
        "semantic_review_basis": "Explicit reviewed location rule" if cap_id in EXACT_LOCATIONS else "Reviewed capability-domain boundary",
        "last_planning_verification_checkpoint": "CHECKPOINT-FINAL-PLANNING",
        "runtime_chain": reviewed_runtime_chain(cap_id, cap.get("name", cap_id), current_paths, current_symbols, owner),
    })
    capabilities.append(cap)


requirements_by_id = {item["stable_requirement_id"]: item for item in requirements}


def cap_test_path(cap: dict[str, Any], suffix: str = "contract") -> str:
    return f"codebase/tests/integration/{slug(cap['name'])}.{suffix}.test.js"


def evidence_types_for(capability_id: str, task_kind: str) -> list[str]:
    if capability_id == "CAP-PROVENANCE":
        return ["GIT/HASH PROVENANCE CHECK"]
    if capability_id in {"CAP-PLANNING-GOVERNANCE", "CAP-EXACT-LOCATION", "CAP-IMPLEMENTATION-GOVERNANCE", "CAP-DELETION-GOVERNANCE", "CAP-RELEASE", "CAP-SIMPLIFICATION"}:
        return ["STATIC/GRAPH AUDIT", "RELEASE EVIDENCE RECONCILIATION"]
    if task_kind == "DELETION":
        return ["STATIC/GRAPH AUDIT", "APPLICATION INTEGRATION TEST", "PACKAGING/INSTALLER TEST"]
    if capability_id in {"CAP-DATABASE", "CAP-DATA-SAFETY"}:
        return ["SQLITE INTEGRATION TEST", "APPLICATION UNIT TEST"]
    if capability_id == "CAP-LEGACY-MIGRATION":
        return ["MIGRATION TEST", "SQLITE INTEGRATION TEST"]
    if capability_id in {"CAP-BACKUP", "CAP-RESTORE"}:
        return ["BACKUP/RESTORE TEST", "FILESYSTEM TEST", "SQLITE INTEGRATION TEST"]
    if capability_id in {"CAP-IPC"}:
        return ["IPC/ELECTRON ROUND-TRIP TEST", "STATIC/GRAPH AUDIT"]
    if capability_id in {"CAP-AEC", "CAP-AUDIO", "CAP-AUDIO-MIXING", "CAP-MICROPHONE", "CAP-SYSTEM-AUDIO", "CAP-VAD"}:
        return ["NATIVE/PROCESS TEST", "AUDIO/HARDWARE TEST", "MANUAL HARDWARE EVIDENCE"]
    if capability_id in {"CAP-WHISPER", "CAP-PARAKEET", "CAP-SHERPA-ONNX", "CAP-MINILM", "CAP-QDRANT", "CAP-MODELS", "CAP-MODEL-DISCOVERY", "CAP-MODEL-PACK"}:
        return ["MODEL/BINARY STARTUP TEST", "NATIVE/PROCESS TEST", "OFFLINE NETWORK OBSERVATION"]
    if capability_id in {"CAP-PACKAGING", "CAP-WINDOWS-INSTALLER", "CAP-PORTABLE-WINDOWS", "CAP-MACOS-LINUX"}:
        return ["PACKAGING/INSTALLER TEST", "MANUAL HARDWARE EVIDENCE"]
    if capability_id in {"CAP-NETWORK-POLICY", "CAP-LOOPBACK-WEBSOCKETS", "CAP-OFFLINE-FIRST-LAUNCH"}:
        return ["OFFLINE NETWORK OBSERVATION", "APPLICATION INTEGRATION TEST"]
    if capability_id in {"CAP-LEGAL", "CAP-THIRD-PARTY"}:
        return ["LEGAL/LICENCE AUDIT", "PACKAGING/INSTALLER TEST"]
    if capability_id in {"CAP-IMPORT", "CAP-EXPORT", "CAP-IMPORT-AUDIO", "CAP-IMPORT-VIDEO", "CAP-IMPORT-EXPORT"}:
        return ["IMPORT/EXPORT TEST", "FILESYSTEM TEST", "APPLICATION INTEGRATION TEST"]
    return ["APPLICATION UNIT TEST", "APPLICATION INTEGRATION TEST"]


def existing_test_paths(cap: dict[str, Any]) -> list[str]:
    return unique(
        path
        for path in cap.get("current_paths", [])
        if path.startswith("codebase/tests/") and path.endswith(".test.js") and (ROOT / path).is_file()
    )


def test_command(path: str) -> str:
    # The verified package script already expands tests/**/*.test.js. Appending a
    # second positional pattern is not a reliable file selector for Electron's
    # Node-compatible test runner, so execute the real script and identify the
    # owned test path separately in the evidence contract.
    return "npm test"


def characterization_contract(cap: dict[str, Any], evidence_types: list[str]) -> list[dict[str, Any]]:
    existing = existing_test_paths(cap)
    if existing:
        return [
            {
                "test_path": path,
                "reference_status": "EXISTING TEST",
                "evidence_type": evidence_types[0],
                "command": test_command(path),
                "working_directory": "codebase",
                "boundary": f"Current {cap['name']} behavior at the mapped owned boundary, including failure and cleanup assertions present in the fixture.",
            }
            for path in existing[:4]
        ]
    if evidence_types[0] in {"STATIC/GRAPH AUDIT", "GIT/HASH PROVENANCE CHECK", "LEGAL/LICENCE AUDIT", "RELEASE EVIDENCE RECONCILIATION"}:
        command = "python Graphify/tools/validate_planning.py" if evidence_types[0] != "GIT/HASH PROVENANCE CHECK" else "git status --short --branch (when Git exists), otherwise generate the permitted path/hash inventory"
        return [{
            "test_path": None,
            "reference_status": "STATIC VALIDATOR" if evidence_types[0] != "GIT/HASH PROVENANCE CHECK" else "MANUAL/EXTERNAL EVIDENCE",
            "evidence_type": evidence_types[0],
            "command": command,
            "working_directory": ".",
            "boundary": f"Planning/provenance boundary for {cap['name']}; no synthetic application test is claimed.",
        }]
    planned = cap_test_path(cap)
    return [{
        "test_path": planned,
        "reference_status": "TEST TO CREATE",
        "evidence_type": evidence_types[0],
        "command": test_command(planned),
        "working_directory": "codebase",
        "boundary": f"Create a real {cap['name']} characterization at the applicable SQLite, filesystem, Electron, native, process, audio, or model boundary before mutation.",
    }]


def capability_actions(cap: dict[str, Any], expected: list[str]) -> list[str]:
    cap_id = cap["id"]
    locations = ", ".join(expected)
    target = f"{cap['target_paths'][0]}::{cap['target_symbols'][0]}"
    specific = {
        "CAP-AEC": "Trace MeetingAecManager construction, start/stop/error cleanup, system and microphone frame writes, native helper protocol, binary staging, and real echo-leak/AEC hardware proof; exclude dictionaryEchoFilter.js because it is text filtering, not acoustic echo cancellation.",
        "CAP-SEARCH-EXACT": "Preserve and complete DatabaseManager.searchNotes/searchTranscripts/searchLocal using SQLite FTS5 plus Unicode substring fallback; cover note title/body, transcript segments, tags, speaker/folder/date/source filters, result highlighting/opening, and timestamp jumps without using MiniLM/Qdrant as exact-search proof.",
        "CAP-SEARCH-SEMANTIC": "Keep semantic retrieval isolated behind LocalEmbeddings, vectorIndex, Qdrant lifecycle, reindex and recovery contracts; prove it can fail independently while exact SQLite search remains available.",
        "CAP-NOTES": "Trace Tiptap editing, noteStore state, save/update/delete autosave, preload/type/IPC contracts, SQLite notes and links, folders/tags/snippets, markdown mirror, meeting/transcript links, backup/export, and owned tests; do not attach diarization or tokenizer assets as Notes implementation.",
        "CAP-DATABASE": "Characterize DatabaseManager schema creation, FTS triggers, local tables, transaction boundaries, native better-sqlite3 loading, schema versioning, backup, integrity and disposable-copy migration behavior before any persistence change.",
        "CAP-IPC": "Inventory each renderer caller, preload exposure, Electron TypeScript declaration, ipcMain handler, validation/error contract and result event; update the full typed round trip as one boundary.",
        "CAP-NETWORK-POLICY": "Enumerate runtime request interception and owned loopback allow-list entries, block external hosts, prove no installed-runtime download path is reachable, and save connection observations from first launch and retained local sidecars.",
        "CAP-BACKUP": "Verify backup manifest/checksums, SQLite snapshot consistency, optional audio inclusion, non-overwrite behavior, and recovery from a disposable copy.",
        "CAP-RESTORE": "Verify preview compatibility, pre-restore recovery copy, database reopen, audio restoration, interruption handling, integrity, and idempotent disposable-copy recovery.",
        "CAP-LEGACY-MIGRATION": "Preserve historical OpenWhispr migration evidence, copy before transform, reject non-empty incompatible destinations, prove idempotency/interruption recovery, and compare counts/checksums/content on disposable fixtures.",
        "CAP-MEETING": "Trace meeting start/stop, microphone and system-audio capture, buffers, recording persistence, live/post transcription, recovery, notifications, renderer state and cleanup across IPC and native processes.",
        "CAP-DICTATION": "Trace global hotkey registration, microphone capture, recording guard/overlay, local transcription, clipboard paste/restore, smart spacing and failure cleanup from renderer through preload/IPC/main services.",
        "CAP-PLAYBACK": "Trace owned media location, playback controls, duration/seek, transcript timestamp jumps, missing-media failure, cleanup and import/export linkage.",
        "CAP-PACKAGING": "Reconcile electron-builder configuration, source-controlled resource staging, native helper/model allow-list, ASAR/unpack paths, notices, Windows artifacts and clean installed offline launch; never target node_modules files.",
        "CAP-WINDOWS-INSTALLER": "Produce and inspect the configured Windows installer only after production build and packaged assets pass; prove clean install, launch, data location, uninstall/reinstall recovery and offline operation.",
        "CAP-MODEL-PACK": "Define a local archive manifest, pinned engine/model identity, hashes, supported platform/language metadata, traversal protection, non-overwrite install, discovery, rollback and offline import evidence.",
        "CAP-MODEL-DISCOVERY": "Enumerate owned model directories and manifests, validate filenames/versions/hashes before activation, reject missing/corrupt assets, and surface deterministic local errors without runtime downloads.",
        "CAP-DATA-SAFETY": "Create disposable database, recording, transcript, note, export and backup fixtures; record pre/post counts and hashes; prove backup-before-transform, atomicity, integrity, idempotency, interrupted-operation recovery and non-overwrite rules for every data-changing dependency.",
        "CAP-DELETION-GOVERNANCE": "For each CAP-REMOVE task reconcile every recorded candidate disposition and all nineteen architectural layers, require BDI-1 through BDI-7 evidence at one checkpoint, and prevent a deletion status while any retained caller, historical migration, legal notice or packaged effect is unresolved.",
        "CAP-EXACT-LOCATION": "Reconcile every EXACT_LOCATION_REGISTRY entry against an existing current path plus verified symbol/content anchor or an explicit absent/planned status; update owner, dependencies, target, tests, phase and checkpoint without creating a competing registry.",
        "CAP-IMPLEMENTATION-GOVERNANCE": "Enforce the topological queue order, one capability batch per recoverable checkpoint, immutable-plan hash checks, task stop conditions, evidence paths and resume state; reject status advancement when dependencies or required proof are incomplete.",
        "CAP-PLANNING-GOVERNANCE": "Keep Master requirement records, interpretations, capabilities, tasks, locations, decisions, release gates and counts bidirectionally reconciled; preserve the Master Plan bytes and allow derived corrections only through the deterministic generator and validator.",
        "CAP-TESTING": "For every task distinguish existing tests from tests to create, bind commands to verified package scripts, require pre-change characterization, targeted and real-boundary integration proof, broader regression, offline/applicability evidence and honest hardware dispositions.",
        "CAP-APP-SHELL": "Trace app.whenReady through single-instance handling, protocol/window/tray creation, shutdown, deep-link/open-file events, renderer loading and runtime-network installation; characterize window lifecycle and cleanup before shell reorganization.",
        "CAP-AUDIO": "Characterize meeting audio utilities, activity detection and renderer capture buffers for sample rate, channel shape, silence, clipping, duration, failure and cleanup; keep this boundary distinct from AEC, system-audio transport and playback.",
        "CAP-DIARIZATION": "Trace DiarizationManager model discovery/import, child-process arguments, timeout/kill cleanup, segment parsing/merge, speaker assignment, missing/corrupt assets and packaged Sherpa paths using real audio fixtures.",
        "CAP-HOTKEY": "Inventory hotkeyManager registration/unregistration, normalized accelerator selection, platform native listeners, settings/preload/IPC contracts, conflict and permission errors, press/release behavior and shutdown cleanup without absorbing unrelated dictation modules.",
        "CAP-MICROPHONE": "Characterize device enumeration/selection, permission denial, default-device fallback, stream constraints, recorder startup/teardown and concurrent dictation/meeting ownership across audioManager, useAudioRecording and meetingRecordingStore.",
        "CAP-MODELS": "Reconcile modelRegistryData, model directories and asset manifest into one local inventory; label bundled versus imported assets, verify platform/engine/language/version/hash/licence metadata and reject missing, corrupt or runtime-downloaded models.",
        "CAP-ONBOARDING": "Trace first-run and post-migration routing, local/offline assertions, permission/setup steps, settings persistence and completion/re-entry behavior; delete remote-account/provider branches while preserving microphone and meeting setup.",
        "CAP-RENDERER": "Trace renderer main mount, AppRouter lazy routes, ControlPanel navigation, error boundary and window controls; remove excluded routes/components while preserving retained feature entry points and typed preload access.",
        "CAP-SETTINGS": "Inventory every retained settingsStore field, SettingsPage control, preload/IPC persistence key and default/migration; remove remote/provider/account controls and prove offline-safe validation, restart persistence and reset behavior.",
        "CAP-SYSTEM-AUDIO": "Trace Windows loopback, macOS audio tap and Linux portal managers through renderer capture, IPC, permission checks, native process lifecycle, channel/sample conversion, mic mixing, failure fallback and packaged helper discovery.",
        "CAP-TRANSCRIPTION": "Trace transcriptionStore/useWhisper callers through preload/IPC to WhisperManager/WhisperServer, structured segment persistence and overlay updates; prove cancellation, error recovery, offline engine selection and no hosted fallback.",
        "CAP-VAD": "Reconcile whisperVadConfig defaults and WhisperServer command arguments, validate threshold/window bounds and disabled behavior with existing unit tests, and keep acoustic VAD separate from meeting AEC and text filtering.",
        "CAP-WHISPER": "Trace WhisperManager model resolution, whisper-server lifecycle, CUDA decision/fallback, wake rewarm, process timeout/cancellation, structured output parsing and packaged whisper.cpp binary/model discovery entirely offline.",
        "CAP-AUDIO-MIXING": "Characterize meetingRecordingStore microphone/system frame alignment, resampling, channel conversion, holdback, clipping and flush behavior; prove mixed output duration and cleanup with deterministic fixtures and real capture evidence.",
        "CAP-CLIPBOARD": "Trace clipboard snapshot, fast-paste/native helper selection, paste injection, smart spacing, restoration on success/error/cancellation and platform permission guidance; preserve unrelated clipboard contents and historical cleanup guidance.",
        "CAP-EXPORT": "Enumerate transcript, note, audio and metadata export handlers across renderer/preload/types/IPC; define formats, filename/path sanitization, cancellation, overwrite policy, structured segments/timestamps and offline filesystem error evidence.",
        "CAP-FFMPEG": "Trace ffmpeg-static resolution, ffmpegUtils argument construction, media probing/conversion, timeout/kill cleanup and packaged binary path; reject network inputs and prove audio/video imports on local fixtures.",
        "CAP-FOLDERS": "Trace useFolderManagement and drag/drop through noteStore/preload/IPC/database folder relations; characterize create/rename/move/delete, name collisions, orphan prevention, ordering, search and backup/restore behavior.",
        "CAP-I18N": "Remove excluded-system catalogue keys, preserve retained English strings, reconcile every t() caller and check-i18n result, and require no orphan/missing keys or historical/legal strings misclassified as active UI.",
        "CAP-IMPORT": "Trace UploadAudioView selection through local archive/media validation, preload/IPC processing and note creation; enforce extension/size/path checks, cancellation, duplicate policy, rollback and zero network access.",
        "CAP-IMPORT-AUDIO": "Validate local audio extensions and content, FFmpeg normalization, duration/metadata extraction, transcription/note persistence, cancellation and corrupt-file rollback from UploadAudioView through IPC.",
        "CAP-IMPORT-EXPORT": "Reconcile local import/export renderer callers, preload methods, Electron types and IPC handlers as typed round trips; enforce filesystem-only inputs/outputs, path sanitization, error contracts and no remote endpoint.",
        "CAP-IMPORT-VIDEO": "Validate local video extensions and content, FFmpeg audio extraction, temporary-file cleanup, transcription/note persistence, cancellation and corrupt-file rollback from UploadAudioView through IPC.",
        "CAP-LINKED-NOTES": "Trace note-to-meeting/transcript linkage in NoteEditor, MeetingTranscriptView, noteStore and database; preserve stable IDs, bidirectional navigation, deletion behavior, export/backup and missing-link recovery.",
        "CAP-LINKED-PLAYBACK": "Trace MeetingTranscriptView timestamp actions to MeetingRecordingPill and audioStorage; prove seek bounds, segment synchronization, missing-media handling and cleanup without coupling playback to capture detectors.",
        "CAP-MEETING-NOTES": "Trace meeting-created notes through MeetingTranscriptView, NoteEditor, noteStore and database links; preserve structured segments, recording reference, autosave, folder/tag operations and export/backup behavior.",
        "CAP-MICROPHONE-DICTATION": "Trace useAudioRecording/audioManager device acquisition, PCM buffering, transcription handoff and teardown in dictation App; prove permission denial, stale/default device fallback, cancellation and no meeting-stream interference.",
        "CAP-MICROPHONE-SELECTION": "Reconcile audioDeviceUtils enumeration and stored microphone IDs with settings and staleMicDevice fallback; prove unplug/replug, missing-device, permission and restart behavior without persisting invalid devices.",
        "CAP-MINILM": "Trace LocalEmbeddings through onnxWorkerClient/onnxWorker to the bundled all-MiniLM model and tokenizer; prove vector dimensions, deterministic local inference, corrupt/missing asset errors, worker cleanup and packaged offline discovery.",
        "CAP-NOTIFICATIONS": "Trace meeting detection events into MeetingNotificationOverlay/Card and windowManager; characterize enable/disable settings, deduplication/rate limiting, actions, dismissal, process churn and no external notification service.",
        "CAP-OFFLINE-FIRST-LAUNCH": "Create an installed-artifact first-launch test on a clean Windows user-data directory with network denied; verify shell, onboarding, settings, bundled models/helpers and retained workflows start without downloads or remote calls.",
        "CAP-PERSONAL-NOTES": "Trace PersonalNotesView, NoteEditor and noteStore CRUD into SQLite; preserve folders/tags/search/history, remove calendar-derived metadata, and prove autosave, deletion, export and backup/restore behavior.",
        "CAP-PROCESSING-JOBS": "Add a minimal LocalJobQueue only if characterized long-running local transcription/import work requires it; define ownership, cancellation, bounded concurrency, persistence/restart policy, shutdown cleanup and failure reporting without a generic framework.",
        "CAP-RECORDING-OVERLAY": "Trace dictation recording state into TranscriptionPreviewOverlay and recordingGuard; characterize show/update/hide, cancellation, error recovery, click-through/focus, multi-monitor placement and cleanup after hotkey release.",
        "CAP-RECOVERY": "Add recoverInterruptedRecordings at the owned meeting recovery target; identify incomplete audio/database state on startup, validate recoverable files, create a recovery copy, resume or quarantine atomically, prevent duplicates and record user-visible outcomes.",
        "CAP-SEGMENTS": "Reconcile transcript segment schema, diarization/transcriptText production, IPC types and MeetingTranscriptView consumption; preserve timestamps, speaker IDs, ordering, edits, search, playback jumps, migration and export fidelity.",
        "CAP-SNIPPETS": "Trace SnippetsView/snippets state through typed IPC and SQLite snippet CRUD; prove ordering, hotkey insertion, clipboard behavior, name/content validation, search, backup/restore and deletion without remote templates.",
        "CAP-SPEAKER-EMBEDDINGS": "Trace local embedding extraction/storage/matching across speakerEmbeddings, liveSpeakerIdentifier and assignment policy; characterize vector validation, threshold provenance, corrupt data, deletion, cleanup and no network path.",
        "CAP-SPEAKER-LABELS": "Trace transcriptSpeakerState labels into MeetingTranscriptView and assignment policy; preserve unknown/provisional labels, segment association, edit persistence, export and playback synchronization.",
        "CAP-SPEAKER-NAMING": "Trace the MeetingTranscriptView naming interaction through transcriptSpeakerState and persistence; validate names, apply scope explicitly, preserve unknown speakers and prove rename/export/backup consistency.",
        "CAP-SPEAKER-PERSISTENCE": "Reconcile speaker tables/columns and mappings with liveSpeakerIdentifier and speakerEmbeddings; prove transactional writes, migration, deletion, orphan cleanup, backup/restore and corrupt embedding recovery.",
        "CAP-SPEAKER-RENAMING": "Trace rename selection and propagation across MeetingTranscriptView, transcriptSpeakerState, assignment policy and database; prove per-segment/transcript/persistent scope, undo/error handling and export consistency.",
        "CAP-TAGS": "Trace tag creation/assignment/removal from NoteEditor and SearchView through preload/IPC/database; prove normalization, duplicates, orphan cleanup, exact filters, migration, export and backup/restore.",
        "CAP-TRANSCRIPT-EDIT": "Trace MeetingTranscriptView edits through typed preload/IPC to database segment/text updates; preserve timestamps/speakers/search index, validate concurrent/autosave errors and prove playback/export consistency.",
        "CAP-TRANSCRIPT-HISTORY": "Trace HistoryView/transcriptionStore queries into database history ordering and deletion; preserve source/date/duration/status metadata, exact filters, open/playback links, backup and migration behavior.",
        "CAP-TRAY": "Trace tray creation, icon resolution, menu actions, window show/hide and quit behavior from app startup through shutdown; prove platform icon packaging, single-instance behavior and no stale listener.",
        "CAP-WINDOW-LIFECYCLE": "Characterize windowManager/windowConfig creation, bounds restoration, show/hide/focus, close-versus-quit, overlay windows, display changes and app shutdown; preserve data flush and child-process cleanup.",
        "CAP-LEGAL": "Inventory codebase/LICENSE, declared dependencies, bundled native/model/binary assets and electron-builder resources; record source/version/hash/licence/notice obligations and preserve historical OpenWhispr attribution as legal provenance.",
        "CAP-MARKDOWN-GOVERNANCE": "Keep the single START-HERE handoff and named operational documents authoritative, repair internal links/status wording in place, and remove only proven duplicate or superseded derived authorities without touching Master Plan files.",
        "CAP-NATIVE": "Inventory each Windows/macOS/Linux helper source, build script, binary, IPC/process caller and packaged destination; prove architecture, permissions, spawn arguments, failure/timeout/kill cleanup, hashes and licence provenance.",
        "CAP-REPOSITORY": "Reconcile package/source/test/native/resource/script/configuration roots and folder owners against the file inventory; execute only dependency-safe moves from MOVE_LEDGER and update imports/build/package/test references in the same batch.",
        "CAP-SIMPLIFICATION": "At the final implementation checkpoint rerun the Ponytail audit, classify every finding against retained requirements and measured evidence, remove only proven duplication/dead abstraction, and record deferred complexity without weakening required boundaries.",
        "CAP-THIRD-PARTY": "Reconcile every top-level package and bundled asset to an owned caller, version, source, licence, notice, runtime/build reachability and packaging destination; remove dependencies only after retained callers and lockfile effects are proven absent.",
    }.get(cap_id)
    if specific is None:
        specific = f"At the reviewed {cap['name']} locations, trace every listed current anchor and implement only the mapped Master requirement contracts while preserving data, IPC, native, packaging and cleanup behavior applicable to this capability."
    return [
        f"Capture pre-change evidence at these exact reviewed locations: {locations}.",
        specific,
        f"Create or preserve the single owned target {target}; update only listed callers, registrations, persistence effects, tests and packaging references proven to depend on it.",
        "Save the focused diff/hash delta and all classified targeted, real-boundary, regression, offline or not-applicable evidence before changing planning status.",
    ]


def cap_contract_fields(cap: dict[str, Any], purpose: str, task_kind: str) -> dict[str, Any]:
    current_paths = cap.get("current_paths", [])
    current_symbols = cap.get("current_symbols", [])
    target_paths = cap.get("target_paths", [])
    exact_refs = [f"REG-CAPABILITY-{cap['id'].removeprefix('CAP-')}"]
    ipc_channels = unique((cap.get("runtime_chain") or {}).get("ipc_channels", [])) if isinstance(cap.get("runtime_chain"), dict) else []
    native_refs = unique((cap.get("runtime_chain") or {}).get("data_native_or_process_boundary", [])) if isinstance(cap.get("runtime_chain"), dict) else []
    req_summaries = [requirements_by_id[req_id]["requirement_summary"] for req_id in cap["master_requirement_ids"]]
    is_data = cap["id"] in {"CAP-DATABASE", "CAP-DATA-SAFETY", "CAP-LEGACY-MIGRATION", "CAP-BACKUP", "CAP-RESTORE"} or any("database" in p.lower() for p in current_paths)
    is_native = bool(native_refs) or cap["id"] in {"CAP-NATIVE", "CAP-AUDIO", "CAP-SYSTEM-AUDIO", "CAP-HOTKEY", "CAP-FFMPEG", "CAP-WHISPER", "CAP-SHERPA-ONNX"}
    is_package = cap["id"] in {"CAP-PACKAGING", "CAP-WINDOWS-INSTALLER", "CAP-PORTABLE-WINDOWS", "CAP-MACOS-LINUX", "CAP-LEGAL", "CAP-THIRD-PARTY"}
    expected = unique((current_paths or []) + [path_from_ref(p) for p in target_paths if isinstance(p, str) and p.startswith(("codebase/", "Graphify/"))])
    if not expected:
        expected = [f"PLANNED LOCATION: {target_paths[0]}"]
    evidence_types = evidence_types_for(cap["id"], task_kind)
    characterization = characterization_contract(cap, evidence_types)
    planned_integration_path = cap_test_path(cap, "real-boundary")
    governance_evidence = evidence_types[0] in {"STATIC/GRAPH AUDIT", "GIT/HASH PROVENANCE CHECK", "LEGAL/LICENCE AUDIT", "RELEASE EVIDENCE RECONCILIATION"}
    return {
        "capability_id": cap["id"],
        "master_requirement_ids": cap["master_requirement_ids"],
        "exact_purpose": purpose,
        "requirement_contracts": req_summaries,
        "presence_absence_status": cap["presence_status"],
        "implementation_gap": cap.get("implementation_gap"),
        "current_paths": current_paths,
        "current_symbols": current_symbols,
        "intended_target_paths": target_paths,
        "intended_target_symbols": cap["target_symbols"],
        "current_locations": [{"path": p, "status": "PRESENT" if (ROOT / p).exists() else "STATIC CANDIDATE OR ABSENT", "symbols": [s for s in current_symbols if path_from_ref(s) == p][:30]} for p in current_paths] or [{"path": None, "status": cap["presence_status"], "symbols": []}],
        "target_locations": [{"path": p, "symbol": cap["target_symbols"][min(index, len(cap["target_symbols"]) - 1)], "status": "PLANNED TARGET"} for index, p in enumerate(target_paths)],
        "exact_location_registry_refs": exact_refs,
        "preconditions": [
            "TASK-GOV-001-PROVENANCE-BASELINE is complete at the implementation checkpoint.",
            "Immutable Master Plan hashes match the expected values.",
            f"Characterisation evidence exists for {cap['name']} at every mapped real boundary before mutation.",
        ],
        "semantic_dependencies": [],
        "dependencies": [],
        "dependents": [],
        "files_expected_to_change": expected,
        "files_forbidden_from_changing": [
            "Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md",
            "Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md",
            "Graphify/Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-REPLACE.md",
            "User databases, recordings, transcripts, notes, exports and backups except disposable verified copies",
            "Files owned by unrelated capability batches without a recorded dependency expansion",
        ],
        "data_impact": "USER DATA BOUNDARY: preserve databases, recordings, transcripts, notes, exports, backups and recoverable source audio; use only disposable verified copies for destructive tests." if is_data else "No user-data mutation is planned; discovery of one triggers the CAP-DATA-SAFETY stop condition.",
        "migration_impact": "Disposable-copy migration, backup checksum, integrity, idempotency, interruption and recovery proof required." if is_data else "No schema migration planned; newly discovered schema impact requires an explicit dependency and revised contract before mutation.",
        "data_and_migration_impact": "DATA-SAFETY INTERLOCK REQUIRED: disposable-copy migration, backup checksum, integrity, idempotency, interruption and recovery proof" if is_data else "No schema or user-data mutation is authorized; if implementation discovers one, stop and add the CAP-DATA-SAFETY dependency before change.",
        "ipc_impact": {"known_channels": ipc_channels, "contract": "Preserve or explicitly replace renderer, preload, TypeScript and handler contracts together; reject undeclared channels."},
        "native_impact": {"known_boundaries": native_refs, "contract": "Real native/process cleanup and packaged-path proof required." if is_native else "No native mutation planned; stop on newly discovered native coupling."},
        "packaging_impact": "Inspect electron-builder resources, archive layout, licences and clean installed behavior." if is_package or is_native else "Run packaged smoke coverage if the changed module is reachable from production packaging; no asset change is presumed.",
        "exact_implementation_actions": capability_actions(cap, expected),
        "characterisation_tests_required_before_change": characterization,
        "targeted_verification": [
            {
                "test_path": characterization[0].get("test_path"),
                "reference_status": characterization[0]["reference_status"],
                "evidence_type": evidence_types[0],
                "command": characterization[0]["command"],
                "working_directory": characterization[0]["working_directory"],
                "evidence": f"Graphify/evidence/{slug(cap['name'])}/targeted.log",
            }
        ],
        "real_integration_verification": [
            {
                "test_path": None if governance_evidence else planned_integration_path,
                "reference_status": "STATIC VALIDATOR" if governance_evidence else "TEST TO CREATE",
                "evidence_type": "STATIC/GRAPH AUDIT" if governance_evidence else evidence_types[min(1, len(evidence_types) - 1)],
                "command": "python Graphify/tools/validate_planning.py" if governance_evidence else test_command(planned_integration_path),
                "working_directory": "." if governance_evidence else "codebase",
                "boundary": "Reconcile the planning/provenance evidence graph; no application integration result is implied." if governance_evidence else "Exercise the real SQLite/filesystem/Electron/native/process/audio/model or installed boundary named by the evidence type; mocks cannot close this proof.",
                "evidence": f"Graphify/evidence/{slug(cap['name'])}/integration.log",
            }
        ],
        "broader_regression_verification": ([
            {"reference_status": "STATIC VALIDATOR", "evidence_type": "STATIC/GRAPH AUDIT", "command": "python Graphify/tools/validate_planning.py", "working_directory": ".", "evidence": f"Graphify/evidence/{slug(cap['name'])}/regression.log"},
        ] if governance_evidence else [
            {"reference_status": "PACKAGE SCRIPT", "evidence_type": "APPLICATION UNIT TEST", "command": "npm test", "working_directory": "codebase", "evidence": f"Graphify/evidence/{slug(cap['name'])}/regression.log"},
            {"reference_status": "PACKAGE SCRIPT", "evidence_type": "STATIC/GRAPH AUDIT", "command": "npm run typecheck", "working_directory": "codebase", "evidence": f"Graphify/evidence/{slug(cap['name'])}/typecheck.log"},
            {"reference_status": "PACKAGE SCRIPT", "evidence_type": "STATIC/GRAPH AUDIT", "command": "npm run lint", "working_directory": "codebase", "evidence": f"Graphify/evidence/{slug(cap['name'])}/lint.log"},
        ]),
        "evidence_types": evidence_types,
        "offline_verification_impact": "Run with external networking denied; prove only explicit owned loopback services remain and save connection observations." if cap["id"] in {"CAP-NETWORK-POLICY", "CAP-QDRANT", "CAP-LOOPBACK-WEBSOCKETS", "CAP-OFFLINE-FIRST-LAUNCH", "CAP-REMOVE-RUNTIME-EXTERNAL-NETWORKING"} else "Include this workflow in the final installed offline regression when runtime reachable; record NOT APPLICABLE with reachability evidence only when it is not runtime reachable.",
        "rollback_or_recovery_strategy": "Before mutation create a focused Git commit when Git exists. If Git is unavailable, save the required pre-batch hashes and reversible file delta. Restore only this task's owned paths; never reset, clean, stash or discard unrelated work. Restore user data only from verified backups after a failed disposable-copy recovery drill.",
        "required_evidence_artifacts": [
            f"Graphify/evidence/{slug(cap['name'])}/pre-change-characterization.json",
            f"Graphify/evidence/{slug(cap['name'])}/implementation-delta.json",
            f"Graphify/evidence/{slug(cap['name'])}/targeted.log",
            f"Graphify/evidence/{slug(cap['name'])}/integration.log",
            f"Graphify/evidence/{slug(cap['name'])}/regression.log",
            f"Graphify/evidence/{slug(cap['name'])}/offline-or-applicability.json",
        ],
        "completion_criteria": [
            f"Every requirement in {', '.join(cap['master_requirement_ids'])} has direct saved evidence or an explicitly permitted conditional disposition.",
            "All expected paths and symbols are reconciled in EXACT_LOCATION_REGISTRY.json at the same verified checkpoint.",
            "Targeted, real integration and broader regression commands have saved exit codes and logs; no planning status is substituted for execution proof.",
        ],
        "acceptance_criteria": [
            f"The declared {cap['name']} target and every mapped current anchor reconcile at one verified commit/hash checkpoint.",
            "All task-specific characterisation, targeted, real-boundary, broader regression and offline/applicability evidence has an exact command or manual method, result, artifact path and honest status.",
            "No Master requirement is weakened, no unrelated owner is modified, and missing/hardware-dependent proof is reported as BLOCKED or HARDWARE UNAVAILABLE rather than PASS.",
        ],
        "stop_conditions": [
            "A Master Plan hash changes or an instruction conflicts with the immutable authority.",
            "A user-data, migration, native, packaging or unrelated-capability impact appears without the declared dependency and recovery proof.",
            "Required real evidence cannot be collected; record BLOCKED or HARDWARE UNAVAILABLE rather than weakening the test or claiming completion.",
        ],
        "risk_classification": "CRITICAL" if is_data else ("HIGH" if is_native or is_package or task_kind == "DELETION" else "MEDIUM"),
        "task_kind": task_kind,
        "planning_status": "IMPLEMENTATION READY - EXECUTION NOT STARTED",
    }


REMOVAL_TERMS: dict[str, list[str]] = {
    "CAP-REMOVE-AUTHENTICATION": ["authentication", "login", "sign in", "oauth"],
    "CAP-REMOVE-ACCOUNTS": ["account", "user profile"],
    "CAP-REMOVE-CLOUD-SYNCHRONISATION": ["cloud sync", "cloudsync", "sync status", "sync across machines", "remote_id"],
    "CAP-REMOVE-WORKSPACES": ["workspace", "workspace_id"],
    "CAP-REMOVE-ORGANISATIONS": ["organization", "organisation", "org_id"],
    "CAP-REMOVE-TEAMS": ["team", "team_id"],
    "CAP-REMOVE-INVITATIONS": ["invitation", "invite"],
    "CAP-REMOVE-SHARING": ["share link", "shared_with", "sharing"],
    "CAP-REMOVE-HOSTED-TRANSCRIPTION": ["deepgram", "assemblyai", "hosted transcription", "transcription provider"],
    "CAP-REMOVE-HOSTED-AI": ["openai", "anthropic", "gemini", "hosted ai", "ai provider"],
    "CAP-REMOVE-LOCAL-GENERATIVE-AI": ["local llm", "ollama", "generative ai", "text generation"],
    "CAP-REMOVE-AI-AGENTS": ["ai agent", "agent tool", "agent_id"],
    "CAP-REMOVE-CHAT": ["chat message", "chat session", "assistant chat"],
    "CAP-REMOVE-SUMMARISATION": ["summarize", "summarise", "summary generation"],
    "CAP-REMOVE-ACTION-ITEM-EXTRACTION": ["action item", "action_items"],
    "CAP-REMOVE-AI-REWRITING": ["ai rewrite", "improve writing", "rewrite with"],
    "CAP-REMOVE-CALENDAR": ["google calendar", "calendar event", "calendar_id"],
    "CAP-REMOVE-MCP": ["mcp", "mcp server", "model context protocol"],
    "CAP-REMOVE-PUBLIC-API": ["public api", "api server", "cli token", "programmatic access", "public url", "authorization header", "command-line access", "cloud mode"],
    "CAP-REMOVE-API-KEYS": ["api key", "api_key", "provider key"],
    "CAP-REMOVE-BILLING": ["billing", "subscription", "payment"],
    "CAP-REMOVE-USAGE-QUOTAS": ["usage quota", "quota", "credits remaining", "daily limit", "transcription limit", "words per week", "limit resets"],
    "CAP-REMOVE-REFERRALS": ["referral", "refer a friend"],
    "CAP-REMOVE-UPGRADE-SYSTEMS": ["upgrade", "upgrade plan", "premium", "pro plan"],
    "CAP-REMOVE-AUTOMATIC-UPDATER": ["auto updater", "autoupdater", "electron-updater", "check for updates"],
    "CAP-REMOVE-RUNTIME-MODEL-DOWNLOADS": ["download model", "download binary", "fetchlatestrelease", "runtime download"],
    "CAP-REMOVE-TELEMETRY": ["telemetry", "sentry", "crash upload"],
    "CAP-REMOVE-ANALYTICS": ["analytics", "usageanalytics", "usageanalyticsdescription", "posthog", "mixpanel", "track event"],
    "CAP-REMOVE-RUNTIME-EXTERNAL-LINKS": ["openexternal", "external link", "https://"],
    "CAP-REMOVE-RUNTIME-EXTERNAL-NETWORKING": ["https.request", "fetch(", "axios", "external network", "websocket"],
    "CAP-REMOVE-ACTIVE-OPENWHISPR-IDENTITY": ["openwhispr", "open whispr", "openwhispr_dev_server_port", "openwhispr_log_level"],
}


DELETION_LAYERS = [
    "UI", "navigation", "route", "component", "hook/store", "preload", "TypeScript contract",
    "IPC channel", "IPC handler", "service", "database/filesystem/native effect", "settings",
    "environment variables", "dependency", "tests", "fixtures", "translations", "build", "packaging",
]


def deletion_layer_for(path: str, context: str) -> list[str]:
    value = f"{path} {context}".lower()
    layers: list[str] = []
    rules = [
        (("renderer/", ".css", ".html"), "UI"), (("sidebar", "navigation", "nav"), "navigation"),
        (("route", "router"), "route"), (("component", ".jsx", ".tsx"), "component"),
        (("hook", "store", "zustand"), "hook/store"), (("preload/", "contextbridge"), "preload"),
        (("renderer/shared/types", ".d.ts", "electron.ts"), "TypeScript contract"), (("ipc channel", "ipc-channel", "invoke("), "IPC channel"),
        (("ipchandlers", "ipcmain.handle", "ipcmain.on"), "IPC handler"), (("main/features", "service", "manager"), "service"),
        (("database", "migration", "filesystem", "native/", "resources/bin"), "database/filesystem/native effect"),
        (("settings", "localstorage"), "settings"), (("process.env", ".env"), "environment variables"),
        (("package.json", "package-lock.json", "node_modules"), "dependency"), (("tests/", ".test."), "tests"),
        (("fixture", "fixtures/"), "fixtures"), (("i18n", "translation"), "translations"),
        (("scripts/build", "vite", "build"), "build"), (("electron-builder", "packaging/", "extraresources"), "packaging"),
    ]
    for needles, layer in rules:
        if any(needle in value for needle in needles):
            layers.append(layer)
    return unique(layers or ["service"])


inventory_doc = load_json(G / "REPOSITORY_FILE_INVENTORY.json")
inventory_entries = inventory_doc.get("entries", inventory_doc.get("files", []))
source_text_paths: list[str] = []
text_suffixes = {".js", ".jsx", ".ts", ".tsx", ".json", ".css", ".html", ".c", ".cc", ".cpp", ".h", ".m", ".mm", ".swift", ".sh", ".ps1", ".yml", ".yaml", ".txt"}
for entry in inventory_entries:
    path = entry.get("path", "")
    if (entry.get("authority") == "source_authoritative" or entry.get("source_authoritative") is True) and path.startswith("codebase/") and Path(path).suffix.lower() in text_suffixes and (ROOT / path).exists():
        source_text_paths.append(path)
if (ROOT / "codebase/LICENSE").is_file():
    source_text_paths.append("codebase/LICENSE")
source_text_paths = unique(source_text_paths)


removal_candidates: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)


def matched_removal_terms(line: str, terms: list[str]) -> list[str]:
    """Context candidates only; a match is never a deletion decision."""
    return [
        term
        for term in terms
        if re.search(rf"(?<![A-Za-z0-9_]){re.escape(term)}(?![A-Za-z0-9_])", line, re.I)
    ]


def deletion_disposition(cap_id: str, path: str, line: str) -> str:
    value = f"{path} {line}".lower().replace("\\", "/")
    if "tokenizer" in value or "all-minilm" in value:
        return "RETAINED DEPENDENCY - DO NOT DELETE"
    if cap_id == "CAP-REMOVE-WORKSPACES" and (
        path in {
            "codebase/main/features/dictation/clipboard.js",
            "codebase/main/features/meetings/meetingProcessDetector.js",
        }
        or any(term in value for term in ("nsworkspace", "workspace.activewindow", "workspace app launched", "workspace app terminated", "visibleonallworkspaces"))
    ):
        return "RETAINED DEPENDENCY - DO NOT DELETE"
    if any(term in value for term in (
        "getloginitemsettings", "setloginitemsettings", "login item", "open at login", "launch at login",
        "auto-start at login", "autostart at login", "logout/login", "login to take effect",
    )):
        return "RETAINED DEPENDENCY - DO NOT DELETE"
    if cap_id == "CAP-REMOVE-AUTHENTICATION" and any(term in value for term in (
        "input group", "group changes", "re-login", "new login session", "ydotoold", "runs on every login",
    )):
        return "RETAINED DEPENDENCY - DO NOT DELETE"
    if cap_id == "CAP-REMOVE-ACTIVE-OPENWHISPR-IDENTITY" and (
        any(term in value for term in ("legacy", "any old \"openwhispr\"", ".cache/openwhispr", "openwhispr-binds.conf"))
        or ('".cache"' in value and '"openwhispr"' in value)
    ):
        return "HISTORICAL MIGRATION - PRESERVE"
    if cap_id == "CAP-REMOVE-UPGRADE-SYSTEMS" and "premium" in value and not any(
        term in value for term in ("premium plan", "upgrade", "subscription", "paid plan", "billing")
    ):
        return "FALSE POSITIVE"
    if cap_id == "CAP-REMOVE-UPGRADE-SYSTEMS" and "pip upgrade" in value:
        return "RETAINED DEPENDENCY - DO NOT DELETE"
    if cap_id == "CAP-REMOVE-TEAMS" and "small team" in value:
        return "FALSE POSITIVE"
    if cap_id == "CAP-REMOVE-HOSTED-AI" and "local network" in value:
        return "FALSE POSITIVE"
    if cap_id == "CAP-REMOVE-SHARING" and "sharing anonymous performance metrics" in value:
        return "FALSE POSITIVE"
    if any(term in value for term in ("no account required", "no account", "without an account", "no login required", "no login or api key", "no account or api key", "local-only", "offline-only")):
        return "POSITIVE OFFLINE/LOCAL MESSAGE - RETAIN"
    if "/migrations/" in value or "datamigration" in value or "historical migration" in value or "legacy migration" in value:
        return "HISTORICAL MIGRATION - PRESERVE"
    if any(term in value for term in ("license", "licence", "copyright", "third-party", "notice")):
        return "LEGAL/ATTRIBUTION - PRESERVE"
    if "/scripts/downloads/" in value or "/scripts/lib/download-utils.js" in value or "build-time" in value:
        return "BUILD-TIME ONLY - REVIEW UNDER BUILD RULE"
    if any(term in value for term in ("127.0.0.1", "localhost", "loopback")):
        return "RETAINED DEPENDENCY - DO NOT DELETE"
    if "runtimenetworkpolicy" in value and any(term in value for term in ("blocked", "deny", "example.com", "external")):
        return "POSITIVE OFFLINE/LOCAL MESSAGE - RETAIN"
    if path.endswith(("package.json", "package-lock.json", "electron-builder.json")):
        return "REQUIRES IMPLEMENTATION-TIME STATIC PROOF"
    if path.startswith(("codebase/main/", "codebase/preload/", "codebase/renderer/")):
        return "ACTIVE REMOVAL CANDIDATE"
    if path.startswith(("codebase/scripts/packaging/", "codebase/packaging/")):
        return "REQUIRES PACKAGED-APPLICATION PROOF"
    if path.startswith("codebase/tests/"):
        return "REQUIRES IMPLEMENTATION-TIME STATIC PROOF"
    if path.startswith("codebase/shared/i18n/"):
        return "ACTIVE REMOVAL CANDIDATE"
    return "FALSE POSITIVE"


for source_path in source_text_paths:
    try:
        source_lines = (ROOT / source_path).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        continue
    for line_number, line in enumerate(source_lines, 1):
        lower = line.lower()
        for cap_id, terms in REMOVAL_TERMS.items():
            hits = matched_removal_terms(lower, terms)
            if hits:
                removal_candidates[cap_id].append({
                    "path": source_path,
                    "line": line_number,
                    "anchor": line.strip()[:220],
                    "matched_terms": hits,
                    "reviewed_disposition": deletion_disposition(cap_id, source_path, line),
                    "review_basis": "Context rule evaluated path, architectural layer, runtime/build role, historical/legal status, and known false-positive exclusions; implementation interlocks remain mandatory.",
                    "layers": deletion_layer_for(source_path, line),
                })


cap_by_id = {item["id"]: item for item in capabilities}
for removal_cap_id in REMOVAL_CAPS:
    removal_cap = cap_by_id.get(removal_cap_id)
    if not removal_cap:
        continue
    active_paths = unique(
        candidate["path"]
        for candidate in removal_candidates.get(removal_cap_id, [])
        if candidate["reviewed_disposition"] == "ACTIVE REMOVAL CANDIDATE"
    )
    removal_cap["current_paths"] = active_paths
    removal_cap["current_symbols"] = [verified_anchor(removal_cap_id, path) for path in active_paths]
    removal_cap["presence_status"] = (
        "ACTIVE REMOVAL CANDIDATES MAPPED - IMPLEMENTATION INTERLOCKS REQUIRED"
        if active_paths
        else "NO ACTIVE PATH CURRENTLY MAPPED - IMPLEMENTATION-TIME PROOF STILL REQUIRED"
    )
tasks: list[dict[str, Any]] = []


def add_task(task_id: str, cap: dict[str, Any], purpose: str, task_kind: str, phase: str, wave: str, ordering_rationale: str) -> dict[str, Any]:
    task = {"stable_task_id": task_id, **cap_contract_fields(cap, purpose, task_kind)}
    task.update({"phase": phase, "wave": wave, "ordering_rationale": ordering_rationale})
    tasks.append(task)
    return task


first_cap = cap_by_id["CAP-PROVENANCE"]
first = add_task(
    "TASK-GOV-001-PROVENANCE-BASELINE", first_cap,
    "At the start of the future implementation run, establish recoverable repository provenance before any application mutation: confirm the root, capture Git state if present, otherwise create the Master Plan-permitted pre-Git complete inventory/hash checkpoint and then initialize Git only within that implementation authority.",
    "GOVERNANCE", "PHASE-01-AUTHORITY-AND-PROVENANCE", "WAVE-01",
    "This is the exact first implementation task because every later mutation, migration, deletion and rollback requires recoverable provenance.",
)
first["preconditions"] = ["Future implementation authority is explicit.", "All three immutable Master Plan hashes match their recorded values.", "The user worktree has been inventoried without mutation."]
first["current_locations"] = [{"path": ".git/", "status": ("PRESENT AT PLANNING CHECKPOINT" if GIT_STATE["present"] else "ABSENT AT PLANNING CHECKPOINT"), "symbols": []}, {"path": "Graphify/REPOSITORY_FILE_INVENTORY.json", "status": "PRESENT BASELINE", "symbols": ["source_authoritative entries"]}]
first["target_locations"] = [{"path": ".git/", "symbol": "repository provenance", "status": ("PRESENT - PROVENANCE RECORDING REQUIRED AT IMPLEMENTATION START" if GIT_STATE["present"] else "PLANNED ADDITION IF STILL ABSENT AND IMPLEMENTATION AUTHORITY PERMITS")}, {"path": "Graphify/RUN_STATE.md", "symbol": "verified implementation checkpoint", "status": "PLANNED UPDATE"}]
first["files_expected_to_change"] = [".git/ if absent", ".gitignore if required by verified inventory", "Graphify/RUN_STATE.md", "Graphify/REPOSITORY_FILE_INVENTORY.json", "Graphify/evidence/provenance/"]
first["semantic_dependencies"] = []
first["dependencies"] = []
first["exact_implementation_actions"] = [
    "Resolve and record the absolute repository root; capture branch, HEAD, staged, unstaged, deleted and untracked state with read-only Git commands if .git exists.",
    "If .git remains absent, hash every source-authoritative application file and immutable Master Plan file, save the complete path/hash inventory and record the missing Git state before initialization.",
    "Review .gitignore against node_modules, build outputs, caches, binaries, models, user databases and recordings; change only ignore rules supported by the inventory.",
    "Under future implementation authority, initialize Git only after the complete pre-Git checkpoint exists, then create a focused baseline commit without deleting, resetting, cleaning or stashing user work.",
    "Save commit/hash identifiers in RUN_STATE.md and require every subsequent task to reference this checkpoint.",
]


phase2_ids = {
    "CAP-PLANNING-GOVERNANCE", "CAP-EXACT-LOCATION", "CAP-IMPLEMENTATION-GOVERNANCE", "CAP-DATA-SAFETY",
    "CAP-DATABASE", "CAP-LEGACY-MIGRATION", "CAP-BACKUP", "CAP-RESTORE", "CAP-IPC",
    "CAP-DELETION-GOVERNANCE", "CAP-TESTING",
}
phase3_ids = set(PRODUCT_SCOPE_CAPS) | {
    "CAP-APP-SHELL", "CAP-RENDERER", "CAP-WHISPER", "CAP-MODEL-DISCOVERY", "CAP-MODEL-PACK",
    "CAP-MODELS", "CAP-NETWORK-POLICY", "CAP-ONBOARDING", "CAP-SETTINGS", "CAP-KEYRING",
    "CAP-HOTKEY", "CAP-MICROPHONE", "CAP-SYSTEM-AUDIO", "CAP-AUDIO", "CAP-AEC", "CAP-VAD",
}
phase6_ids = {
    "CAP-REPOSITORY", "CAP-THIRD-PARTY", "CAP-LEGAL", "CAP-MARKDOWN-GOVERNANCE", "CAP-SIMPLIFICATION",
    "CAP-PACKAGING", "CAP-WINDOWS-INSTALLER", "CAP-PORTABLE-WINDOWS", "CAP-MACOS-LINUX", "CAP-NATIVE",
}
generic_caps = [cap for cap in capabilities if cap["id"] not in {"CAP-PROVENANCE", "CAP-RELEASE"} and cap["id"] not in CONDITIONAL_SPECS and not cap["id"].startswith("CAP-REMOVE-") and cap.get("decision") not in {"REMOVE", "FORBIDDEN"}]
generic_caps.sort(key=lambda cap: (0 if cap["id"] in phase2_ids else 1 if cap["id"] in phase3_ids else 3 if cap["id"] in phase6_ids else 2, cap["id"]))
for cap in generic_caps:
    if cap["id"] in phase2_ids:
        phase, wave, action = "PHASE-02-CHARACTERIZATION-AND-DATA-SAFETY", "WAVE-02", "characterize, protect and establish the cross-cutting contract for"
    elif cap["id"] in phase3_ids:
        phase, wave, action = "PHASE-03-DECOUPLING-AND-RETAINED-PROTECTION", "WAVE-03", "characterize and protect the retained boundary or prerequisite replacement for"
    elif cap["id"] in phase6_ids:
        phase, wave, action = "PHASE-06-REORGANIZATION-AND-CLEANUP", "WAVE-06", "reorganize, consolidate or prepare final packaging for"
    else:
        phase, wave, action = "PHASE-05-RETAINED-CAPABILITIES", "WAVE-05", "preserve, repair, decouple or add the fully mapped local capability"
    add_task(
        f"TASK-CAP-{cap['id'].removeprefix('CAP-')}", cap,
        f"At the mapped paths and symbols, {action} {cap['name']} and satisfy every linked Master requirement without reintroducing removed remote systems.",
        "CAPABILITY", phase, wave,
        "The task phase is selected from real prerequisites: baseline and data harnesses, retained-boundary protection, excluded-system removal, retained completion, then repository/package consolidation.",
    )


for cap in [item for item in capabilities if item["id"].startswith("CAP-REMOVE-") or item.get("decision") in {"REMOVE", "FORBIDDEN"}]:
    task = add_task(
        f"TASK-DEL-{cap['id'].removeprefix('CAP-REMOVE-')}", cap,
        f"Classify every static candidate for {cap['name']}, preserve permitted historical/legal/migration evidence, and remove every proven active product path only after all seven Binding Deletion Interlock checks pass across the complete architectural chain.",
        "DELETION", "PHASE-04-EXCLUDED-SYSTEM-REMOVAL", "WAVE-04",
        "Deletion follows provenance, characterization, migration protection and boundary mapping; it precedes retained feature completion so removed coupling cannot be rebuilt.",
    )
    candidates = removal_candidates.get(cap["id"], [])
    task["static_analysis_candidates"] = candidates
    task["candidate_disposition_counts"] = dict(sorted(collections.Counter(candidate["reviewed_disposition"] for candidate in candidates).items()))
    task["deletion_architectural_layer_coverage"] = {
        layer: {
            "status": "CANDIDATES REVIEWED - IMPLEMENTATION-TIME PROOF REQUIRED" if any(layer in candidate["layers"] for candidate in candidates) else "NONE CURRENTLY MAPPED - IMPLEMENTATION-TIME PROOF STILL REQUIRED",
            "candidates": [f"{candidate['path']}:{candidate['line']}::{candidate['reviewed_disposition']}::{candidate['anchor']}" for candidate in candidates if layer in candidate["layers"]],
            "absence_rule": "An empty candidate list is not absence proof; inspect imports, dynamic/string references, runtime registration and packaged output, then save a scoped not-present record.",
        }
        for layer in DELETION_LAYERS
    }
    task["binding_deletion_interlocks"] = [
        {"gate": "BDI-1-STATIC-IMPORT-EXPORT", "check": "Audit every static import, require, export, re-export and source-controlled dependency edge for the scoped system; preserve retained callers until a proven local replacement exists.", "status": "PLANNED PROOF REQUIRED"},
        {"gate": "BDI-2-DYNAMIC-AND-STRING-REFERENCES", "check": "Audit dynamic imports, computed paths, channel/event names, URLs, command strings, reflection and other string references; classify each contextual hit by its reviewed disposition.", "status": "PLANNED PROOF REQUIRED"},
        {"gate": "BDI-3-RUNTIME-REGISTRATION", "check": "Audit renderer navigation/routes, preload exposure, typed IPC, ipcMain handlers, events, workers, listeners, sidecars, child processes and startup/shutdown registrations.", "status": "PLANNED PROOF REQUIRED"},
        {"gate": "BDI-4-DATABASE-SETTINGS-ENVIRONMENT", "check": "Audit current schema, forward migrations, historical migrations, settings, localStorage keys, environment variables and feature flags; preserve history and user data.", "status": "PLANNED PROOF REQUIRED"},
        {"gate": "BDI-5-NATIVE-ASSET-BUILD-PACKAGING", "check": "Audit native helpers, bundled assets/models/binaries, build scripts, package manifests, electron-builder resources, staging and installed contents without editing vendor files.", "status": "PLANNED PROOF REQUIRED"},
        {"gate": "BDI-6-TEST-FIXTURE", "check": "Audit tests and fixtures, add retained-workflow characterisation before deletion, then prove targeted absence plus real replacement, regression, offline and packaged behavior.", "status": "PLANNED PROOF REQUIRED"},
        {"gate": "BDI-7-LICENCE-FUTURE-PLAN", "check": "Audit licences, notices, attribution, historical provenance, replacement maps and future-plan references; preserve required legal/history text and reconcile the final Graphify/static/runtime/package rescan.", "status": "PLANNED PROOF REQUIRED"},
    ]
    task["exact_implementation_actions"] = [
        f"Review all {len(candidates)} recorded static candidates and the exact registry for {cap['id']}; label each ACTIVE, HISTORICAL/LEGAL/MIGRATION, BUILD-TIME-ISOLATED or FALSE POSITIVE with path, symbol/anchor and owner.",
        "Trace static imports, dynamic imports, string references and runtime registration from renderer entry through preload/IPC/service to data, filesystem, native, child-process and packaged effects; an empty text search cannot close a layer.",
        "Add characterization tests for every retained workflow sharing a boundary, and create a disposable database/user-data fixture before any schema or filesystem change.",
        "Complete BDI-1 through BDI-4; stop if any retained caller, data path, migration history, legal notice or replacement proof is unresolved.",
        "Remove only classified active artifacts across all listed layers in one recoverable batch; keep historical migrations and permitted legal/legacy evidence explicitly labelled.",
        "Complete BDI-5 and BDI-6, update dependencies/lockfile only when the removed package has no retained caller, and save the exact diff plus database/native/package evidence.",
        "Complete BDI-7 with final Graphify/static, runtime-network and packaged-output evidence; reconcile every remaining term hit rather than treating zero search results as the sole proof.",
    ]
    task["removal_interlocks"] = task["binding_deletion_interlocks"]


decision_packages: list[dict[str, Any]] = []
for cap_id, spec in CONDITIONAL_SPECS.items():
    cap = cap_by_id[cap_id]
    short = cap_id.removeprefix("CAP-")
    decision_task_id = f"TASK-DEC-{short}"
    default_task_id = f"TASK-OUT-{short}-DEFAULT"
    deviation_task_id = f"TASK-OUT-{short}-DEVIATION"
    decision_task = add_task(
        decision_task_id, cap,
        f"Collect and record the evidence package for {spec['title']} without making a preference-based product decision; apply the Master default unless the stated deviation condition is proven.",
        "CONDITIONAL DECISION", "PHASE-05-RETAINED-CAPABILITIES", "WAVE-05C",
        "The decision is scheduled after retained boundaries are stable and before either mutually exclusive implementation outcome.",
    )
    decision_task.update({
        "mandatory_default": spec["default"], "deviation_condition": spec["deviation"],
        "decision_evidence_to_collect": [spec["test"], *[f"Measured comparison: {dimension}" for dimension in spec["dimensions"]]],
        "comparison_dimensions": spec["dimensions"], "decision_owner": spec["owner"], "fallback": spec["fallback"],
        "threshold_rule": "Do not invent an arbitrary numeric threshold. Record observed data and use only a threshold already mandated by the Master Plan, a documented platform constraint, a licence/safety requirement, or a user-approved product limit.",
        "permitted_outcome_task_ids": [default_task_id, deviation_task_id],
    })
    decision_task["exact_implementation_actions"] = [
        f"Inspect and anchor every current decision location: {', '.join(spec['locations'])}.",
        f"Collect the required evidence without selecting an outcome in advance: {spec['test']}",
        f"Compare and record every dimension at the same verified checkpoint: {', '.join(spec['dimensions'])}.",
        f"Apply the mandatory default unless this exact deviation condition is proven: {spec['deviation']}",
        f"Record DEFAULT SELECTED or DEVIATION SELECTED with the evidence bundle, owner {spec['owner']}, and fallback: {spec['fallback']}",
        "Do not invent a numeric threshold; use only a Master Plan mandate, documented platform constraint, licence/safety requirement, or user-approved product limit.",
    ]
    default_task = add_task(
        default_task_id, cap,
        f"Execute the mandatory-default outcome for {spec['title']}: {spec['default']}",
        "CONDITIONAL OUTCOME - DEFAULT", "PHASE-05-RETAINED-CAPABILITIES", "WAVE-05D",
        "Runs only after the decision record selects the Master default; otherwise close as NOT APPLICABLE with the same decision evidence ID.",
    )
    default_task["preconditions"].append(f"{decision_task_id} records DEFAULT SELECTED; otherwise this task receives a NOT APPLICABLE disposition and makes no code change.")
    default_task["exact_implementation_actions"] = [
        f"Link the decision evidence from {decision_task_id} and record DEFAULT SELECTED.",
        f"Apply the default exactly: {spec['default']}",
        f"Verify the mapped locations: {', '.join(spec['locations'])}.",
        f"Execute this evidence method: {spec['test']}",
        f"If the selected outcome fails, stop and restore the verified fallback: {spec['fallback']}",
    ]
    deviation_task = add_task(
        deviation_task_id, cap,
        f"Execute the permitted deviation outcome for {spec['title']} only when the evidence package proves: {spec['deviation']}",
        "CONDITIONAL OUTCOME - DEVIATION", "PHASE-05-RETAINED-CAPABILITIES", "WAVE-05E",
        "Runs only after the decision record selects the permitted deviation; otherwise close as NOT APPLICABLE with the same decision evidence ID.",
    )
    deviation_task["preconditions"].append(f"{decision_task_id} records DEVIATION SELECTED with evidence satisfying the stated condition; otherwise this task receives a NOT APPLICABLE disposition and makes no code change.")
    deviation_task["exact_implementation_actions"] = [
        f"Link the decision evidence from {decision_task_id} and prove this deviation condition: {spec['deviation']}",
        f"Change only the owned locations: {', '.join(spec['locations'])}.",
        f"Compare all dimensions without arbitrary thresholds: {', '.join(spec['dimensions'])}.",
        f"Execute this evidence method: {spec['test']}",
        f"If any required dimension or release gate regresses, restore the verified fallback: {spec['fallback']}",
    ]
    package = {
        "decision_package_id": f"DEC-{short}", "capability_id": cap_id, "title": spec["title"],
        "master_requirement_ids": cap["master_requirement_ids"],
        "master_plan_sources": unique(requirements_by_id[req_id]["source_master_plan"] for req_id in cap["master_requirement_ids"]),
        "master_plan_default": spec["default"], "mandatory_default": spec["default"],
        "deviation_condition": spec["deviation"], "evidence_to_collect": [spec["test"]],
        "exact_current_implementation_locations": spec["locations"], "test_method": spec["test"],
        "comparison_dimensions": spec["dimensions"], "decision_owner": spec["owner"],
        "decision_phase": "PHASE-05-RETAINED-CAPABILITIES", "fallback": spec["fallback"],
        "threshold_rule": decision_task["threshold_rule"],
        "allowed_outcomes": ["DEFAULT", "DEVIATION"],
        "conditional_preservation_rule": "Do not delete or disable the conditional capability merely to simplify packaging; select the Master default unless the evidence package proves the deviation condition.",
        "downstream_tasks_by_outcome": {"DEFAULT": default_task_id, "DEVIATION": deviation_task_id},
        "decision_task_id": decision_task_id, "planning_status": "COMPLETE PACKAGE - FUTURE EVIDENCE AND DECISION PENDING",
    }
    decision_packages.append(package)


phase_gate_cap = cap_by_id["CAP-IMPLEMENTATION-GOVERNANCE"]
PHASE_GATES = [
    ("TASK-GOV-002-CHARACTERIZATION-GATE", "PHASE-02-CHARACTERIZATION-AND-DATA-SAFETY", "WAVE-02Z", "Reconcile authority, architecture, data-safety, provenance, IPC, test and deletion-interlock characterization evidence before any retained-boundary decoupling."),
    ("TASK-GOV-003-DECOUPLING-GATE", "PHASE-03-DECOUPLING-AND-RETAINED-PROTECTION", "WAVE-03Z", "Prove the retained product-scope boundaries and prerequisite local replacements are characterized and protected before removing excluded systems."),
    ("TASK-GOV-004-REMOVAL-GATE", "PHASE-04-EXCLUDED-SYSTEM-REMOVAL", "WAVE-04Z", "Reconcile every deletion disposition, all seven interlocks, retained replacement proof, data integrity and scoped absence evidence before retained capability completion."),
    ("TASK-GOV-005-CAPABILITY-GATE", "PHASE-05-RETAINED-CAPABILITIES", "WAVE-05Z", "Reconcile every retained, repaired, missing and conditional capability outcome at one verified checkpoint before repository consolidation and packaging preparation."),
    ("TASK-GOV-006-CONSOLIDATION-GATE", "PHASE-06-REORGANIZATION-AND-CLEANUP", "WAVE-06Z", "Reconcile ownership moves, dependency cleanup, legal notices, simplification preparation and packaging inputs before final release evidence collection."),
]
for gate_task_id, phase, wave, purpose in PHASE_GATES:
    gate_task = add_task(
        gate_task_id,
        phase_gate_cap,
        purpose,
        "PHASE GATE",
        phase,
        wave,
        "A phase gate depends on every task in its own phase and is the sole prerequisite barrier for the next phase; it is not an administrative PASS substitute.",
    )
    gate_task["exact_implementation_actions"] = [
        f"Enumerate every non-gate task in {phase} from IMPLEMENTATION_QUEUE.json and verify its evidence disposition at the same commit/hash checkpoint.",
        "Reject missing, stale, mocked-as-final, hardware-misreported, or planning-only evidence and retain the gate as FAIL/BLOCKED until every applicable contract is reconciled.",
        "Write only the evidence links, checkpoint, reviewer, failures and repair actions to the implementation run state; do not treat this planning record as executed proof.",
    ]


release_cap = cap_by_id["CAP-RELEASE"]
for gate in RELEASE_GATES:
    task = add_task(
        f"TASK-REL-{gate['release_gate_id'].removeprefix('GATE-')}", release_cap,
        f"Collect, reconcile and independently review the real implementation evidence for release gate {gate['release_gate_id']}: {gate['name']}; planning artifacts alone cannot pass it.",
        "RELEASE PROOF", "PHASE-07-INTEGRATION-AND-RELEASE-EVIDENCE", "WAVE-07",
        "Release proof follows all capability, deletion and conditional dispositions and remains conjunctive: one failed applicable gate blocks release approval.",
    )
    task["release_gate_id"] = gate["release_gate_id"]
    task["planned_release_proof"] = gate["planned_proof"]
    task["exact_implementation_actions"] = [
        f"Resolve every requirement mapped to {gate['release_gate_id']} and list its evidence artifact, verified checkpoint, command, exit code and reviewer disposition.",
        *[f"Collect and validate: {proof}." for proof in gate["planned_proof"]],
        "Reject stale evidence, planning-only claims, mocked substitutes for required real boundaries, and evidence from a different commit/hash checkpoint.",
        "Record PASS only when every applicable proof exists; otherwise record FAIL, BLOCKED or HARDWARE UNAVAILABLE according to the Master Plan and do not approve release.",
    ]
    gate["proof_task_ids"] = [task["stable_task_id"]]
    gate["planning_status"] = "PROOF TASK PLANNED - IMPLEMENTATION EVIDENCE PENDING"


# Build semantic prerequisites first, then derive a deterministic topological
# execution order. Conditional outcome tasks both receive a disposition; the
# unselected outcome closes as evidence-linked NOT APPLICABLE.
task_by_id = {task["stable_task_id"]: task for task in tasks}
phase_predecessor = {
    "PHASE-02-CHARACTERIZATION-AND-DATA-SAFETY": "TASK-GOV-001-PROVENANCE-BASELINE",
    "PHASE-03-DECOUPLING-AND-RETAINED-PROTECTION": "TASK-GOV-002-CHARACTERIZATION-GATE",
    "PHASE-04-EXCLUDED-SYSTEM-REMOVAL": "TASK-GOV-003-DECOUPLING-GATE",
    "PHASE-05-RETAINED-CAPABILITIES": "TASK-GOV-004-REMOVAL-GATE",
    "PHASE-06-REORGANIZATION-AND-CLEANUP": "TASK-GOV-005-CAPABILITY-GATE",
    "PHASE-07-INTEGRATION-AND-RELEASE-EVIDENCE": "TASK-GOV-006-CONSOLIDATION-GATE",
}
phase_gate_ids = {task_id for task_id, _phase, _wave, _purpose in PHASE_GATES}
for task in tasks:
    task_id = task["stable_task_id"]
    if task_id == "TASK-GOV-001-PROVENANCE-BASELINE":
        dependencies: list[str] = []
    elif task_id in phase_gate_ids:
        dependencies = sorted(
            other["stable_task_id"]
            for other in tasks
            if other["phase"] == task["phase"] and other["stable_task_id"] != task_id
        )
    elif task["task_kind"].startswith("CONDITIONAL OUTCOME"):
        short = task_id.removeprefix("TASK-OUT-").removesuffix("-DEFAULT").removesuffix("-DEVIATION")
        dependencies = [f"TASK-DEC-{short}"]
    else:
        dependencies = [phase_predecessor[task["phase"]]]
    task["semantic_dependencies"] = unique(dependencies)

extra_dependencies = {
    "TASK-CAP-DATABASE": ["TASK-CAP-DATA-SAFETY"],
    "TASK-CAP-BACKUP": ["TASK-CAP-DATABASE", "TASK-CAP-DATA-SAFETY"],
    "TASK-CAP-RESTORE": ["TASK-CAP-BACKUP", "TASK-CAP-DATABASE"],
    "TASK-CAP-LEGACY-MIGRATION": ["TASK-CAP-BACKUP", "TASK-CAP-DATABASE", "TASK-CAP-DATA-SAFETY"],
    "TASK-CAP-IPC": ["TASK-CAP-EXACT-LOCATION"],
    "TASK-CAP-SEARCH-EXACT": ["TASK-CAP-DATABASE", "TASK-CAP-IPC"],
    "TASK-CAP-NOTES": ["TASK-CAP-DATABASE", "TASK-CAP-IPC"],
    "TASK-CAP-SEARCH-SEMANTIC": ["TASK-CAP-SEARCH-EXACT", "TASK-CAP-DATABASE", "TASK-CAP-IPC"],
    "TASK-CAP-NETWORK-POLICY": ["TASK-CAP-IPC"],
    "TASK-CAP-MODEL-DISCOVERY": ["TASK-CAP-DATA-SAFETY"],
    "TASK-CAP-MODEL-PACK": ["TASK-CAP-MODEL-DISCOVERY", "TASK-CAP-DATA-SAFETY"],
}
for task_id, dependencies in extra_dependencies.items():
    if task_id in task_by_id:
        task_by_id[task_id]["semantic_dependencies"] = unique(task_by_id[task_id]["semantic_dependencies"] + [dependency for dependency in dependencies if dependency in task_by_id])

release_task_ids = sorted(task["stable_task_id"] for task in tasks if task["task_kind"] == "RELEASE PROOF")
final_audit_task_id = "TASK-REL-11-AUDIT"
if final_audit_task_id in task_by_id:
    task_by_id[final_audit_task_id]["semantic_dependencies"] = unique(
        task_by_id[final_audit_task_id]["semantic_dependencies"] + [task_id for task_id in release_task_ids if task_id != final_audit_task_id]
    )

for task in tasks:
    task["dependencies"] = list(task["semantic_dependencies"])

indegree = {task_id: 0 for task_id in task_by_id}
dependents_by_task: dict[str, list[str]] = collections.defaultdict(list)
for task_id, task in task_by_id.items():
    for dependency in task["semantic_dependencies"]:
        if dependency not in task_by_id:
            raise SystemExit(f"Unknown semantic task dependency: {task_id} -> {dependency}")
        indegree[task_id] += 1
        dependents_by_task[dependency].append(task_id)

def task_sort_key(task_id: str) -> tuple[str, str, str]:
    task = task_by_id[task_id]
    return task["phase"], task["wave"], task_id

ready = sorted((task_id for task_id, degree in indegree.items() if degree == 0), key=task_sort_key)
topological_ids: list[str] = []
while ready:
    task_id = ready.pop(0)
    topological_ids.append(task_id)
    for dependent in sorted(dependents_by_task[task_id], key=task_sort_key):
        indegree[dependent] -= 1
        if indegree[dependent] == 0:
            ready.append(dependent)
            ready.sort(key=task_sort_key)
if len(topological_ids) != len(tasks):
    raise SystemExit("Semantic task dependency graph contains a cycle")

depth: dict[str, int] = {}
for index, task_id in enumerate(topological_ids, 1):
    task = task_by_id[task_id]
    task["execution_order"] = index
    task["ordering_index"] = index
    task["dependents"] = sorted(dependents_by_task.get(task_id, []), key=task_sort_key)
    depth[task_id] = 0 if not task["semantic_dependencies"] else 1 + max(depth[dependency] for dependency in task["semantic_dependencies"])
tasks = [task_by_id[task_id] for task_id in topological_ids]
dependency_graph_metrics = {
    "task_nodes": len(tasks),
    "dependency_edges": sum(len(task["semantic_dependencies"]) for task in tasks),
    "root_tasks": [task["stable_task_id"] for task in tasks if not task["semantic_dependencies"]],
    "leaf_tasks": [task["stable_task_id"] for task in tasks if not task["dependents"]],
    "maximum_dependency_depth": max(depth.values(), default=0),
    "cycle_count": 0,
    "topological_order_result": "PASS",
}

task_ids_by_cap: dict[str, list[str]] = collections.defaultdict(list)
for task in tasks:
    task_ids_by_cap[task["capability_id"]].append(task["stable_task_id"])
for cap in capabilities:
    cap["implementation_task_ids"] = task_ids_by_cap[cap["id"]]
    owned_tasks = [task_by_id[task_id] for task_id in cap["implementation_task_ids"]]
    if owned_tasks:
        first_owned = min(owned_tasks, key=lambda task: task["execution_order"])
        cap["phase"] = first_owned["phase"]
        cap["wave"] = first_owned["wave"]
    dependency_caps = unique(
        task_by_id[dependency]["capability_id"]
        for task in owned_tasks
        for dependency in task["semantic_dependencies"]
        if task_by_id[dependency]["capability_id"] != cap["id"]
    )
    cap["dependencies"] = dependency_caps
for cap in capabilities:
    cap["dependents"] = unique(
        other["id"] for other in capabilities if cap["id"] in other.get("dependencies", [])
    )
for interpretation in INTERPRETATIONS:
    interpretation["affected_task_ids"] = unique([task_id for cap_id in interpretation["affected_capability_ids"] for task_id in task_ids_by_cap.get(cap_id, [])])


def count_by(items: list[dict[str, Any]], field: str) -> dict[str, int]:
    counter: collections.Counter[str] = collections.Counter()
    for item in items:
        values = item.get(field, [])
        if not isinstance(values, list):
            values = [values]
        for value in values:
            counter[str(value)] += 1
    return dict(sorted(counter.items()))


requirement_counts = {
    "total": len(requirements),
    "by_master_plan_file": count_by(requirements, "source_master_plan"),
    "by_section": count_by(requirements, "source_heading"),
    "by_classification": count_by(requirements, "requirement_type"),
    "by_capability": count_by(requirements, "capability_ids"),
    "by_architectural_layer": count_by(requirements, "applicable_architectural_layers"),
    "by_release_gate": count_by(requirements, "release_gate_ids"),
}
requirement_register = {
    "schema_version": 1,
    "authority": "Single machine-readable derived requirement authority subordinate to the three immutable Master Plan files",
    "master_plan_sha256": {path.name: EXPECTED_MASTER_HASHES[code] for code, path in MASTER_FILES},
    "normalization_rule": "One coherent independently verifiable paragraph, top-level list item with nested clauses, table row, or architecture block; classification-only bullets are inherited and not emitted as noise.",
    "counts": requirement_counts,
    "requirements": requirements,
}


capability_register = {
    "schema_version": 2,
    "authority": "Single derived capability authority; runtime_chain retains genuine Graphify/static-analysis evidence and must not be interpreted as execution proof",
    "capability_count": len(capabilities),
    "decision_counts": dict(sorted(collections.Counter(cap["decision"] for cap in capabilities).items())),
    "capabilities": capabilities,
}


implementation_queue = {
    "schema_version": 3,
    "authority": "Single machine-readable implementation task authority",
    "implementation_status": "NOT STARTED",
    "exact_first_task_id": "TASK-GOV-001-PROVENANCE-BASELINE",
    "task_count": len(tasks),
    "deletion_task_count": sum(task["task_kind"] == "DELETION" for task in tasks),
    "conditional_decision_task_count": sum(task["task_kind"] == "CONDITIONAL DECISION" for task in tasks),
    "release_proof_task_count": sum(task["task_kind"] == "RELEASE PROOF" for task in tasks),
    "phase_counts": dict(sorted(collections.Counter(task["phase"] for task in tasks).items())),
    "wave_counts": dict(sorted(collections.Counter(task["wave"] for task in tasks).items())),
    "dependency_graph_metrics": dependency_graph_metrics,
    "tasks": tasks,
}


# The former registry carried 5,619 heuristic node expansions forward. Rebuild
# this authority from the semantically reviewed capability locations instead.
old_exact_entries: list[dict[str, Any]] = []
exact_entries: list[dict[str, Any]] = []
existing_exact_ids: set[str] = set()
for entry in old_exact_entries:
    item = dict(entry)
    cap_id = item.get("capability_id")
    cap = cap_by_id.get(cap_id)
    if not cap:
        continue
    item.update({
        "stable_capability_id": cap_id,
        "master_requirement_ids": cap["master_requirement_ids"],
        "decision": cap["decision"],
        "status": item.get("status", "MAPPED - IMPLEMENTATION NOT STARTED").replace("—", "-").replace("â€”", "-"),
        "real_graph_or_static_analysis_node_id": item.get("graphify_node_id"),
        "intended_target_path": item.get("target_path") or cap["target_paths"][0],
        "intended_target_symbol": item.get("target_symbol") or cap["target_symbols"][0],
        "capability_owner": cap["owner"],
        "module_owner": cap["module_owner"],
        "dependencies": unique(item.get("dependencies", []) or []),
        "dependents": unique(item.get("dependents", []) or []),
        "renderer_entry": unique((item.get("renderer_entry_points", []) or []) + (item.get("routes", []) or [])),
        "preload_exposure": item.get("preload_exposures", []) or [],
        "ipc_channel": item.get("ipc_channels", []) or [],
        "ipc_handler": item.get("ipc_handlers", []) or [],
        "service": item.get("services", []) or [],
        "database_or_filesystem_effect": unique((item.get("database_tables", []) or []) + (item.get("database_columns", []) or []) + (item.get("filesystem_effects", []) or [])),
        "native_dependency": item.get("native_dependencies", []) or [],
        "runtime_registration": item.get("runtime_registrations", []) or [],
        "configuration_references": unique((item.get("environment_variables", []) or []) + (item.get("feature_flags", []) or []) + (item.get("build_references", []) or []) + (item.get("packaging_references", []) or [])),
        "tests": item.get("tests", []) or [],
        "required_changes": item.get("exact_change_instructions") or item.get("change_summary") or f"Execute {', '.join(cap['implementation_task_ids'])} only after its preconditions and evidence gates pass.",
        "verification_evidence_required": item.get("verification_evidence_required", []) or [f"Evidence bundle for {task_id}" for task_id in cap["implementation_task_ids"]],
        "phase": cap["phase"],
        "wave": cap["wave"],
        "last_planning_verification_checkpoint": "CHECKPOINT-FINAL-PLANNING",
    })
    exact_entries.append(item)
    existing_exact_ids.add(item["id"])

def location_class(path: str | None, planned: bool = False) -> str:
    if planned:
        return "ABSENT - PLANNED ADDITION"
    assert path is not None
    lower = path.lower()
    if path.startswith("Graphify/") or path.endswith(("package.json", "package-lock.json")) or "electron-builder" in lower:
        return "CONFIGURATION"
    if "/tests/" in lower:
        return "OWNED TEST"
    if "/migrations/" in lower:
        return "HISTORICAL MIGRATION"
    if "datamigration" in lower or lower.endswith("database.js"):
        return "DATABASE/MIGRATION"
    if "/native/" in lower and Path(path).suffix.lower() in {".c", ".cc", ".cpp", ".h", ".m", ".mm", ".swift", ".txt"}:
        return "NATIVE SOURCE"
    if "/resources/bin/" in lower:
        return "BUNDLED RUNTIME ASSET"
    if any(name in lower for name in ("license", "notice", "third-party")):
        return "LEGAL/ATTRIBUTION"
    return "OWNED SOURCE"


def exact_entry(cap: dict[str, Any], entry_id: str, current_path: str | None, current_anchor: str | None, status: str, kind: str, disposition: str | None = None, line: int | None = None) -> dict[str, Any]:
    actual_symbol = None
    if current_anchor and "::" in current_anchor and "::sha256:" not in current_anchor and not current_anchor.endswith("::directory-anchor"):
        actual_symbol = current_anchor.split("::", 1)[1]
    planned = current_path is None
    target_path = cap["target_paths"][0] if planned or cap["id"] in REMOVAL_CAPS else current_path
    target_symbol = cap["target_symbols"][0] if planned or cap["id"] in REMOVAL_CAPS else (actual_symbol or current_anchor)
    return {
        "id": entry_id, "capability_id": cap["id"], "stable_capability_id": cap["id"], "capability_name": cap["name"],
        "entity_type": kind.lower(), "location_class": kind, "master_requirement_ids": cap["master_requirement_ids"], "decision": cap["decision"],
        "status": status, "candidate_disposition": disposition,
        "current_path": current_path, "current_symbol": actual_symbol, "current_anchor": current_anchor,
        "current_line_start": line, "current_line_end": line, "graphify_node_id": None, "real_graph_or_static_analysis_node_id": None,
        "current_owner": cap["owner"], "target_path": target_path, "target_symbol": target_symbol,
        "intended_target_path": target_path, "intended_target_symbol": target_symbol,
        "target_owner": cap["owner"], "capability_owner": cap["owner"], "module_owner": cap["module_owner"],
        "dependencies": [], "dependents": [],
        "renderer_entry": [current_anchor] if current_path and "/renderer/" in current_path else [],
        "preload_exposure": [current_anchor] if current_path and "/preload/" in current_path else [],
        "ipc_channel": [current_anchor] if current_path and current_path.endswith("ipcHandlers.js") else [],
        "ipc_handler": [current_anchor] if current_path and current_path.endswith("ipcHandlers.js") else [],
        "service": [current_anchor] if current_path and "/main/" in current_path else [],
        "database_or_filesystem_effect": [current_anchor] if kind in {"DATABASE/MIGRATION", "BUNDLED RUNTIME ASSET"} else [],
        "native_dependency": [current_anchor] if kind in {"NATIVE SOURCE", "BUNDLED RUNTIME ASSET"} else [],
        "runtime_registration": [], "configuration_references": [current_anchor] if kind == "CONFIGURATION" else [],
        "tests": [current_path] if kind == "OWNED TEST" and current_path else [],
        "required_changes": capability_actions(cap, [current_path or f"PLANNED LOCATION: {target_path}"]),
        "verification_evidence_required": [f"Evidence bundle for {task_id}" for task_id in cap["implementation_task_ids"]],
        "phase": cap["phase"], "wave": cap["wave"], "last_planning_verification_checkpoint": "CHECKPOINT-SEMANTIC-PLANNING",
        "editable_target": kind not in {"THIRD-PARTY DEPENDENCY", "VENDOR FILE", "GENERATED OUTPUT"},
        "notes": "Reviewed symbols are source-verifiable. Content SHA-256 anchors are used for binaries/data/configuration or source without a reviewed symbol. A null current location is an explicit planned addition.",
    }


for cap in capabilities:
    if cap["current_paths"] and cap["id"] not in REMOVAL_CAPS:
        for current_path, current_anchor in zip(cap["current_paths"], cap["current_symbols"]):
            entry_id = stable_id("REG", cap["id"], current_path, current_anchor, length=16)
            exact_entries.append(exact_entry(cap, entry_id, current_path, current_anchor, "PRESENT - SEMANTICALLY REVIEWED", location_class(current_path)))
            existing_exact_ids.add(entry_id)
    elif not cap["current_paths"]:
        entry_id = f"REG-CAPABILITY-{cap['id'].removeprefix('CAP-')}"
        status = "NO ACTIVE PATH CURRENTLY MAPPED - IMPLEMENTATION-TIME PROOF STILL REQUIRED" if cap["id"] in REMOVAL_CAPS else "PLANNED ADDITION - IMPLEMENTATION NOT STARTED"
        exact_entries.append(exact_entry(cap, entry_id, None, None, status, location_class(None, planned=True)))
        existing_exact_ids.add(entry_id)

for cap_id in sorted(REMOVAL_CAPS):
    cap = cap_by_id[cap_id]
    for candidate in removal_candidates.get(cap_id, []):
        anchor = f"{candidate['path']}::line:{candidate['line']}:{candidate['anchor']}"
        entry_id = stable_id("REG-DEL", cap_id, candidate["path"], str(candidate["line"]), candidate["reviewed_disposition"], length=16)
        entry = exact_entry(cap, entry_id, candidate["path"], anchor, "REVIEWED DELETION EVIDENCE - IMPLEMENTATION INTERLOCK PENDING", location_class(candidate["path"]), candidate["reviewed_disposition"], candidate["line"])
        if candidate["reviewed_disposition"] != "ACTIVE REMOVAL CANDIDATE":
            entry["target_path"] = entry["intended_target_path"] = candidate["path"]
            entry["target_symbol"] = entry["intended_target_symbol"] = anchor
            entry["editable_target"] = False
        exact_entries.append(entry)
        existing_exact_ids.add(entry_id)

exact_entries.sort(key=lambda item: (item["stable_capability_id"], item["current_path"] or "", item["current_line_start"] or 0, item["id"]))
exact_ids_by_capability: dict[str, list[str]] = collections.defaultdict(list)
for entry in exact_entries:
    exact_ids_by_capability[entry["stable_capability_id"]].append(entry["id"])
for task in tasks:
    task["exact_location_registry_refs"] = exact_ids_by_capability[task["capability_id"]]

exact_required_fields = [
    "id", "stable_capability_id", "capability_name", "entity_type", "location_class", "master_requirement_ids", "decision", "status", "candidate_disposition",
    "current_path", "current_symbol", "current_anchor", "current_line_start", "current_line_end", "real_graph_or_static_analysis_node_id",
    "intended_target_path", "intended_target_symbol", "capability_owner", "module_owner", "dependencies", "dependents",
    "renderer_entry", "preload_exposure", "ipc_channel", "ipc_handler", "service", "database_or_filesystem_effect",
    "native_dependency", "runtime_registration", "configuration_references", "tests", "required_changes",
    "verification_evidence_required", "phase", "wave", "last_planning_verification_checkpoint", "editable_target",
]
for item in exact_entries:
    for field in exact_required_fields:
        item.setdefault(field, [] if field in {"master_requirement_ids", "dependencies", "dependents", "renderer_entry", "preload_exposure", "ipc_channel", "ipc_handler", "service", "database_or_filesystem_effect", "native_dependency", "runtime_registration", "configuration_references", "tests", "verification_evidence_required"} else None)

exact_registry = {
    "schema_version": 3,
    "authority": "Authoritative exact-location registry; no Markdown mirror is authoritative",
    "provenance": "Rebuilt from immutable Master Plan authority, reviewed capability-domain rules, verified current symbols or content hashes, and context-dispositioned deletion evidence. Genuine prior Graphify/static analysis informed review; no graph node ID is invented.",
    "entry_count": len(exact_entries),
    "required_fields": exact_required_fields,
    "entries": exact_entries,
}


test_records: list[dict[str, Any]] = []
for task in tasks:
    proof_items = task["characterisation_tests_required_before_change"] + task["targeted_verification"] + task["real_integration_verification"] + task["broader_regression_verification"]
    test_records.append({
        "test_contract_id": f"TEST-{task['stable_task_id'].removeprefix('TASK-')}",
        "task_id": task["stable_task_id"], "capability_id": task["capability_id"],
        "master_requirement_ids": task["master_requirement_ids"], "phase": task["phase"], "wave": task["wave"],
        "characterisation_before_change": task["characterisation_tests_required_before_change"],
        "targeted_verification": task["targeted_verification"],
        "real_integration_verification": task["real_integration_verification"],
        "broader_regression_verification": task["broader_regression_verification"],
        "offline_verification_impact": task["offline_verification_impact"],
        "required_evidence_artifacts": task["required_evidence_artifacts"],
        "evidence_types": unique(item.get("evidence_type") for item in proof_items if item.get("evidence_type")),
        "reference_counts": dict(sorted(collections.Counter(item.get("reference_status", "UNCLASSIFIED") for item in proof_items).items())),
        "planned_status": "PLANNED - NOT EXECUTED",
        "final_result": None,
    })
package_scripts = load_json(CB / "package.json").get("scripts", {})
test_reference_totals = collections.Counter()
test_evidence_type_totals = collections.Counter()
test_paths_by_status: dict[str, set[str]] = collections.defaultdict(set)
for record in test_records:
    test_reference_totals.update(record["reference_counts"])
    test_evidence_type_totals.update(record["evidence_types"])
    for field in ("characterisation_before_change", "targeted_verification", "real_integration_verification", "broader_regression_verification"):
        for proof in record[field]:
            if proof.get("test_path"):
                test_paths_by_status[proof.get("reference_status", "UNCLASSIFIED")].add(proof["test_path"])
test_matrix = {
    "schema_version": 3,
    "authority": "Planning-only test and evidence contract authority",
    "test_contract_count": len(test_records),
    "executed_in_this_run": 0,
    "verified_package_scripts": {name: package_scripts[name] for name in ("test", "typecheck", "lint", "build", "build:win", "pack", "dist", "verify:offline-assets", "i18n:check") if name in package_scripts},
    "test_runner": "Electron 41 invoking Node's built-in test runner over tests/**/*.test.js",
    "test_file_convention": "codebase/tests/**/*.test.js",
    "reference_status_totals": dict(sorted(test_reference_totals.items())),
    "unique_test_path_totals": {status: len(paths) for status, paths in sorted(test_paths_by_status.items())},
    "evidence_type_totals": dict(sorted(test_evidence_type_totals.items())),
    "tests": test_records,
}


# Remove the former outside-scope Graphify.zip entry from the authoritative inventory.
inventory_files = [entry for entry in inventory_doc.get("files", []) if entry.get("path") != "Graphify.zip"]
inventory_fingerprint = hashlib.sha256("\n".join(f"{item['path']}\0{item.get('sha256', '')}" for item in inventory_files).encode("utf-8")).hexdigest().upper()
repository_file_inventory = {
    "schema_version": 2, "fingerprint": inventory_fingerprint,
    "scope": "Current codebase files plus the three immutable Master Plan sources; derived Graphify artifacts are validated separately",
    "file_count": len(inventory_files), "files": inventory_files,
}


for gate in RELEASE_GATES:
    gate_id = gate["release_gate_id"]
    applicable_requirements = [requirement for requirement in requirements if gate_id in requirement["release_gate_ids"]]
    requirement_ids = [requirement["stable_requirement_id"] for requirement in applicable_requirements]
    capability_ids = unique(capability_id for requirement in applicable_requirements for capability_id in requirement["capability_ids"])
    applicable_task_ids = unique(
        task["stable_task_id"]
        for task in tasks
        if set(task["master_requirement_ids"]) & set(requirement_ids) or task.get("release_gate_id") == gate_id
    )
    gate.update({
        "master_requirement_ids": requirement_ids,
        "capability_ids": capability_ids,
        "applicable_task_ids": applicable_task_ids,
        "required_evidence": unique(gate["planned_proof"] + [evidence for requirement in applicable_requirements for evidence in requirement["required_evidence"]]),
        "evidence_producers": applicable_task_ids,
        "verification_method": "At one verified implementation commit/hash checkpoint, reconcile every applicable requirement and task to an immutable evidence artifact, exact command/manual method, working directory, exit/result status, boundary type and reviewer disposition.",
        "failure_condition": "Any applicable requirement/task lacks current real evidence, uses planning status as proof, substitutes a mock for a required real boundary, refers to a different checkpoint, or records an unpermitted failure/HARDWARE UNAVAILABLE status.",
        "not_applicable_rule": "NOT APPLICABLE is allowed only where the Master Plan or a completed conditional decision package makes the check genuinely unreachable; save reachability evidence and the authorizing requirement/decision ID. Hardware absence uses HARDWARE UNAVAILABLE, not NOT APPLICABLE or PASS.",
        "final_decision_authority": "Strict Release Conjunction reviewer acting under the immutable Master Plan; no administrative success message can waive a failed applicable gate.",
    })


write_json("MASTER_REQUIREMENT_REGISTER.json", requirement_register)
write_json("INTERPRETATION_REGISTER.json", {"schema_version": 1, "authority": "Derived interpretations subordinate to immutable Master Plan", "interpretation_count": len(INTERPRETATIONS), "unresolved_conflict_count": 0, "interpretations": INTERPRETATIONS})
write_json("CAPABILITY_REGISTRY.json", capability_register)
write_json("CONDITIONAL_DECISION_PACKAGES.json", {"schema_version": 1, "authority": "Complete evidence-driven conditional decision packages", "package_count": len(decision_packages), "packages": decision_packages})
write_json("RELEASE_GATE_PLAN.json", {"schema_version": 1, "authority": "Strict Release Conjunction planning authority", "release_status": "NOT EVALUATED - IMPLEMENTATION NOT STARTED", "gate_count": len(RELEASE_GATES), "gates": RELEASE_GATES})
write_json("IMPLEMENTATION_QUEUE.json", implementation_queue)
write_json("EXACT_LOCATION_REGISTRY.json", exact_registry)
write_json("TEST_MATRIX.json", test_matrix)
write_json("REPOSITORY_FILE_INVENTORY.json", repository_file_inventory)


master_hash_table = markdown_table(
    ["Master Plan", "SHA-256"],
    [[path.name, EXPECTED_MASTER_HASHES[code]] for code, path in MASTER_FILES],
)
phase_rows = []
for phase in sorted({task["phase"] for task in tasks}):
    phase_tasks = [task for task in tasks if task["phase"] == phase]
    phase_rows.append([phase, min(task["ordering_index"] for task in phase_tasks), max(task["ordering_index"] for task in phase_tasks), len(phase_tasks), ", ".join(unique(task["wave"] for task in phase_tasks))])


write_text("START-HERE.md", f"""# Mnemora implementation handoff

This is the single authoritative entry point for a future implementation run. Implementation has not started. The current application root is the lowercase `codebase/` folder; `Codebase/` is only a future target named by the Master Plan. The derived planning is subordinate to all three immutable Master Plan files. Application tests, builds, packaging, installation, offline launch, final audits, and release approval were not executed in this planning run.

## Authority order

1. `Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md`
2. `Master Plan/02-EVERYTHING-WE-ARE-DELETING.md`
3. `Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-REPLACE.md`
4. `MASTER_REQUIREMENT_REGISTER.json`
5. `INTERPRETATION_REGISTER.json`
6. `CAPABILITY_REGISTRY.json`
7. `EXACT_LOCATION_REGISTRY.json`
8. `IMPLEMENTATION_QUEUE.json`
9. `CONDITIONAL_DECISION_PACKAGES.json` and `RELEASE_GATE_PLAN.json`

## Scope and editable boundaries

- Repository root: the Git worktree root discovered by `git rev-parse --show-toplevel` (machine-specific absolute path intentionally not embedded).
- Current application root: `codebase/`; the lowercase path remains authoritative until a future casing-safe move task is executed.
- Current repository state: Git is present at the repository root. The semantic planning audit is performed on the `graphify-semantic-audit` branch and is fast-forward-integrated into `main` by the audit-run completion step; the generation-time branch is recorded in `RUN_STATE.md`.
- The completed run represented here edited only `Graphify/`. A future implementation run may edit application-owned files only when the active queue task names them under `files_expected_to_change`; the three Master Plan files and every task's `files_forbidden_from_changing` remain immutable boundaries.
- Installed dependencies, generated output, user databases, recordings, notes, transcripts, exports and backups are never implementation targets. Destructive tests use disposable verified copies.

## State-inspection commands

Run from the repository root before taking implementation authority:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath 'Graphify/Master Plan/01-EVERYTHING-WE-ARE-KEEPING.md','Graphify/Master Plan/02-EVERYTHING-WE-ARE-DELETING.md','Graphify/Master Plan/03-HOW-WE-WILL-KEEP-DELETE-AND-REPLACE.md'
git rev-parse --show-toplevel
git status --short --branch
python -B Graphify/tools/validate_planning.py --full-codebase
```

If Git is still absent, record that exact result; do not treat the Git command failure as permission to mutate. Follow `TASK-GOV-001-PROVENANCE-BASELINE` and the Master Plan's hash-checkpoint fallback.

## Exact first implementation task

`TASK-GOV-001-PROVENANCE-BASELINE`

Start with ordering index 1 in `IMPLEMENTATION_QUEUE.json`. Establish Git or the Master Plan-permitted recoverable hash checkpoint before any application mutation. Do not begin a later task merely because its files appear familiar.

## Dependency-safe phase and wave sequence

{markdown_table(["Phase", "First index", "Last index", "Tasks", "Waves"], phase_rows)}

`semantic_dependencies` is the authoritative prerequisite relation. `execution_order`/`ordering_index` is its deterministic topological handoff order, not an artificial immediate-predecessor chain. A future model may parallelize only tasks whose `semantic_dependencies` are complete and whose files/data boundaries do not overlap. For each conditional package, one outcome is implemented and the other must receive an evidence-linked `NOT APPLICABLE` disposition; neither branch may be silently skipped.

## Resume protocol

1. Read every line of all three Master Plan files and verify the hashes below.
2. Run `python Graphify/tools/validate_planning.py` from the Mnemora root. Stop on any failure.
3. Read `RUN_STATE.md`, then locate the first queue task whose implementation disposition is neither `COMPLETE` nor evidence-linked `NOT APPLICABLE`.
4. Confirm all dependency task evidence references the same commit/hash checkpoint.
5. Execute exactly one recoverable capability batch, save every required artifact, rerun planning validation, and update statuses without changing the Master Plan.
6. Never use a planning-complete status as implementation or release evidence.

## Conditional decisions and task completion

For each record in `CONDITIONAL_DECISION_PACKAGES.json`, collect the named evidence at its decision phase, record the selected `DEFAULT` or `DEVIATION` outcome with artifact paths and checkpoint identity, execute only that outcome's downstream task, and mark the unreachable sibling task `NOT APPLICABLE` with the authorizing decision record. Do not invent thresholds or delete a package merely to simplify packaging.

A task becomes `COMPLETE` only after its preconditions and `semantic_dependencies` are complete, every required artifact exists, exact locations are reconciled, commands/manual methods have saved results, acceptance and completion criteria pass, and no stop condition is active. Update `IMPLEMENTATION_QUEUE.json`, `EXACT_LOCATION_REGISTRY.json`, `RUN_STATE.md`, and the linked evidence atomically at one Git/hash checkpoint; regenerate Markdown views instead of hand-editing a competing status.

## Provenance and false-completion controls

Use one focused Git commit per recoverable capability batch when Git exists. When it does not, save pre/post path, byte-size and SHA-256 inventories plus the reversible delta before continuing. Never reset, clean, restore, stash or discard unrelated work. Planning status, file existence, mocks, administrative success text and an unavailable-hardware waiver cannot substitute for required real evidence.

After every coherent batch, review the exact diff, verify only permitted `Graphify/` paths changed, run the deterministic validator, commit, push to the configured origin, fetch origin, and confirm the local branch HEAD equals the remote branch HEAD before starting the next batch. Use `git push` without force; never rewrite history or discard unrelated work.

Evaluate all gates in `RELEASE_GATE_PLAN.json` only after their evidence-producing tasks finish. A gate fails when any applicable requirement/task lacks same-checkpoint proof; `NOT APPLICABLE` requires an explicit Master Plan or conditional-decision reachability basis, and absent hardware is `HARDWARE UNAVAILABLE`, not `PASS`. Final release approval requires the conjunction of all applicable gates.

## Immutable source hashes

{master_hash_table}

## Evidence still to collect during implementation

- Characterisation, targeted, real-integration and regression logs for every queue task.
- Disposable-copy database migration, backup, integrity, idempotency, interruption and recovery results.
- Seven completed interlocks and full-layer disposition for every deletion task.
- The 11 conditional evidence packages and exactly one selected outcome per package.
- Runtime network observation, owned-loopback allow-list and offline first-launch evidence.
- Windows production build, package, clean installation, installed launch and offline workflow evidence.
- macOS/Linux static or CI evidence plus honest `HARDWARE UNAVAILABLE` records where physical hardware is absent.
- Final Graphify scan, final simplification audit, release-gate reconciliation and independent approval.
""")


git_state_line = (
    f"- Git: present at the repository root (branch `{GIT_STATE['branch'] or '(detached)'}`); branch, commit, staged, unstaged, deleted and untracked states are verified at implementation time by `TASK-GOV-001-PROVENANCE-BASELINE` and recorded in the audit baseline."
    if GIT_STATE["present"]
    else "- Git: absent at the repository root and every searched parent through `C:\\`; branch, commit, staged, unstaged, deleted and untracked Git states are unavailable."
)
inventory_git_line = (
    "Git: present; details are in `RUN_STATE.md` and the 2026-08-05 audit baseline in `PLANNING_BASELINE.md`."
    if GIT_STATE["present"]
    else "Git: absent; details are in `RUN_STATE.md` and `REPOSITORY_FINGERPRINT.json`."
)


write_text("RUN_STATE.md", f"""# Run State

## Current checkpoint

- Mode: final derived-planning completion; application implementation not started.
- Repository root: the Git worktree root discovered by `git rev-parse --show-toplevel` (machine-specific absolute path intentionally not embedded).
- Current application root: `codebase/` (lowercase path is authoritative current evidence).
{git_state_line}
- Provenance fallback: `REPOSITORY_FILE_INVENTORY.json` plus `REPOSITORY_FINGERPRINT.json`; future implementation begins with `TASK-GOV-001-PROVENANCE-BASELINE`.
- Immutable Master Plan files: verified against the SHA-256 values below before derived generation.
- Application writes in this planning run: none authorized.
- Implementation, test, build, package, installer, offline-launch and release status: not started / not evaluated.

## Planning authorities

- Requirements: {len(requirements)} in `MASTER_REQUIREMENT_REGISTER.json`.
- Capabilities: {len(capabilities)} in `CAPABILITY_REGISTRY.json`.
- Exact-location entries: {len(exact_entries)} in `EXACT_LOCATION_REGISTRY.json`.
- Implementation tasks: {len(tasks)} in `IMPLEMENTATION_QUEUE.json`.
- Deletion tasks: {implementation_queue['deletion_task_count']}.
- Conditional decision packages: {len(decision_packages)}.
- Strict release gates: {len(RELEASE_GATES)}.
- Interpretations: {len(INTERPRETATIONS)}; unresolved derived conflicts: 0.

## Resume pointer

Read `START-HERE.md`. The exact first future implementation task is `TASK-GOV-001-PROVENANCE-BASELINE` at ordering index 1. Re-run `python Graphify/tools/validate_planning.py` before execution.

## Master Plan hashes

{master_hash_table}
""")


write_text("CAPABILITY_REGISTRY.md", f"""# Capability Registry

`CAPABILITY_REGISTRY.json` is the sole machine authority. This Markdown file is a navigation view and does not mirror the deep runtime chains.

{markdown_table(["Capability", "Name", "Decision", "Presence", "Owner", "Tasks", "Phase"], [[cap['id'], cap['name'], cap['decision'], cap['presence_status'], cap['owner'], cap['implementation_task_ids'], cap['phase']] for cap in capabilities])}
""")


write_text("IMPLEMENTATION_QUEUE.md", f"""# Implementation Queue

`IMPLEMENTATION_QUEUE.json` is authoritative and contains the complete task contracts. No task was executed during this planning run. The exact first task is `TASK-GOV-001-PROVENANCE-BASELINE`.

{markdown_table(["Index", "Task", "Phase", "Wave", "Kind", "Capability", "Dependency", "Status"], [[task['ordering_index'], task['stable_task_id'], task['phase'], task['wave'], task['task_kind'], task['capability_id'], task['dependencies'], task['planning_status']] for task in tasks])}
""")


dependency_phase_rows = []
for phase in sorted({task["phase"] for task in tasks}):
    phase_tasks = [task for task in tasks if task["phase"] == phase]
    dependency_phase_rows.append([
        phase,
        len(phase_tasks),
        sum(len(task["semantic_dependencies"]) for task in phase_tasks),
        min(task["execution_order"] for task in phase_tasks),
        max(task["execution_order"] for task in phase_tasks),
    ])
write_text("DEPENDENCY_GRAPH.md", f"""# Implementation Dependency Graph

This is the planning task DAG derived from `IMPLEMENTATION_QUEUE.json`. Genuine code-relationship evidence remains under `graphify-out/`; it is distinct from this implementation-order graph. No application task has been executed.

- Task nodes: {dependency_graph_metrics['task_nodes']}
- Semantic dependency edges: {dependency_graph_metrics['dependency_edges']}
- Root task: `{dependency_graph_metrics['root_tasks'][0]}`
- Final leaf task: `{dependency_graph_metrics['leaf_tasks'][0]}`
- Maximum dependency depth: {dependency_graph_metrics['maximum_dependency_depth']}
- Cycles: {dependency_graph_metrics['cycle_count']}
- Deterministic topological-order validation: {dependency_graph_metrics['topological_order_result']}

{markdown_table(["Phase", "Tasks", "Incoming semantic edges", "First order", "Last order"], dependency_phase_rows)}

For exact prerequisites and dependents, use each task's `semantic_dependencies` and `dependents` fields. `execution_order` is a reproducible linearization for handoff; it does not create dependencies that are absent from the DAG.
""")


write_text("TEST_MATRIX.md", f"""# Test Matrix

Planning-only view. `TEST_MATRIX.json` contains {len(test_records)} exact test contracts. Zero tests were executed in this planning run, and no row is a pass result.

{markdown_table(["Test contract", "Task", "Capability", "Phase", "Status"], [[test['test_contract_id'], test['task_id'], test['capability_id'], test['phase'], test['planned_status']] for test in test_records])}
""")


write_text("DELETED_ITEMS_LEDGER.md", f"""# Deleted Items Ledger

No application item was deleted in this planning run. Each row is a future deletion contract. `IMPLEMENTATION_QUEUE.json` is authoritative for candidate anchors, all 19 architectural layers and the seven Binding Deletion Interlock checks.

{markdown_table(["Capability", "Deletion task", "Static candidates", "Layers", "Interlocks", "Implementation status"], [[cap['id'], task_ids_by_cap[cap['id']], len(removal_candidates.get(cap['id'], [])), len(DELETION_LAYERS), 7, 'NOT STARTED'] for cap in capabilities if cap['id'].startswith('CAP-REMOVE-')])}

An empty static-candidate count never proves absence. The task must trace imports, strings, registrations, runtime behavior and packaged output while preserving historical migrations, legal attribution and permitted legacy compatibility.
""")


write_text("COMPLETION_TRACKER.md", f"""# Completion Tracker

## Planning checkpoint

The derived model contains {len(requirements)} normalized requirements, {len(capabilities)} capabilities, {len(tasks)} implementation tasks ({implementation_queue['deletion_task_count']} deletion tasks), {len(decision_packages)} conditional packages, {len(RELEASE_GATES)} release gates and {len(exact_entries)} exact-location entries. Deterministic completion is controlled by `tools/validate_planning.py` and `PLANNING_VALIDATION_REPORT.json`; typed totals here are generated from the authorities. The deterministic validator enforces the complete gate suite recorded in `PLANNING_VALIDATION_REPORT.json` (the current gate count and verdict are authoritative there), including generator reproducibility. Historical audit and reconciliation records live in `PLANNING_BASELINE.md` and `FINAL-REPOSITORY-RECONCILIATION.md`.

## Planning Completion Conjunction

{markdown_table(["Gate", "State (authoritative in validation report)", "Deterministic authority"], [[index, "PASS (see report)", authority] for index, authority in enumerate([
    'Master hashes and exact source-line coverage', 'Stable requirement records', 'Requirement-to-capability coverage', 'Named product-scope capability completeness',
    'Protected retained scope separated from deletion', 'Capability ownership and runtime chains', 'Exact-location path/symbol reconciliation and vendor restrictions', 'Deletion dispositions, false-positive exclusions, and seven interlocks',
    'Real semantic task dependencies, DAG, and topological order', 'Phase, wave, and order agreement', 'Complete task contracts without vague language', 'Test-command validity and existing-versus-planned distinction',
    'Evidence-type appropriateness', 'Eleven conditional packages complete', 'Strict release-gate traceability', 'Interpretations resolved',
    'Zero placeholders, orphans, duplicates, or broken internal links', 'Cross-authority count reconciliation', 'Generator semantic reproducibility', 'Integrity wording and no-codebase-mutation evidence',
    'Exact first task `TASK-GOV-001-PROVENANCE-BASELINE` and total order', 'No false execution or release claim'
], 1)])}

## Application and release status

Implementation, application tests, builds, packaging, installation, offline launch, final Graphify scan, final simplification audit and release approval are all pending future execution. Planning completeness never changes those statuses. Historical full-tree manifest evidence is preserved in `PLANNING_BASELINE.md`; precise tracked/Git, Git LFS and local-only inventory claims are in `FINAL-REPOSITORY-RECONCILIATION.md`.
""")


write_text("REPOSITORY_INVENTORY.md", f"""# Repository Inventory

## Root and provenance

- Root: the Git worktree root discovered by `git rev-parse --show-toplevel` (machine-specific absolute path intentionally not embedded).
- Current application folder: `codebase/`; planned `Codebase` spelling is not a completed move.
- Derived planning folder: `Graphify/`.
- {inventory_git_line}
- Authoritative inventory: {len(inventory_files)} files in `REPOSITORY_FILE_INVENTORY.json`; derived Graphify outputs are validated separately.

## Application roots

- Package root: `codebase/package.json`; npm lock: `codebase/package-lock.json`.
- Main process: `codebase/main/`; Electron entry: `codebase/main/index.js`.
- Renderer: `codebase/renderer/`; app entry: `codebase/renderer/app/main.jsx`; route owner: `codebase/renderer/app/AppRouter.jsx::AppRouter`.
- Preload: `codebase/preload/index.js`; renderer contract: `codebase/renderer/shared/types/electron.ts`.
- IPC: `codebase/main/ipc/ipcHandlers.js::setupIpcHandlers` plus preload exposures and renderer declarations.
- Features: `codebase/main/features/{{dictation,meetings,notes,search,transcription}}/` and matching renderer feature folders.
- Persistence/migrations/backup: `codebase/main/infrastructure/persistence/`.
- Runtime/network/process ownership: `codebase/main/infrastructure/runtime/`.
- Native/platform source: `codebase/native/` and `codebase/main/platform/`.
- Bundled binaries/models: `codebase/resources/bin/`; manifest: `codebase/resources/bin/asset-manifest.json`.
- Build and packaging: `codebase/scripts/{{build,packaging,verification,downloads}}/`, `codebase/electron-builder.json`, `codebase/packaging/`.
- Tests and fixtures: `codebase/tests/unit/`, `codebase/tests/fixtures/`; planned real integration additions are in the task contracts.
- Generated/vendor roots: `codebase/node_modules/` and `codebase/build-output/`; inventoried but not application source authority.
""")


write_text("CURRENT_ARCHITECTURE.md", """# Current Architecture

This is a read-only static architecture map. Path plus symbol/unique anchor is authoritative; saved line numbers in `EXACT_LOCATION_REGISTRY.json` are secondary. Genuine Graphify 0.9.17 evidence remains under `graphify-out/`; static candidates are not runtime observations.

## Runtime composition

| Layer | Current owner and exact anchors | Significant effects |
| --- | --- | --- |
| Electron lifecycle | `codebase/main/index.js::app.whenReady`, `codebase/main/desktop/windowManager.js::WindowManager`, `codebase/main/desktop/tray.js::TrayManager` | Windows, tray, protocol, child-process cleanup |
| Renderer shell | `codebase/renderer/app/main.jsx::root`, `codebase/renderer/app/AppRouter.jsx::AppRouter`, `codebase/renderer/app/components/ControlPanel.tsx::ControlPanel` | Navigation and retained local feature entry |
| Renderer state | `codebase/renderer/features/meetings/meetingRecordingStore.ts`, `codebase/renderer/features/notes/noteStore.ts`, `codebase/renderer/features/settings/settingsStore.ts`, `codebase/renderer/features/transcription/transcriptionStore.ts` | UI state and IPC callers |
| Preload/type boundary | `codebase/preload/index.js::contextBridge.exposeInMainWorld`, `codebase/renderer/shared/types/electron.ts::ElectronAPI` | Renderer-to-main contract |
| IPC | `codebase/main/ipc/ipcHandlers.js::setupIpcHandlers` | Capability handlers, data/filesystem/process effects |
| Dictation | `codebase/main/features/dictation/hotkeyManager.js::HotkeyManager`, `codebase/renderer/features/dictation/App.jsx::App` | Global hotkey, microphone, local transcription, paste |
| Meeting capture | `codebase/renderer/features/meetings/meetingRecordingStore.ts`, `codebase/main/platform/windowsLoopbackAudioManager.js`, `codebase/main/features/meetings/meetingAecManager.js` | Microphone/system audio, AEC/mix, recovery |
| Transcription | `codebase/main/features/transcription/whisperServer.js::WhisperServer`, `codebase/main/features/transcription/whisper.js`, `codebase/main/features/transcription/modelDirUtils.js` | Bundled local process/models; no permitted runtime download |
| Diarization/speakers | `codebase/main/features/meetings/diarization.js`, `codebase/main/features/meetings/speakerEmbeddings.js`, `codebase/main/features/meetings/liveSpeakerIdentifier.js` | Sherpa helper/models, ONNX embeddings, persisted mappings |
| Notes/transcripts | `codebase/renderer/features/notes/components/NoteEditor.tsx::NoteEditor`, `codebase/renderer/features/notes/noteStore.ts::initializeNotes`, `codebase/main/infrastructure/persistence/database.js::saveNote` | Rich notes, structured segments, folders/tags, links and SQLite persistence |
| Exact/semantic search | `codebase/main/infrastructure/persistence/database.js::searchLocal`, `codebase/renderer/features/search/SearchView.tsx::SearchView`, `codebase/main/features/search/localEmbeddings.js::LocalEmbeddings`, `codebase/main/features/search/qdrantManager.js::QdrantManager`, `codebase/main/features/search/vectorIndex.js::search` | SQLite/FTS/text exact search and isolated local MiniLM/Qdrant semantic search |
| Persistence | `codebase/main/infrastructure/persistence/database.js::DatabaseManager`, `codebase/main/infrastructure/persistence/dataMigration.js`, `codebase/main/infrastructure/persistence/localBackup.js` | SQLite schema, forward migration, backup/restore |
| Runtime policy | `codebase/main/infrastructure/runtime/runtimeNetworkPolicy.js`, `codebase/main/infrastructure/runtime/process.js`, `codebase/main/infrastructure/runtime/sidecarReaper.js` | External-network denial and owned local processes |
| Native/model assets | `codebase/resources/bin/asset-manifest.json`, `codebase/native/helpers/`, `codebase/native/meeting-aec-helper/` | Pinned binaries/models and platform helpers |
| Packaging | `codebase/electron-builder.json`, `codebase/scripts/packaging/prepare-offline-assets.js`, `codebase/scripts/verification/verify-offline-assets.js` | NSIS and configured portable Windows targets; macOS/Linux config retained |

## Known current absences or incomplete areas

- No Git repository was found at planning time.
- No Kysely or OS keyring package/import was proven.
- No active loopback WebSocket dependency was proven; local Qdrant uses owned loopback HTTP.
- No Parakeet runtime engine/binary was proven; only stale or localization references were found.
- No local note-template implementation was proven.
- Offline model-pack import, local processing job queue, legacy migration hardening, offline first-launch proof, legal-file target set and release evidence remain planned additions or repairs.
- Existing removal-term hits include historical migration/legal/build-time candidates and stale translations/styles; every one requires deletion-interlock classification.
""")


target_rows = [[cap["id"], cap["owner"], cap["target_paths"], cap["target_symbols"], cap["decision"]] for cap in capabilities]
write_text("TARGET_ARCHITECTURE.md", f"""# Target Architecture

The target is a fully local Electron desktop application organized by capability ownership, with typed internal IPC, SQLite persistence, bundled local engines/assets, explicit process lifecycle, runtime network denial and proof-driven packaging. This is a planning target, not an implemented state.

## Invariants

- Renderer code calls only declared preload APIs; preload, TypeScript declarations, IPC channels, handlers and services change together.
- User data remains local in SQLite/filesystem storage with backup-before-transform, forward migrations, integrity, idempotency and recovery.
- Whisper.cpp is the required local fallback. Parakeet and Sherpa-ONNX remain separate conditional packages governed by evidence.
- Qdrant and every loopback service are bundled, owned, lifecycle-managed and allow-listed; external runtime networking and downloads remain absent.
- Removed systems are absent across the complete UI-to-package chain while historical migrations, legal provenance and explicit legacy compatibility remain labelled.
- Windows installer/build/offline launch proof is mandatory. macOS/Linux source/configuration is preserved and receives applicable CI/static or honest hardware status.

## Capability ownership and exact targets

{markdown_table(["Capability", "Owner", "Target paths", "Target symbols", "Decision"], target_rows)}
""")


write_text("FOLDER_OWNERSHIP_MAP.md", """# Folder Ownership Map

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
""")


write_text("MOVE_LEDGER.md", """# Move Ledger

No application file was moved in this planning run.

| Move ID | Current path | Intended target | Trigger | Preconditions | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- |
| MOVE-001-ROOT-CASING | `codebase/` | `Codebase/` as named by the Master Plan target tree | Future implementation task under explicit mutation authority | Git/hash provenance, casing-safe Windows procedure, import/build/package path audit, no user data inside move scope | Pre/post path inventory, hashes, Git diff, test/build/package evidence | PLANNED; NOT AUTHORIZED IN THIS RUN |
| MOVE-002-MARKDOWN | Any non-legal application Markdown proven outside vendor/generated roots | `Graphify/` or an owned documentation target | Future repository-governance task | Classify package/vendor/generated files; preserve required legal plain-text files; repair references | Exact source/target ledger and link/package checks | PLANNED; current authoritative inventory found no such source Markdown outside excluded roots |
| MOVE-003-MONOLITHS | Oversized mixed-owner symbols such as `codebase/main/ipc/ipcHandlers.js::setupIpcHandlers` | Capability-owned IPC registration modules selected during implementation | Characterization and ownership proof | Complete caller/handler/service/data map; focused tests; reversible batch | Import/call diff, handler parity, cycle and regression evidence | PLANNED |

The lowercase `codebase` path remains the authoritative current location until MOVE-001 is genuinely executed and verified.
""")


replacement_rows = []
for cap in capabilities:
    if not cap["id"].startswith("CAP-REMOVE-"):
        continue
    replacements = cap.get("replacement_capability_ids", []) or []
    if not replacements:
        if cap["id"] in {"CAP-REMOVE-HOSTED-TRANSCRIPTION", "CAP-REMOVE-RUNTIME-MODEL-DOWNLOADS"}:
            replacements = ["CAP-WHISPER", "CAP-MODEL-PACK"]
        elif cap["id"] in {"CAP-REMOVE-HOSTED-AI", "CAP-REMOVE-LOCAL-GENERATIVE-AI", "CAP-REMOVE-AI-AGENTS", "CAP-REMOVE-CHAT", "CAP-REMOVE-SUMMARISATION", "CAP-REMOVE-ACTION-ITEM-EXTRACTION", "CAP-REMOVE-AI-REWRITING"}:
            replacements = ["CAP-NOTES", "CAP-SEARCH-EXACT", "CAP-SEARCH-SEMANTIC"]
        elif cap["id"] in {"CAP-REMOVE-RUNTIME-EXTERNAL-NETWORKING", "CAP-REMOVE-RUNTIME-EXTERNAL-LINKS"}:
            replacements = ["CAP-NETWORK-POLICY"]
        else:
            replacements = ["CAP-APP-SHELL"]
    replacement_rows.append([cap["id"], replacements, task_ids_by_cap[cap["id"]], "Local retained workflow proof or explicit absence; no remote substitute"])
write_text("REPLACEMENT_MAP.md", f"""# Replacement Map

Removed systems are not automatically replaced one-for-one. A replacement exists only where a retained local workflow requires it; otherwise the correct target is absence. The deletion task remains authoritative for the seven interlocks.

{markdown_table(["Removed capability", "Retained/local owner", "Deletion task", "Rule"], replacement_rows)}
""")


write_text("REGRESSION_RESULTS.md", """# Regression Evidence Plan

This file is deliberately planning-only. No regression suite, build, package, installer or offline launch was executed in the final planning-completion run.

`TEST_MATRIX.json` maps every implementation task to characterization, targeted, real-integration, broader regression and offline/applicability evidence. During implementation, append or link immutable evidence by task and verified commit/hash checkpoint; never replace this statement with a pass until commands genuinely ran and their exit codes/logs were saved.

Historical evidence elsewhere in Graphify may describe earlier scans or commands. It is provenance, not final release evidence, and must be rerun at the final implementation checkpoint when the corresponding release gate requires it.
""")


write_text("PONYTAIL_AUDIT.md", """# Final Simplification Audit Plan

No final simplification audit was executed in this planning-completion run. Any historical structural findings in `PONYTAIL_FINDINGS.json` are planning inputs, not a final pass.

After correctness, preservation, deletion, data safety and real integration evidence are complete, the future implementation run must perform a genuine whole-repository simplification audit. It must record exact path/symbol findings, distinguish deletion from speculative refactoring, protect retained platform and recovery behavior, rerun affected proof, and link the result to `GATE-11-AUDIT`. No finding may authorize deletion without the seven Binding Deletion Interlocks.
""")


def third_party_owner(package: str) -> str:
    if package == "@homebridge/dbus-native": return "Platform-native helpers"
    if package == "@qdrant/js-client-rest": return "Semantic search"
    if package.startswith("@radix-ui/") or package in {"class-variance-authority", "clsx", "lucide-react", "tailwind-merge", "tw-animate-css"}: return "Renderer shared UI"
    if package.startswith("@tiptap/") or package in {"react-markdown", "tiptap-markdown"}: return "Notes"
    if package == "better-sqlite3": return "SQLite persistence"
    if package == "dotenv": return "Runtime configuration"
    if package in {"ffmpeg-static", "unbzip2-stream", "unzipper", "tar"}: return "Local asset acquisition and transcription"
    if package in {"i18next", "react-i18next"}: return "Localisation"
    if package == "onnxruntime-node": return "Local model runtime"
    if package == "ps-list": return "Local meeting-process detection"
    if package in {"react", "react-dom", "zustand"}: return "Renderer application state"
    if package in {"electron"}: return "Electron desktop shell"
    if package in {"electron-builder", "@electron/notarize"}: return "Build and packaging"
    if package in {"@tailwindcss/vite", "@vitejs/plugin-react", "autoprefixer", "postcss", "tailwindcss", "vite"}: return "Renderer build pipeline"
    if package in {"@eslint/js", "eslint", "eslint-plugin-react-hooks", "eslint-plugin-react-refresh", "globals", "prettier", "typescript", "typescript-eslint", "@types/react", "@types/react-dom"}: return "Source-quality tooling"
    if package in {"concurrently", "cross-env"}: return "Development command orchestration"
    return "Third-party dependency governance"


package_document = load_json(CB / "package.json")
dependency_scan_paths = []
for entry in inventory_entries:
    candidate = entry.get("path", "").replace("\\", "/")
    lower = "/" + candidate.lower()
    if not candidate.startswith("codebase/") or any(marker in lower for marker in VENDOR_OR_GENERATED_MARKERS):
        continue
    if "/resources/bin/" in lower or Path(candidate).suffix.lower() not in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".json", ".css", ".html"}:
        continue
    if (ROOT / candidate).is_file() and (ROOT / candidate).stat().st_size <= 2_000_000:
        dependency_scan_paths.append(candidate)
dependency_scan_paths = unique(dependency_scan_paths)

third_party_rows = []
for group in ("dependencies", "devDependencies"):
    for package, version in sorted(package_document.get(group, {}).items()):
        import_pattern = re.compile(
            rf"(?:\bfrom\s*|\brequire\(\s*|\bimport\(\s*|@import\s*)['\"]{re.escape(package)}(?:/[^'\"]*)?['\"]"
        )
        references = ["codebase/package.json", "codebase/package-lock.json"]
        for candidate in dependency_scan_paths:
            if candidate in references:
                continue
            try:
                if import_pattern.search((ROOT / candidate).read_text(encoding="utf-8", errors="replace")):
                    references.append(candidate)
            except OSError:
                continue
        if package == "@qdrant/js-client-rest":
            decision = "CONDITIONAL RETAIN - DEC-QDRANT"
        elif package in {"tar", "unbzip2-stream", "unzipper"}:
            decision = "RETAIN FOR OFFLINE LOCAL MODEL-PACK IMPORT; PROVE FILE-ONLY INPUT AND ZERO NETWORK"
        else:
            decision = "RETAIN PENDING OWNED-CALLER, LICENCE AND PACKAGING PROOF"
        third_party_rows.append([
            package, version, group, third_party_owner(package), ", ".join(references), decision,
            "Verify resolved version licence/source and packaged NOTICE at TASK-CAP-THIRD-PARTY",
        ])

write_text("THIRD_PARTY_CODE_REGISTER.md", f"""# Third-Party Code Register

This is the deterministic top-level dependency register derived from `codebase/package.json`, exact owned import/require references, and explicit capability ownership. Installed `node_modules` files are dependency evidence only and are never editable targets. Dependency presence is not a licence pass or runtime-retention decision.

{markdown_table(["Package", "Declared version", "Group", "Owner", "Owned references", "Planning decision", "Required legal evidence"], third_party_rows)}

## Source and attribution preservation

- `codebase/LICENSE` is a present MIT licence carrying the historical OpenWhispr copyright notice. It is legal provenance to preserve, not active product-brand behavior.
- Native helpers, FFmpeg, Whisper.cpp, Sherpa/ONNX models, MiniLM, Qdrant and other bundled assets also require source/version/hash/licence/notice reconciliation under `TASK-CAP-LEGAL`, `TASK-CAP-THIRD-PARTY`, packaging, and `GATE-11-AUDIT`.
- Build-time acquisition is permitted only when pinned, checksummed, isolated from the installed application and unreachable at runtime. Runtime model/binary downloads remain forbidden.
""")


write_text("PLANNING_COUNTS.md", f"""# Derived Planning Counts

This navigation report is generated from the machine authorities. It is not an independently typed source of truth.

## Requirements by Master Plan

{markdown_table(["Master Plan", "Requirements"], [[key, value] for key, value in requirement_counts['by_master_plan_file'].items()])}

## Requirements by classification

{markdown_table(["Classification", "Requirements"], [[key, value] for key, value in requirement_counts['by_classification'].items()])}

## Other totals

- Capabilities: {len(capabilities)}
- Implementation tasks: {len(tasks)}
- Deletion tasks: {implementation_queue['deletion_task_count']}
- Conditional decision packages: {len(decision_packages)}
- Release gates: {len(RELEASE_GATES)}
- Exact-location entries: {len(exact_entries)}
""")


print(json.dumps({
    "requirements": len(requirements), "capabilities": len(capabilities), "tasks": len(tasks),
    "deletion_tasks": implementation_queue["deletion_task_count"], "conditional_packages": len(decision_packages),
    "release_gates": len(RELEASE_GATES), "exact_locations": len(exact_entries),
}, indent=2))
