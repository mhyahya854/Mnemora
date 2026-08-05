const { contextBridge, ipcRenderer, webUtils } = require("electron");

/**
 * Helper to register an IPC listener and return a cleanup function.
 * Ensures renderer code can easily remove listeners to avoid leaks.
 */
const registerListener = (channel, handlerFactory) => {
  return (callback) => {
    if (typeof callback !== "function") {
      return () => {};
    }

    const listener =
      typeof handlerFactory === "function"
        ? handlerFactory(callback)
        : (event, ...args) => callback(event, ...args);

    ipcRenderer.on(channel, listener);
    return () => {
      ipcRenderer.removeListener(channel, listener);
    };
  };
};

contextBridge.exposeInMainWorld("electronAPI", {
  pasteText: (text, options) => ipcRenderer.invoke("paste-text", text, options),
  hideWindow: () => ipcRenderer.invoke("hide-window"),
  showDictationPanel: () => ipcRenderer.invoke("show-dictation-panel"),
  onToggleDictation: registerListener("toggle-dictation", (callback) => () => callback()),
  onStartDictation: registerListener("start-dictation", (callback) => () => callback()),
  onStopDictation: registerListener("stop-dictation", (callback) => () => callback()),

  // Database functions
  saveTranscription: (text, rawText, options) =>
    ipcRenderer.invoke("db-save-transcription", text, rawText, options),
  getTranscriptions: (limit, options) =>
    ipcRenderer.invoke("db-get-transcriptions", limit, options),
  clearTranscriptions: () => ipcRenderer.invoke("db-clear-transcriptions"),
  deleteTranscription: (id) => ipcRenderer.invoke("db-delete-transcription", id),

  // Audio storage functions
  saveTranscriptionAudio: (id, audioBuffer, metadata) =>
    ipcRenderer.invoke("save-transcription-audio", id, audioBuffer, metadata),
  getAudioPath: (id) => ipcRenderer.invoke("get-audio-path", id),
  showAudioInFolder: (id) => ipcRenderer.invoke("show-audio-in-folder", id),
  getAudioBuffer: (id) => ipcRenderer.invoke("get-audio-buffer", id),
  deleteTranscriptionAudio: (id) => ipcRenderer.invoke("delete-transcription-audio", id),
  getAudioStorageUsage: () => ipcRenderer.invoke("get-audio-storage-usage"),
  deleteAllAudio: () => ipcRenderer.invoke("delete-all-audio"),
  retryTranscription: (id, settings) => ipcRenderer.invoke("retry-transcription", id, settings),
  updateTranscriptionText: (id, text, rawText) =>
    ipcRenderer.invoke("update-transcription-text", id, text, rawText),
  getTranscriptionById: (id) => ipcRenderer.invoke("get-transcription-by-id", id),

  // Dictionary functions
  getDictionary: () => ipcRenderer.invoke("db-get-dictionary"),
  setDictionary: (words) => ipcRenderer.invoke("db-set-dictionary", words),
  onDictionaryUpdated: (callback) => {
    const listener = (_event, words) => callback?.(words);
    ipcRenderer.on("dictionary-updated", listener);
    return () => ipcRenderer.removeListener("dictionary-updated", listener);
  },
  getSnippets: () => ipcRenderer.invoke("db-get-snippets"),
  setSnippets: (snippets) => ipcRenderer.invoke("db-set-snippets", snippets),
  onSnippetsUpdated: (callback) => {
    const listener = (_event, snippets) => callback?.(snippets);
    ipcRenderer.on("snippets-updated", listener);
    return () => ipcRenderer.removeListener("snippets-updated", listener);
  },
  setAutoLearnEnabled: (enabled) => ipcRenderer.send("auto-learn-changed", enabled),
  onCorrectionsLearned: (callback) => {
    const listener = (_event, words) => callback?.(words);
    ipcRenderer.on("corrections-learned", listener);
    return () => ipcRenderer.removeListener("corrections-learned", listener);
  },
  undoLearnedCorrections: (words) => ipcRenderer.invoke("undo-learned-corrections", words),

  // Note functions
  saveNote: (title, content, noteType, sourceFile, audioDuration, folderId) =>
    ipcRenderer.invoke(
      "db-save-note",
      title,
      content,
      noteType,
      sourceFile,
      audioDuration,
      folderId
    ),
  getNote: (id) => ipcRenderer.invoke("db-get-note", id),
  getNotes: (noteType, limit, folderId) =>
    ipcRenderer.invoke("db-get-notes", noteType, limit, folderId),
  updateNote: (id, updates) => ipcRenderer.invoke("db-update-note", id, updates),
  deleteNote: (id) => ipcRenderer.invoke("db-delete-note", id),
  exportNote: (noteId, format) => ipcRenderer.invoke("export-note", noteId, format),
  exportTranscript: (noteId, format) => ipcRenderer.invoke("export-transcript", noteId, format),
  exportDictionary: (words) => ipcRenderer.invoke("export-dictionary", words),
  createLocalBackup: (options) => ipcRenderer.invoke("create-local-backup", options),
  previewLocalBackup: (sourcePath) => ipcRenderer.invoke("preview-local-backup", sourcePath),
  restoreLocalBackup: (options) => ipcRenderer.invoke("restore-local-backup", options),
  searchNotes: (query, limit) => ipcRenderer.invoke("db-search-notes", query, limit),
  semanticSearchNotes: (query, limit) =>
    ipcRenderer.invoke("db-semantic-search-notes", query, limit),
  semanticReindexAll: () => ipcRenderer.invoke("db-semantic-reindex-all"),
  onSemanticReindexProgress: (callback) => {
    const listener = (_event, data) => callback?.(data);
    ipcRenderer.on("semantic-reindex-progress", listener);
    return () => ipcRenderer.removeListener("semantic-reindex-progress", listener);
  },
  // Folder functions
  getFolders: () => ipcRenderer.invoke("db-get-folders"),
  createFolder: (name) => ipcRenderer.invoke("db-create-folder", name),
  deleteFolder: (id) => ipcRenderer.invoke("db-delete-folder", id),
  renameFolder: (id, name) => ipcRenderer.invoke("db-rename-folder", id, name),
  getFolderNoteCounts: () => ipcRenderer.invoke("db-get-folder-note-counts"),

  // Note files (markdown mirror) functions
  noteFilesSetEnabled: (enabled, customPath, options) =>
    ipcRenderer.invoke("note-files-set-enabled", enabled, customPath, options),
  noteFilesSetPath: (path) => ipcRenderer.invoke("note-files-set-path", path),
  noteFilesRebuild: () => ipcRenderer.invoke("note-files-rebuild"),
  noteFilesGetDefaultPath: () => ipcRenderer.invoke("note-files-get-default-path"),
  noteFilesPickFolder: () => ipcRenderer.invoke("note-files-pick-folder"),
  showNoteFile: (noteId) => ipcRenderer.invoke("show-note-file", noteId),
  showFolderInExplorer: (folderName) => ipcRenderer.invoke("show-folder-in-explorer", folderName),

  // Audio file operations
  selectAudioFile: () => ipcRenderer.invoke("select-audio-file"),
  getFileSize: (filePath) => ipcRenderer.invoke("get-file-size", filePath),
  transcribeAudioFile: (filePath, options) =>
    ipcRenderer.invoke("transcribe-audio-file", filePath, options),
  getPathForFile: (file) => webUtils.getPathForFile(file),

  onNoteAdded: (callback) => {
    const listener = (_event, note) => callback?.(note);
    ipcRenderer.on("note-added", listener);
    return () => ipcRenderer.removeListener("note-added", listener);
  },
  onNoteUpdated: (callback) => {
    const listener = (_event, note) => callback?.(note);
    ipcRenderer.on("note-updated", listener);
    return () => ipcRenderer.removeListener("note-updated", listener);
  },
  onNoteDeleted: (callback) => {
    const listener = (_event, data) => callback?.(data);
    ipcRenderer.on("note-deleted", listener);
    return () => ipcRenderer.removeListener("note-deleted", listener);
  },

  onTranscriptionAdded: (callback) => {
    const listener = (_event, transcription) => callback?.(transcription);
    ipcRenderer.on("transcription-added", listener);
    return () => ipcRenderer.removeListener("transcription-added", listener);
  },
  onTranscriptionDeleted: (callback) => {
    const listener = (_event, data) => callback?.(data);
    ipcRenderer.on("transcription-deleted", listener);
    return () => ipcRenderer.removeListener("transcription-deleted", listener);
  },
  onTranscriptionsCleared: (callback) => {
    const listener = (_event, data) => callback?.(data);
    ipcRenderer.on("transcriptions-cleared", listener);
    return () => ipcRenderer.removeListener("transcriptions-cleared", listener);
  },
  onTranscriptionUpdated: (callback) => {
    const listener = (_event, transcription) => callback?.(transcription);
    ipcRenderer.on("transcription-updated", listener);
    return () => ipcRenderer.removeListener("transcription-updated", listener);
  },

  // Clipboard functions
  checkAccessibilityPermission: (silent) =>
    ipcRenderer.invoke("check-accessibility-permission", silent),
  promptAccessibilityPermission: () => ipcRenderer.invoke("prompt-accessibility-permission"),
  readClipboard: () => ipcRenderer.invoke("read-clipboard"),
  writeClipboard: (text) => ipcRenderer.invoke("write-clipboard", text),
  checkPasteTools: () => ipcRenderer.invoke("check-paste-tools"),

  // Local Whisper functions (whisper.cpp)
  transcribeLocalWhisper: (audioBlob, options) =>
    ipcRenderer.invoke("transcribe-local-whisper", audioBlob, options),
  checkWhisperInstallation: () => ipcRenderer.invoke("check-whisper-installation"),
  importWhisperModel: (modelName) => ipcRenderer.invoke("import-whisper-model", modelName),
  onWhisperImportProgress: registerListener("whisper-import-progress"),
  checkModelStatus: (modelName) => ipcRenderer.invoke("check-model-status", modelName),
  listWhisperModels: () => ipcRenderer.invoke("list-whisper-models"),
  deleteWhisperModel: (modelName) => ipcRenderer.invoke("delete-whisper-model", modelName),
  deleteAllWhisperModels: () => ipcRenderer.invoke("delete-all-whisper-models"),
  cancelWhisperImport: () => ipcRenderer.invoke("cancel-whisper-import"),
  checkFFmpegAvailability: () => ipcRenderer.invoke("check-ffmpeg-availability"),
  getAudioDiagnostics: () => ipcRenderer.invoke("get-audio-diagnostics"),

  // Whisper server functions (faster repeated transcriptions)
  whisperServerStart: (modelName) => ipcRenderer.invoke("whisper-server-start", modelName),
  whisperServerStop: () => ipcRenderer.invoke("whisper-server-stop"),
  whisperServerStatus: () => ipcRenderer.invoke("whisper-server-status"),

  // CUDA GPU acceleration
  listGpus: () => ipcRenderer.invoke("list-gpus"),
  setGpuDeviceIndex: (purpose, uuid) => ipcRenderer.invoke("set-gpu-device-index", purpose, uuid),
  getGpuDeviceIndex: (purpose) => ipcRenderer.invoke("get-gpu-device-index", purpose),
  detectGpu: () => ipcRenderer.invoke("detect-gpu"),
  getCudaWhisperStatus: () => ipcRenderer.invoke("get-cuda-whisper-status"),
  importCudaWhisperBinary: () => ipcRenderer.invoke("import-cuda-whisper-binary"),
  cancelCudaWhisperImport: () => ipcRenderer.invoke("cancel-cuda-whisper-import"),
  deleteCudaWhisperBinary: () => ipcRenderer.invoke("delete-cuda-whisper-binary"),
  onCudaImportProgress: registerListener(
    "cuda-import-progress",
    (callback) => (_event, data) => callback(data)
  ),
  onCudaFallbackNotification: registerListener(
    "cuda-fallback-notification",
    (callback) => () => callback()
  ),

  // Diarization (speaker identification) functions
  importDiarizationModels: () => ipcRenderer.invoke("import-diarization-models"),
  getDiarizationModelStatus: () => ipcRenderer.invoke("get-diarization-model-status"),
  deleteDiarizationModels: () => ipcRenderer.invoke("delete-diarization-models"),
  cancelDiarizationImport: () => ipcRenderer.invoke("cancel-diarization-import"),
  onDiarizationImportProgress: registerListener(
    "diarization-import-progress",
    (callback) => (_event, data) => callback(data)
  ),
  onMeetingDiarizationComplete: registerListener(
    "meeting-diarization-complete",
    (callback) => (_event, data) => callback(data)
  ),

  // Speaker name mapping
  getSpeakerMappings: (noteId) => ipcRenderer.invoke("get-speaker-mappings", noteId),
  setSpeakerMapping: (noteId, speakerId, displayName, email, profileId) =>
    ipcRenderer.invoke("set-speaker-mapping", noteId, speakerId, displayName, email, profileId),
  removeSpeakerMapping: (noteId, speakerId) =>
    ipcRenderer.invoke("remove-speaker-mapping", noteId, speakerId),
  getSpeakerProfiles: () => ipcRenderer.invoke("get-speaker-profiles"),
  attachSpeakerEmail: (profileId, email) =>
    ipcRenderer.invoke("attach-speaker-email", profileId, email),
  saveNoteSpeakerEmbeddings: (noteId, embeddings) =>
    ipcRenderer.invoke("save-note-speaker-embeddings", noteId, embeddings),

  // Window control functions
  windowMinimize: () => ipcRenderer.invoke("window-minimize"),
  windowMaximize: () => ipcRenderer.invoke("window-maximize"),
  windowClose: () => ipcRenderer.invoke("window-close"),
  windowIsMaximized: () => ipcRenderer.invoke("window-is-maximized"),
  snapToMeetingMode: () => ipcRenderer.invoke("snap-to-meeting-mode"),
  restoreFromMeetingMode: () => ipcRenderer.invoke("restore-from-meeting-mode"),
  getPlatform: () => process.platform,

  // Cleanup function
  cleanupApp: () => ipcRenderer.invoke("cleanup-app"),
  updateHotkey: (hotkey) => ipcRenderer.invoke("update-hotkey", hotkey),
  setHotkeyListeningMode: (enabled) => ipcRenderer.invoke("set-hotkey-listening-mode", enabled),
  getHotkeyModeInfo: () => ipcRenderer.invoke("get-hotkey-mode-info"),
  getHyprlandConfigStatus: () => ipcRenderer.invoke("get-hyprland-config-status"),
  startWindowDrag: () => ipcRenderer.invoke("start-window-drag"),
  stopWindowDrag: () => ipcRenderer.invoke("stop-window-drag"),
  setMainWindowInteractivity: (interactive) =>
    ipcRenderer.invoke("set-main-window-interactivity", interactive),
  setNotificationInteractivity: (interactive) =>
    ipcRenderer.invoke("set-notification-interactivity", interactive),
  resizeMainWindow: (sizeKey) => ipcRenderer.invoke("resize-main-window", sizeKey),

  getAppVersion: () => ipcRenderer.invoke("get-app-version"),
  getPostMigrationState: () => ipcRenderer.invoke("get-post-migration-state"),
  markBundleMigrated: () => ipcRenderer.invoke("mark-bundle-migrated"),
  markBundleMigrationDismissed: () => ipcRenderer.invoke("mark-bundle-migration-dismissed"),

  // Audio event listeners
  onNoAudioDetected: registerListener("no-audio-detected"),
  onCancelHotkeyPressed: registerListener("cancel-hotkey-pressed", (cb) => () => cb()),
  registerCancelHotkey: (key) => ipcRenderer.invoke("register-cancel-hotkey", key),
  unregisterCancelHotkey: () => ipcRenderer.invoke("unregister-cancel-hotkey"),

  getUiLanguage: () => ipcRenderer.invoke("get-ui-language"),
  saveUiLanguage: (language) => ipcRenderer.invoke("save-ui-language", language),
  setUiLanguage: (language) => ipcRenderer.invoke("set-ui-language", language),

  // Dictation key persistence (file-based for reliable startup)
  getDictationKey: () => ipcRenderer.invoke("get-dictation-key"),
  getActiveDictationKey: () => ipcRenderer.invoke("get-active-dictation-key"),
  getEffectiveDefaultHotkey: () => ipcRenderer.invoke("get-effective-default-hotkey"),
  saveDictationKey: (key) => ipcRenderer.invoke("save-dictation-key", key),

  // Activation mode persistence (file-based for reliable startup)
  getActivationMode: () => ipcRenderer.invoke("get-activation-mode"),
  saveActivationMode: (mode) => ipcRenderer.invoke("save-activation-mode", mode),

  saveAllKeysToEnv: () => ipcRenderer.invoke("save-all-keys-to-env"),
  syncStartupPreferences: (prefs) => ipcRenderer.invoke("sync-startup-preferences", prefs),



  getLogLevel: () => ipcRenderer.invoke("get-log-level"),
  log: (entry) => ipcRenderer.invoke("app-log", entry),

  // ydotool status check
  getYdotoolStatus: () => ipcRenderer.invoke("get-ydotool-status"),

  // Debug logging management
  getDebugState: () => ipcRenderer.invoke("get-debug-state"),
  setDebugLogging: (enabled) => ipcRenderer.invoke("set-debug-logging", enabled),
  openLogsFolder: () => ipcRenderer.invoke("open-logs-folder"),

  // System settings helpers for microphone/audio permissions
  requestMicrophoneAccess: () => ipcRenderer.invoke("request-microphone-access"),
  checkMicrophoneAccess: () => ipcRenderer.invoke("check-microphone-access"),
  checkSystemAudioAccess: () => ipcRenderer.invoke("check-system-audio-access"),
  requestSystemAudioAccess: () => ipcRenderer.invoke("request-system-audio-access"),
  openMicrophoneSettings: () => ipcRenderer.invoke("open-microphone-settings"),
  openSoundInputSettings: () => ipcRenderer.invoke("open-sound-input-settings"),
  openAccessibilitySettings: () => ipcRenderer.invoke("open-accessibility-settings"),
  openSystemAudioSettings: () => ipcRenderer.invoke("open-system-audio-settings"),
  toggleMediaPlayback: () => ipcRenderer.invoke("toggle-media-playback"),
  pauseMediaPlayback: () => ipcRenderer.invoke("pause-media-playback"),
  resumeMediaPlayback: () => ipcRenderer.invoke("resume-media-playback"),
  openMnemoraModelsFolder: () => ipcRenderer.invoke("open-mnemora-models-folder"),

  // Local Whisper meeting transcription (dual-channel capture)
  meetingTranscriptionPrepare: (options) =>
    ipcRenderer.invoke("meeting-transcription-prepare", options),
  meetingTranscriptionStart: (options) =>
    ipcRenderer.invoke("meeting-transcription-start", options),
  meetingTranscriptionSend: (buffer, source) =>
    ipcRenderer.send("meeting-transcription-send", buffer, source),
  meetingTranscriptionStop: () => ipcRenderer.invoke("meeting-transcription-stop"),
  meetingTranscriptionCancel: () => ipcRenderer.invoke("meeting-transcription-cancel"),
  onMeetingTranscriptionSegment: registerListener(
    "meeting-transcription-segment",
    (callback) => (_event, data) => callback(data)
  ),
  onMeetingSpeakerIdentified: registerListener(
    "meeting-speaker-identified",
    (callback) => (_event, data) => callback(data)
  ),
  onMeetingSpeakersMerged: registerListener(
    "meeting-speakers-merged",
    (callback) => (_event, data) => callback(data)
  ),
  onMeetingTranscriptionError: registerListener(
    "meeting-transcription-error",
    (callback) => (_event, data) => callback(data)
  ),

  // Globe key listener for hotkey capture (macOS only)
  onGlobeKeyPressed: (callback) => {
    const listener = () => callback?.();
    ipcRenderer.on("globe-key-pressed", listener);
    return () => ipcRenderer.removeListener("globe-key-pressed", listener);
  },
  onGlobeKeyReleased: (callback) => {
    const listener = () => callback?.();
    ipcRenderer.on("globe-key-released", listener);
    return () => ipcRenderer.removeListener("globe-key-released", listener);
  },

  // Hotkey registration events (for notifying user when hotkey fails)
  onHotkeyFallbackUsed: (callback) => {
    const listener = (_event, data) => callback?.(data);
    ipcRenderer.on("hotkey-fallback-used", listener);
    return () => ipcRenderer.removeListener("hotkey-fallback-used", listener);
  },
  onHotkeyRegistrationFailed: (callback) => {
    const listener = (_event, data) => callback?.(data);
    ipcRenderer.on("hotkey-registration-failed", listener);
    return () => ipcRenderer.removeListener("hotkey-registration-failed", listener);
  },
  onSettingUpdated: (callback) => {
    const listener = (_event, data) => callback?.(data);
    ipcRenderer.on("setting-updated", listener);
    return () => ipcRenderer.removeListener("setting-updated", listener);
  },
  onDictationKeyActive: (callback) => {
    const listener = (_event, key) => callback?.(key);
    ipcRenderer.on("dictation-key-active", listener);
    return () => ipcRenderer.removeListener("dictation-key-active", listener);
  },
  onWindowsPushToTalkUnavailable: registerListener("windows-ptt-unavailable"),
  onLinuxPttPermissionDenied: registerListener(
    "linux-ptt-permission-denied",
    (callback) => () => callback()
  ),

  // Settings shortcut (Cmd+, / Ctrl+,)
  onShowSettings: registerListener("show-settings", (callback) => () => callback()),

  // Accessibility permission events (macOS)
  onAccessibilityMissing: (callback) => {
    const listener = () => callback?.();
    ipcRenderer.on("accessibility-missing", listener);
    return () => ipcRenderer.removeListener("accessibility-missing", listener);
  },
  checkAccessibilityTrusted: () => ipcRenderer.invoke("check-accessibility-trusted"),

  // Notify main process of activation mode changes (for Windows Push-to-Talk)
  notifyActivationModeChanged: (mode) => ipcRenderer.send("activation-mode-changed", mode),
  notifyHotkeyChanged: (hotkey) => ipcRenderer.send("hotkey-changed", hotkey),
  registerMeetingHotkey: (hotkey) => ipcRenderer.invoke("register-meeting-hotkey", hotkey),

  // Floating icon auto-hide
  notifyFloatingIconAutoHideChanged: (enabled) =>
    ipcRenderer.send("floating-icon-auto-hide-changed", enabled),
  onFloatingIconAutoHideChanged: registerListener(
    "floating-icon-auto-hide-changed",
    (callback) => (_event, enabled) => callback(enabled)
  ),

  // Panel start position
  notifyPanelStartPositionChanged: (position) =>
    ipcRenderer.send("panel-start-position-changed", position),

  // Start minimized
  notifyStartMinimizedChanged: (enabled) => ipcRenderer.send("start-minimized-changed", enabled),

  // Auto-start management
  getAutoStartEnabled: () => ipcRenderer.invoke("get-auto-start-enabled"),
  setAutoStartEnabled: (enabled) => ipcRenderer.invoke("set-auto-start-enabled", enabled),


  onPreviewText: registerListener("preview-text", (callback) => (_event, text) => callback(text)),
  onPreviewAppend: registerListener(
    "preview-append",
    (callback) => (_event, text) => callback(text)
  ),
  onPreviewHold: registerListener(
    "preview-hold",
    (callback) => (_event, payload) => callback(payload)
  ),
  onPreviewResult: registerListener(
    "preview-result",
    (callback) => (_event, payload) => callback(payload)
  ),
  onPreviewHide: registerListener("preview-hide", (callback) => () => callback()),
  startDictationPreview: (opts) => ipcRenderer.invoke("start-dictation-preview", opts),
  stopDictationPreview: (opts) => ipcRenderer.invoke("stop-dictation-preview", opts),
  dismissDictationPreview: () => ipcRenderer.invoke("dismiss-dictation-preview"),
  completeDictationPreview: (payload) => ipcRenderer.invoke("complete-dictation-preview", payload),
  hideDictationPreview: () => ipcRenderer.invoke("hide-dictation-preview"),
  resizeTranscriptionPreviewWindow: (width, height) =>
    ipcRenderer.invoke("resize-transcription-preview-window", width, height),
  sendDictationPreviewAudio: (data) => ipcRenderer.send("dictation-preview-audio", data),
  acquireRecordingLock: (pipeline) => ipcRenderer.invoke("acquire-recording-lock", pipeline),
  releaseRecordingLock: (pipeline) => ipcRenderer.invoke("release-recording-lock", pipeline),



  // Contacts
  searchContacts: (query) => ipcRenderer.invoke("search-contacts", query),
  upsertContact: (contact) => ipcRenderer.invoke("upsert-contact", contact),
  getMD5Hash: (text) => ipcRenderer.invoke("get-md5-hash", text),



  // Meeting detection
  meetingDetectionGetPreferences: () => ipcRenderer.invoke("meeting-detection-get-preferences"),
  meetingDetectionSetPreferences: (prefs) =>
    ipcRenderer.invoke("meeting-detection-set-preferences", prefs),
  syncNotificationPreferences: (prefs) =>
    ipcRenderer.invoke("sync-notification-preferences", prefs),
  setSpeakerDiarizationEnabled: (enabled) =>
    ipcRenderer.invoke("meeting-set-speaker-diarization-enabled", { enabled }),
  setMeetingSessionSpeakerConfig: (config) =>
    ipcRenderer.invoke("meeting-set-session-speaker-config", config),
  getWhisperVadConfig: () => ipcRenderer.invoke("whisper-vad-get-config"),
  setWhisperVadConfig: (config) => ipcRenderer.invoke("whisper-vad-set-config", config),
  onMeetingDetected: registerListener(
    "meeting-detected",
    (callback) => (_event, data) => callback(data)
  ),
  onMeetingDetectedStartRecording: registerListener(
    "meeting-detected-start-recording",
    (callback) => (_event, data) => callback(data)
  ),
  onMeetingNotificationData: registerListener(
    "meeting-notification-data",
    (callback) => (_event, data) => callback(data)
  ),
  getMeetingNotificationData: () => ipcRenderer.invoke("get-meeting-notification-data"),
  meetingNotificationReady: () => ipcRenderer.invoke("meeting-notification-ready"),
  meetingNotificationRespond: (detectionId, action) =>
    ipcRenderer.invoke("meeting-notification-respond", detectionId, action),

  getPendingMeetingNoteNavigation: () => ipcRenderer.invoke("get-pending-meeting-note-navigation"),
  onMeetingNoteNavigationPending: registerListener(
    "meeting-note-navigation-pending",
    (callback) => () => callback()
  ),
  onNavigateToNote: registerListener(
    "navigate-to-note",
    (callback) => (_event, data) => callback(data)
  ),

});
