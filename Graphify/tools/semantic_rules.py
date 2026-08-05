"""Reviewed semantic rules for Mnemora's derived planning generator.

This module contains deliberately explicit source-context, ownership, and location
rules.  It does not scan by an unqualified keyword and it never treats vendor or
generated files as editable implementation targets.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable


PRODUCT_SCOPE_CAPS = [
    "CAP-DICTATION",
    "CAP-MEETING",
    "CAP-TRANSCRIPTION",
    "CAP-DATABASE",
    "CAP-NOTES",
    "CAP-DIARIZATION",
    "CAP-SEARCH-EXACT",
    "CAP-SEARCH-SEMANTIC",
]


# These are section owners, not keyword matches. Context-specific additions are
# applied separately by complete_planning.py.
PRIMARY_CAPS_BY_SECTION: dict[tuple[str, str], list[str]] = {
    ("MP1", "mnemora-everything-we-are-keeping"): PRODUCT_SCOPE_CAPS,
    ("MP1", "governing-rule"): ["CAP-PLANNING-GOVERNANCE", "CAP-IMPLEMENTATION-GOVERNANCE"],
    ("MP1", "1-product-and-legal-identity"): ["CAP-LEGAL", "CAP-APP-SHELL"],
    ("MP1", "2-core-desktop-stack"): ["CAP-APP-SHELL", "CAP-DATABASE"],
    ("MP1", "3-application-shell"): ["CAP-APP-SHELL"],
    ("MP1", "4-voice-dictation"): ["CAP-DICTATION"],
    ("MP1", "5-local-transcription-engines"): ["CAP-TRANSCRIPTION"],
    ("MP1", "6-local-model-handling"): ["CAP-MODELS", "CAP-MODEL-DISCOVERY"],
    ("MP1", "7-meeting-recording"): ["CAP-MEETING"],
    ("MP1", "8-audio-processing"): ["CAP-AUDIO"],
    ("MP1", "9-speaker-diarization"): ["CAP-DIARIZATION"],
    ("MP1", "10-transcripts-and-history"): ["CAP-TRANSCRIPTION", "CAP-SEGMENTS"],
    ("MP1", "11-notes"): ["CAP-NOTES"],
    ("MP1", "12-folders-tags-and-snippets"): ["CAP-NOTES"],
    ("MP1", "13-exact-search"): ["CAP-SEARCH-EXACT"],
    ("MP1", "14-semantic-search"): ["CAP-SEARCH-SEMANTIC"],
    ("MP1", "15-local-actions-and-clipboard"): ["CAP-CLIPBOARD"],
    ("MP1", "16-notifications-and-process-detection"): ["CAP-NOTIFICATIONS"],
    ("MP1", "17-internal-ipc"): ["CAP-IPC"],
    ("MP1", "18-sqlite-and-local-persistence"): ["CAP-DATABASE", "CAP-DATA-SAFETY"],
    ("MP1", "19-import-and-export"): ["CAP-IMPORT-EXPORT"],
    ("MP1", "20-playback"): ["CAP-PLAYBACK"],
    ("MP1", "21-settings"): ["CAP-SETTINGS"],
    ("MP1", "22-native-and-platform-components"): ["CAP-NATIVE"],
    ("MP1", "23-packaging"): ["CAP-PACKAGING"],
    ("MP1", "24-tests-and-proof"): ["CAP-TESTING"],
    ("MP1", "25-preservation-first-policy"): ["CAP-IMPLEMENTATION-GOVERNANCE", "CAP-THIRD-PARTY"],
    ("MP1", "26-conditional-keeps-summary"): ["CAP-PLANNING-GOVERNANCE"],
    ("MP1", "final-keep-acceptance"): ["CAP-RELEASE"],
    ("MP2", "mnemora-everything-we-are-deleting"): PRODUCT_SCOPE_CAPS,
    ("MP2", "governing-rule"): ["CAP-DELETION-GOVERNANCE"],
    ("MP2", "binding-deletion-interlock"): ["CAP-DELETION-GOVERNANCE", "CAP-EXACT-LOCATION"],
    ("MP2", "1-active-openwhispr-identity"): ["CAP-REMOVE-ACTIVE-OPENWHISPR-IDENTITY"],
    ("MP2", "2-authentication-and-accounts"): ["CAP-REMOVE-AUTHENTICATION", "CAP-REMOVE-ACCOUNTS"],
    ("MP2", "3-cloud-synchronization"): ["CAP-REMOVE-CLOUD-SYNCHRONISATION"],
    ("MP2", "4-workspaces-organisations-and-teams"): ["CAP-REMOVE-WORKSPACES", "CAP-REMOVE-ORGANISATIONS", "CAP-REMOVE-TEAMS"],
    ("MP2", "5-invitations-and-sharing"): ["CAP-REMOVE-INVITATIONS", "CAP-REMOVE-SHARING"],
    ("MP2", "6-hosted-transcription-providers"): ["CAP-REMOVE-HOSTED-TRANSCRIPTION"],
    ("MP2", "7-hosted-ai-and-provider-systems"): ["CAP-REMOVE-HOSTED-AI"],
    ("MP2", "8-ai-agents-and-chat"): ["CAP-REMOVE-AI-AGENTS", "CAP-REMOVE-CHAT", "CAP-REMOVE-SUMMARISATION", "CAP-REMOVE-ACTION-ITEM-EXTRACTION", "CAP-REMOVE-AI-REWRITING", "CAP-REMOVE-LOCAL-GENERATIVE-AI"],
    ("MP2", "9-agent-tools-and-remote-actions"): ["CAP-REMOVE-AI-AGENTS"],
    ("MP2", "10-google-calendar-and-remote-calendars"): ["CAP-REMOVE-CALENDAR"],
    ("MP2", "11-mcp-public-api-and-cli-authentication"): ["CAP-REMOVE-MCP", "CAP-REMOVE-PUBLIC-API", "CAP-REMOVE-AUTHENTICATION"],
    ("MP2", "12-api-key-and-provider-configuration"): ["CAP-REMOVE-API-KEYS"],
    ("MP2", "13-billing-usage-referrals-and-upgrades"): ["CAP-REMOVE-BILLING", "CAP-REMOVE-USAGE-QUOTAS", "CAP-REMOVE-REFERRALS", "CAP-REMOVE-UPGRADE-SYSTEMS"],
    ("MP2", "14-automatic-updates"): ["CAP-REMOVE-AUTOMATIC-UPDATER"],
    ("MP2", "15-runtime-model-and-binary-downloads"): ["CAP-REMOVE-RUNTIME-MODEL-DOWNLOADS"],
    ("MP2", "16-external-runtime-networking"): ["CAP-REMOVE-RUNTIME-EXTERNAL-NETWORKING", "CAP-REMOVE-RUNTIME-EXTERNAL-LINKS"],
    ("MP2", "17-cloud-audio-and-streaming"): ["CAP-REMOVE-HOSTED-TRANSCRIPTION"],
    ("MP2", "18-remote-speaker-systems"): ["CAP-DIARIZATION", "CAP-VOICE-FINGERPRINTING"],
    ("MP2", "19-cloud-metadata-in-local-data"): ["CAP-REMOVE-CLOUD-SYNCHRONISATION", "CAP-DATA-SAFETY"],
    ("MP2", "20-navigation-and-ui"): ["CAP-DELETION-GOVERNANCE", "CAP-RENDERER"],
    ("MP2", "21-onboarding"): ["CAP-DELETION-GOVERNANCE", "CAP-ONBOARDING"],
    ("MP2", "22-settings"): ["CAP-DELETION-GOVERNANCE", "CAP-SETTINGS"],
    ("MP2", "23-notifications-and-hotkeys"): ["CAP-DELETION-GOVERNANCE", "CAP-NOTIFICATIONS", "CAP-HOTKEY"],
    ("MP2", "24-native-and-packaging-remnants"): ["CAP-DELETION-GOVERNANCE", "CAP-NATIVE", "CAP-PACKAGING"],
    ("MP2", "25-dependencies"): ["CAP-DELETION-GOVERNANCE", "CAP-THIRD-PARTY"],
    ("MP2", "26-dead-code-and-bloat"): ["CAP-DELETION-GOVERNANCE", "CAP-SIMPLIFICATION"],
    ("MP2", "27-generic-dumping-grounds"): ["CAP-REPOSITORY"],
    ("MP2", "28-markdown-from-codebase"): ["CAP-MARKDOWN-GOVERNANCE"],
    ("MP2", "protected-until-proven-otherwise"): ["CAP-DATA-SAFETY", "CAP-DELETION-GOVERNANCE"],
    ("MP2", "final-deletion-acceptance"): ["CAP-DELETION-GOVERNANCE", "CAP-RELEASE"],
}


CAPABILITY_OWNERS: dict[str, str] = {}


def _own(owner: str, ids: Iterable[str]) -> None:
    for capability_id in ids:
        CAPABILITY_OWNERS[capability_id] = owner


_own("Meeting audio", ["CAP-AEC", "CAP-AUDIO", "CAP-AUDIO-MIXING", "CAP-MICROPHONE", "CAP-SYSTEM-AUDIO"])
_own("Desktop shell", ["CAP-APP-SHELL", "CAP-NOTIFICATIONS", "CAP-TRAY", "CAP-WINDOW-LIFECYCLE"])
_own("SQLite persistence", ["CAP-BACKUP", "CAP-DATA-SAFETY", "CAP-DATABASE", "CAP-KYSELY", "CAP-LEGACY-MIGRATION", "CAP-RESTORE"])
_own("Dictation", ["CAP-CLIPBOARD", "CAP-DICTATION", "CAP-HOTKEY", "CAP-MICROPHONE-DICTATION", "CAP-MICROPHONE-SELECTION", "CAP-RECORDING-OVERLAY"])
_own("Diarization and speakers", ["CAP-DIARIZATION", "CAP-SPEAKER-EMBEDDINGS", "CAP-SPEAKER-LABELS", "CAP-SPEAKER-NAMING", "CAP-SPEAKER-PERSISTENCE", "CAP-SPEAKER-RENAMING", "CAP-VOICE-FINGERPRINTING"])
_own("Import and export", ["CAP-EXPORT", "CAP-IMPORT", "CAP-IMPORT-AUDIO", "CAP-IMPORT-EXPORT", "CAP-IMPORT-VIDEO"])
_own("Local transcription", ["CAP-FFMPEG", "CAP-PARAKEET", "CAP-SEGMENTS", "CAP-SHERPA-ONNX", "CAP-TRANSCRIPT-EDIT", "CAP-TRANSCRIPT-HISTORY", "CAP-TRANSCRIPTION", "CAP-VAD", "CAP-WHISPER"])
_own("Notes", ["CAP-FOLDERS", "CAP-LINKED-NOTES", "CAP-MEETING-NOTES", "CAP-NOTE-TEMPLATES", "CAP-NOTES", "CAP-PERSONAL-NOTES", "CAP-SNIPPETS", "CAP-TAGS"])
_own("Playback", ["CAP-LINKED-PLAYBACK", "CAP-PLAYBACK"])
_own("Search", ["CAP-MINILM", "CAP-QDRANT", "CAP-SEARCH-EXACT", "CAP-SEARCH-SEMANTIC"])
_own("Local model handling", ["CAP-MODEL-DISCOVERY", "CAP-MODEL-PACK", "CAP-MODELS"])
_own("Electron IPC", ["CAP-IPC"])
_own("Runtime network policy", ["CAP-LOOPBACK-WEBSOCKETS", "CAP-NETWORK-POLICY"])
_own("Settings and platform security", ["CAP-KEYRING", "CAP-SETTINGS"])
_own("Meeting workflow", ["CAP-MEETING", "CAP-MEETING-DETECTION", "CAP-RECOVERY"])
_own("Platform-native helpers", ["CAP-NATIVE"])
_own("Windows packaging", ["CAP-PACKAGING", "CAP-PORTABLE-WINDOWS", "CAP-WINDOWS-INSTALLER"])
_own("Cross-platform source", ["CAP-MACOS-LINUX"])
_own("Renderer application", ["CAP-ONBOARDING", "CAP-RENDERER"])
_own("Localisation", ["CAP-I18N"])
_own("Local processing", ["CAP-PROCESSING-JOBS"])
_own("Legal and licensing", ["CAP-LEGAL", "CAP-THIRD-PARTY"])
_own("Repository governance", ["CAP-MARKDOWN-GOVERNANCE", "CAP-PROVENANCE", "CAP-REPOSITORY", "CAP-SIMPLIFICATION"])
_own("Graphify governance", ["CAP-DELETION-GOVERNANCE", "CAP-EXACT-LOCATION", "CAP-IMPLEMENTATION-GOVERNANCE", "CAP-PLANNING-GOVERNANCE", "CAP-RELEASE", "CAP-TESTING"])


# All excluded product systems share a deliberately narrow absence-proof owner.
REMOVAL_CAPS = {
    "CAP-REMOVE-ACCOUNTS", "CAP-REMOVE-ACTION-ITEM-EXTRACTION", "CAP-REMOVE-ACTIVE-OPENWHISPR-IDENTITY",
    "CAP-REMOVE-AI-AGENTS", "CAP-REMOVE-AI-REWRITING", "CAP-REMOVE-ANALYTICS", "CAP-REMOVE-API-KEYS",
    "CAP-REMOVE-AUTHENTICATION", "CAP-REMOVE-AUTOMATIC-UPDATER", "CAP-REMOVE-BILLING", "CAP-REMOVE-CALENDAR",
    "CAP-REMOVE-CHAT", "CAP-REMOVE-CLOUD-SYNCHRONISATION", "CAP-REMOVE-HOSTED-AI",
    "CAP-REMOVE-HOSTED-TRANSCRIPTION", "CAP-REMOVE-INVITATIONS", "CAP-REMOVE-LOCAL-GENERATIVE-AI",
    "CAP-REMOVE-MCP", "CAP-REMOVE-ORGANISATIONS", "CAP-REMOVE-PUBLIC-API", "CAP-REMOVE-REFERRALS",
    "CAP-REMOVE-RUNTIME-EXTERNAL-LINKS", "CAP-REMOVE-RUNTIME-EXTERNAL-NETWORKING",
    "CAP-REMOVE-RUNTIME-MODEL-DOWNLOADS", "CAP-REMOVE-SHARING", "CAP-REMOVE-SUMMARISATION",
    "CAP-REMOVE-TEAMS", "CAP-REMOVE-TELEMETRY", "CAP-REMOVE-UPGRADE-SYSTEMS",
    "CAP-REMOVE-USAGE-QUOTAS", "CAP-REMOVE-WORKSPACES",
}
_own("Excluded-system removal", REMOVAL_CAPS)


# Exact reviewed locations for the capabilities most vulnerable to cross-domain
# contamination. Other capabilities are constrained by the domain prefixes below.
EXACT_LOCATIONS: dict[str, list[str]] = {
    "CAP-AEC": [
        "codebase/main/features/meetings/meetingAecManager.js",
        "codebase/main/features/meetings/meetingEchoLeakDetector.js",
        "codebase/main/ipc/ipcHandlers.js",
        "codebase/main/index.js",
        "codebase/native/meeting-aec-helper/CMakeLists.txt",
        "codebase/native/meeting-aec-helper/src/aec_processor.cc",
        "codebase/native/meeting-aec-helper/src/aec_processor.h",
        "codebase/native/meeting-aec-helper/src/main.cc",
        "codebase/native/meeting-aec-helper/src/null_aec_dump_factory.cc",
        "codebase/resources/bin/meeting-aec-helper-win32-x64.exe",
        "codebase/scripts/build/build-meeting-aec-helper.js",
        "codebase/scripts/downloads/download-meeting-aec-helper.js",
        "codebase/scripts/packaging/prepare-offline-assets.js",
        "codebase/tests/unit/meetings/meetingEchoLeakDetector.test.js",
        "codebase/electron-builder.json",
    ],
    "CAP-SEARCH-EXACT": [
        "codebase/main/infrastructure/persistence/database.js",
        "codebase/main/ipc/ipcHandlers.js",
        "codebase/preload/index.js",
        "codebase/renderer/shared/types/electron.ts",
        "codebase/renderer/features/search/SearchView.tsx",
        "codebase/tests/unit/persistence/localDataDatabase.test.js",
        "codebase/tests/unit/persistence/localBackup.test.js",
    ],
    "CAP-SEARCH-SEMANTIC": [
        "codebase/main/features/search/localEmbeddings.js",
        "codebase/main/features/search/onnxWorkerClient.js",
        "codebase/main/features/search/qdrantManager.js",
        "codebase/main/features/search/vectorIndex.js",
        "codebase/main/ipc/ipcHandlers.js",
        "codebase/preload/index.js",
        "codebase/renderer/shared/types/electron.ts",
        "codebase/renderer/features/search/SearchView.tsx",
        "codebase/tests/unit/search/vectorIndex.test.js",
    ],
    "CAP-DATABASE": [
        "codebase/main/infrastructure/persistence/database.js",
        "codebase/main/infrastructure/persistence/dataMigration.js",
        "codebase/main/infrastructure/persistence/localBackup.js",
        "codebase/tests/unit/persistence/localDataDatabase.test.js",
        "codebase/tests/unit/persistence/dataMigration.test.js",
        "codebase/tests/unit/persistence/localBackup.test.js",
    ],
    "CAP-IPC": [
        "codebase/main/ipc/ipcHandlers.js",
        "codebase/preload/index.js",
        "codebase/renderer/shared/types/electron.ts",
        "codebase/tests/unit/security/offlineIpcSurface.test.js",
    ],
    "CAP-NETWORK-POLICY": [
        "codebase/main/infrastructure/runtime/runtimeNetworkPolicy.js",
        "codebase/main/index.js",
        "codebase/tests/unit/security/runtimeNetworkPolicy.test.js",
        "codebase/tests/unit/security/offlineIpcSurface.test.js",
    ],
    "CAP-I18N": [
        "codebase/shared/i18n/en/translation.json",
        "codebase/main/infrastructure/runtime/i18nMain.js",
        "codebase/scripts/verification/check-i18n.js",
    ],
    "CAP-NOTES": [
        "codebase/main/features/notes/markdownMirror.js",
        "codebase/main/infrastructure/persistence/database.js",
        "codebase/main/ipc/ipcHandlers.js",
        "codebase/preload/index.js",
        "codebase/renderer/shared/types/electron.ts",
        "codebase/renderer/features/notes/noteStore.ts",
        "codebase/renderer/features/notes/useFolderManagement.ts",
        "codebase/renderer/features/notes/useNoteDragAndDrop.ts",
        "codebase/renderer/features/notes/components/AddNotesToFolderDialog.tsx",
        "codebase/renderer/features/notes/components/MeetingRecordingPill.tsx",
        "codebase/renderer/features/notes/components/MeetingTranscriptView.tsx",
        "codebase/renderer/features/notes/components/NoteEditor.tsx",
        "codebase/renderer/features/notes/components/RichTextEditor.tsx",
        "codebase/renderer/features/notes/components/PersonalNotesView.tsx",
        "codebase/tests/unit/persistence/localDataDatabase.test.js",
        "codebase/tests/unit/persistence/snippetsDatabase.test.js",
        "codebase/tests/unit/snippets/snippets.test.js",
    ],
    "CAP-MINILM": [
        "codebase/main/features/search/localEmbeddings.js",
        "codebase/main/features/search/onnxWorkerClient.js",
        "codebase/main/features/search/vectorIndex.js",
        "codebase/resources/bin/all-MiniLM-L6-v2/model.onnx",
        "codebase/resources/bin/all-MiniLM-L6-v2/tokenizer.json",
        "codebase/tests/unit/search/vectorIndex.test.js",
    ],
    "CAP-PARAKEET": [],
    "CAP-KEYRING": [],
    "CAP-KYSELY": [],
    "CAP-NOTE-TEMPLATES": [],
    "CAP-PROCESSING-JOBS": [],
    "CAP-OFFLINE-FIRST-LAUNCH": [],
}

# Every narrower retained capability below has a reviewed path set.  This avoids
# inheriting every file in a same-named feature folder merely because the old
# graph layer attached that folder to a broad concept.
EXACT_LOCATIONS.update({
    "CAP-APP-SHELL": [
        "codebase/main/index.js", "codebase/main/desktop/windowManager.js", "codebase/main/desktop/windowConfig.js",
        "codebase/main/desktop/tray.js", "codebase/main/desktop/menuManager.js", "codebase/renderer/app/main.jsx",
        "codebase/renderer/app/AppRouter.jsx", "codebase/renderer/app/components/ControlPanel.tsx",
        "codebase/renderer/app/components/ControlPanelSidebar.tsx", "codebase/preload/index.js",
    ],
    "CAP-AUDIO": [
        "codebase/main/features/meetings/audioUtils.js", "codebase/main/features/meetings/audioActivityDetector.js",
        "codebase/renderer/features/meetings/meetingRecordingStore.ts", "codebase/main/ipc/ipcHandlers.js",
    ],
    "CAP-AUDIO-MIXING": [
        "codebase/renderer/features/meetings/meetingRecordingStore.ts", "codebase/main/features/meetings/audioUtils.js",
        "codebase/main/ipc/ipcHandlers.js", "codebase/tests/unit/meetings/meetingMicHoldback.test.js",
    ],
    "CAP-BACKUP": [
        "codebase/main/infrastructure/persistence/localBackup.js", "codebase/main/infrastructure/persistence/database.js",
        "codebase/main/ipc/ipcHandlers.js", "codebase/preload/index.js", "codebase/renderer/shared/types/electron.ts",
        "codebase/tests/unit/persistence/localBackup.test.js",
    ],
    "CAP-CLIPBOARD": [
        "codebase/main/features/dictation/clipboard.js", "codebase/renderer/features/dictation/useClipboard.ts",
        "codebase/main/ipc/ipcHandlers.js", "codebase/preload/index.js", "codebase/renderer/shared/types/electron.ts",
        "codebase/tests/unit/dictation/clipboardRestore.test.js",
    ],
    "CAP-DATA-SAFETY": [
        "codebase/main/infrastructure/persistence/database.js", "codebase/main/infrastructure/persistence/localBackup.js",
        "codebase/main/infrastructure/persistence/dataMigration.js", "codebase/main/infrastructure/persistence/audioStorage.js",
        "codebase/tests/unit/persistence/localDataDatabase.test.js", "codebase/tests/unit/persistence/localBackup.test.js",
        "codebase/tests/unit/persistence/dataMigration.test.js",
    ],
    "CAP-DIARIZATION": [
        "codebase/main/features/meetings/diarization.js", "codebase/renderer/features/meetings/meetingRecordingStore.ts",
        "codebase/main/ipc/ipcHandlers.js", "codebase/preload/index.js", "codebase/renderer/shared/types/electron.ts",
        "codebase/resources/bin/sherpa-onnx-diarize-win32-x64.exe",
        "codebase/resources/bin/diarization-models/sherpa-onnx-pyannote-segmentation-3-0/model.onnx",
        "codebase/resources/bin/diarization-models/3dspeaker_speech_campplus_sv_en_voxceleb_16k.onnx",
        "codebase/resources/bin/diarization-models/silero_vad.onnx", "codebase/scripts/downloads/download-diarization-models.js",
        "codebase/scripts/diagnostics/meeting-diarization-eval.js", "codebase/scripts/packaging/prepare-offline-assets.js",
    ],
    "CAP-EXPORT": [
        "codebase/main/ipc/ipcHandlers.js", "codebase/preload/index.js", "codebase/renderer/shared/types/electron.ts",
        "codebase/main/features/dictation/transcriptFormatter.js",
    ],
    "CAP-FFMPEG": [
        "codebase/main/features/transcription/ffmpegUtils.js", "codebase/main/features/transcription/whisper.js",
        "codebase/main/features/transcription/whisperServer.js", "codebase/main/ipc/ipcHandlers.js",
        "codebase/scripts/packaging/afterPack.js", "codebase/scripts/packaging/prepare-offline-assets.js", "codebase/electron-builder.json",
    ],
    "CAP-FOLDERS": [
        "codebase/renderer/features/notes/useFolderManagement.ts", "codebase/renderer/features/notes/useNoteDragAndDrop.ts",
        "codebase/renderer/features/notes/components/AddNotesToFolderDialog.tsx", "codebase/main/infrastructure/persistence/database.js",
        "codebase/main/ipc/ipcHandlers.js", "codebase/preload/index.js", "codebase/renderer/shared/types/electron.ts",
        "codebase/tests/unit/persistence/localDataDatabase.test.js",
    ],
    "CAP-HOTKEY": [
        "codebase/main/features/dictation/hotkeyManager.js", "codebase/main/features/dictation/hotkeyList.js",
        "codebase/renderer/features/dictation/useHotkey.js", "codebase/renderer/features/dictation/useHotkeyRegistration.ts",
        "codebase/renderer/features/dictation/hotkeys.ts", "codebase/renderer/features/dictation/hotkeyValidation.ts",
        "codebase/main/platform/windowsKeyManager.js", "codebase/main/platform/linuxKeyManager.js", "codebase/main/platform/globeKeyManager.js",
        "codebase/main/ipc/ipcHandlers.js", "codebase/tests/unit/dictation/hotkeyList.test.js",
        "codebase/tests/unit/dictation/hotkeySlotRollback.test.js", "codebase/tests/unit/platform/nativeListenerKeys.test.js",
    ],
    "CAP-IMPORT": [
        "codebase/renderer/features/notes/components/UploadAudioView.tsx", "codebase/main/ipc/ipcHandlers.js",
        "codebase/preload/index.js", "codebase/renderer/shared/types/electron.ts", "codebase/main/features/transcription/downloadUtils.js",
    ],
    "CAP-IMPORT-AUDIO": [
        "codebase/renderer/features/notes/components/UploadAudioView.tsx", "codebase/main/ipc/ipcHandlers.js",
        "codebase/preload/index.js", "codebase/renderer/shared/types/electron.ts", "codebase/main/features/transcription/ffmpegUtils.js",
    ],
    "CAP-IMPORT-VIDEO": [
        "codebase/renderer/features/notes/components/UploadAudioView.tsx", "codebase/main/ipc/ipcHandlers.js",
        "codebase/preload/index.js", "codebase/renderer/shared/types/electron.ts", "codebase/main/features/transcription/ffmpegUtils.js",
    ],
    "CAP-IMPORT-EXPORT": [
        "codebase/main/ipc/ipcHandlers.js", "codebase/preload/index.js", "codebase/renderer/shared/types/electron.ts",
        "codebase/renderer/features/notes/components/UploadAudioView.tsx", "codebase/main/features/dictation/transcriptFormatter.js",
        "codebase/main/infrastructure/persistence/localBackup.js",
    ],
    "CAP-LEGACY-MIGRATION": [
        "codebase/main/infrastructure/persistence/dataMigration.js", "codebase/main/infrastructure/persistence/postMigrationDetector.js",
        "codebase/main/infrastructure/persistence/database.js", "codebase/renderer/features/onboarding/PostMigrationOnboarding.tsx",
        "codebase/tests/unit/persistence/dataMigration.test.js", "codebase/tests/unit/persistence/localDataDatabase.test.js",
    ],
    "CAP-LEGAL": ["codebase/LICENSE", "codebase/package.json", "codebase/package-lock.json", "codebase/electron-builder.json"],
    "CAP-LINKED-NOTES": [
        "codebase/renderer/features/notes/components/NoteEditor.tsx", "codebase/renderer/features/notes/components/MeetingTranscriptView.tsx",
        "codebase/renderer/features/notes/components/MeetingRecordingPill.tsx", "codebase/main/infrastructure/persistence/database.js",
        "codebase/main/ipc/ipcHandlers.js", "codebase/preload/index.js", "codebase/renderer/shared/types/electron.ts",
    ],
    "CAP-LINKED-PLAYBACK": [
        "codebase/renderer/features/notes/components/MeetingTranscriptView.tsx", "codebase/renderer/features/notes/components/MeetingRecordingPill.tsx",
        "codebase/main/infrastructure/persistence/audioStorage.js", "codebase/main/ipc/ipcHandlers.js", "codebase/preload/index.js",
    ],
    "CAP-LOOPBACK-WEBSOCKETS": ["codebase/main/infrastructure/runtime/runtimeNetworkPolicy.js", "codebase/tests/unit/security/runtimeNetworkPolicy.test.js"],
    "CAP-MACOS-LINUX": [
        "codebase/native/helpers/macos", "codebase/native/helpers/linux", "codebase/packaging/macos", "codebase/packaging/linux",
        "codebase/scripts/build/build-macos-audio-tap.js", "codebase/scripts/build/build-linux-system-audio.js",
        "codebase/electron-builder.json", "codebase/tests/unit/platform/linuxLauncherSandbox.test.js",
    ],
    "CAP-MEETING": [
        "codebase/renderer/features/meetings/meetingRecordingStore.ts", "codebase/renderer/features/meetings/MeetingsView.tsx",
        "codebase/renderer/features/meetings/MeetingRecordingMount.tsx", "codebase/main/ipc/ipcHandlers.js",
        "codebase/preload/index.js", "codebase/renderer/shared/types/electron.ts", "codebase/main/infrastructure/persistence/database.js",
        "codebase/main/infrastructure/persistence/audioStorage.js", "codebase/main/features/meetings/audioUtils.js",
        "codebase/main/features/meetings/diarization.js", "codebase/tests/unit/meetings/meetingMicHoldback.test.js",
    ],
    "CAP-MEETING-DETECTION": [
        "codebase/main/features/meetings/meetingDetectionEngine.js", "codebase/main/features/meetings/meetingProcessDetector.js",
        "codebase/renderer/features/meetings/MeetingNotificationOverlay.tsx", "codebase/renderer/features/meetings/MeetingNotificationCard.tsx",
        "codebase/main/ipc/ipcHandlers.js", "codebase/preload/index.js", "codebase/renderer/shared/types/electron.ts",
    ],
    "CAP-MEETING-NOTES": [
        "codebase/renderer/features/notes/components/NoteEditor.tsx", "codebase/renderer/features/notes/components/MeetingTranscriptView.tsx",
        "codebase/renderer/features/notes/components/MeetingRecordingPill.tsx", "codebase/renderer/features/meetings/MeetingsView.tsx",
        "codebase/main/infrastructure/persistence/database.js", "codebase/main/ipc/ipcHandlers.js", "codebase/preload/index.js",
    ],
    "CAP-MICROPHONE": [
        "codebase/renderer/features/meetings/meetingRecordingStore.ts", "codebase/renderer/features/dictation/useAudioRecording.js",
        "codebase/renderer/features/dictation/audioManager.js", "codebase/renderer/features/transcription/audioDeviceUtils.ts",
        "codebase/main/ipc/ipcHandlers.js", "codebase/tests/unit/dictation/micTrackHealth.test.js",
    ],
    "CAP-MICROPHONE-DICTATION": [
        "codebase/renderer/features/dictation/useAudioRecording.js", "codebase/renderer/features/dictation/audioManager.js",
        "codebase/renderer/features/dictation/App.jsx", "codebase/renderer/features/dictation/micTrackHealth.js",
        "codebase/main/ipc/ipcHandlers.js", "codebase/tests/unit/dictation/micTrackHealth.test.js",
        "codebase/tests/unit/dictation/recordingValidation.test.js",
    ],
    "CAP-MICROPHONE-SELECTION": [
        "codebase/renderer/features/transcription/audioDeviceUtils.ts", "codebase/renderer/features/dictation/staleMicDevice.js",
        "codebase/renderer/features/settings/SettingsPage.tsx", "codebase/main/ipc/ipcHandlers.js",
        "codebase/tests/unit/dictation/staleMicDevice.test.js",
    ],
    "CAP-MODEL-DISCOVERY": [
        "codebase/main/features/transcription/modelDirUtils.js", "codebase/main/features/transcription/modelRegistryData.json",
        "codebase/main/features/transcription/whisper.js", "codebase/main/features/meetings/diarization.js",
        "codebase/resources/bin/asset-manifest.json", "codebase/main/ipc/ipcHandlers.js",
    ],
    "CAP-MODEL-PACK": [
        "codebase/main/features/transcription/downloadUtils.js", "codebase/main/features/transcription/modelDirUtils.js",
        "codebase/main/features/transcription/modelRegistryData.json", "codebase/main/features/transcription/whisper.js",
        "codebase/main/features/meetings/diarization.js", "codebase/main/ipc/ipcHandlers.js", "codebase/preload/index.js",
        "codebase/tests/unit/transcription/extractArchive.test.js",
    ],
    "CAP-MODELS": [
        "codebase/main/features/transcription/modelDirUtils.js", "codebase/main/features/transcription/modelRegistryData.json",
        "codebase/resources/bin/asset-manifest.json", "codebase/main/ipc/ipcHandlers.js", "codebase/renderer/features/transcription/modelPickerStyles.ts",
    ],
    "CAP-NATIVE": ["codebase/native/helpers", "codebase/native/meeting-aec-helper", "codebase/main/platform", "codebase/scripts/build", "codebase/electron-builder.json"],
    "CAP-NOTIFICATIONS": [
        "codebase/renderer/features/meetings/MeetingNotificationCard.tsx", "codebase/renderer/features/meetings/MeetingNotificationOverlay.tsx",
        "codebase/main/desktop/windowManager.js", "codebase/main/ipc/ipcHandlers.js", "codebase/preload/index.js",
    ],
    "CAP-ONBOARDING": [
        "codebase/renderer/features/onboarding/OnboardingFlow.tsx", "codebase/renderer/features/onboarding/PostMigrationOnboarding.tsx",
        "codebase/renderer/features/onboarding/components/MeetingSetupStep.tsx", "codebase/main/infrastructure/persistence/postMigrationDetector.js",
    ],
    "CAP-PACKAGING": [
        "codebase/electron-builder.json", "codebase/electron-builder.unsigned-win.json", "codebase/scripts/packaging/afterPack.js",
        "codebase/scripts/packaging/prepare-offline-assets.js", "codebase/scripts/verification/verify-offline-assets.js",
        "codebase/packaging/windows/installer.nsh", "codebase/packaging/macos/entitlements.mac.plist",
        "codebase/packaging/linux/after-install.sh", "codebase/packaging/linux/after-remove.sh", "codebase/package.json",
    ],
    "CAP-PERSONAL-NOTES": [
        "codebase/renderer/features/notes/components/PersonalNotesView.tsx", "codebase/renderer/features/notes/components/NoteEditor.tsx",
        "codebase/renderer/features/notes/noteStore.ts", "codebase/main/infrastructure/persistence/database.js",
        "codebase/main/ipc/ipcHandlers.js", "codebase/preload/index.js", "codebase/tests/unit/persistence/localDataDatabase.test.js",
    ],
    "CAP-PLAYBACK": [
        "codebase/renderer/features/notes/components/MeetingRecordingPill.tsx", "codebase/renderer/features/notes/components/MeetingTranscriptView.tsx",
        "codebase/main/infrastructure/persistence/audioStorage.js", "codebase/main/ipc/ipcHandlers.js", "codebase/preload/index.js",
        "codebase/renderer/shared/types/electron.ts",
    ],
    "CAP-PORTABLE-WINDOWS": ["codebase/electron-builder.json", "codebase/scripts/packaging/prepare-offline-assets.js", "codebase/scripts/verification/verify-offline-assets.js"],
    "CAP-QDRANT": [
        "codebase/main/features/search/qdrantManager.js", "codebase/main/features/search/vectorIndex.js",
        "codebase/resources/bin/qdrant-win32-x64.exe", "codebase/scripts/downloads/download-qdrant.js",
        "codebase/scripts/packaging/prepare-offline-assets.js", "codebase/electron-builder.json", "codebase/package.json",
        "codebase/tests/unit/search/vectorIndex.test.js",
    ],
    "CAP-RECORDING-OVERLAY": [
        "codebase/renderer/features/transcription/TranscriptionPreviewOverlay.tsx", "codebase/renderer/features/dictation/App.jsx",
        "codebase/renderer/features/dictation/recordingGuard.js", "codebase/renderer/features/dictation/recordingValidation.js",
        "codebase/renderer/features/dictation/discardedRecording.js", "codebase/tests/unit/dictation/recordingGuard.test.js",
        "codebase/tests/unit/dictation/discardedRecording.test.js",
    ],
    "CAP-RECOVERY": [
        "codebase/renderer/features/meetings/meetingRecordingStore.ts", "codebase/renderer/features/meetings/MeetingRecordingMount.tsx",
        "codebase/main/infrastructure/persistence/audioStorage.js", "codebase/main/infrastructure/persistence/database.js",
        "codebase/main/ipc/ipcHandlers.js",
    ],
    "CAP-RENDERER": [
        "codebase/renderer/app/main.jsx", "codebase/renderer/app/AppRouter.jsx", "codebase/renderer/app/components/ControlPanel.tsx",
        "codebase/renderer/app/components/ControlPanelSidebar.tsx", "codebase/renderer/app/components/ErrorBoundary.tsx",
        "codebase/renderer/app/components/WindowControls.tsx", "codebase/renderer/shared/types/electron.ts",
    ],
    "CAP-REPOSITORY": ["codebase/package.json", "codebase/package-lock.json", "codebase/main", "codebase/preload", "codebase/renderer", "codebase/tests", "codebase/scripts"],
    "CAP-RESTORE": [
        "codebase/main/infrastructure/persistence/localBackup.js", "codebase/main/infrastructure/persistence/database.js",
        "codebase/main/ipc/ipcHandlers.js", "codebase/preload/index.js", "codebase/renderer/shared/types/electron.ts",
        "codebase/tests/unit/persistence/localBackup.test.js",
    ],
    "CAP-SEGMENTS": [
        "codebase/main/infrastructure/persistence/database.js", "codebase/main/features/meetings/diarization.js",
        "codebase/main/features/meetings/transcriptText.js", "codebase/renderer/features/meetings/parseTranscriptSegments.ts",
        "codebase/renderer/features/notes/components/MeetingTranscriptView.tsx", "codebase/main/ipc/ipcHandlers.js",
        "codebase/tests/unit/meetings/transcriptText.test.js", "codebase/tests/unit/persistence/localDataDatabase.test.js",
    ],
    "CAP-SETTINGS": [
        "codebase/renderer/features/settings/SettingsPage.tsx", "codebase/renderer/features/settings/settingsStore.ts",
        "codebase/renderer/features/settings/useSettings.ts", "codebase/main/infrastructure/persistence/database.js",
        "codebase/main/ipc/ipcHandlers.js", "codebase/preload/index.js", "codebase/renderer/shared/types/electron.ts",
    ],
    "CAP-SHERPA-ONNX": [
        "codebase/main/features/meetings/diarization.js", "codebase/resources/bin/sherpa-onnx-diarize-win32-x64.exe",
        "codebase/resources/bin/sherpa-onnx-c-api.dll", "codebase/resources/bin/sherpa-onnx-cxx-api.dll",
        "codebase/resources/bin/diarization-models/sherpa-onnx-pyannote-segmentation-3-0/model.onnx",
        "codebase/scripts/downloads/download-sherpa-onnx.js", "codebase/scripts/packaging/prepare-offline-assets.js",
        "codebase/electron-builder.json", "codebase/scripts/diagnostics/meeting-diarization-eval.js",
    ],
    "CAP-SNIPPETS": [
        "codebase/renderer/features/snippets/SnippetsView.tsx", "codebase/renderer/features/snippets/snippets.ts",
        "codebase/main/infrastructure/persistence/database.js", "codebase/main/ipc/ipcHandlers.js", "codebase/preload/index.js",
        "codebase/renderer/shared/types/electron.ts", "codebase/tests/unit/persistence/snippetsDatabase.test.js",
        "codebase/tests/unit/snippets/snippets.test.js",
    ],
    "CAP-SPEAKER-EMBEDDINGS": [
        "codebase/main/features/meetings/speakerEmbeddings.js", "codebase/main/features/meetings/liveSpeakerIdentifier.js",
        "codebase/main/features/meetings/speakerAssignmentPolicy.js", "codebase/main/infrastructure/persistence/database.js",
        "codebase/renderer/features/meetings/transcriptSpeakerState.ts", "codebase/main/workers/onnxWorker.js",
    ],
    "CAP-SPEAKER-LABELS": [
        "codebase/renderer/features/meetings/transcriptSpeakerState.ts", "codebase/renderer/features/notes/components/MeetingTranscriptView.tsx",
        "codebase/main/features/meetings/speakerAssignmentPolicy.js", "codebase/main/infrastructure/persistence/database.js",
    ],
    "CAP-SPEAKER-NAMING": [
        "codebase/renderer/features/notes/components/MeetingTranscriptView.tsx", "codebase/renderer/features/meetings/transcriptSpeakerState.ts",
        "codebase/main/features/meetings/speakerAssignmentPolicy.js", "codebase/main/infrastructure/persistence/database.js", "codebase/main/ipc/ipcHandlers.js",
    ],
    "CAP-SPEAKER-PERSISTENCE": [
        "codebase/main/infrastructure/persistence/database.js", "codebase/main/features/meetings/liveSpeakerIdentifier.js",
        "codebase/main/features/meetings/speakerEmbeddings.js", "codebase/main/ipc/ipcHandlers.js", "codebase/tests/unit/persistence/localDataDatabase.test.js",
    ],
    "CAP-SPEAKER-RENAMING": [
        "codebase/renderer/features/notes/components/MeetingTranscriptView.tsx", "codebase/renderer/features/meetings/transcriptSpeakerState.ts",
        "codebase/main/features/meetings/speakerAssignmentPolicy.js", "codebase/main/infrastructure/persistence/database.js", "codebase/main/ipc/ipcHandlers.js",
    ],
    "CAP-SYSTEM-AUDIO": [
        "codebase/main/platform/windowsLoopbackAudioManager.js", "codebase/main/features/meetings/audioTapManager.js",
        "codebase/main/platform/linuxPortalAudioManager.js", "codebase/renderer/features/meetings/systemAudioAccess.ts",
        "codebase/renderer/features/meetings/useSystemAudioPermission.ts", "codebase/renderer/features/meetings/meetingRecordingStore.ts",
        "codebase/native/helpers/windows/windows-system-audio-helper.c", "codebase/native/helpers/linux/linux-system-audio-helper.c",
        "codebase/native/helpers/macos/macos-audio-tap.swift", "codebase/main/ipc/ipcHandlers.js",
    ],
    "CAP-TAGS": [
        "codebase/main/infrastructure/persistence/database.js", "codebase/renderer/features/search/SearchView.tsx",
        "codebase/renderer/features/notes/components/NoteEditor.tsx", "codebase/main/ipc/ipcHandlers.js", "codebase/preload/index.js",
        "codebase/renderer/shared/types/electron.ts", "codebase/tests/unit/persistence/localDataDatabase.test.js",
    ],
    "CAP-TESTING": ["codebase/tests", "codebase/scripts/verification", "codebase/package.json", "codebase/renderer/tsconfig.json", "codebase/eslint.config.js"],
    "CAP-TRANSCRIPT-EDIT": [
        "codebase/renderer/features/notes/components/MeetingTranscriptView.tsx", "codebase/renderer/features/notes/components/NoteEditor.tsx",
        "codebase/main/infrastructure/persistence/database.js", "codebase/main/ipc/ipcHandlers.js", "codebase/preload/index.js",
        "codebase/renderer/shared/types/electron.ts", "codebase/tests/unit/persistence/localDataDatabase.test.js",
    ],
    "CAP-TRANSCRIPT-HISTORY": [
        "codebase/renderer/features/dictation/HistoryView.tsx", "codebase/renderer/features/transcription/transcriptionStore.ts",
        "codebase/main/infrastructure/persistence/database.js", "codebase/main/infrastructure/persistence/audioStorage.js",
        "codebase/main/ipc/ipcHandlers.js", "codebase/preload/index.js", "codebase/renderer/shared/types/electron.ts",
    ],
    "CAP-TRANSCRIPTION": [
        "codebase/main/features/transcription/whisper.js", "codebase/main/features/transcription/whisperServer.js",
        "codebase/renderer/features/transcription/transcriptionStore.ts", "codebase/renderer/features/transcription/useWhisper.ts",
        "codebase/renderer/features/transcription/TranscriptionPreviewOverlay.tsx", "codebase/main/infrastructure/persistence/database.js",
        "codebase/main/ipc/ipcHandlers.js", "codebase/preload/index.js", "codebase/renderer/shared/types/electron.ts",
        "codebase/tests/unit/transcription/whisperWakeRewarm.test.js",
    ],
    "CAP-TRAY": ["codebase/main/desktop/tray.js", "codebase/main/index.js", "codebase/renderer/assets/iconTemplate@3x.png"],
    "CAP-VOICE-FINGERPRINTING": [
        "codebase/main/features/meetings/speakerEmbeddings.js", "codebase/main/features/meetings/liveSpeakerIdentifier.js",
        "codebase/main/infrastructure/persistence/database.js", "codebase/renderer/features/notes/components/NoteEditor.tsx",
        "codebase/main/ipc/ipcHandlers.js",
    ],
    "CAP-WHISPER": [
        "codebase/main/features/transcription/whisper.js", "codebase/main/features/transcription/whisperServer.js",
        "codebase/main/features/transcription/whisperCudaManager.js", "codebase/main/features/transcription/whisperVadConfig.js",
        "codebase/resources/bin/whisper-server-win32-x64.exe", "codebase/resources/bin/whisper-models/ggml-base.bin",
        "codebase/scripts/downloads/download-whisper-cpp.js", "codebase/scripts/downloads/download-whisper-model.js",
        "codebase/scripts/packaging/prepare-offline-assets.js", "codebase/main/ipc/ipcHandlers.js",
        "codebase/tests/unit/transcription/whisperWakeRewarm.test.js",
    ],
    "CAP-WINDOW-LIFECYCLE": [
        "codebase/main/desktop/windowManager.js", "codebase/main/desktop/windowConfig.js", "codebase/main/index.js",
        "codebase/renderer/app/components/WindowControls.tsx", "codebase/main/ipc/ipcHandlers.js", "codebase/preload/index.js",
    ],
    "CAP-WINDOWS-INSTALLER": [
        "codebase/electron-builder.json", "codebase/electron-builder.unsigned-win.json", "codebase/packaging/windows/installer.nsh",
        "codebase/scripts/packaging/afterPack.js", "codebase/scripts/packaging/prepare-offline-assets.js", "codebase/scripts/verification/verify-offline-assets.js",
    ],
})


DOMAIN_PREFIXES: dict[str, tuple[str, ...]] = {
    "dictation": ("codebase/main/features/dictation/", "codebase/renderer/features/dictation/", "codebase/tests/unit/dictation/"),
    "meetings": ("codebase/main/features/meetings/", "codebase/renderer/features/meetings/", "codebase/tests/unit/meetings/", "codebase/native/meeting-aec-helper/"),
    "transcription": ("codebase/main/features/transcription/", "codebase/renderer/features/transcription/", "codebase/tests/unit/transcription/"),
    "notes": ("codebase/main/features/notes/", "codebase/renderer/features/notes/", "codebase/tests/unit/persistence/", "codebase/tests/unit/snippets/"),
    "search": ("codebase/main/features/search/", "codebase/renderer/features/search/", "codebase/tests/unit/search/"),
    "persistence": ("codebase/main/infrastructure/persistence/", "codebase/tests/unit/persistence/"),
    "shell": ("codebase/main/desktop/", "codebase/renderer/app/", "codebase/renderer/shared/layout/"),
    "platform": ("codebase/main/platform/", "codebase/native/helpers/", "codebase/tests/unit/platform/"),
    "packaging": ("codebase/packaging/", "codebase/scripts/packaging/", "codebase/scripts/verification/", "codebase/electron-builder"),
    "i18n": ("codebase/shared/i18n/", "codebase/main/infrastructure/runtime/i18n", "codebase/renderer/i18n"),
    "runtime": ("codebase/main/infrastructure/runtime/", "codebase/tests/unit/security/"),
    "settings": ("codebase/renderer/features/settings/",),
    "renderer": ("codebase/renderer/",),
    "tests": ("codebase/tests/", "codebase/scripts/verification/"),
    "imports": ("codebase/renderer/features/notes/components/UploadAudioView.tsx", "codebase/main/features/dictation/transcriptFormatter.js"),
}


CAPABILITY_DOMAINS: dict[str, tuple[str, ...]] = {}


def _domains(names: tuple[str, ...], ids: Iterable[str]) -> None:
    for capability_id in ids:
        CAPABILITY_DOMAINS[capability_id] = names


_domains(("dictation",), ["CAP-CLIPBOARD", "CAP-DICTATION", "CAP-HOTKEY", "CAP-MICROPHONE-DICTATION", "CAP-MICROPHONE-SELECTION", "CAP-RECORDING-OVERLAY"])
_domains(("meetings",), ["CAP-AEC", "CAP-AUDIO", "CAP-AUDIO-MIXING", "CAP-DIARIZATION", "CAP-MEETING", "CAP-MEETING-DETECTION", "CAP-MICROPHONE", "CAP-RECOVERY", "CAP-SPEAKER-EMBEDDINGS", "CAP-SPEAKER-LABELS", "CAP-SPEAKER-NAMING", "CAP-SPEAKER-PERSISTENCE", "CAP-SPEAKER-RENAMING", "CAP-SYSTEM-AUDIO", "CAP-VOICE-FINGERPRINTING"])
_domains(("transcription",), ["CAP-FFMPEG", "CAP-IMPORT-AUDIO", "CAP-IMPORT-VIDEO", "CAP-MODEL-DISCOVERY", "CAP-MODEL-PACK", "CAP-MODELS", "CAP-PARAKEET", "CAP-SEGMENTS", "CAP-SHERPA-ONNX", "CAP-TRANSCRIPT-EDIT", "CAP-TRANSCRIPT-HISTORY", "CAP-TRANSCRIPTION", "CAP-VAD", "CAP-WHISPER"])
_domains(("notes",), ["CAP-FOLDERS", "CAP-LINKED-NOTES", "CAP-MEETING-NOTES", "CAP-NOTE-TEMPLATES", "CAP-NOTES", "CAP-PERSONAL-NOTES", "CAP-SNIPPETS", "CAP-TAGS"])
_domains(("search",), ["CAP-MINILM", "CAP-QDRANT", "CAP-SEARCH-EXACT", "CAP-SEARCH-SEMANTIC"])
_domains(("persistence",), ["CAP-BACKUP", "CAP-DATA-SAFETY", "CAP-DATABASE", "CAP-LEGACY-MIGRATION", "CAP-RESTORE"])
_domains(("shell",), ["CAP-APP-SHELL", "CAP-NOTIFICATIONS", "CAP-TRAY", "CAP-WINDOW-LIFECYCLE"])
_domains(("platform",), ["CAP-NATIVE"])
_domains(("packaging",), ["CAP-PACKAGING", "CAP-PORTABLE-WINDOWS", "CAP-WINDOWS-INSTALLER", "CAP-MACOS-LINUX"])
_domains(("runtime",), ["CAP-LOOPBACK-WEBSOCKETS", "CAP-NETWORK-POLICY"])
_domains(("i18n",), ["CAP-I18N"])
_domains(("settings",), ["CAP-SETTINGS", "CAP-KEYRING"])
_domains(("renderer",), ["CAP-RENDERER", "CAP-ONBOARDING"])
_domains(("tests",), ["CAP-TESTING"])
_domains(("imports", "notes", "transcription"), ["CAP-EXPORT", "CAP-IMPORT", "CAP-IMPORT-AUDIO", "CAP-IMPORT-EXPORT", "CAP-IMPORT-VIDEO"])
_domains(("meetings", "notes"), ["CAP-LINKED-PLAYBACK", "CAP-PLAYBACK", "CAP-LINKED-NOTES", "CAP-MEETING-NOTES"])
_domains(("persistence", "runtime"), ["CAP-REPOSITORY"])


SHARED_BOUNDARY_PATHS = {
    "codebase/main/index.js",
    "codebase/main/ipc/ipcHandlers.js",
    "codebase/preload/index.js",
    "codebase/renderer/shared/types/electron.ts",
    "codebase/main/infrastructure/persistence/database.js",
    "codebase/package.json",
    "codebase/package-lock.json",
    "codebase/electron-builder.json",
}


TARGET_OVERRIDES = {
    "CAP-AEC": ("codebase/main/features/meetings/meetingAecManager.js", "MeetingAecManager"),
    "CAP-APP-SHELL": ("codebase/main/index.js", "app.whenReady"),
    "CAP-DATABASE": ("codebase/main/infrastructure/persistence/database.js", "DatabaseManager"),
    "CAP-DIARIZATION": ("codebase/main/features/meetings/diarization.js", "DiarizationManager"),
    "CAP-EXPORT": ("codebase/main/ipc/ipcHandlers.js", "export handlers"),
    "CAP-FOLDERS": ("codebase/renderer/features/notes/useFolderManagement.ts", "useFolderManagement"),
    "CAP-HOTKEY": ("codebase/main/features/dictation/hotkeyManager.js", "HotkeyManager"),
    "CAP-I18N": ("codebase/shared/i18n/en/translation.json", "local translation catalogue"),
    "CAP-IMPORT": ("codebase/renderer/features/notes/components/UploadAudioView.tsx", "UploadAudioView"),
    "CAP-IMPORT-AUDIO": ("codebase/renderer/features/notes/components/UploadAudioView.tsx", "UploadAudioView"),
    "CAP-IMPORT-EXPORT": ("codebase/main/ipc/ipcHandlers.js", "local import and export handlers"),
    "CAP-IMPORT-VIDEO": ("codebase/renderer/features/notes/components/UploadAudioView.tsx", "UploadAudioView"),
    "CAP-IPC": ("codebase/main/ipc/ipcHandlers.js", "IPCHandlers"),
    "CAP-KEYRING": ("codebase/main/infrastructure/persistence/localSecretStore.js", "LocalSecretStore"),
    "CAP-KYSELY": ("codebase/main/infrastructure/persistence/database.js", "persistence query boundary"),
    "CAP-LEGAL": ("codebase/LICENSE", "license text"),
    "CAP-MACOS-LINUX": ("codebase/native/helpers", "platform helper source roots"),
    "CAP-MEETING": ("codebase/renderer/features/meetings/meetingRecordingStore.ts", "startRecording"),
    "CAP-MEETING-NOTES": ("codebase/renderer/features/notes/components/NoteEditor.tsx", "NoteEditor"),
    "CAP-MINILM": ("codebase/main/features/search/localEmbeddings.js", "LocalEmbeddings"),
    "CAP-NATIVE": ("codebase/native/helpers", "platform helper source roots"),
    "CAP-NETWORK-POLICY": ("codebase/main/infrastructure/runtime/runtimeNetworkPolicy.js", "installRuntimeNetworkPolicy"),
    "CAP-NOTES": ("codebase/renderer/features/notes/components/NoteEditor.tsx", "NoteEditor"),
    "CAP-NOTE-TEMPLATES": ("codebase/renderer/features/notes/noteTemplates.ts", "local note template contract"),
    "CAP-NOTIFICATIONS": ("codebase/renderer/features/meetings/MeetingNotificationCard.tsx", "MeetingNotificationCard"),
    "CAP-OFFLINE-FIRST-LAUNCH": ("codebase/tests/integration/offlineFirstLaunch.test.js", "offline installed-launch proof"),
    "CAP-PACKAGING": ("codebase/electron-builder.json", "electron-builder configuration"),
    "CAP-PARAKEET": ("codebase/main/features/transcription/parakeetEngine.js", "ParakeetEngine"),
    "CAP-PLAYBACK": ("codebase/renderer/features/notes/components/MeetingRecordingPill.tsx", "MeetingRecordingPill"),
    "CAP-RECOVERY": ("codebase/main/features/meetings/recordingRecovery.js", "recoverInterruptedRecordings"),
    "CAP-RENDERER": ("codebase/renderer/app/AppRouter.jsx", "AppRouter"),
    "CAP-REPOSITORY": ("codebase/package.json", "repository package root"),
    "CAP-PROCESSING-JOBS": ("codebase/main/infrastructure/runtime/localJobQueue.js", "LocalJobQueue"),
    "CAP-SEARCH-EXACT": ("codebase/main/infrastructure/persistence/database.js", "DatabaseManager.searchLocal"),
    "CAP-SEARCH-SEMANTIC": ("codebase/main/features/search/vectorIndex.js", "vectorIndex.search"),
    "CAP-SEGMENTS": ("codebase/main/infrastructure/persistence/database.js", "transcript segment persistence"),
    "CAP-SHERPA-ONNX": ("codebase/main/features/meetings/diarization.js", "DiarizationManager"),
    "CAP-SNIPPETS": ("codebase/renderer/features/snippets/SnippetsView.tsx", "SnippetsView"),
    "CAP-TAGS": ("codebase/main/infrastructure/persistence/database.js", "DatabaseManager.getTags"),
    "CAP-TESTING": ("codebase/tests", "test roots"),
    "CAP-TRANSCRIPT-EDIT": ("codebase/main/infrastructure/persistence/database.js", "updateTranscriptSegment"),
    "CAP-TRANSCRIPT-HISTORY": ("codebase/main/infrastructure/persistence/database.js", "transcript history persistence"),
    "CAP-TRANSCRIPTION": ("codebase/main/features/transcription/whisper.js", "WhisperManager"),
    "CAP-WINDOWS-INSTALLER": ("codebase/electron-builder.json", "Windows installer targets"),
}


SYMBOL_OVERRIDES: dict[tuple[str, str], str] = {
    ("CAP-AEC", "codebase/main/features/meetings/meetingAecManager.js"): "MeetingAecManager",
    ("CAP-AEC", "codebase/main/features/meetings/meetingEchoLeakDetector.js"): "MeetingEchoLeakDetector",
    ("CAP-AEC", "codebase/main/ipc/ipcHandlers.js"): "startMeetingAec",
    ("CAP-AEC", "codebase/main/index.js"): "meetingAecManager",
    ("CAP-SEARCH-EXACT", "codebase/main/infrastructure/persistence/database.js"): "searchLocal",
    ("CAP-SEARCH-EXACT", "codebase/main/ipc/ipcHandlers.js"): "db-search-notes",
    ("CAP-SEARCH-EXACT", "codebase/preload/index.js"): "searchNotes",
    ("CAP-SEARCH-EXACT", "codebase/renderer/shared/types/electron.ts"): "searchNotes",
    ("CAP-SEARCH-EXACT", "codebase/renderer/features/search/SearchView.tsx"): "SearchView",
    ("CAP-SEARCH-SEMANTIC", "codebase/main/features/search/localEmbeddings.js"): "LocalEmbeddings",
    ("CAP-SEARCH-SEMANTIC", "codebase/main/features/search/qdrantManager.js"): "QdrantManager",
    ("CAP-SEARCH-SEMANTIC", "codebase/main/features/search/vectorIndex.js"): "search",
    ("CAP-NOTES", "codebase/main/features/notes/markdownMirror.js"): "MarkdownMirror",
    ("CAP-NOTES", "codebase/main/infrastructure/persistence/database.js"): "saveNote",
    ("CAP-NOTES", "codebase/main/ipc/ipcHandlers.js"): "db-save-note",
    ("CAP-NOTES", "codebase/preload/index.js"): "saveNote",
    ("CAP-NOTES", "codebase/renderer/features/notes/noteStore.ts"): "initializeNotes",
    ("CAP-NOTES", "codebase/renderer/features/notes/useFolderManagement.ts"): "useFolderManagement",
    ("CAP-NOTES", "codebase/renderer/features/notes/useNoteDragAndDrop.ts"): "useNoteDragAndDrop",
    ("CAP-NOTES", "codebase/renderer/features/notes/components/AddNotesToFolderDialog.tsx"): "AddNotesToFolderDialog",
    ("CAP-NOTES", "codebase/renderer/features/notes/components/MeetingRecordingPill.tsx"): "MeetingRecordingPill",
    ("CAP-NOTES", "codebase/renderer/features/notes/components/MeetingTranscriptView.tsx"): "MeetingTranscriptView",
    ("CAP-NOTES", "codebase/renderer/features/notes/components/NoteEditor.tsx"): "NoteEditor",
    ("CAP-NOTES", "codebase/renderer/features/notes/components/RichTextEditor.tsx"): "RichTextEditor",
    ("CAP-MINILM", "codebase/main/features/search/localEmbeddings.js"): "LocalEmbeddings",
}


VENDOR_OR_GENERATED_MARKERS = ("/node_modules/", "/build-output/", "/dist/", "/release/", "/coverage/", "/.cache/")


def reviewed_paths(capability_id: str, candidates: Iterable[str], root: Path) -> list[str]:
    """Return only reviewed, real current paths for one capability."""
    if capability_id in REMOVAL_CAPS:
        return []
    if capability_id in EXACT_LOCATIONS:
        raw = EXACT_LOCATIONS[capability_id]
    else:
        prefixes = tuple(prefix for domain in CAPABILITY_DOMAINS.get(capability_id, ()) for prefix in DOMAIN_PREFIXES[domain])
        raw = [path for path in candidates if path in SHARED_BOUNDARY_PATHS or any(path.startswith(prefix) for prefix in prefixes)]
    result: list[str] = []
    for path in raw:
        normalized = path.replace("\\", "/")
        probe = "/" + normalized.lower()
        if any(marker in probe for marker in VENDOR_OR_GENERATED_MARKERS):
            continue
        if normalized.startswith("codebase/") and (root / normalized).exists() and normalized not in result:
            result.append(normalized)
    return result


def owner_for(capability_id: str, fallback: str) -> str:
    return CAPABILITY_OWNERS.get(capability_id, fallback)


def target_for(capability_id: str, current_paths: list[str], declared_targets: Iterable[str], name: str) -> tuple[str, str]:
    if capability_id in REMOVAL_CAPS:
        return "ABSENT_FROM_ACTIVE_PRODUCT", f"absence::{capability_id.lower()}"
    if capability_id in TARGET_OVERRIDES:
        return TARGET_OVERRIDES[capability_id]
    if current_paths:
        return current_paths[0], f"owned::{capability_id.lower()}"
    for path in declared_targets:
        normalized = str(path).split("::", 1)[0].replace("\\", "/")
        probe = "/" + normalized.lower()
        if normalized.startswith(("codebase/", "Graphify/", ".git")) and not any(marker in probe for marker in VENDOR_OR_GENERATED_MARKERS):
            return normalized, f"owned::{capability_id.lower()}"
    return f"codebase/planned/{capability_id.removeprefix('CAP-').lower()}.js", f"planned::{name.lower().replace(' ', '-')}"
