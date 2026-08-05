# Graph Report - C:\Users\mhyah\Downloads\Code\Mnemora  (2026-07-28)

## Corpus Check
- Second source-authoritative scan excludes installed dependencies and generated build-output symbols; both remain in the complete inventory.

## Summary
- 3641 nodes · 6837 edges · 212 communities (147 shown, 65 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 177 edges (avg confidence: 0.64)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Features Dictation
- Scripts Build
- Features Meetings
- Main Platform
- Native Helpers
- Features Dictation
- Scripts Build
- Features Renderer
- Renderer Shared
- Features Meetings
- Persistence Database Js
- Renderer Features
- Features Settings
- Scripts Downloads
- Native Helpers
- Autoprefixer Concurrently
- Features Meetings
- Native Helpers
- Renderer Shared
- Features Renderer
- Tests Unit
- Main Index Js
- Features Notes
- Keep Decision Classification Framework
- Features Dictation
- Features Settings
- Main Platform
- Features Transcription
- Features Notes
- Scripts Packaging
- Overrides Fast Xml Builder
- Main Desktop
- Main Infrastructure
- Ipc Ipchandlers Js
- Main Platform
- Renderer Tsconfig Json
- Native Helpers
- Ipc Ipchandlers Js
- Features Transcription
- Features Meetings
- Features Search
- Features Transcription
- Native Helpers
- Native Helpers
- Features Dictation
- Features Search
- Features Transcription
- Scripts Build
- Scripts Downloads
- Native Helpers
- Features Dictation
- Main Workers
- Features Onboarding
- Persistence Localdatadatabase Test Js
- Features Dictation
- Native Meeting Aec Helper
- Main Platform
- Features Meetings
- Features Transcription
- Main Infrastructure
- Scripts Downloads
- Main Desktop
- Scripts Build
- Features Dictation
- Persistence Localbackup Js
- Scripts Build
- Scripts Build
- Scripts Build
- Scripts Build
- Scripts Build
- Scripts Build
- Features Meetings
- Features Meetings
- Native Helpers
- Native Meeting Aec Helper
- Features Notes
- Features Meetings
- Native Helpers
- Renderer Components Json
- Scripts Build
- Scripts Build
- Main Desktop
- Main Desktop
- Features Meetings
- Features Notes
- Features Transcription
- Main Infrastructure
- Main Infrastructure
- Renderer Vite Config Mjs
- Scripts Build
- Features Search
- Main Platform
- Main Platform
- Native Meeting Aec Helper
- Features Dictation
- Scripts Build
- Scripts Build
- Scripts Build
- Tests Unit
- Features Meetings
- Main Platform
- Main Platform
- Renderer Shared
- Scripts Downloads
- Tests Unit
- Main Desktop
- Main Desktop
- Scripts Verification
- Features Notes
- Main Desktop
- Features Dictation
- Features Meetings
- Features Meetings
- Features Meetings
- Features Transcription
- Persistence Localbackup Test Js
- Name Author
- Main Desktop
- Features Dictation
- Features Search
- Persistence Audiostorage Js
- Persistence Postmigrationdetector Js
- Scripts Downloads
- Persistence Snippetsdatabase Test Js
- Native Helpers
- Features Meetings
- Main Index Js
- Main Platform
- Main Platform
- Features Snippets
- Renderer Shared
- Scripts Development
- Scripts Downloads
- Scripts Verification
- Tests Unit
- Native Meeting Aec Helper
- Better Sqlite3 Homebridge Dbus
- Features Search
- Main Infrastructure
- Native Helpers
- Renderer App
- Features Search
- Persistence Datamigration Js
- Main Platform
- Renderer Eslint Config Js
- Tests Unit
- Tests Unit
- Features Meetings
- Features Search
- Features Transcription
- Features Transcription
- Main Platform
- Renderer Shared
- Renderer Vite Env D
- Scripts Packaging
- Features Dictation
- Main Infrastructure
- Extends Win
- Features Transcription
- Tests Unit
- Features Onboarding
- Native Meeting Aec Helper
- Renderer Index Html
- Class Variance Authority
- Clsx Runtime
- Dotenv Runtime
- Ffmpeg Static
- I18next Runtime
- Lucide React
- Onnxruntime Node
- Ps List
- Qdrant Js Client Rest
- Radix Ui React Accordion
- Radix Ui React Dialog
- Radix Ui React Dropdown
- Radix Ui React Label
- Radix Ui React Popover
- Radix Ui React Progress
- Radix Ui React Select
- Radix Ui React Slot
- Radix Ui React Tabs
- React Runtime
- React Dom
- React I18next
- React Markdown
- Tailwind Merge
- Tiptap Extension Placeholder
- Tiptap Extension Task Item
- Tiptap Markdown
- Tiptap React
- Tiptap Starter Kit
- Tw Animate Css
- Unbzip2 Stream
- Unzipper Runtime
- Zustand Runtime
- After Install Sh Script
- After Remove Sh Script
- Renderer Assets

## God Nodes (most connected - your core abstractions)
1. `DatabaseManager` - 98 edges
2. `path` - 77 edges
3. `fs` - 74 edges
4. `react` - 73 edges
5. `scripts` - 69 edges
6. `cn()` - 65 edges
7. `WindowManager` - 62 edges
8. `child process` - 46 edges
9. `HotkeyManager` - 43 edges
10. `ClipboardManager` - 42 edges

## Surprising Connections (you probably didn't know these)
- `partitionPendingMicFinals()` --indirect_call--> `entry()`  [INFERRED]
  codebase/main/features/meetings/meetingMicHoldback.js → codebase/tests/unit/meetings/meetingMicHoldback.test.js
- `cleanupStaleImports()` --indirect_call--> `entry()`  [INFERRED]
  codebase/main/features/transcription/downloadUtils.js → codebase/tests/unit/meetings/meetingMicHoldback.test.js
- `extractArchive()` --indirect_call--> `entry()`  [INFERRED]
  codebase/main/features/transcription/downloadUtils.js → codebase/tests/unit/meetings/meetingMicHoldback.test.js
- `validateHotkey()` --indirect_call--> `entry()`  [INFERRED]
  codebase/renderer/features/dictation/hotkeyValidator.ts → codebase/tests/unit/meetings/meetingMicHoldback.test.js
- `SpeakerBadge()` --calls--> `cn()`  [EXTRACTED]
  codebase/renderer/features/notes/components/MeetingTranscriptView.tsx → codebase/renderer/shared/ui/utils.ts

## Import Cycles
- 1-file cycle: `codebase/eslint.config.js -> codebase/eslint.config.js`
- 1-file cycle: `codebase/renderer/eslint.config.js -> codebase/renderer/eslint.config.js`
- 1-file cycle: `codebase/main/infrastructure/runtime/i18nMain.js -> codebase/main/infrastructure/runtime/i18nMain.js`
- 1-file cycle: `codebase/main/desktop/tray.js -> codebase/main/desktop/tray.js`
- 1-file cycle: `codebase/main/features/dictation/clipboard.js -> codebase/main/features/dictation/clipboard.js`
- 1-file cycle: `codebase/main/features/meetings/audioActivityDetector.js -> codebase/main/features/meetings/audioActivityDetector.js`
- 1-file cycle: `codebase/main/features/search/qdrantManager.js -> codebase/main/features/search/qdrantManager.js`
- 1-file cycle: `codebase/main/features/transcription/downloadUtils.js -> codebase/main/features/transcription/downloadUtils.js`
- 1-file cycle: `codebase/main/features/transcription/whisper.js -> codebase/main/features/transcription/whisper.js`
- 1-file cycle: `codebase/main/infrastructure/persistence/database.js -> codebase/main/infrastructure/persistence/database.js`
- 1-file cycle: `codebase/main/infrastructure/runtime/serverUtils.js -> codebase/main/infrastructure/runtime/serverUtils.js`
- 1-file cycle: `codebase/scripts/lib/download-utils.js -> codebase/scripts/lib/download-utils.js`
- 1-file cycle: `codebase/scripts/packaging/afterPack.js -> codebase/scripts/packaging/afterPack.js`
- 1-file cycle: `codebase/main/features/meetings/liveSpeakerIdentifier.js -> codebase/main/features/meetings/liveSpeakerIdentifier.js`
- 1-file cycle: `codebase/main/features/dictation/hotkeyManager.js -> codebase/main/features/dictation/hotkeyManager.js`
- 1-file cycle: `codebase/main/features/search/vectorIndex.js -> codebase/main/features/search/vectorIndex.js`
- 1-file cycle: `codebase/main/features/transcription/whisperVadConfig.js -> codebase/main/features/transcription/whisperVadConfig.js`
- 1-file cycle: `codebase/main/infrastructure/runtime/environment.js -> codebase/main/infrastructure/runtime/environment.js`
- 1-file cycle: `codebase/main/infrastructure/persistence/localBackup.js -> codebase/main/infrastructure/persistence/localBackup.js`
- 1-file cycle: `codebase/native/helpers/linux/linux-text-monitor.py -> codebase/native/helpers/linux/linux-text-monitor.py`

## Hyperedges (group relationships)
- **Authoritative Mnemora Master Plan** — graphify_master_plan_01_everything_we_are_keeping_everything_we_are_keeping, graphify_master_plan_02_everything_we_are_deleting_everything_we_are_deleting, graphify_master_plan_03_how_we_will_keep_delete_and_replace_how_we_will_keep_delete_and_replace [EXTRACTED 1.00]
- **Local-Only Product Transformation** — graphify_master_plan_01_everything_we_are_keeping_local_only_runtime_boundary, graphify_master_plan_02_everything_we_are_deleting_updates_runtime_downloads_and_external_network, graphify_master_plan_03_how_we_will_keep_delete_and_replace_runtime_offline_enforcement [INFERRED 0.95]
- **Evidence-Gated Release Control** — graphify_master_plan_01_everything_we_are_keeping_preservation_first_acceptance, graphify_master_plan_02_everything_we_are_deleting_evidence_based_deletion_acceptance, graphify_master_plan_03_how_we_will_keep_delete_and_replace_strict_release_conjunction [INFERRED 0.95]

## Communities (212 total, 65 thin omitted)

### Community 0 - "Features Dictation"
Cohesion: 0.05
Nodes (66): AccordionPlatform, HotkeyGuidanceAccordion(), HotkeyGuidanceAccordionProps, PLATFORM_MAP, CODE_TO_KEY, HotkeyInput(), HotkeyInputProps, HotkeyInputVariant (+58 more)

### Community 1 - "Scripts Build"
Cohesion: 0.03
Nodes (69): scripts, build, build:linux, build:linux:appimage, build:linux:deb, build:linux:rpm, build:linux:tar, build:mac (+61 more)

### Community 2 - "Features Meetings"
Cohesion: 0.06
Nodes (62): applySpeakerIdentification(), assignProvisionalSpeaker(), buildTranscriptText(), cleanup(), createAudioPipeline(), detachFromOutputDevice(), ensureRendererSystemAudioCapture(), flushAndDisconnectProcessor() (+54 more)

### Community 3 - "Main Platform"
Cohesion: 0.04
Nodes (52): fs, path, ARCH_CPU_TYPE, compareVersions(), debugLogger, fs, path, { spawn } (+44 more)

### Community 4 - "Native Helpers"
Cohesion: 0.06
Nodes (51): Any, AudioBufferList, AudioDeviceID, AudioDeviceIOProcID, AudioObjectID, AudioToolbox, AVAudioConverter, AVAudioFormat (+43 more)

### Community 5 - "Features Dictation"
Cohesion: 0.08
Nodes (21): { clipboard, systemPreferences }, ClipboardManager, debugLogger, fs, getLinuxDesktopEnv(), getLinuxSessionInfo(), isGnomeDesktop(), isKdeDesktop() (+13 more)

### Community 6 - "Scripts Build"
Cohesion: 0.06
Nodes (57): archIndex, buildCMake(), buildDir, buildDirect(), {
  buildManifest,
  computeManifestHash,
  ensureThirdPartySources,
  writeCmakeManifest,
}, builtBinary, configureCMake(), crypto (+49 more)

### Community 7 - "Features Renderer"
Cohesion: 0.06
Nodes (49): parseTranscriptSegments(), Participant, resolveExpectedSpeakerCount(), serializeTranscriptSegments(), formatNoteDate(), formatShortDate(), MeetingViewMode, NoteEditor() (+41 more)

### Community 8 - "Renderer Shared"
Cohesion: 0.05
Nodes (44): ControlPanelSidebar(), ControlPanelView, items, Props, c users mhyah downloads code mnemora codebase renderer assets icon png, DictationWidget(), DictationWidgetProps, MarkdownRenderer() (+36 more)

### Community 9 - "Features Meetings"
Cohesion: 0.07
Nodes (23): appendFloat32(), clampMaxSpeakers(), cloneFloat32Array(), concatFloat32Arrays(), debugLogger, DEFAULT_VAD_STATE_SHAPE, { downsample24kTo16k }, fs (+15 more)

### Community 11 - "Renderer Features"
Cohesion: 0.06
Nodes (32): AppRouter(), ControlPanel, MainApp(), OnboardingFlow, TitleBarProps, WindowControls(), root, UseClipboardProps (+24 more)

### Community 12 - "Features Settings"
Cohesion: 0.07
Nodes (36): c users mhyah downloads code mnemora codebase renderer app index css, App(), c users mhyah downloads code mnemora codebase renderer features dictation historyview clear, formatWhen(), HistoryView(), Props, c users mhyah downloads code mnemora codebase renderer features dictation historyview remove, c users mhyah downloads code mnemora codebase renderer features dictation historyview retry (+28 more)

### Community 13 - "Scripts Downloads"
Cohesion: 0.08
Nodes (40): BIN_DIR, { downloadFile, extractZip }, fs, main(), NIRCMD_PATH, path, BIN_DIR, {
  downloadFile,
  extractArchive,
  fetchLatestRelease,
  setExecutable,
} (+32 more)

### Community 14 - "Native Helpers"
Cohesion: 0.10
Nodes (42): FILE, gboolean, gpointer, check_pipewire_available(), cleanup_pipewire(), close_audio_pipe(), emit_event(), enqueue_audio_bytes() (+34 more)

### Community 15 - "Autoprefixer Concurrently"
Cohesion: 0.05
Nodes (43): autoprefixer, devDependencies, autoprefixer, concurrently, cross-env, electron, electron-builder, @electron/notarize (+35 more)

### Community 16 - "Features Meetings"
Cohesion: 0.10
Nodes (15): AudioActivityDetector, execAsync, compareExpectedToActual(), FIXTURE_DIR, fs, { isDeepStrictEqual }, loadFixtures(), main() (+7 more)

### Community 17 - "Native Helpers"
Cohesion: 0.09
Nodes (40): activate_window(), gboolean, gpointer, check_parent_terminal(), detect_terminal_atspi(), emit(), emit_key(), get_active_window() (+32 more)

### Community 18 - "Renderer Shared"
Cohesion: 0.06
Nodes (34): Filter, filters, Props, Result, SearchView(), normalizeSection(), OfflineBridge, Props (+26 more)

### Community 19 - "Features Renderer"
Cohesion: 0.09
Nodes (30): useSystemAudioPermission(), AddNotesToFolderDialog(), AddNotesToFolderDialogProps, groupNotesByDate(), PostMigrationOnboarding(), PostMigrationOnboardingProps, describeMicError(), getPlatform() (+22 more)

### Community 20 - "Tests Unit"
Cohesion: 0.06
Nodes (29): assert, test, assert, base, test, assert, test, assert (+21 more)

### Community 21 - "Main Index Js"
Cohesion: 0.06
Nodes (37): APP_CHANNEL, {
  app,
  desktopCapturer,
  globalShortcut,
  BrowserWindow,
  dialog,
  ipcMain,
  session,
  systemPreferences,
}, AudioActivityDetector, AudioTapManager, cleanupOrphanedLinuxRestoreToken(), ClipboardManager, DatabaseManager, DiarizationManager (+29 more)

### Community 22 - "Features Notes"
Cohesion: 0.14
Nodes (32): ControlPanel(), PersonalNotesView, platform, Props, SettingsPage, UploadAudioView, MeetingRecordingMount(), getMicAnalyser() (+24 more)

### Community 23 - "Keep Decision Classification Framework"
Cohesion: 0.09
Nodes (38): Keep Decision Classification Framework, Diarization, Structured Transcripts, and Notes, Everything We Are Keeping, Exact and Semantic Search, Legal Identity and Core Desktop Stack, Local Dictation, Transcription, and Model Handling, Local-Only Runtime Boundary, Meeting Audio, Recording, and Recovery (+30 more)

### Community 25 - "Features Settings"
Cohesion: 0.10
Nodes (24): ActivationMode, ActivationModeSelectorProps, OPTIONS, formatDate(), MeetingsView(), Props, canManageSystemAudioInApp(), FinishStepProps (+16 more)

### Community 26 - "Main Platform"
Cohesion: 0.11
Nodes (15): buildManagedBindsContent(), debugLogger, ELECTRON_TO_HYPRLAND_KEY, ELECTRON_TO_HYPRLAND_MOD, { execFileSync }, fs, getBindsFilePath(), getDBus() (+7 more)

### Community 27 - "Features Transcription"
Cohesion: 0.08
Nodes (31): { app }, buildWhisperServerArgs(), clamp(), { convertToWav }, createThreadResolution(), debugLogger, EventEmitter, fs (+23 more)

### Community 28 - "Features Notes"
Cohesion: 0.08
Nodes (28): EditContactEmail(), EditContactEmailProps, getEmailPrefix(), getSpeakerColorClass(), isValidEmail(), MeetingTranscriptView(), MeetingTranscriptViewProps, NameSelectorList() (+20 more)

### Community 29 - "Scripts Packaging"
Cohesion: 0.10
Nodes (28): buildLinuxWrapperScript(), { Arch }, { buildLinuxWrapperScript }, collectFiles(), crypto, default(), { execFileSync }, fs (+20 more)

### Community 30 - "Overrides Fast Xml Builder"
Cohesion: 0.06
Nodes (32): overrides, fast-xml-builder, fast-xml-parser, ip-address, markdown-it, @tiptap/extension-blockquote, @tiptap/extension-bold, @tiptap/extension-bubble-menu (+24 more)

### Community 35 - "Renderer Tsconfig Json"
Cohesion: 0.07
Nodes (27): compilerOptions, allowJs, checkJs, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+19 more)

### Community 36 - "Native Helpers"
Cohesion: 0.10
Nodes (23): atspi, AtspiAccessible, AtspiText, BSTR, base64_encode(), find_focused(), main(), print_text_output() (+15 more)

### Community 37 - "Ipc Ipchandlers Js"
Cohesion: 0.08
Nodes (24): downsample24kTo16k(), pcm16ToWav(), {
  applyConfirmedSpeaker,
  applySuggestedSpeaker,
  canAutoRelabelSpeaker,
  isSpeakerLocked,
}, { applySmartSpacing }, AudioStorageManager, crypto, debugLogger, {
  DEFAULT_EXPECTED_SPEAKER_COUNT,
  MAX_SPEAKER_COUNT,
} (+16 more)

### Community 38 - "Features Transcription"
Cohesion: 0.12
Nodes (23): assertSafeTarEntry(), copyFileWithProgress(), debugLogger, extractArchive(), fs, importLocalFile(), inspectTarArchive(), isSafeArchivePath() (+15 more)

### Community 39 - "Features Meetings"
Cohesion: 0.08
Nodes (22): debugLogger, EventEmitter, fs, MACOS_AX_SCRIPT_BY_PID(), path, { spawn, execFile }, debugLogger, EventEmitter (+14 more)

### Community 40 - "Features Search"
Cohesion: 0.11
Nodes (13): chunkText(), debugLogger, documentText(), instance, localEmbeddings, pointId(), { QdrantClient }, transcriptText() (+5 more)

### Community 42 - "Native Helpers"
Cohesion: 0.15
Nodes (24): add_device(), emit_key_down(), emit_key_up(), handle_key_event(), is_alt_held(), is_ctrl_held(), is_key_held(), is_keyboard_device() (+16 more)

### Community 43 - "Native Helpers"
Cohesion: 0.14
Nodes (24): audioclient, audioclientactivationparams, activate_process_loopback(), BOOL, DWORD, console_ctrl_handler(), create_completion_handler(), emit_event() (+16 more)

### Community 44 - "Features Dictation"
Cohesion: 0.15
Nodes (18): debugLogger, EventEmitter, FALLBACK_HOTKEYS, { globalShortcut, BrowserWindow }, GNOME_NATIVE_SLOTS, GnomeShortcutManager, HyprlandShortcutManager, { i18nMain } (+10 more)

### Community 45 - "Features Search"
Cohesion: 0.10
Nodes (20): CACHE_ROOT, debugLogger, {
  findAvailablePort,
  resolveBinaryPath,
  gracefulStopProcess,
}, fs, http, LEGACY_STORAGE_DIR, os, path (+12 more)

### Community 46 - "Features Transcription"
Cohesion: 0.12
Nodes (15): cleanupStaleImports(), findFile(), findFiles(), { app }, COMPANION_PATTERNS, {
  createImportSignal,
  cleanupStaleImports,
  extractArchive,
  findFile,
  findFiles,
  importLocalFile,
}, debugLogger, fs (+7 more)

### Community 47 - "Scripts Build"
Cohesion: 0.09
Nodes (16): atspiAvailable, attemptCompile(), compileArgs, crypto, cSource, fs, gioAvailable, hashFile (+8 more)

### Community 48 - "Scripts Downloads"
Cohesion: 0.11
Nodes (21): { downloadFile, parseArgs }, { execFileSync }, extractTarBz2(), fs, getModelDir(), main(), os, path (+13 more)

### Community 49 - "Native Helpers"
Cohesion: 0.13
Nodes (20): AXObserver, AXUIElement, emit(), emitMouseEvent(), mouseButtonName(), Bool, Int, String (+12 more)

### Community 50 - "Features Dictation"
Cohesion: 0.21
Nodes (3): AudioManager, useAudioRecording(), getSettings()

### Community 51 - "Main Workers"
Cohesion: 0.13
Nodes (21): buildTextTokenizer(), computeFbank(), dispatch(), FBANK_FRAME_LENGTH, FBANK_FRAME_SHIFT, fs, getMelFilterbank(), handlers (+13 more)

### Community 52 - "Features Onboarding"
Cohesion: 0.12
Nodes (16): DictionaryView(), parseWords(), OptionCard(), OptionCardProps, USE_CASE_IDS, USE_CASE_OPTIONS, UseCaseId, UseCaseOption (+8 more)

### Community 53 - "Persistence Localdatadatabase Test Js"
Cohesion: 0.10
Nodes (18): { app }, Database, debugLogger, fs, localBackup, path, assert, BetterSqlite (+10 more)

### Community 54 - "Features Dictation"
Cohesion: 0.15
Nodes (13): matchesDictionaryPrompt(), normalize(), shouldSaveDiscardedRecording(), createLocalSpeechGateState(), getLocalSpeechGateDecision(), recordLocalSpeechWindow(), reacquireIfDead(), waitForTrackReady() (+5 more)

### Community 55 - "Native Meeting Aec Helper"
Cohesion: 0.16
Nodes (19): algorithm, array, audio processing, builtin audio processing builder, DrainCleanedOutput, Flush, isReady, ProcessMicChunk (+11 more)

### Community 56 - "Main Platform"
Cohesion: 0.16
Nodes (7): debugLogger, ELECTRON_TO_GNOME_KEY_MAP, { execFileSync }, getDBus(), getSlotConfig(), GnomeShortcutManager, SLOT_CONFIG

### Community 57 - "Features Meetings"
Cohesion: 0.18
Nodes (4): DiarizationManager, createImportSignal(), getSafeTempDir(), resolveBinaryPath()

### Community 58 - "Features Transcription"
Cohesion: 0.11
Nodes (16): checkDiskSpace(), validateFileSize(), c users mhyah downloads code mnemora codebase main features transcription modelregistrydata json, {
  createImportSignal,
  validateFileSize,
  cleanupStaleImports,
  checkDiskSpace,
  importLocalFile,
}, debugLogger, fs, { getModelsDirForService }, getWhisperModelConfig() (+8 more)

### Community 60 - "Scripts Downloads"
Cohesion: 0.13
Nodes (19): archiveName(), BIN_DIR, binaryName(), {
  cleanupFiles,
  downloadFile,
  extractArchive,
  fetchLatestRelease,
  parseArgs,
  setExecutable,
}, downloadTarget(), fs, main(), path (+11 more)

### Community 61 - "Main Desktop"
Cohesion: 0.13
Nodes (16): DEV_SERVER_PORT, CONTROL_PANEL_CONFIG, MAIN_WINDOW_CONFIG, NOTIFICATION_WINDOW_CONFIG, path, TRANSCRIPTION_PREVIEW_CONFIG, TRANSCRIPTION_PREVIEW_SIZE_LIMITS, WINDOW_SIZES (+8 more)

### Community 62 - "Scripts Build"
Cohesion: 0.10
Nodes (17): os, fs, os, path, actoolLookup, { execFileSync, spawnSync }, fs, ICON_BUNDLE (+9 more)

### Community 64 - "Persistence Localbackup Js"
Cohesion: 0.23
Nodes (19): createBackup(), crypto, Database, fs, inspectDatabase(), isInside(), listFiles(), openBackup() (+11 more)

### Community 65 - "Scripts Build"
Cohesion: 0.11
Nodes (17): ARCH_CPU_TYPE, ARCH_TO_TARGET, archIndex, attemptCompile(), compileArgs, crypto, fs, hashFile (+9 more)

### Community 66 - "Scripts Build"
Cohesion: 0.11
Nodes (17): ARCH_CPU_TYPE, ARCH_TO_TARGET, archIndex, attemptCompile(), compileArgs, crypto, fs, hashFile (+9 more)

### Community 67 - "Scripts Build"
Cohesion: 0.11
Nodes (17): ARCH_CPU_TYPE, ARCH_TO_TARGET, archIndex, attemptCompile(), compileArgs, crypto, fs, hashFile (+9 more)

### Community 68 - "Scripts Build"
Cohesion: 0.11
Nodes (17): ARCH_CPU_TYPE, ARCH_TO_TARGET, archIndex, attemptCompile(), compileArgs, crypto, fs, hashFile (+9 more)

### Community 69 - "Scripts Build"
Cohesion: 0.11
Nodes (17): ARCH_CPU_TYPE, ARCH_TO_TARGET, archIndex, attemptCompile(), compileArgs, crypto, fs, hashFile (+9 more)

### Community 70 - "Scripts Build"
Cohesion: 0.11
Nodes (17): ARCH_CPU_TYPE, ARCH_TO_TARGET, archIndex, attemptCompile(), compileArgs, crypto, fs, hashFile (+9 more)

### Community 72 - "Features Meetings"
Cohesion: 0.19
Nodes (4): computeRms(), MeetingEchoLeakDetector, pcm16BufferToFloat32(), entry()

### Community 73 - "Native Helpers"
Cohesion: 0.32
Nodes (18): AreRequiredModifiersPressed(), BOOL, DWORD, ConsoleHandler(), IsAltVk(), IsCtrlVk(), IsRequiredModifierEvent(), IsShiftVk() (+10 more)

### Community 74 - "Native Meeting Aec Helper"
Cohesion: 0.13
Nodes (18): AecProcessor, apm_, cleaned_output_, input_frame_samples_, mic_downsampler_, mic_upsampler_, pending_mic_input_, pending_system_input_ (+10 more)

### Community 75 - "Features Notes"
Cohesion: 0.13
Nodes (14): stopRecording(), computeBarHeight(), c users mhyah downloads code mnemora codebase renderer features notes components meetingrecordingpill handlestop, isControlPanelWindow(), MeetingRecordingPill(), MeetingRecordingPillProps, truncateTitle(), LanguageOption (+6 more)

### Community 77 - "Native Helpers"
Cohesion: 0.22
Nodes (16): BOOL, DWORD, GetExeName(), IsTerminalClass(), IsTerminalExe(), main(), ReleaseModifiers(), RestoreModifiers() (+8 more)

### Community 78 - "Renderer Components Json"
Cohesion: 0.11
Nodes (17): aliases, components, hooks, lib, ui, utils, iconLibrary, rsc (+9 more)

### Community 79 - "Scripts Build"
Cohesion: 0.20
Nodes (17): attemptCompile(), crypto, cSource, ensureDir(), fs, getGioFlags(), getPkgConfigFlags(), hashFile (+9 more)

### Community 80 - "Scripts Build"
Cohesion: 0.19
Nodes (17): attemptCompile(), crypto, cSource, ensureDir(), fs, getPkgConfigFlags(), hashFile, isBinaryUpToDate() (+9 more)

### Community 82 - "Main Desktop"
Cohesion: 0.14
Nodes (13): { i18nMain }, debugLogger, { i18nMain }, { Tray, Menu, nativeImage, app }, enTranslation, i18next, i18nMain, SUPPORTED_UI_LANGUAGES (+5 more)

### Community 83 - "Features Meetings"
Cohesion: 0.12
Nodes (15): { applyConfirmedSpeaker }, { convertToWav }, { createImportSignal, importLocalFile }, debugLogger, dedupeMicAgainstSystem(), fs, { getModelsDirForService }, { getSafeTempDir } (+7 more)

### Community 85 - "Features Transcription"
Cohesion: 0.24
Nodes (3): getThreadSignature(), shouldFallbackToDefaultThreads(), WhisperServerManager

### Community 86 - "Main Infrastructure"
Cohesion: 0.18
Nodes (15): { app }, clear(), fs, path, pidDir(), pidPath(), readAll(), write() (+7 more)

### Community 87 - "Main Infrastructure"
Cohesion: 0.19
Nodes (10): hasExactLoopbackAuthority(), installRuntimeNetworkPolicy(), isAllowedRuntimeUrl(), LOCAL_SCHEMES, LOOPBACK_HOSTS, NETWORK_SCHEMES, normalizeHostname(), assert (+2 more)

### Community 88 - "Renderer Vite Config Mjs"
Cohesion: 0.12
Nodes (12): __dirname, assert, fs, path, root, test, node fs, node path (+4 more)

### Community 89 - "Scripts Build"
Cohesion: 0.13
Nodes (13): attemptCompile(), compileArgs, crypto, cSource, fs, hashFile, log(), outputBinary (+5 more)

### Community 91 - "Main Platform"
Cohesion: 0.26
Nodes (14): commandExists(), { dialog }, ensureYdotool(), fs, getLogger(), getYdotoolStatus(), isNixOS(), isUinputAccessible() (+6 more)

### Community 92 - "Main Platform"
Cohesion: 0.19
Nodes (5): debugLogger, getDBus(), KDEShortcutManager, QT_KEYS, QT_MODIFIERS

### Community 93 - "Native Meeting Aec Helper"
Cohesion: 0.25
Nodes (14): BytesToSamples(), string, vector, EmitJsonLine(), main(), ParseSampleRate(), ReadExact(), ReadUint32Le() (+6 more)

### Community 94 - "Features Dictation"
Cohesion: 0.23
Nodes (12): getAudioContext(), isEnabled(), playCue(), playStartCue(), playStopCue(), resumeContextIfNeeded(), scheduleTone(), START_NOTES (+4 more)

### Community 95 - "Scripts Build"
Cohesion: 0.21
Nodes (14): cSource, ensureDir(), fs, isBinaryUpToDate(), log(), main(), outputBinary, outputDir (+6 more)

### Community 96 - "Scripts Build"
Cohesion: 0.21
Nodes (14): cSource, ensureDir(), fs, isBinaryUpToDate(), log(), main(), outputBinary, outputDir (+6 more)

### Community 97 - "Scripts Build"
Cohesion: 0.21
Nodes (14): cSource, ensureDir(), fs, isBinaryUpToDate(), log(), main(), outputBinary, outputDir (+6 more)

### Community 98 - "Tests Unit"
Cohesion: 0.13
Nodes (12): assert, childProcess, ClipboardManager, clipboardModulePath, emptyImage, { EventEmitter }, fakeClipboard, Module (+4 more)

### Community 99 - "Features Meetings"
Cohesion: 0.29
Nodes (8): applyConfirmedSpeaker(), applyProvisionalSpeaker(), applySpeakerUpdate(), applySuggestedSpeaker(), canAutoRelabelSpeaker(), canonicalizeSpeakerStatus(), isSpeakerLocked(), SPEAKER_STATUS

### Community 102 - "Renderer Shared"
Cohesion: 0.21
Nodes (12): DEFAULT_INFO, HotkeyModeInfo, HyprlandConfigStatus, useHotkeyModeInfo(), log(), LOG_LEVELS, logger, LogLevel (+4 more)

### Community 103 - "Scripts Downloads"
Cohesion: 0.21
Nodes (13): BIN_DIR, BINARIES, downloadBinary(), { downloadFile, findBinaryInDir, parseArgs, setExecutable }, { execFileSync }, extractTarBz2(), findLibrariesInDir(), fs (+5 more)

### Community 104 - "Tests Unit"
Cohesion: 0.14
Nodes (5): assert, FakeStream, FakeTrack, noopLogger, test

### Community 107 - "Scripts Verification"
Cohesion: 0.19
Nodes (12): crypto, binDir, collectAssets(), crypto, fs, hashFile(), manifestPath, path (+4 more)

### Community 108 - "Features Notes"
Cohesion: 0.21
Nodes (11): fileFromPath(), formatSize(), ImportBridge, Props, SelectedFile, State, supportedExtensions, c users mhyah downloads code mnemora codebase renderer features notes components uploadaudioview transcribe (+3 more)

### Community 109 - "Main Desktop"
Cohesion: 0.17
Nodes (9): { screen }, keywords, { contextBridge, ipcRenderer, webUtils }, desktop-app, dictation, electron, speech-to-text, whisper (+1 more)

### Community 110 - "Features Dictation"
Cohesion: 0.27
Nodes (10): applyAppend(), applyPrepend(), applySmartSpacing(), LEADING_PUNCTUATION, OPENING_CHARS, append(), { applySmartSpacing }, assert (+2 more)

### Community 113 - "Features Meetings"
Cohesion: 0.32
Nodes (10): countCommonTokens(), longestCommonTokenSubsequence(), LOW_SIGNAL_TOKENS, normalizeTranscriptText(), toMeaningfulTokens(), transcriptsLooselyOverlap(), transcriptsOverlap(), assert (+2 more)

### Community 114 - "Features Transcription"
Cohesion: 0.21
Nodes (9): convertToWav(), debugLogger, fs, getFFmpegPath(), isWavFormat(), path, { spawn }, splitAudioFile() (+1 more)

### Community 115 - "Persistence Localbackup Test Js"
Cohesion: 0.17
Nodes (11): tar, assert, DatabaseManager, fs, Module, os, path, tar (+3 more)

### Community 116 - "Name Author"
Cohesion: 0.17
Nodes (11): author, email, name, description, engines, node, license, main (+3 more)

### Community 118 - "Features Dictation"
Cohesion: 0.44
Nodes (10): extractMetadata(), formatJson(), formatMd(), formatSrt(), formatSrtTimestamp(), formatTimestamp(), formatTxt(), { i18nMain } (+2 more)

### Community 119 - "Features Search"
Cohesion: 0.18
Nodes (8): { app, utilityProcess, MessageChannelMain }, debugLogger, instance, path, RESPAWN_BACKOFF_MS, WORKER_SCRIPT, WorkerCrashedError, WorkerOverloadedError

### Community 122 - "Persistence Postmigrationdetector Js"
Cohesion: 0.29
Nodes (10): { app }, DB_FILENAMES, fs, getDismissedPath(), getSentinelPath(), isReturningFromOldBundle(), isWithinDismissBackoff(), markBundleMigrated() (+2 more)

### Community 123 - "Scripts Downloads"
Cohesion: 0.22
Nodes (10): checksum(), crypto, { downloadFile }, fs, isValid(), main(), MODEL, outputDir (+2 more)

### Community 124 - "Persistence Snippetsdatabase Test Js"
Cohesion: 0.18
Nodes (9): assert, DatabaseManager, fs, Module, os, path, test, userDataDir (+1 more)

### Community 125 - "Native Helpers"
Cohesion: 0.22
Nodes (9): base64, _emit_text(), _find_focused(), main(), Recursively find the focused accessible element., gi, gi repository, sys (+1 more)

### Community 127 - "Main Index Js"
Cohesion: 0.22
Nodes (8): initializeDeferredManagers(), isLiveWindow(), performSyncTeardown(), registerSidecars(), startApp(), debugLogger, register(), sidecars

### Community 130 - "Features Snippets"
Cohesion: 0.29
Nodes (8): buildMatcher(), expandSnippets(), foldCapitalIDot(), getDictionaryHintWords(), SnippetMatcher, assert, { expandSnippets }, test

### Community 131 - "Renderer Shared"
Cohesion: 0.27
Nodes (8): Toast(), ToastProvider(), ToastState, ToastViewport(), variantConfig, ToastContext, ToastContextType, ToastProps

### Community 132 - "Scripts Development"
Cohesion: 0.20
Nodes (8): appArgs, appDir, args, child, chromiumFlags, electronPath, path, { spawn }

### Community 133 - "Scripts Downloads"
Cohesion: 0.27
Nodes (9): BIN_DIR, BINARIES, downloadBinary(), {
  downloadFile,
  extractArchive,
  fetchLatestRelease,
  findBinaryInDir,
  parseArgs,
  setExecutable,
  cleanupFiles,
}, fs, getDownloadUrl(), getRelease(), main() (+1 more)

### Community 134 - "Scripts Verification"
Cohesion: 0.20
Nodes (5): fs, languages, LOCALES_DIR, NAMESPACES, path

### Community 135 - "Tests Unit"
Cohesion: 0.20
Nodes (4): assert, HotkeyManager, registered, test

### Community 136 - "Native Meeting Aec Helper"
Cohesion: 0.22
Nodes (8): aec dump factory, AecDump, AecDumpFactory::Create(), FILE, unique_ptr, FileWrapper, string_view, TaskQueueBase

### Community 137 - "Better Sqlite3 Homebridge Dbus"
Cohesion: 0.22
Nodes (9): better-sqlite3, dependencies, better-sqlite3, @homebridge/dbus-native, tar, @tiptap/extension-task-list, @homebridge/dbus-native, tar (+1 more)

### Community 140 - "Main Infrastructure"
Cohesion: 0.22
Nodes (8): { app }, envWriteQueue, fs, fsPromises, { normalizeUiLanguage }, path, PERSISTED_KEYS, node fs promises

### Community 141 - "Native Helpers"
Cohesion: 0.28
Nodes (9): CH_ActivateCompleted(), CH_AddRef(), CH_QueryInterface(), CH_Release(), HRESULT, IActivateAudioInterfaceAsyncOperation, IActivateAudioInterfaceCompletionHandler, REFIID (+1 more)

### Community 142 - "Renderer App"
Cohesion: 0.22
Nodes (3): ErrorBoundary, ErrorBoundaryProps, ErrorBoundaryState

### Community 145 - "Persistence Datamigration Js"
Cohesion: 0.29
Nodes (6): fs, migrateUserData(), path, assert, { migrateUserData }, test

### Community 147 - "Renderer Eslint Config Js"
Cohesion: 0.33
Nodes (5): globals, eslint js, eslint plugin react hooks, eslint plugin react refresh, typescript eslint

### Community 148 - "Tests Unit"
Cohesion: 0.43
Nodes (5): parseHotkeyList(), serializeHotkeyList(), assert, { parseHotkeyList, serializeHotkeyList }, test

### Community 149 - "Tests Unit"
Cohesion: 0.38
Nodes (5): isWithinRetractWindow(), partitionPendingMicFinals(), assert, {
  partitionPendingMicFinals,
  isWithinRetractWindow,
}, test

### Community 150 - "Features Meetings"
Cohesion: 0.29
Nodes (6): debugLogger, fs, { getModelsDirForService }, instance, onnxWorkerClient, path

### Community 151 - "Features Search"
Cohesion: 0.29
Nodes (6): debugLogger, fs, { getCacheRoot }, instance, onnxWorkerClient, path

### Community 152 - "Features Transcription"
Cohesion: 0.33
Nodes (6): { app }, fs, getCacheRoot(), getModelsDirForService(), os, path

### Community 153 - "Features Transcription"
Cohesion: 0.38
Nodes (5): { app }, detectVulkanGpu(), parseDeviceName(), VENDOR_NAMES, VULKAN_VENDOR_IDS

### Community 154 - "Main Platform"
Cohesion: 0.29
Nodes (6): ARCH_CPU_TYPE, debugLogger, EventEmitter, fs, path, { spawn }

### Community 155 - "Renderer Shared"
Cohesion: 0.33
Nodes (3): RETRY_CONFIG, RetryOptions, withRetry()

### Community 156 - "Renderer Vite Env D"
Cohesion: 0.29
Nodes (6): CSSProperties, *.gif, *.jpg, *.png, react, *.svg

### Community 157 - "Scripts Packaging"
Cohesion: 0.29
Nodes (5): ffmpegBinary, fs, path, root, { spawnSync }

### Community 159 - "Features Dictation"
Cohesion: 0.67
Nodes (5): editDistance(), extractCorrections(), findEditedRegion(), findSubstitutions(), tokenize()

### Community 161 - "Extends Win"
Cohesion: 0.40
Nodes (4): extends, win, azureSignOptions, electron-builder.json

### Community 164 - "Features Transcription"
Cohesion: 0.40
Nodes (3): ColorScheme, MODEL_PICKER_COLORS, ModelPickerStyles

### Community 165 - "Tests Unit"
Cohesion: 0.40
Nodes (3): assert, HotkeyManager, test

### Community 171 - "Native Meeting Aec Helper"
Cohesion: 0.67
Nodes (3): Conditional AVX2 Compilation, Generated WebRTC Source Manifest, Meeting AEC Helper Native Build

### Community 172 - "Renderer Index Html"
Cohesion: 0.67
Nodes (3): Local Renderer Assets, Mnemora Renderer Entrypoint, Renderer Module Bootstrap

## Knowledge Gaps
- **1273 isolated node(s):** `extends`, `electron-builder.json`, `azureSignOptions`, `DEV_SERVER_PORT`, `{ screen }` (+1268 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **65 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `path` connect `Main Platform` to `Scripts Development`, `Features Dictation`, `Scripts Build`, `Scripts Downloads`, `Scripts Verification`, `Scripts Downloads`, `Features Meetings`, `Persistence Datamigration Js`, `Main Index Js`, `Features Meetings`, `Features Search`, `Features Transcription`, `Main Platform`, `Features Transcription`, `Main Platform`, `Scripts Packaging`, `Scripts Packaging`, `Ipc Ipchandlers Js`, `Features Transcription`, `Features Meetings`, `Features Search`, `Features Transcription`, `Scripts Build`, `Scripts Downloads`, `Main Workers`, `Persistence Localdatadatabase Test Js`, `Features Transcription`, `Scripts Downloads`, `Main Desktop`, `Scripts Build`, `Scripts Build`, `Scripts Build`, `Scripts Build`, `Scripts Build`, `Scripts Build`, `Scripts Build`, `Scripts Build`, `Scripts Build`, `Main Desktop`, `Features Meetings`, `Main Infrastructure`, `Scripts Build`, `Scripts Build`, `Scripts Build`, `Scripts Build`, `Scripts Downloads`, `Scripts Verification`, `Features Transcription`, `Features Search`, `Persistence Postmigrationdetector Js`, `Scripts Downloads`?**
  _High betweenness centrality (0.129) - this node is a cross-community bridge._
- **Why does `fs` connect `Main Platform` to `Features Dictation`, `Scripts Build`, `Scripts Downloads`, `Scripts Verification`, `Features Meetings`, `Scripts Downloads`, `Features Meetings`, `Persistence Datamigration Js`, `Features Meetings`, `Features Search`, `Features Transcription`, `Main Platform`, `Features Transcription`, `Main Platform`, `Scripts Packaging`, `Scripts Packaging`, `Ipc Ipchandlers Js`, `Features Transcription`, `Features Meetings`, `Features Search`, `Features Transcription`, `Scripts Build`, `Scripts Downloads`, `Main Workers`, `Persistence Localdatadatabase Test Js`, `Features Transcription`, `Scripts Downloads`, `Scripts Build`, `Scripts Build`, `Scripts Build`, `Scripts Build`, `Scripts Build`, `Scripts Build`, `Scripts Build`, `Scripts Build`, `Scripts Build`, `Main Desktop`, `Features Meetings`, `Main Infrastructure`, `Scripts Build`, `Main Platform`, `Scripts Build`, `Scripts Build`, `Scripts Build`, `Scripts Downloads`, `Scripts Verification`, `Features Transcription`, `Persistence Postmigrationdetector Js`, `Scripts Downloads`?**
  _High betweenness centrality (0.126) - this node is a cross-community bridge._
- **Why does `electron` connect `Main Desktop` to `Main Platform`, `Features Dictation`, `Ipc Ipchandlers Js`, `Features Meetings`, `Main Platform`, `Features Dictation`, `Main Infrastructure`, `Features Transcription`, `Main Desktop`, `Main Index Js`, `Persistence Localdatadatabase Test Js`, `Features Search`, `Features Transcription`, `Features Transcription`, `Persistence Postmigrationdetector Js`, `Features Transcription`, `Main Infrastructure`, `Main Desktop`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **What connects `extends`, `electron-builder.json`, `azureSignOptions` to the rest of the system?**
  _1273 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Features Dictation` be split into smaller, more focused modules?**
  _Cohesion score 0.05480277024992472 - nodes in this community are weakly interconnected._
- **Should `Scripts Build` be split into smaller, more focused modules?**
  _Cohesion score 0.028985507246376812 - nodes in this community are weakly interconnected._
- **Should `Features Meetings` be split into smaller, more focused modules?**
  _Cohesion score 0.06189640035118525 - nodes in this community are weakly interconnected._