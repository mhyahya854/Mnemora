# Import and Call Map

Graphify raw edges cover imports, re-exports, calls, references, containment, and semantic relations. TypeScript compiler module resolution and Tarjan SCC evidence are in `IMPORT_CYCLES.json`. This runtime overlay adds dynamic/string-based registrations, processes, environment/configuration, translation, build, and packaging evidence; text search is supporting evidence only.

## Static graph relations

| Relation | Edges |
| --- | --- |
| contains | 2173 |
| calls | 1788 |
| imports_from | 1000 |
| method | 806 |
| imports | 691 |
| references | 285 |
| indirect_call | 151 |
| defines | 19 |
| extends | 16 |
| rationale_for | 10 |
| conceptually_related_to | 10 |
| semantically_similar_to | 5 |
| implements | 3 |
| shares_data_with | 2 |
| loads_asset | 2 |
| inherits | 1 |
| builds_asset_bundle | 1 |

## IPC/runtime contracts

| IPC channel | Handler registrations | Caller/listener references | Main senders | Status |
| --- | --- | --- | --- | --- |
| accessibility-missing |  | codebase/preload/index.js:390 | codebase/main/index.js:764 | MAPPED VALID CHAIN |
| acquire-recording-lock | codebase/main/ipc/ipcHandlers.js:3498 | codebase/preload/index.js:442 |  | MAPPED VALID CHAIN |
| activation-mode-changed | codebase/main/index.js:379, codebase/main/index.js:879 | codebase/preload/index.js:396 |  | MAPPED VALID CHAIN |
| app-log | codebase/main/ipc/ipcHandlers.js:1784 | codebase/preload/index.js:295 |  | MAPPED VALID CHAIN |
| attach-speaker-email | codebase/main/ipc/ipcHandlers.js:3786 | codebase/preload/index.js:237 |  | MAPPED VALID CHAIN |
| auto-learn-changed | codebase/main/ipc/ipcHandlers.js:584 | codebase/preload/index.js:70 |  | MAPPED VALID CHAIN |
| cancel-cuda-whisper-import | codebase/main/ipc/ipcHandlers.js:1354 | codebase/preload/index.js:204 |  | MAPPED VALID CHAIN |
| cancel-diarization-import | codebase/main/ipc/ipcHandlers.js:1418 | codebase/preload/index.js:219 |  | MAPPED VALID CHAIN |
| cancel-whisper-import | codebase/main/ipc/ipcHandlers.js:1238 | codebase/preload/index.js:188 |  | MAPPED VALID CHAIN |
| check-accessibility-permission | codebase/main/ipc/ipcHandlers.js:1085 | codebase/preload/index.js:172 |  | MAPPED VALID CHAIN |
| check-accessibility-trusted | codebase/main/index.js:774 | codebase/preload/index.js:393 |  | MAPPED VALID CHAIN |
| check-ffmpeg-availability | codebase/main/ipc/ipcHandlers.js:1370 | codebase/preload/index.js:189 |  | MAPPED VALID CHAIN |
| check-microphone-access | codebase/main/ipc/ipcHandlers.js:1861 | codebase/preload/index.js:307 |  | MAPPED VALID CHAIN |
| check-model-status | codebase/main/ipc/ipcHandlers.js:1222 | codebase/preload/index.js:184 |  | MAPPED VALID CHAIN |
| check-paste-tools | codebase/main/ipc/ipcHandlers.js:1103 | codebase/preload/index.js:176 |  | MAPPED VALID CHAIN |
| check-system-audio-access | codebase/main/ipc/ipcHandlers.js:1955 | codebase/preload/index.js:308 |  | MAPPED VALID CHAIN |
| check-whisper-installation | codebase/main/ipc/ipcHandlers.js:1189 | codebase/preload/index.js:181 |  | MAPPED VALID CHAIN |
| cleanup-app | codebase/main/ipc/ipcHandlers.js:1422 | codebase/preload/index.js:251 |  | MAPPED VALID CHAIN |
| complete-dictation-preview | codebase/main/ipc/ipcHandlers.js:3306 | codebase/preload/index.js:437 |  | MAPPED VALID CHAIN |
| corrections-learned |  | codebase/preload/index.js:73 | codebase/main/ipc/ipcHandlers.js:381 | MAPPED VALID CHAIN |
| create-local-backup | codebase/main/ipc/ipcHandlers.js:806 | codebase/preload/index.js:97 |  | MAPPED VALID CHAIN |
| db-clear-transcriptions | codebase/main/ipc/ipcHandlers.js:492 | codebase/preload/index.js:38 |  | MAPPED VALID CHAIN |
| db-create-folder | codebase/main/ipc/ipcHandlers.js:755 | codebase/preload/index.js:111 |  | MAPPED VALID CHAIN |
| db-delete-folder | codebase/main/ipc/ipcHandlers.js:769 | codebase/preload/index.js:112 |  | MAPPED VALID CHAIN |
| db-delete-note | codebase/main/ipc/ipcHandlers.js:685 | codebase/preload/index.js:93 |  | MAPPED VALID CHAIN |
| db-delete-transcription | codebase/main/ipc/ipcHandlers.js:505 | codebase/preload/index.js:39 |  | MAPPED VALID CHAIN |
| db-get-dictionary | codebase/main/ipc/ipcHandlers.js:596 | codebase/preload/index.js:56 |  | MAPPED VALID CHAIN |
| db-get-folder-note-counts | codebase/main/ipc/ipcHandlers.js:802 | codebase/preload/index.js:114 |  | MAPPED VALID CHAIN |
| db-get-folders | codebase/main/ipc/ipcHandlers.js:751 | codebase/preload/index.js:110 |  | MAPPED VALID CHAIN |
| db-get-note | codebase/main/ipc/ipcHandlers.js:666 | codebase/preload/index.js:89 |  | MAPPED VALID CHAIN |
| db-get-notes | codebase/main/ipc/ipcHandlers.js:670 | codebase/preload/index.js:91 |  | MAPPED VALID CHAIN |
| db-get-snippets | codebase/main/ipc/ipcHandlers.js:607 | codebase/preload/index.js:63 |  | MAPPED VALID CHAIN |
| db-get-transcriptions | codebase/main/ipc/ipcHandlers.js:488 | codebase/preload/index.js:37 |  | MAPPED VALID CHAIN |
| db-rename-folder | codebase/main/ipc/ipcHandlers.js:787 | codebase/preload/index.js:113 |  | MAPPED VALID CHAIN |
| db-save-note | codebase/main/ipc/ipcHandlers.js:646 | codebase/preload/index.js:80 |  | MAPPED VALID CHAIN |
| db-save-transcription | codebase/main/ipc/ipcHandlers.js:478 | codebase/preload/index.js:35 |  | MAPPED VALID CHAIN |
| db-search-notes | codebase/main/ipc/ipcHandlers.js:689 | codebase/preload/index.js:100 |  | MAPPED VALID CHAIN |
| db-semantic-reindex-all | codebase/main/ipc/ipcHandlers.js:738 | codebase/preload/index.js:103 |  | MAPPED VALID CHAIN |
| db-semantic-search-notes | codebase/main/ipc/ipcHandlers.js:693 | codebase/preload/index.js:102 |  | MAPPED VALID CHAIN |
| db-set-dictionary | codebase/main/ipc/ipcHandlers.js:600 | codebase/preload/index.js:57 |  | MAPPED VALID CHAIN |
| db-set-snippets | codebase/main/ipc/ipcHandlers.js:611 | codebase/preload/index.js:64 |  | MAPPED VALID CHAIN |
| db-update-note | codebase/main/ipc/ipcHandlers.js:674 | codebase/preload/index.js:92 |  | MAPPED VALID CHAIN |
| delete-all-audio | codebase/main/ipc/ipcHandlers.js:560 | codebase/preload/index.js:49 |  | MAPPED VALID CHAIN |
| delete-all-whisper-models | codebase/main/ipc/ipcHandlers.js:1234 | codebase/preload/index.js:187 |  | MAPPED VALID CHAIN |
| delete-cuda-whisper-binary | codebase/main/ipc/ipcHandlers.js:1359 | codebase/preload/index.js:205 |  | MAPPED VALID CHAIN |
| delete-diarization-models | codebase/main/ipc/ipcHandlers.js:1408 | codebase/preload/index.js:218 |  | MAPPED VALID CHAIN |
| delete-transcription-audio | codebase/main/ipc/ipcHandlers.js:543 | codebase/preload/index.js:47 |  | MAPPED VALID CHAIN |
| delete-whisper-model | codebase/main/ipc/ipcHandlers.js:1230 | codebase/preload/index.js:186 |  | MAPPED VALID CHAIN |
| detect-gpu | codebase/main/ipc/ipcHandlers.js:1256 | codebase/preload/index.js:201 |  | MAPPED VALID CHAIN |
| dictation-key-active |  | codebase/preload/index.js:375 | codebase/main/features/dictation/hotkeyManager.js:1086 | MAPPED VALID CHAIN |
| dictation-preview-audio | codebase/main/ipc/ipcHandlers.js:3285 | codebase/preload/index.js:441 |  | MAPPED VALID CHAIN |
| dictionary-updated |  | codebase/preload/index.js:60 | codebase/main/ipc/ipcHandlers.js:377, codebase/main/ipc/ipcHandlers.js:637 | MAPPED VALID CHAIN |
| dismiss-dictation-preview | codebase/main/ipc/ipcHandlers.js:3300 | codebase/preload/index.js:436 |  | MAPPED VALID CHAIN |
| export-dictionary | codebase/main/ipc/ipcHandlers.js:970 | codebase/preload/index.js:96 |  | MAPPED VALID CHAIN |
| export-note | codebase/main/ipc/ipcHandlers.js:881 | codebase/preload/index.js:94 |  | MAPPED VALID CHAIN |
| export-transcript | codebase/main/ipc/ipcHandlers.js:922 | codebase/preload/index.js:95 |  | MAPPED VALID CHAIN |
| floating-icon-auto-hide-changed | codebase/main/index.js:384 | codebase/preload/index.js:402 | codebase/main/index.js:389 | MAPPED VALID CHAIN |
| get-activation-mode | codebase/main/ipc/ipcHandlers.js:1741 | codebase/preload/index.js:286 |  | MAPPED VALID CHAIN |
| get-active-dictation-key | codebase/main/ipc/ipcHandlers.js:1732 | codebase/preload/index.js:281 |  | MAPPED VALID CHAIN |
| get-app-version | codebase/main/ipc/ipcHandlers.js:3477 | codebase/preload/index.js:264 |  | MAPPED VALID CHAIN |
| get-audio-buffer | codebase/main/ipc/ipcHandlers.js:538 | codebase/preload/index.js:46 |  | MAPPED VALID CHAIN |
| get-audio-diagnostics | codebase/main/ipc/ipcHandlers.js:1193 | codebase/preload/index.js:190 |  | MAPPED VALID CHAIN |
| get-audio-path | codebase/main/ipc/ipcHandlers.js:527 | codebase/preload/index.js:44 |  | MAPPED VALID CHAIN |
| get-audio-storage-usage | codebase/main/ipc/ipcHandlers.js:556 | codebase/preload/index.js:48 |  | MAPPED VALID CHAIN |
| get-auto-start-enabled | codebase/main/ipc/ipcHandlers.js:1700 | codebase/preload/index.js:416 |  | MAPPED VALID CHAIN |
| get-cuda-whisper-status | codebase/main/ipc/ipcHandlers.js:1313 | codebase/preload/index.js:202 |  | MAPPED VALID CHAIN |
| get-debug-state | codebase/main/ipc/ipcHandlers.js:3396 | codebase/preload/index.js:301 |  | MAPPED VALID CHAIN |
| get-diarization-model-status | codebase/main/ipc/ipcHandlers.js:1399 | codebase/preload/index.js:217 |  | MAPPED VALID CHAIN |
| get-dictation-key | codebase/main/ipc/ipcHandlers.js:1724 | codebase/preload/index.js:280 |  | MAPPED VALID CHAIN |
| get-effective-default-hotkey | codebase/main/ipc/ipcHandlers.js:1737 | codebase/preload/index.js:282 |  | MAPPED VALID CHAIN |
| get-file-size | codebase/main/ipc/ipcHandlers.js:1007 | codebase/preload/index.js:128 |  | MAPPED VALID CHAIN |
| get-gpu-device-index | codebase/main/ipc/ipcHandlers.js:1309 | codebase/preload/index.js:200 |  | MAPPED VALID CHAIN |
| get-hotkey-mode-info | codebase/main/ipc/ipcHandlers.js:1658 | codebase/preload/index.js:254 |  | MAPPED VALID CHAIN |
| get-hyprland-config-status | codebase/main/ipc/ipcHandlers.js:1674 | codebase/preload/index.js:255 |  | MAPPED VALID CHAIN |
| get-log-level | codebase/main/ipc/ipcHandlers.js:1780 | codebase/preload/index.js:294 |  | MAPPED VALID CHAIN |
| get-md5-hash | codebase/main/ipc/ipcHandlers.js:3531 | codebase/preload/index.js:450 |  | MAPPED VALID CHAIN |
| get-meeting-notification-data | codebase/main/ipc/ipcHandlers.js:3635 | codebase/preload/index.js:478 |  | MAPPED VALID CHAIN |
| get-pending-meeting-note-navigation | codebase/main/ipc/ipcHandlers.js:3639 | codebase/preload/index.js:483 |  | MAPPED VALID CHAIN |
| get-post-migration-state | codebase/main/ipc/ipcHandlers.js:3481 | codebase/preload/index.js:265 |  | MAPPED VALID CHAIN |
| get-speaker-mappings | codebase/main/ipc/ipcHandlers.js:3745 | codebase/preload/index.js:230 |  | MAPPED VALID CHAIN |
| get-speaker-profiles | codebase/main/ipc/ipcHandlers.js:3782 | codebase/preload/index.js:235 |  | MAPPED VALID CHAIN |
| get-transcription-by-id | codebase/main/ipc/ipcHandlers.js:579 | codebase/preload/index.js:53 |  | MAPPED VALID CHAIN |
| get-ui-language | codebase/main/ipc/ipcHandlers.js:1749 | codebase/preload/index.js:275 |  | MAPPED VALID CHAIN |
| get-ydotool-status | codebase/main/ipc/ipcHandlers.js:3376 | codebase/preload/index.js:298 |  | MAPPED VALID CHAIN |
| globe-key-pressed |  | codebase/preload/index.js:348 | codebase/main/index.js:541 | MAPPED VALID CHAIN |
| globe-key-released |  | codebase/preload/index.js:353 | codebase/main/index.js:586 | MAPPED VALID CHAIN |
| hide-dictation-preview | codebase/main/ipc/ipcHandlers.js:3319 | codebase/preload/index.js:438 |  | MAPPED VALID CHAIN |
| hide-window | codebase/main/ipc/ipcHandlers.js:451 | codebase/preload/index.js:27 |  | MAPPED VALID CHAIN |
| hotkey-changed | codebase/main/index.js:783, codebase/main/index.js:884 | codebase/preload/index.js:397 |  | MAPPED VALID CHAIN |
| hotkey-fallback-used |  | codebase/preload/index.js:360 | codebase/main/features/dictation/hotkeyManager.js:1101 | MAPPED VALID CHAIN |
| hotkey-listening-mode-changed | codebase/main/index.js:750 |  |  | MAPPED PURPOSE; NO STATIC CALLER — PONY-008 / TASK-07 SEVEN-GATE REVIEW |
| hotkey-registration-failed |  | codebase/preload/index.js:365 | codebase/main/features/dictation/hotkeyManager.js:1110 | MAPPED VALID CHAIN |
| import-cuda-whisper-binary | codebase/main/ipc/ipcHandlers.js:1327 | codebase/preload/index.js:203 |  | MAPPED VALID CHAIN |
| import-diarization-models | codebase/main/ipc/ipcHandlers.js:1375 | codebase/preload/index.js:216 |  | MAPPED VALID CHAIN |
| import-whisper-model | codebase/main/ipc/ipcHandlers.js:1197 | codebase/preload/index.js:182 |  | MAPPED VALID CHAIN |
| list-gpus | codebase/main/ipc/ipcHandlers.js:1261 | codebase/preload/index.js:198 |  | MAPPED VALID CHAIN |
| list-whisper-models | codebase/main/ipc/ipcHandlers.js:1226 | codebase/preload/index.js:185 |  | MAPPED VALID CHAIN |
| mark-bundle-migrated | codebase/main/ipc/ipcHandlers.js:3485 | codebase/preload/index.js:266 |  | MAPPED VALID CHAIN |
| mark-bundle-migration-dismissed | codebase/main/ipc/ipcHandlers.js:3489 | codebase/preload/index.js:267 |  | MAPPED VALID CHAIN |
| meeting-detection-get-preferences | codebase/main/ipc/ipcHandlers.js:3535 | codebase/preload/index.js:455 |  | MAPPED VALID CHAIN |
| meeting-detection-set-preferences | codebase/main/ipc/ipcHandlers.js:3543 | codebase/preload/index.js:457 |  | MAPPED VALID CHAIN |
| meeting-notification-ready | codebase/main/ipc/ipcHandlers.js:3643 | codebase/preload/index.js:479 |  | MAPPED VALID CHAIN |
| meeting-notification-respond | codebase/main/ipc/ipcHandlers.js:3626 | codebase/preload/index.js:481 |  | MAPPED VALID CHAIN |
| meeting-set-session-speaker-config | codebase/main/ipc/ipcHandlers.js:3605 | codebase/preload/index.js:463 |  | MAPPED VALID CHAIN |
| meeting-set-speaker-diarization-enabled | codebase/main/ipc/ipcHandlers.js:3579 | codebase/preload/index.js:461 |  | MAPPED VALID CHAIN |
| meeting-transcription-cancel | codebase/main/ipc/ipcHandlers.js:3007 | codebase/preload/index.js:327 |  | MAPPED VALID CHAIN |
| meeting-transcription-prepare | codebase/main/ipc/ipcHandlers.js:3002 | codebase/preload/index.js:321 |  | MAPPED VALID CHAIN |
| meeting-transcription-send | codebase/main/ipc/ipcHandlers.js:3222 | codebase/preload/index.js:325 |  | MAPPED VALID CHAIN |
| meeting-transcription-start | codebase/main/ipc/ipcHandlers.js:3015 | codebase/preload/index.js:323 |  | MAPPED VALID CHAIN |
| meeting-transcription-stop | codebase/main/ipc/ipcHandlers.js:3226 | codebase/preload/index.js:326 |  | MAPPED VALID CHAIN |
| note-added |  | codebase/preload/index.js:135 | codebase/main/features/meetings/meetingDetectionEngine.js:135, codebase/main/features/meetings/meetingDetectionEngine.js:190, codebase/main/ipc/ipcHandlers.js:658 | MAPPED VALID CHAIN |
| note-deleted |  | codebase/preload/index.js:145 | codebase/main/ipc/ipcHandlers.js:4311 | MAPPED VALID CHAIN |
| note-files-get-default-path | codebase/main/ipc/ipcHandlers.js:3693 | codebase/preload/index.js:121 |  | MAPPED VALID CHAIN |
| note-files-pick-folder | codebase/main/ipc/ipcHandlers.js:3731 | codebase/preload/index.js:122 |  | MAPPED VALID CHAIN |
| note-files-rebuild | codebase/main/ipc/ipcHandlers.js:3682 | codebase/preload/index.js:120 |  | MAPPED VALID CHAIN |
| note-files-set-enabled | codebase/main/ipc/ipcHandlers.js:3650 | codebase/preload/index.js:118 |  | MAPPED VALID CHAIN |
| note-files-set-path | codebase/main/ipc/ipcHandlers.js:3671 | codebase/preload/index.js:119 |  | MAPPED VALID CHAIN |
| note-updated |  | codebase/preload/index.js:140 | codebase/main/ipc/ipcHandlers.js:677, codebase/main/ipc/ipcHandlers.js:3942 | MAPPED VALID CHAIN |
| open-accessibility-settings | codebase/main/ipc/ipcHandlers.js:1835 | codebase/preload/index.js:312 |  | MAPPED VALID CHAIN |
| open-logs-folder | codebase/main/ipc/ipcHandlers.js:3466 | codebase/preload/index.js:303 |  | MAPPED VALID CHAIN |
| open-microphone-settings | codebase/main/ipc/ipcHandlers.js:1833 | codebase/preload/index.js:310 |  | MAPPED VALID CHAIN |
| open-mnemora-models-folder | codebase/main/ipc/ipcHandlers.js:3362 | codebase/preload/index.js:317 |  | MAPPED VALID CHAIN |
| open-sound-input-settings | codebase/main/ipc/ipcHandlers.js:1834 | codebase/preload/index.js:311 |  | MAPPED VALID CHAIN |
| open-system-audio-settings | codebase/main/ipc/ipcHandlers.js:1836 | codebase/preload/index.js:313 |  | MAPPED VALID CHAIN |
| panel-start-position-changed | codebase/main/index.js:398 | codebase/preload/index.js:410 |  | MAPPED VALID CHAIN |
| paste-text | codebase/main/ipc/ipcHandlers.js:1033 | codebase/preload/index.js:26 |  | MAPPED VALID CHAIN |
| pause-media-playback | codebase/main/ipc/ipcHandlers.js:1843 | codebase/preload/index.js:315 |  | MAPPED VALID CHAIN |
| preview-local-backup | codebase/main/ipc/ipcHandlers.js:834 | codebase/preload/index.js:98 |  | MAPPED VALID CHAIN |
| prompt-accessibility-permission | codebase/main/ipc/ipcHandlers.js:1090 | codebase/preload/index.js:173 |  | MAPPED VALID CHAIN |
| read-clipboard | codebase/main/ipc/ipcHandlers.js:1095 | codebase/preload/index.js:174 |  | MAPPED VALID CHAIN |
| register-cancel-hotkey | codebase/main/ipc/ipcHandlers.js:1679 | codebase/preload/index.js:272 |  | MAPPED VALID CHAIN |
| register-meeting-hotkey | codebase/main/index.js:443 | codebase/preload/index.js:398 |  | MAPPED VALID CHAIN |
| release-recording-lock | codebase/main/ipc/ipcHandlers.js:3506 | codebase/preload/index.js:443 |  | MAPPED VALID CHAIN |
| remove-speaker-mapping | codebase/main/ipc/ipcHandlers.js:3777 | codebase/preload/index.js:234 |  | MAPPED VALID CHAIN |
| request-microphone-access | codebase/main/ipc/ipcHandlers.js:1853 | codebase/preload/index.js:306 |  | MAPPED VALID CHAIN |
| request-system-audio-access | codebase/main/ipc/ipcHandlers.js:1957 | codebase/preload/index.js:309 |  | MAPPED VALID CHAIN |
| resize-main-window | codebase/main/ipc/ipcHandlers.js:474 | codebase/preload/index.js:262 |  | MAPPED VALID CHAIN |
| resize-transcription-preview-window | codebase/main/ipc/ipcHandlers.js:3325 | codebase/preload/index.js:440 |  | MAPPED VALID CHAIN |
| restore-from-meeting-mode | codebase/main/ipc/ipcHandlers.js:446 | codebase/preload/index.js:247 |  | MAPPED VALID CHAIN |
| restore-local-backup | codebase/main/ipc/ipcHandlers.js:842 | codebase/preload/index.js:99 |  | MAPPED VALID CHAIN |
| resume-media-playback | codebase/main/ipc/ipcHandlers.js:1848 | codebase/preload/index.js:316 |  | MAPPED VALID CHAIN |
| retry-transcription | codebase/main/ipc/ipcHandlers.js:1994 | codebase/preload/index.js:50 |  | MAPPED VALID CHAIN |
| save-activation-mode | codebase/main/ipc/ipcHandlers.js:1745 | codebase/preload/index.js:287 |  | MAPPED VALID CHAIN |
| save-all-keys-to-env | codebase/main/ipc/ipcHandlers.js:1766 | codebase/preload/index.js:289 |  | MAPPED VALID CHAIN |
| save-dictation-key | codebase/main/ipc/ipcHandlers.js:1728 | codebase/preload/index.js:283 |  | MAPPED VALID CHAIN |
| save-note-speaker-embeddings | codebase/main/ipc/ipcHandlers.js:3809 | codebase/preload/index.js:239 |  | MAPPED VALID CHAIN |
| save-transcription-audio | codebase/main/ipc/ipcHandlers.js:510 | codebase/preload/index.js:43 |  | MAPPED VALID CHAIN |
| save-ui-language | codebase/main/ipc/ipcHandlers.js:1753 | codebase/preload/index.js:276 |  | MAPPED VALID CHAIN |
| search-contacts | codebase/main/ipc/ipcHandlers.js:3513 | codebase/preload/index.js:448 |  | MAPPED VALID CHAIN |
| select-audio-file | codebase/main/ipc/ipcHandlers.js:990 | codebase/preload/index.js:127 |  | MAPPED VALID CHAIN |
| semantic-reindex-progress |  | codebase/preload/index.js:106 | codebase/main/ipc/ipcHandlers.js:746 | MAPPED VALID CHAIN |
| set-auto-start-enabled | codebase/main/ipc/ipcHandlers.js:1710 | codebase/preload/index.js:417 |  | MAPPED VALID CHAIN |
| set-debug-logging | codebase/main/ipc/ipcHandlers.js:3409 | codebase/preload/index.js:302 |  | MAPPED VALID CHAIN |
| set-gpu-device-index | codebase/main/ipc/ipcHandlers.js:1266 | codebase/preload/index.js:199 |  | MAPPED VALID CHAIN |
| set-hotkey-listening-mode | codebase/main/ipc/ipcHandlers.js:1497 | codebase/preload/index.js:253 |  | MAPPED VALID CHAIN |
| set-main-window-interactivity | codebase/main/ipc/ipcHandlers.js:464 | codebase/preload/index.js:259 |  | MAPPED VALID CHAIN |
| set-notification-interactivity | codebase/main/ipc/ipcHandlers.js:469 | codebase/preload/index.js:261 |  | MAPPED VALID CHAIN |
| set-speaker-mapping | codebase/main/ipc/ipcHandlers.js:3749 | codebase/preload/index.js:232 |  | MAPPED VALID CHAIN |
| set-ui-language | codebase/main/ipc/ipcHandlers.js:1757 | codebase/preload/index.js:277 |  | MAPPED VALID CHAIN |
| setting-updated |  | codebase/preload/index.js:370 | codebase/main/features/dictation/hotkeyManager.js:989 | MAPPED VALID CHAIN |
| show-audio-in-folder | codebase/main/ipc/ipcHandlers.js:531 | codebase/preload/index.js:45 |  | MAPPED VALID CHAIN |
| show-dictation-panel | codebase/main/ipc/ipcHandlers.js:460 | codebase/preload/index.js:28 |  | MAPPED VALID CHAIN |
| show-folder-in-explorer | codebase/main/ipc/ipcHandlers.js:3714 | codebase/preload/index.js:124 |  | MAPPED VALID CHAIN |
| show-note-file | codebase/main/ipc/ipcHandlers.js:3697 | codebase/preload/index.js:123 |  | MAPPED VALID CHAIN |
| snap-to-meeting-mode | codebase/main/ipc/ipcHandlers.js:442 | codebase/preload/index.js:246 |  | MAPPED VALID CHAIN |
| snippets-updated |  | codebase/preload/index.js:67 |  | MAPPED DYNAMIC-DIRECTION REVIEW |
| start-dictation-preview | codebase/main/ipc/ipcHandlers.js:3272 | codebase/preload/index.js:434 |  | MAPPED VALID CHAIN |
| start-minimized-changed | codebase/main/index.js:393 | codebase/preload/index.js:413 |  | MAPPED VALID CHAIN |
| start-window-drag | codebase/main/ipc/ipcHandlers.js:1692 | codebase/preload/index.js:256 |  | MAPPED VALID CHAIN |
| stop-dictation-preview | codebase/main/ipc/ipcHandlers.js:3332 | codebase/preload/index.js:435 |  | MAPPED VALID CHAIN |
| stop-window-drag | codebase/main/ipc/ipcHandlers.js:1696 | codebase/preload/index.js:257 |  | MAPPED VALID CHAIN |
| sync-notification-preferences | codebase/main/ipc/ipcHandlers.js:3557 | codebase/preload/index.js:459 |  | MAPPED VALID CHAIN |
| sync-startup-preferences | codebase/main/ipc/ipcHandlers.js:1770 | codebase/preload/index.js:290 |  | MAPPED VALID CHAIN |
| toggle-media-playback | codebase/main/ipc/ipcHandlers.js:1838 | codebase/preload/index.js:314 |  | MAPPED VALID CHAIN |
| transcribe-audio-file | codebase/main/ipc/ipcHandlers.js:1017 | codebase/preload/index.js:130 |  | MAPPED VALID CHAIN |
| transcribe-local-whisper | codebase/main/ipc/ipcHandlers.js:1107 | codebase/preload/index.js:180 |  | MAPPED VALID CHAIN |
| transcription-added |  | codebase/preload/index.js:151 | codebase/main/ipc/ipcHandlers.js:482 | MAPPED VALID CHAIN |
| transcription-deleted |  | codebase/preload/index.js:156 | codebase/main/ipc/ipcHandlers.js:4302 | MAPPED VALID CHAIN |
| transcription-updated |  | codebase/preload/index.js:166 | codebase/main/ipc/ipcHandlers.js:522, codebase/main/ipc/ipcHandlers.js:2026 | MAPPED VALID CHAIN |
| transcriptions-cleared |  | codebase/preload/index.js:161 | codebase/main/ipc/ipcHandlers.js:497 | MAPPED VALID CHAIN |
| undo-learned-corrections | codebase/main/ipc/ipcHandlers.js:618 | codebase/preload/index.js:76 |  | MAPPED VALID CHAIN |
| unregister-cancel-hotkey | codebase/main/ipc/ipcHandlers.js:1687 | codebase/preload/index.js:273 |  | MAPPED VALID CHAIN |
| update-hotkey | codebase/main/ipc/ipcHandlers.js:1493 | codebase/preload/index.js:252 |  | MAPPED VALID CHAIN |
| update-transcription-text | codebase/main/ipc/ipcHandlers.js:3347 | codebase/preload/index.js:52 |  | MAPPED VALID CHAIN |
| upsert-contact | codebase/main/ipc/ipcHandlers.js:3522 | codebase/preload/index.js:449 |  | MAPPED VALID CHAIN |
| whisper-server-start | codebase/main/ipc/ipcHandlers.js:1242 | codebase/preload/index.js:193 |  | MAPPED VALID CHAIN |
| whisper-server-status | codebase/main/ipc/ipcHandlers.js:1252 | codebase/preload/index.js:195 |  | MAPPED VALID CHAIN |
| whisper-server-stop | codebase/main/ipc/ipcHandlers.js:1248 | codebase/preload/index.js:194 |  | MAPPED VALID CHAIN |
| whisper-vad-get-config | codebase/main/ipc/ipcHandlers.js:3588 | codebase/preload/index.js:464 |  | MAPPED VALID CHAIN |
| whisper-vad-set-config | codebase/main/ipc/ipcHandlers.js:3596 | codebase/preload/index.js:465 |  | MAPPED VALID CHAIN |
| window-close | codebase/main/ipc/ipcHandlers.js:429 | codebase/preload/index.js:244 |  | MAPPED VALID CHAIN |
| window-is-maximized | codebase/main/ipc/ipcHandlers.js:435 | codebase/preload/index.js:245 |  | MAPPED VALID CHAIN |
| window-maximize | codebase/main/ipc/ipcHandlers.js:419 | codebase/preload/index.js:243 |  | MAPPED VALID CHAIN |
| window-minimize | codebase/main/ipc/ipcHandlers.js:413 | codebase/preload/index.js:242 |  | MAPPED VALID CHAIN |
| write-clipboard | codebase/main/ipc/ipcHandlers.js:1099 | codebase/preload/index.js:175 |  | MAPPED VALID CHAIN |

## Dynamic and string-based runtime evidence

| Kind | Symbol/anchor | Path | Line | Status |
| --- | --- | --- | --- | --- |
| Dynamic/lazy import | import( | codebase/main/features/dictation/textEditMonitor.js | 111 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/main/features/dictation/textEditMonitor.js | 132 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/main/infrastructure/runtime/processListCache.js | 30 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/renderer/app/AppRouter.jsx | 10 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/renderer/app/AppRouter.jsx | 11 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/renderer/app/AppRouter.jsx | 39 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/renderer/app/AppRouter.jsx | 42 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/renderer/app/components/ControlPanel.tsx | 29 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/renderer/app/components/ControlPanel.tsx | 31 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/renderer/app/components/ControlPanel.tsx | 32 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | require(p | codebase/scripts/verification/verify-offline-assets.js | 93 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/dictionaryEchoFilter.test.js | 5 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/dictionaryEchoFilter.test.js | 13 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/dictionaryEchoFilter.test.js | 21 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/dictionaryEchoFilter.test.js | 29 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/dictionaryEchoFilter.test.js | 37 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/dictionaryEchoFilter.test.js | 45 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/dictionaryEchoFilter.test.js | 56 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/dictionaryEchoFilter.test.js | 64 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/dictionaryEchoFilter.test.js | 69 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/dictionaryEchoFilter.test.js | 74 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/dictionaryEchoFilter.test.js | 79 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/dictionaryEchoFilter.test.js | 85 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/dictionaryEchoFilter.test.js | 91 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/dictionaryEchoFilter.test.js | 96 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/dictionaryEchoFilter.test.js | 103 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/dictionaryEchoFilter.test.js | 110 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/discardedRecording.test.js | 4 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/localSpeechGate.test.js | 6 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/localSpeechGate.test.js | 17 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/localSpeechGate.test.js | 37 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/localSpeechGate.test.js | 58 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/micTrackHealth.test.js | 29 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/micTrackHealth.test.js | 36 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/micTrackHealth.test.js | 41 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/micTrackHealth.test.js | 48 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/micTrackHealth.test.js | 58 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/micTrackHealth.test.js | 68 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/micTrackHealth.test.js | 78 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/micTrackHealth.test.js | 117 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/micTrackHealth.test.js | 134 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/micTrackHealth.test.js | 149 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/micTrackHealth.test.js | 176 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/recordingGuard.test.js | 4 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/recordingValidation.test.js | 4 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/dictation/staleMicDevice.test.js | 4 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/transcription/whisperVadConfig.test.js | 6 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Dynamic/lazy import | import( | codebase/tests/unit/transcription/whisperVadConfig.test.js | 28 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/desktop/windowManager.js | 334 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/desktop/windowManager.js | 443 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/desktop/windowManager.js | 461 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/desktop/windowManager.js | 471 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/desktop/windowManager.js | 708 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/desktop/windowManager.js | 715 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/desktop/windowManager.js | 720 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/desktop/windowManager.js | 727 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/desktop/windowManager.js | 735 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/desktop/windowManager.js | 951 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/desktop/windowManager.js | 1005 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/desktop/windowManager.js | 1008 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/desktop/windowManager.js | 1071 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | globalShortcut.register | codebase/main/features/dictation/hotkeyManager.js | 427 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | globalShortcut.register | codebase/main/features/dictation/hotkeyManager.js | 599 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/features/dictation/hotkeyManager.js | 989 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/features/dictation/hotkeyManager.js | 1086 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/features/dictation/hotkeyManager.js | 1101 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/features/dictation/hotkeyManager.js | 1110 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/features/meetings/meetingDetectionEngine.js | 311 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/index.js | 389 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/index.js | 541 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/index.js | 586 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/index.js | 764 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/index.js | 842 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/index.js | 854 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/index.js | 871 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | globalShortcut.register | codebase/main/ipc/ipcHandlers.js | 1591 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/ipc/ipcHandlers.js | 2630 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/ipc/ipcHandlers.js | 2679 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/ipc/ipcHandlers.js | 2800 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/ipc/ipcHandlers.js | 2816 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/ipc/ipcHandlers.js | 2860 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/ipc/ipcHandlers.js | 3138 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/ipc/ipcHandlers.js | 4104 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | webContents.send | codebase/main/ipc/ipcHandlers.js | 4322 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | addEventListener | codebase/renderer/app/components/ControlPanel.tsx | 144 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | addEventListener | codebase/renderer/features/dictation/App.jsx | 259 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | addEventListener | codebase/renderer/features/dictation/App.jsx | 274 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | addEventListener | codebase/renderer/features/dictation/audioManager.js | 45 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | addEventListener | codebase/renderer/features/dictation/micTrackHealth.js | 48 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | addEventListener | codebase/renderer/features/dictation/micTrackHealth.js | 49 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | addEventListener | codebase/renderer/features/meetings/meetingRecordingStore.ts | 1210 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | addEventListener | codebase/renderer/features/meetings/useSystemAudioPermission.ts | 32 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | addEventListener | codebase/renderer/features/notes/components/MeetingTranscriptView.tsx | 512 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | addEventListener | codebase/renderer/features/notes/components/NoteEditor.tsx | 438 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | addEventListener | codebase/renderer/features/notes/noteStore.ts | 61 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | addEventListener | codebase/renderer/features/transcription/components/LanguageSelector.tsx | 101 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | addEventListener | codebase/renderer/features/transcription/transcriptionStore.ts | 67 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | addEventListener | codebase/renderer/shared/hooks/useTheme.ts | 40 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | addEventListener | codebase/renderer/shared/hooks/useWindowDrag.js | 35 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | addEventListener | codebase/tests/unit/dictation/micTrackHealth.test.js | 13 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Runtime/event registration | addEventListener | codebase/tests/unit/dictation/micTrackHealth.test.js | 15 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/features/dictation/clipboard.js | 447 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/features/dictation/clipboard.js | 851 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/features/dictation/clipboard.js | 852 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/features/dictation/clipboard.js | 929 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/features/dictation/clipboard.js | 999 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/features/dictation/clipboard.js | 1088 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/features/dictation/clipboard.js | 1160 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/features/dictation/clipboard.js | 1469 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/features/dictation/clipboard.js | 1759 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/features/dictation/clipboard.js | 2011 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/features/dictation/clipboard.js | 2036 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/features/dictation/clipboard.js | 2050 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/features/dictation/clipboard.js | 2051 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | execFile( | codebase/main/features/dictation/textEditMonitor.js | 112 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | execFile( | codebase/main/features/dictation/textEditMonitor.js | 139 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | execFile( | codebase/main/features/dictation/textEditMonitor.js | 182 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/features/dictation/textEditMonitor.js | 248 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/features/dictation/textEditMonitor.js | 392 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | execFile( | codebase/main/features/dictation/textEditMonitor.js | 435 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/features/meetings/audioActivityDetector.js | 220 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/features/meetings/audioActivityDetector.js | 263 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/features/meetings/audioActivityDetector.js | 317 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/features/meetings/audioTapManager.js | 149 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/features/meetings/audioTapManager.js | 285 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/features/meetings/diarization.js | 235 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/features/meetings/meetingAecManager.js | 79 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | fork( | codebase/main/features/search/onnxWorkerClient.js | 59 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/features/search/qdrantManager.js | 108 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/features/transcription/ffmpegUtils.js | 145 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/features/transcription/ffmpegUtils.js | 283 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | execFile( | codebase/main/features/transcription/gpuDetection.js | 14 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | execFile( | codebase/main/features/transcription/gpuDetection.js | 58 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/features/transcription/whisperServer.js | 427 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/index.js | 11 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/infrastructure/runtime/process.js | 15 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/infrastructure/runtime/process.js | 102 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/platform/globeKeyManager.js | 97 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/platform/linuxKeyManager.js | 51 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/platform/linuxPortalAudioManager.js | 112 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/platform/linuxPortalAudioManager.js | 294 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/platform/windowsKeyManager.js | 58 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/platform/windowsLoopbackAudioManager.js | 134 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/main/platform/windowsLoopbackAudioManager.js | 291 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Local process spawn | spawn( | codebase/scripts/development/run-electron.js | 71 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | OPENWHISPR_DEV_SERVER_PORT | codebase/main/desktop/devServerManager.js | 4 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | VITE_DEV_SERVER_PORT | codebase/main/desktop/devServerManager.js | 5 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | NODE_ENV | codebase/main/desktop/devServerManager.js | 58 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | NODE_ENV | codebase/main/desktop/devServerManager.js | 73 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | NODE_ENV | codebase/main/desktop/tray.js | 132 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | XDG_SESSION_TYPE | codebase/main/desktop/windowConfig.js | 5 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | XDG_CURRENT_DESKTOP | codebase/main/desktop/windowConfig.js | 6 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | XDG_SESSION_TYPE | codebase/main/desktop/windowConfig.js | 10 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | XDG_CURRENT_DESKTOP | codebase/main/desktop/windowConfig.js | 11 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | NODE_ENV | codebase/main/desktop/windowManager.js | 75 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | NODE_ENV | codebase/main/desktop/windowManager.js | 180 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | NODE_ENV | codebase/main/desktop/windowManager.js | 630 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | NODE_ENV | codebase/main/desktop/windowManager.js | 678 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | NODE_ENV | codebase/main/desktop/windowManager.js | 931 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | XDG_CURRENT_DESKTOP | codebase/main/features/dictation/clipboard.js | 16 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | XDG_SESSION_DESKTOP | codebase/main/features/dictation/clipboard.js | 16 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | DESKTOP_SESSION | codebase/main/features/dictation/clipboard.js | 16 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | SWAYSOCK | codebase/main/features/dictation/clipboard.js | 29 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | HYPRLAND_INSTANCE_SIGNATURE | codebase/main/features/dictation/clipboard.js | 30 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | XDG_SESSION_TYPE | codebase/main/features/dictation/clipboard.js | 36 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | WAYLAND_DISPLAY | codebase/main/features/dictation/clipboard.js | 37 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | DISPLAY | codebase/main/features/dictation/clipboard.js | 38 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | HYPRLAND_INSTANCE_SIGNATURE | codebase/main/features/dictation/clipboard.js | 43 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | YDOTOOL_SOCKET | codebase/main/features/dictation/clipboard.js | 347 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | YDOTOOL_SOCKET | codebase/main/features/dictation/clipboard.js | 356 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | XDG_CACHE_HOME | codebase/main/features/dictation/clipboard.js | 403 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | NODE_ENV | codebase/main/features/dictation/clipboard.js | 690 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | DISPLAY | codebase/main/features/dictation/clipboard.js | 1269 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | WAYLAND_DISPLAY | codebase/main/features/dictation/clipboard.js | 1270 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | XDG_SESSION_TYPE | codebase/main/features/dictation/clipboard.js | 1271 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | XDG_CURRENT_DESKTOP | codebase/main/features/dictation/clipboard.js | 1272 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | XDG_SESSION_TYPE | codebase/main/features/dictation/hotkeyManager.js | 670 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | HYPRLAND_INSTANCE_SIGNATURE | codebase/main/features/dictation/hotkeyManager.js | 671 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | XDG_CURRENT_DESKTOP | codebase/main/features/dictation/hotkeyManager.js | 672 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | DICTATION_KEY | codebase/main/features/dictation/hotkeyManager.js | 862 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | DICTATION_KEY | codebase/main/features/dictation/hotkeyManager.js | 887 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | DICTATION_KEY | codebase/main/features/dictation/hotkeyManager.js | 964 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | PATH | codebase/main/features/transcription/ffmpegUtils.js | 72 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | PATH | codebase/main/features/transcription/whisperServer.js | 247 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | PATH | codebase/main/features/transcription/whisperServer.js | 387 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | TRANSCRIPTION_GPU_UUID | codebase/main/features/transcription/whisperServer.js | 392 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | TRANSCRIPTION_GPU_UUID | codebase/main/features/transcription/whisperServer.js | 393 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | XDG_SESSION_TYPE | codebase/main/index.js | 5 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | XDG_CURRENT_DESKTOP | codebase/main/index.js | 8 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | NODE_ENV | codebase/main/index.js | 45 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | MNEMORA_CHANNEL | codebase/main/index.js | 52 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | VITE_MNEMORA_CHANNEL | codebase/main/index.js | 52 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | MNEMORA_CHANNEL | codebase/main/index.js | 64 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | MNEMORA_USER_DATA_DIR | codebase/main/index.js | 70 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | MNEMORA_USER_DATA_DIR | codebase/main/index.js | 71 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | XDG_SESSION_TYPE | codebase/main/index.js | 118 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | NODE_ENV | codebase/main/index.js | 218 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | PATH | codebase/main/index.js | 228 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | PATH | codebase/main/index.js | 232 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | UI_LANGUAGE | codebase/main/index.js | 257 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | NODE_ENV | codebase/main/index.js | 348 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | NODE_ENV | codebase/main/index.js | 408 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | LOCAL_WHISPER_MODEL | codebase/main/index.js | 479 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | WHISPER_CUDA_ENABLED | codebase/main/index.js | 480 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | NODE_ENV | codebase/main/infrastructure/persistence/database.js | 493 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | NODE_ENV | codebase/main/infrastructure/persistence/database.js | 2145 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | NODE_ENV | codebase/main/infrastructure/runtime/debugLogger.js | 80 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | OPENWHISPR_LOG_LEVEL | codebase/main/infrastructure/runtime/debugLogger.js | 105 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | LOG_LEVEL | codebase/main/infrastructure/runtime/debugLogger.js | 105 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | P | codebase/main/infrastructure/runtime/debugLogger.js | 308 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | P | codebase/main/infrastructure/runtime/safeTempDir.js | 23 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | S | codebase/main/infrastructure/runtime/safeTempDir.js | 31 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | WHISPER_CUDA_ENABLED | codebase/main/ipc/ipcHandlers.js | 1244 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | WHISPER_CUDA_ENABLED | codebase/main/ipc/ipcHandlers.js | 1293 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | TRANSCRIPTION_GPU_UUID | codebase/main/ipc/ipcHandlers.js | 1310 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | NODE_ENV | codebase/main/ipc/ipcHandlers.js | 1460 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | UI_LANGUAGE | codebase/main/ipc/ipcHandlers.js | 1759 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | LOCAL_WHISPER_MODEL | codebase/main/ipc/ipcHandlers.js | 3040 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | XDG_CURRENT_DESKTOP | codebase/main/ipc/ipcHandlers.js | 3380 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | MNEMORA_LOG_LEVEL | codebase/main/ipc/ipcHandlers.js | 3450 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | XDG_SESSION_TYPE | codebase/main/platform/ensureYdotool.js | 89 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | WAYLAND_DISPLAY | codebase/main/platform/ensureYdotool.js | 90 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | XDG_SESSION_TYPE | codebase/main/platform/ensureYdotool.js | 195 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | WAYLAND_DISPLAY | codebase/main/platform/ensureYdotool.js | 196 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | XDG_CURRENT_DESKTOP | codebase/main/platform/gnomeShortcut.js | 87 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | XDG_SESSION_TYPE | codebase/main/platform/gnomeShortcut.js | 96 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | HYPRLAND_CONFIG | codebase/main/platform/hyprlandShortcut.js | 65 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | HYPRLAND_CONFIG | codebase/main/platform/hyprlandShortcut.js | 66 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | XDG_CONFIG_HOME | codebase/main/platform/hyprlandShortcut.js | 68 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | HYPRLAND_CONFIG | codebase/main/platform/hyprlandShortcut.js | 73 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | HYPRLAND_CONFIG | codebase/main/platform/hyprlandShortcut.js | 74 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | HYPRLAND_INSTANCE_SIGNATURE | codebase/main/platform/hyprlandShortcut.js | 110 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | XDG_CURRENT_DESKTOP | codebase/main/platform/hyprlandShortcut.js | 113 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | XDG_SESSION_TYPE | codebase/main/platform/hyprlandShortcut.js | 118 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | XDG_CURRENT_DESKTOP | codebase/main/platform/kdeShortcut.js | 111 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | XDG_SESSION_TYPE | codebase/main/platform/kdeShortcut.js | 116 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | MNEMORA_ONNX_WORKER_LOG | codebase/main/workers/onnxWorker.js | 8 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | TARGET_ARCH | codebase/scripts/build/build-globe-listener.js | 16 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | TARGET_ARCH | codebase/scripts/build/build-macos-audio-tap.js | 14 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | TARGET_ARCH | codebase/scripts/build/build-macos-fast-paste.js | 16 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | TARGET_ARCH | codebase/scripts/build/build-macos-mic-listener.js | 16 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | TARGET_ARCH | codebase/scripts/build/build-macos-text-monitor.js | 16 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | TARGET_ARCH | codebase/scripts/build/build-media-remote.js | 16 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | TARGET_ARCH | codebase/scripts/build/build-meeting-aec-helper.js | 25 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | ELECTRON_RUN_AS_NODE | codebase/scripts/development/run-electron.js | 12 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | ELECTRON_SKIP_BINARY_DOWNLOAD | codebase/scripts/development/run-electron.js | 27 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | XDG_SESSION_TYPE | codebase/scripts/development/run-electron.js | 58 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | XDG_CURRENT_DESKTOP | codebase/scripts/development/run-electron.js | 61 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | DIARIZATION_MODEL_DIR | codebase/scripts/downloads/download-diarization-models.js | 26 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | DIARIZATION_MODEL_DIR | codebase/scripts/downloads/download-diarization-models.js | 27 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | MEETING_AEC_HELPER_VERSION | codebase/scripts/downloads/download-meeting-aec-helper.js | 22 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | QDRANT_VERSION | codebase/scripts/downloads/download-qdrant.js | 17 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | WHISPER_CPP_VERSION | codebase/scripts/downloads/download-whisper-cpp.js | 17 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | WINDOWS_FAST_PASTE_VERSION | codebase/scripts/downloads/download-windows-fast-paste.js | 27 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | WINDOWS_KEY_LISTENER_VERSION | codebase/scripts/downloads/download-windows-key-listener.js | 28 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | WINDOWS_SYSTEM_AUDIO_HELPER_VERSION | codebase/scripts/downloads/download-windows-system-audio-helper.js | 29 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | GITHUB_TOKEN | codebase/scripts/lib/download-utils.js | 30 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | GH_TOKEN | codebase/scripts/lib/download-utils.js | 30 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | TARGET_PLATFORM | codebase/scripts/lib/download-utils.js | 288 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | TARGET_ARCH | codebase/scripts/lib/download-utils.js | 289 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | CI | codebase/scripts/lib/download-utils.js | 311 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | GITHUB_ACTIONS | codebase/scripts/lib/download-utils.js | 312 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | APPDATA | codebase/scripts/maintenance/cleanup.js | 16 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | NODE_ENV | codebase/tests/unit/persistence/localBackup.test.js | 25 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | NODE_ENV | codebase/tests/unit/persistence/localDataDatabase.test.js | 25 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | NODE_ENV | codebase/tests/unit/persistence/snippetsDatabase.test.js | 24 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Environment variable | PATH | codebase/tests/unit/platform/linuxLauncherSandbox.test.js | 42 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | menu.appLabel | codebase/main/desktop/menuManager.js | 9 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | menu.settings | codebase/main/desktop/menuManager.js | 14 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | menu.quit | codebase/main/desktop/menuManager.js | 25 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | menu.appLabel | codebase/main/desktop/menuManager.js | 39 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | menu.settings | codebase/main/desktop/menuManager.js | 44 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | menu.quit | codebase/main/desktop/menuManager.js | 55 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | menu.speech | codebase/main/desktop/menuManager.js | 72 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | menu.file | codebase/main/desktop/menuManager.js | 110 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | menu.settings | codebase/main/desktop/menuManager.js | 113 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | menu.closeWindow | codebase/main/desktop/menuManager.js | 118 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | tray.toggleDictation.hide | codebase/main/desktop/tray.js | 236 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | tray.toggleDictation.show | codebase/main/desktop/tray.js | 237 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | tray.openControlPanel | codebase/main/desktop/tray.js | 249 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | tray.quit | codebase/main/desktop/tray.js | 256 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | tray.tooltip | codebase/main/desktop/tray.js | 269 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | window.voiceRecorderTitle | codebase/main/desktop/windowManager.js | 92 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | window.controlPanelTitle | codebase/main/desktop/windowManager.js | 620 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | window.controlPanelTitle | codebase/main/desktop/windowManager.js | 1058 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | window.voiceRecorderTitle | codebase/main/desktop/windowManager.js | 1062 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dialog.loadFailure.detail.window | codebase/main/desktop/windowManager.js | 1081 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dialog.loadFailure.detail.error | codebase/main/desktop/windowManager.js | 1082 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dialog.loadFailure.detail.url | codebase/main/desktop/windowManager.js | 1083 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dialog.loadFailure.detail.hint | codebase/main/desktop/windowManager.js | 1084 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dialog.loadFailure.title | codebase/main/desktop/windowManager.js | 1088 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dialog.loadFailure.message | codebase/main/desktop/windowManager.js | 1089 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkey.errors.alreadyRegistered | codebase/main/features/dictation/hotkeyManager.js | 25 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkey.errors.osReserved | codebase/main/features/dictation/hotkeyManager.js | 26 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkey.errors.alreadyRegistered | codebase/main/features/dictation/hotkeyManager.js | 147 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkey.errors.osReserved | codebase/main/features/dictation/hotkeyManager.js | 157 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkey.errors.registrationFailed | codebase/main/features/dictation/hotkeyManager.js | 165 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkey.errors.registrationFailed | codebase/main/features/dictation/hotkeyManager.js | 190 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkey.errors.registrationFailed | codebase/main/features/dictation/hotkeyManager.js | 217 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkey.errors.registrationFailed | codebase/main/features/dictation/hotkeyManager.js | 234 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkey.errors.registrationFailed | codebase/main/features/dictation/hotkeyManager.js | 260 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkey.errors.mouseButtonOnlyMac | codebase/main/features/dictation/hotkeyManager.js | 390 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkey.errors.globeOnlyMac | codebase/main/features/dictation/hotkeyManager.js | 401 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkey.errors.callbackRequired | codebase/main/features/dictation/hotkeyManager.js | 461 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkey.errors.registrationFailed | codebase/main/features/dictation/hotkeyManager.js | 478 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkey.errors.registrationFailed | codebase/main/features/dictation/hotkeyManager.js | 535 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkey.errors.trySuggestions | codebase/main/features/dictation/hotkeyManager.js | 538 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkey.errors.slotConflict | codebase/main/features/dictation/hotkeyManager.js | 580 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkey.errors.registrationFailed | codebase/main/features/dictation/hotkeyManager.js | 827 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkey.errors.registrationFailed | codebase/main/features/dictation/hotkeyManager.js | 1112 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkey.errors.registrationFailed | codebase/main/features/dictation/hotkeyManager.js | 1128 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkey.errors.updateFailedCheckFormat | codebase/main/features/dictation/hotkeyManager.js | 1149 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkey.errors.updateFailedCheckFormat | codebase/main/features/dictation/hotkeyManager.js | 1172 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkey.errors.registrationFailed | codebase/main/features/dictation/hotkeyManager.js | 1207 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | transcript.speaker.you | codebase/main/features/dictation/transcriptFormatter.js | 11 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | transcript.speaker.others | codebase/main/features/dictation/transcriptFormatter.js | 12 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | startup.globeHotkey.details.unknown | codebase/main/index.js | 344 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | startup.globeHotkey.details.fallback | codebase/main/index.js | 345 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | startup.globeHotkey.details.devHint | codebase/main/index.js | 349 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | startup.globeHotkey.details.reinstallHint | codebase/main/index.js | 351 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | startup.globeHotkey.title | codebase/main/index.js | 356 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | startup.globeHotkey.message | codebase/main/index.js | 357 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | windows.pttUnavailable | codebase/main/index.js | 856 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | startup.error.title | codebase/main/index.js | 958 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | startup.error.message | codebase/main/index.js | 959 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | systemSettings.microphone | codebase/main/ipc/ipcHandlers.js | 1812 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | systemSettings.sound | codebase/main/ipc/ipcHandlers.js | 1813 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | systemSettings.accessibility | codebase/main/ipc/ipcHandlers.js | 1814 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | systemSettings.systemAudio | codebase/main/ipc/ipcHandlers.js | 1815 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | common.loading | codebase/renderer/app/AppRouter.jsx | 96 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | errorBoundary.title | codebase/renderer/app/components/ErrorBoundary.tsx | 37 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | errorBoundary.description | codebase/renderer/app/components/ErrorBoundary.tsx | 39 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | errorBoundary.reload | codebase/renderer/app/components/ErrorBoundary.tsx | 49 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | windowControls.minimize | codebase/renderer/app/components/WindowControls.tsx | 55 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | windowControls.restore | codebase/renderer/app/components/WindowControls.tsx | 64 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | windowControls.maximize | codebase/renderer/app/components/WindowControls.tsx | 64 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | windowControls.close | codebase/renderer/app/components/WindowControls.tsx | 74 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | app.toasts.hotkeyChanged.title | codebase/renderer/features/dictation/App.jsx | 110 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | app.toasts.hotkeyChanged.description | codebase/renderer/features/dictation/App.jsx | 111 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | app.toasts.hotkeyUnavailable.title | codebase/renderer/features/dictation/App.jsx | 121 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | app.toasts.hotkeyUnavailable.description | codebase/renderer/features/dictation/App.jsx | 122 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | app.toasts.addedToDict | codebase/renderer/features/dictation/App.jsx | 132 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | app.toasts.undo | codebase/renderer/features/dictation/App.jsx | 153 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | app.mic.recording | codebase/renderer/features/dictation/App.jsx | 302 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | app.mic.processing | codebase/renderer/features/dictation/App.jsx | 307 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | app.mic.clickToSpeak | codebase/renderer/features/dictation/App.jsx | 313 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | app.buttons.cancelRecording | codebase/renderer/features/dictation/App.jsx | 348 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | app.buttons.cancelProcessing | codebase/renderer/features/dictation/App.jsx | 348 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | app.commandMenu.stopListening | codebase/renderer/features/dictation/App.jsx | 478 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | app.commandMenu.startListening | codebase/renderer/features/dictation/App.jsx | 479 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | app.commandMenu.hideForNow | codebase/renderer/features/dictation/App.jsx | 490 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyGuidance.recommended.macos.0 | codebase/renderer/features/dictation/components/HotkeyGuidanceAccordion.tsx | 38 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyGuidance.recommended.macos.1 | codebase/renderer/features/dictation/components/HotkeyGuidanceAccordion.tsx | 39 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyGuidance.recommended.macos.2 | codebase/renderer/features/dictation/components/HotkeyGuidanceAccordion.tsx | 40 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyGuidance.recommended.macos.3 | codebase/renderer/features/dictation/components/HotkeyGuidanceAccordion.tsx | 41 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyGuidance.recommended.macos.4 | codebase/renderer/features/dictation/components/HotkeyGuidanceAccordion.tsx | 42 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyGuidance.recommended.windows.0 | codebase/renderer/features/dictation/components/HotkeyGuidanceAccordion.tsx | 45 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyGuidance.recommended.windows.1 | codebase/renderer/features/dictation/components/HotkeyGuidanceAccordion.tsx | 46 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyGuidance.recommended.windows.2 | codebase/renderer/features/dictation/components/HotkeyGuidanceAccordion.tsx | 47 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyGuidance.recommended.windows.3 | codebase/renderer/features/dictation/components/HotkeyGuidanceAccordion.tsx | 48 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyGuidance.recommended.linux.0 | codebase/renderer/features/dictation/components/HotkeyGuidanceAccordion.tsx | 51 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyGuidance.recommended.linux.1 | codebase/renderer/features/dictation/components/HotkeyGuidanceAccordion.tsx | 52 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyGuidance.recommended.linux.2 | codebase/renderer/features/dictation/components/HotkeyGuidanceAccordion.tsx | 53 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyGuidance.recommended.linux.3 | codebase/renderer/features/dictation/components/HotkeyGuidanceAccordion.tsx | 54 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyGuidance.recommended.linux.4 | codebase/renderer/features/dictation/components/HotkeyGuidanceAccordion.tsx | 55 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyGuidance.validationRules.0 | codebase/renderer/features/dictation/components/HotkeyGuidanceAccordion.tsx | 60 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyGuidance.validationRules.1 | codebase/renderer/features/dictation/components/HotkeyGuidanceAccordion.tsx | 61 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyGuidance.validationRules.2 | codebase/renderer/features/dictation/components/HotkeyGuidanceAccordion.tsx | 62 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyGuidance.validationRules.3 | codebase/renderer/features/dictation/components/HotkeyGuidanceAccordion.tsx | 63 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyGuidance.platforms.macos | codebase/renderer/features/dictation/components/HotkeyGuidanceAccordion.tsx | 67 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyGuidance.platforms.windows | codebase/renderer/features/dictation/components/HotkeyGuidanceAccordion.tsx | 68 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyGuidance.platforms.linux | codebase/renderer/features/dictation/components/HotkeyGuidanceAccordion.tsx | 69 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyGuidance.blockedDescription | codebase/renderer/features/dictation/components/HotkeyGuidanceAccordion.tsx | 83 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyGuidance.showFewer | codebase/renderer/features/dictation/components/HotkeyGuidanceAccordion.tsx | 104 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyGuidance.showAll | codebase/renderer/features/dictation/components/HotkeyGuidanceAccordion.tsx | 104 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyGuidance.recommendedTitle | codebase/renderer/features/dictation/components/HotkeyGuidanceAccordion.tsx | 126 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyGuidance.rulesTitle | codebase/renderer/features/dictation/components/HotkeyGuidanceAccordion.tsx | 137 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyGuidance.blockedTitle | codebase/renderer/features/dictation/components/HotkeyGuidanceAccordion.tsx | 148 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyGuidance.examplesTitle | codebase/renderer/features/dictation/components/HotkeyGuidanceAccordion.tsx | 155 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyGuidance.title | codebase/renderer/features/dictation/components/HotkeyGuidanceAccordion.tsx | 176 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyGuidance.description | codebase/renderer/features/dictation/components/HotkeyGuidanceAccordion.tsx | 177 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyInput.remove | codebase/renderer/features/dictation/components/HotkeyInput.tsx | 481 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyInput.ariaLabel | codebase/renderer/features/dictation/components/HotkeyInput.tsx | 506 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyInput.listening | codebase/renderer/features/dictation/components/HotkeyInput.tsx | 531 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyInput.fnHeldHint | codebase/renderer/features/dictation/components/HotkeyInput.tsx | 548 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyInput.pressAnyKeyMac | codebase/renderer/features/dictation/components/HotkeyInput.tsx | 554 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyInput.pressAnyKey | codebase/renderer/features/dictation/components/HotkeyInput.tsx | 554 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyInput.clickToChange | codebase/renderer/features/dictation/components/HotkeyInput.tsx | 592 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyInput.clickToSet | codebase/renderer/features/dictation/components/HotkeyInput.tsx | 598 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyInput.ariaLabel | codebase/renderer/features/dictation/components/HotkeyInput.tsx | 612 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyInput.recording | codebase/renderer/features/dictation/components/HotkeyInput.tsx | 642 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyInput.fnCaptureHint | codebase/renderer/features/dictation/components/HotkeyInput.tsx | 656 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyInput.keyHint | codebase/renderer/features/dictation/components/HotkeyInput.tsx | 656 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyInput.tryShortcutMac | codebase/renderer/features/dictation/components/HotkeyInput.tsx | 661 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyInput.tryShortcut | codebase/renderer/features/dictation/components/HotkeyInput.tsx | 661 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyInput.hotkeyLabel | codebase/renderer/features/dictation/components/HotkeyInput.tsx | 677 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyInput.globe | codebase/renderer/features/dictation/components/HotkeyInput.tsx | 696 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyInput.clickToChangeLower | codebase/renderer/features/dictation/components/HotkeyInput.tsx | 704 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyInput.clickToSet | codebase/renderer/features/dictation/components/HotkeyInput.tsx | 711 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyInput.duplicate | codebase/renderer/features/dictation/components/HotkeyListInput.tsx | 69 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkeyInput.addAnother | codebase/renderer/features/dictation/components/HotkeyListInput.tsx | 143 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.exportFailed | codebase/renderer/features/dictation/DictionaryView.tsx | 97 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.emptyTitle | codebase/renderer/features/dictation/DictionaryView.tsx | 109 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.emptyDescription | codebase/renderer/features/dictation/DictionaryView.tsx | 111 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.addFirstWord | codebase/renderer/features/dictation/DictionaryView.tsx | 115 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.importList | codebase/renderer/features/dictation/DictionaryView.tsx | 122 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.clearTitle | codebase/renderer/features/dictation/DictionaryView.tsx | 132 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.clearDescription | codebase/renderer/features/dictation/DictionaryView.tsx | 133 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.tabDictionary | codebase/renderer/features/dictation/DictionaryView.tsx | 141 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.tabSnippets | codebase/renderer/features/dictation/DictionaryView.tsx | 144 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.addPlaceholder | codebase/renderer/features/dictation/DictionaryView.tsx | 156 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.addWord | codebase/renderer/features/dictation/DictionaryView.tsx | 168 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.add | codebase/renderer/features/dictation/DictionaryView.tsx | 171 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.importWords | codebase/renderer/features/dictation/DictionaryView.tsx | 177 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.importPlaceholder | codebase/renderer/features/dictation/DictionaryView.tsx | 193 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.separateWithCommas | codebase/renderer/features/dictation/DictionaryView.tsx | 199 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.wordsReady | codebase/renderer/features/dictation/DictionaryView.tsx | 203 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | common.cancel | codebase/renderer/features/dictation/DictionaryView.tsx | 216 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.import | codebase/renderer/features/dictation/DictionaryView.tsx | 219 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.yourDictionary | codebase/renderer/features/dictation/DictionaryView.tsx | 232 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.clearAll | codebase/renderer/features/dictation/DictionaryView.tsx | 237 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.clearAll | codebase/renderer/features/dictation/DictionaryView.tsx | 240 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.exportDictionary | codebase/renderer/features/dictation/DictionaryView.tsx | 244 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.noMatches | codebase/renderer/features/dictation/DictionaryView.tsx | 259 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.editWord | codebase/renderer/features/dictation/DictionaryView.tsx | 289 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.removeWord | codebase/renderer/features/dictation/DictionaryView.tsx | 296 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hotkey.errors.slotConflict | codebase/renderer/features/dictation/hotkeyValidation.ts | 24 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.audioRecording.noAudio.title | codebase/renderer/features/dictation/useAudioRecording.js | 82 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.audioRecording.noAudio.description | codebase/renderer/features/dictation/useAudioRecording.js | 83 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.audioRecording.noAudio.title | codebase/renderer/features/dictation/useAudioRecording.js | 115 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.audioRecording.noAudio.description | codebase/renderer/features/dictation/useAudioRecording.js | 116 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.clipboard.pasteFailed.title | codebase/renderer/features/dictation/useClipboard.ts | 57 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.clipboard.pasteFailed.description | codebase/renderer/features/dictation/useClipboard.ts | 58 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.clipboard.pasteFailed.description | codebase/renderer/features/dictation/useClipboard.ts | 61 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.hotkeyRegistration.errors.enterValidHotkey | codebase/renderer/features/dictation/useHotkeyRegistration.ts | 103 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.hotkeyRegistration.titles.invalidHotkey | codebase/renderer/features/dictation/useHotkeyRegistration.ts | 107 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.hotkeyRegistration.errors.unsupportedShortcut | codebase/renderer/features/dictation/useHotkeyRegistration.ts | 119 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.hotkeyRegistration.titles.invalidHotkey | codebase/renderer/features/dictation/useHotkeyRegistration.ts | 123 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.hotkeyRegistration.errors.couldNotRegister | codebase/renderer/features/dictation/useHotkeyRegistration.ts | 148 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.hotkeyRegistration.titles.notRegistered | codebase/renderer/features/dictation/useHotkeyRegistration.ts | 153 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.hotkeyRegistration.titles.saved | codebase/renderer/features/dictation/useHotkeyRegistration.ts | 166 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.hotkeyRegistration.messages.nowUsing | codebase/renderer/features/dictation/useHotkeyRegistration.ts | 167 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.hotkeyRegistration.errors.failedToRegister | codebase/renderer/features/dictation/useHotkeyRegistration.ts | 177 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.hotkeyRegistration.titles.error | codebase/renderer/features/dictation/useHotkeyRegistration.ts | 182 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.meeting.title | codebase/renderer/features/meetings/MeetingRecordingMount.tsx | 26 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.addToFolder.title | codebase/renderer/features/notes/components/AddNotesToFolderDialog.tsx | 90 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.addToFolder.searchPlaceholder | codebase/renderer/features/notes/components/AddNotesToFolderDialog.tsx | 99 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.addToFolder.noResults | codebase/renderer/features/notes/components/AddNotesToFolderDialog.tsx | 113 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.addToFolder.noNotesAvailable | codebase/renderer/features/notes/components/AddNotesToFolderDialog.tsx | 114 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.list.untitled | codebase/renderer/features/notes/components/AddNotesToFolderDialog.tsx | 140 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.addToFolder.addCount | codebase/renderer/features/notes/components/AddNotesToFolderDialog.tsx | 169 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.editor.stop | codebase/renderer/features/notes/components/DictationWidget.tsx | 95 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.editor.processing | codebase/renderer/features/notes/components/DictationWidget.tsx | 112 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.editor.transcribe | codebase/renderer/features/notes/components/DictationWidget.tsx | 131 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.meetingPill.returnToNote | codebase/renderer/features/notes/components/MeetingRecordingPill.tsx | 64 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.editor.stop | codebase/renderer/features/notes/components/MeetingRecordingPill.tsx | 65 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.speaker.addContact | codebase/renderer/features/notes/components/MeetingTranscriptView.tsx | 65 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.speaker.emailPlaceholder | codebase/renderer/features/notes/components/MeetingTranscriptView.tsx | 83 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.speaker.cancel | codebase/renderer/features/notes/components/MeetingTranscriptView.tsx | 93 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.speaker.save | codebase/renderer/features/notes/components/MeetingTranscriptView.tsx | 100 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.speaker.nameOrEmailPlaceholder | codebase/renderer/features/notes/components/MeetingTranscriptView.tsx | 184 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.speaker.meetingAttendees | codebase/renderer/features/notes/components/MeetingTranscriptView.tsx | 193 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.speaker.knownSpeakers | codebase/renderer/features/notes/components/MeetingTranscriptView.tsx | 213 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.speaker.createNewPrefix | codebase/renderer/features/notes/components/MeetingTranscriptView.tsx | 237 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.speaker.nameOrEmailPlaceholder | codebase/renderer/features/notes/components/MeetingTranscriptView.tsx | 255 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.speaker.you | codebase/renderer/features/notes/components/MeetingTranscriptView.tsx | 326 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.speaker.label | codebase/renderer/features/notes/components/MeetingTranscriptView.tsx | 326 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.speaker.selected | codebase/renderer/features/notes/components/MeetingTranscriptView.tsx | 411 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.speaker.assignTo | codebase/renderer/features/notes/components/MeetingTranscriptView.tsx | 417 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.speaker.deselectAll | codebase/renderer/features/notes/components/MeetingTranscriptView.tsx | 436 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.editor.conversationWillAppear | codebase/renderer/features/notes/components/MeetingTranscriptView.tsx | 529 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.speaker.you | codebase/renderer/features/notes/components/MeetingTranscriptView.tsx | 538 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.speaker.pill.finalizing | codebase/renderer/features/notes/components/MeetingTranscriptView.tsx | 559 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.speaker.pill.defaultingHint | codebase/renderer/features/notes/components/MeetingTranscriptView.tsx | 564 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.speaker.pill.identifying | codebase/renderer/features/notes/components/MeetingTranscriptView.tsx | 565 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.speaker.pill.notLabeled | codebase/renderer/features/notes/components/MeetingTranscriptView.tsx | 566 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.speaker.pill.justYou | codebase/renderer/features/notes/components/MeetingTranscriptView.tsx | 572 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.speaker.pill.othersInCall | codebase/renderer/features/notes/components/MeetingTranscriptView.tsx | 573 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.speaker.pill.decAria | codebase/renderer/features/notes/components/MeetingTranscriptView.tsx | 580 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.speaker.pill.incAria | codebase/renderer/features/notes/components/MeetingTranscriptView.tsx | 589 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.editor.transcribe | codebase/renderer/features/notes/components/NoteBottomBar.tsx | 95 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.editor.untitled | codebase/renderer/features/notes/components/NoteEditor.tsx | 510 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.editor.noteTitle | codebase/renderer/features/notes/components/NoteEditor.tsx | 513 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.editor.noFolder | codebase/renderer/features/notes/components/NoteEditor.tsx | 539 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.context.searchFolders | codebase/renderer/features/notes/components/NoteEditor.tsx | 554 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.context.noResults | codebase/renderer/features/notes/components/NoteEditor.tsx | 579 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.folders.folderName | codebase/renderer/features/notes/components/NoteEditor.tsx | 604 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.context.newFolder | codebase/renderer/features/notes/components/NoteEditor.tsx | 617 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.editor.saving | codebase/renderer/features/notes/components/NoteEditor.tsx | 628 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.editor.transcript | codebase/renderer/features/notes/components/NoteEditor.tsx | 655 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.editor.notes | codebase/renderer/features/notes/components/NoteEditor.tsx | 670 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.editor.export | codebase/renderer/features/notes/components/NoteEditor.tsx | 679 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.editor.asTranscriptText | codebase/renderer/features/notes/components/NoteEditor.tsx | 692 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.editor.asSubtitles | codebase/renderer/features/notes/components/NoteEditor.tsx | 699 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.editor.asTranscriptMarkdown | codebase/renderer/features/notes/components/NoteEditor.tsx | 706 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.editor.asJson | codebase/renderer/features/notes/components/NoteEditor.tsx | 713 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.editor.asMarkdown | codebase/renderer/features/notes/components/NoteEditor.tsx | 723 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.editor.asPlainText | codebase/renderer/features/notes/components/NoteEditor.tsx | 730 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.editor.startWriting | codebase/renderer/features/notes/components/NoteEditor.tsx | 774 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.list.timeNow | codebase/renderer/features/notes/components/NoteListItem.tsx | 75 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.list.minutesAgo | codebase/renderer/features/notes/components/NoteListItem.tsx | 76 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.list.hoursAgo | codebase/renderer/features/notes/components/NoteListItem.tsx | 77 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.list.daysAgo | codebase/renderer/features/notes/components/NoteListItem.tsx | 78 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.list.untitled | codebase/renderer/features/notes/components/NoteListItem.tsx | 135 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.context.showInFileManager | codebase/renderer/features/notes/components/NoteListItem.tsx | 174 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.context.moveToFolder | codebase/renderer/features/notes/components/NoteListItem.tsx | 185 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.context.searchFolders | codebase/renderer/features/notes/components/NoteListItem.tsx | 202 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.context.noResults | codebase/renderer/features/notes/components/NoteListItem.tsx | 229 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.folders.folderName | codebase/renderer/features/notes/components/NoteListItem.tsx | 252 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.context.newFolder | codebase/renderer/features/notes/components/NoteListItem.tsx | 265 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.context.delete | codebase/renderer/features/notes/components/NoteListItem.tsx | 279 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.participants.attendee | codebase/renderer/features/notes/components/NoteParticipants.tsx | 128 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.participants.attendees | codebase/renderer/features/notes/components/NoteParticipants.tsx | 128 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.participants.addAttendees | codebase/renderer/features/notes/components/NoteParticipants.tsx | 129 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.participants.addPlaceholder | codebase/renderer/features/notes/components/NoteParticipants.tsx | 151 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.participants.typeEmail | codebase/renderer/features/notes/components/NoteParticipants.tsx | 175 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.participants.me | codebase/renderer/features/notes/components/NoteParticipants.tsx | 195 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.participants.typeEmail | codebase/renderer/features/notes/components/NoteParticipants.tsx | 213 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.folders.deleteTitle | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 170 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.folders.deleteDescription | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 173 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.folders.deleteDescriptionEmpty | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 174 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.folders.deleteConfirm | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 175 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.list.untitledNote | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 301 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.list.untitledNote | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 344 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.folders.couldNotCreate | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 404 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.sidebar.newNote | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 509 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.sidebar.searchNotes | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 522 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.folders.title | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 530 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.context.newFolder | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 536 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.context.showInFileManager | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 651 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.context.rename | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 666 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.context.delete | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 677 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.folders.folderName | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 702 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.list.title | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 714 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.list.newNote | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 720 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.empty.emptyFolder | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 793 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.empty.createNote | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 801 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.addToFolder.addExisting | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 807 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.empty.title | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 973 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.empty.description | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 976 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.empty.createNote | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 984 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.addToFolder.addExisting | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 990 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.empty.selectTitle | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 997 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.empty.selectDescription | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 1000 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.upload.newFolder | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 1030 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.sidebar.newNote | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 1030 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.upload.folderName | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 1037 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.folders.folderName | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 1042 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.folders.title | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 1053 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.upload.selectFolder | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 1057 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.upload.newFolder | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 1069 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | common.back | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 1088 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.upload.create | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 1091 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.upload.cancel | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 1097 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.upload.create | codebase/renderer/features/notes/components/PersonalNotesView.tsx | 1100 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.folders.couldNotCreate | codebase/renderer/features/notes/useFolderManagement.ts | 168 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.folders.couldNotRename | codebase/renderer/features/notes/useFolderManagement.ts | 190 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | notes.folders.couldNotDelete | codebase/renderer/features/notes/useFolderManagement.ts | 210 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | onboarding.finish.title | codebase/renderer/features/onboarding/components/FinishStep.tsx | 22 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | onboarding.finish.localDescription | codebase/renderer/features/onboarding/components/FinishStep.tsx | 24 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | onboarding.finish.openSettings | codebase/renderer/features/onboarding/components/FinishStep.tsx | 35 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | onboarding.finish.skipForNow | codebase/renderer/features/onboarding/components/FinishStep.tsx | 44 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | onboarding.meeting.title | codebase/renderer/features/onboarding/components/MeetingSetupStep.tsx | 46 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | onboarding.meeting.description | codebase/renderer/features/onboarding/components/MeetingSetupStep.tsx | 48 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | onboarding.meeting.notification.title | codebase/renderer/features/onboarding/components/MeetingSetupStep.tsx | 56 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | onboarding.meeting.notification.body | codebase/renderer/features/onboarding/components/MeetingSetupStep.tsx | 57 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | onboarding.meeting.notification.cta | codebase/renderer/features/onboarding/components/MeetingSetupStep.tsx | 58 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | onboarding.meeting.autoDetect | codebase/renderer/features/onboarding/components/MeetingSetupStep.tsx | 64 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | onboarding.meeting.hotkeyLabel | codebase/renderer/features/onboarding/components/MeetingSetupStep.tsx | 71 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | onboarding.meeting.hotkeyHint | codebase/renderer/features/onboarding/components/MeetingSetupStep.tsx | 74 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | settingsPage.general.meetingHotkey.clear | codebase/renderer/features/onboarding/components/MeetingSetupStep.tsx | 97 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | onboarding.useCase.title | codebase/renderer/features/onboarding/components/UseCaseStep.tsx | 29 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | onboarding.useCase.description | codebase/renderer/features/onboarding/components/UseCaseStep.tsx | 32 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | onboarding.useCase.selectHint | codebase/renderer/features/onboarding/components/UseCaseStep.tsx | 38 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | onboarding.useCase.noteLabel | codebase/renderer/features/onboarding/components/UseCaseStep.tsx | 54 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | onboarding.useCase.notePlaceholder | codebase/renderer/features/onboarding/components/UseCaseStep.tsx | 60 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | postMigration.title | codebase/renderer/features/onboarding/PostMigrationOnboarding.tsx | 39 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | postMigration.description | codebase/renderer/features/onboarding/PostMigrationOnboarding.tsx | 40 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | postMigration.remindLater | codebase/renderer/features/onboarding/PostMigrationOnboarding.tsx | 47 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | postMigration.done | codebase/renderer/features/onboarding/PostMigrationOnboarding.tsx | 50 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.permissions.warning.messages.macos | codebase/renderer/features/settings/components/MicPermissionWarning.tsx | 41 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.permissions.warning.soundLabel | codebase/renderer/features/settings/components/MicPermissionWarning.tsx | 42 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.permissions.warning.privacyLabel | codebase/renderer/features/settings/components/MicPermissionWarning.tsx | 43 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.permissions.warning.messages.windows | codebase/renderer/features/settings/components/MicPermissionWarning.tsx | 47 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.permissions.warning.soundLabel | codebase/renderer/features/settings/components/MicPermissionWarning.tsx | 48 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.permissions.warning.privacyLabel | codebase/renderer/features/settings/components/MicPermissionWarning.tsx | 49 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.permissions.warning.messages.linux | codebase/renderer/features/settings/components/MicPermissionWarning.tsx | 53 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.permissions.warning.soundLabel | codebase/renderer/features/settings/components/MicPermissionWarning.tsx | 54 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | pasteToolsInfo.title | codebase/renderer/features/settings/components/PasteToolsInfo.tsx | 26 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | pasteToolsInfo.checking | codebase/renderer/features/settings/components/PasteToolsInfo.tsx | 27 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | pasteToolsInfo.readyTitle | codebase/renderer/features/settings/components/PasteToolsInfo.tsx | 47 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | pasteToolsInfo.windowsReady | codebase/renderer/features/settings/components/PasteToolsInfo.tsx | 50 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | pasteToolsInfo.xwaylandAppsOnly | codebase/renderer/features/settings/components/PasteToolsInfo.tsx | 68 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | pasteToolsInfo.methodReady | codebase/renderer/features/settings/components/PasteToolsInfo.tsx | 69 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | pasteToolsInfo.readyTitle | codebase/renderer/features/settings/components/PasteToolsInfo.tsx | 78 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | pasteToolsInfo.usingMethodPrefix | codebase/renderer/features/settings/components/PasteToolsInfo.tsx | 81 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | pasteToolsInfo.optionalEnableTitle | codebase/renderer/features/settings/components/PasteToolsInfo.tsx | 107 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | pasteToolsInfo.waylandClipboardTitle | codebase/renderer/features/settings/components/PasteToolsInfo.tsx | 108 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | pasteToolsInfo.installPrefix | codebase/renderer/features/settings/components/PasteToolsInfo.tsx | 114 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | pasteToolsInfo.installCommands.fedoraRhel | codebase/renderer/features/settings/components/PasteToolsInfo.tsx | 122 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | pasteToolsInfo.installCommands.debianUbuntu | codebase/renderer/features/settings/components/PasteToolsInfo.tsx | 126 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | pasteToolsInfo.installCommands.archLinux | codebase/renderer/features/settings/components/PasteToolsInfo.tsx | 130 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | pasteToolsInfo.installCommands.debianUbuntuMint | codebase/renderer/features/settings/components/PasteToolsInfo.tsx | 137 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | pasteToolsInfo.installCommands.fedoraRhel | codebase/renderer/features/settings/components/PasteToolsInfo.tsx | 141 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | pasteToolsInfo.installCommands.archLinux | codebase/renderer/features/settings/components/PasteToolsInfo.tsx | 145 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | pasteToolsInfo.noteXwaylandAlso | codebase/renderer/features/settings/components/PasteToolsInfo.tsx | 154 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | pasteToolsInfo.noteXwaylandOnly | codebase/renderer/features/settings/components/PasteToolsInfo.tsx | 160 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | pasteToolsInfo.waylandClipboardDescription | codebase/renderer/features/settings/components/PasteToolsInfo.tsx | 166 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | pasteToolsInfo.withoutToolPrefix | codebase/renderer/features/settings/components/PasteToolsInfo.tsx | 173 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | pasteToolsInfo.recheckChecking | codebase/renderer/features/settings/components/PasteToolsInfo.tsx | 182 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | pasteToolsInfo.recheck | codebase/renderer/features/settings/components/PasteToolsInfo.tsx | 182 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | onboarding.permissions.microphoneTitle | codebase/renderer/features/settings/components/PermissionsSection.tsx | 34 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | onboarding.permissions.microphoneDescription | codebase/renderer/features/settings/components/PermissionsSection.tsx | 35 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | onboarding.permissions.grantAccess | codebase/renderer/features/settings/components/PermissionsSection.tsx | 38 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | onboarding.permissions.accessibilityTitle | codebase/renderer/features/settings/components/PermissionsSection.tsx | 44 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | onboarding.permissions.accessibilityDescription | codebase/renderer/features/settings/components/PermissionsSection.tsx | 45 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | onboarding.permissions.grantAccess | codebase/renderer/features/settings/components/PermissionsSection.tsx | 48 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | onboarding.permissions.recommended | codebase/renderer/features/settings/components/PermissionsSection.tsx | 49 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | onboarding.permissions.accessibilityTroubleshooting | codebase/renderer/features/settings/components/PermissionsSection.tsx | 52 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | onboarding.permissions.systemAudioTitle | codebase/renderer/features/settings/components/PermissionsSection.tsx | 61 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | onboarding.permissions.systemAudioDescription | codebase/renderer/features/settings/components/PermissionsSection.tsx | 62 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | onboarding.permissions.grantAccess | codebase/renderer/features/settings/components/PermissionsSection.tsx | 65 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | onboarding.permissions.recommended | codebase/renderer/features/settings/components/PermissionsSection.tsx | 68 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | onboarding.permissions.optional | codebase/renderer/features/settings/components/PermissionsSection.tsx | 69 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.permissions.paths.windowsMicrophone | codebase/renderer/features/settings/usePermissions.ts | 41 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.permissions.paths.linuxSound | codebase/renderer/features/settings/usePermissions.ts | 42 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.permissions.paths.defaultSound | codebase/renderer/features/settings/usePermissions.ts | 44 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.permissions.paths.windowsMicrophone | codebase/renderer/features/settings/usePermissions.ts | 50 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.permissions.paths.linuxPrivacy | codebase/renderer/features/settings/usePermissions.ts | 51 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.permissions.paths.defaultPrivacy | codebase/renderer/features/settings/usePermissions.ts | 53 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.permissions.micErrors.accessFailed | codebase/renderer/features/settings/usePermissions.ts | 75 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.permissions.micErrors.noMicrophones | codebase/renderer/features/settings/usePermissions.ts | 85 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.permissions.micErrors.permissionDenied | codebase/renderer/features/settings/usePermissions.ts | 89 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.permissions.micErrors.couldNotStart | codebase/renderer/features/settings/usePermissions.ts | 93 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.permissions.micErrors.noActiveInput | codebase/renderer/features/settings/usePermissions.ts | 97 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.permissions.micErrors.unknown | codebase/renderer/features/settings/usePermissions.ts | 100 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.permissions.micErrors.unknownFallback | codebase/renderer/features/settings/usePermissions.ts | 101 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.permissions.settingsTitles.microphone | codebase/renderer/features/settings/usePermissions.ts | 137 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.permissions.settingsTitles.sound | codebase/renderer/features/settings/usePermissions.ts | 138 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.permissions.settingsTitles.accessibility | codebase/renderer/features/settings/usePermissions.ts | 139 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.permissions.settingsErrors.unableToOpenMicrophone | codebase/renderer/features/settings/usePermissions.ts | 142 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.permissions.settingsErrors.unableToOpenSound | codebase/renderer/features/settings/usePermissions.ts | 143 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.permissions.settingsErrors.unableToOpenAccessibility | codebase/renderer/features/settings/usePermissions.ts | 144 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.permissions.micUnavailable | codebase/renderer/features/settings/usePermissions.ts | 174 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.permissions.titles.microphoneUnavailable | codebase/renderer/features/settings/usePermissions.ts | 178 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | hooks.permissions.titles.microphonePermissionRequired | codebase/renderer/features/settings/usePermissions.ts | 209 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.snippets.editTitle | codebase/renderer/features/snippets/SnippetsView.tsx | 60 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.snippets.dialogDescription | codebase/renderer/features/snippets/SnippetsView.tsx | 61 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.snippets.triggerLabel | codebase/renderer/features/snippets/SnippetsView.tsx | 66 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.snippets.triggerPlaceholder | codebase/renderer/features/snippets/SnippetsView.tsx | 72 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.snippets.duplicate | codebase/renderer/features/snippets/SnippetsView.tsx | 76 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.snippets.replacementLabel | codebase/renderer/features/snippets/SnippetsView.tsx | 81 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.snippets.replacementPlaceholder | codebase/renderer/features/snippets/SnippetsView.tsx | 88 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | common.cancel | codebase/renderer/features/snippets/SnippetsView.tsx | 94 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | common.save | codebase/renderer/features/snippets/SnippetsView.tsx | 97 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.snippets.addPlaceholder | codebase/renderer/features/snippets/SnippetsView.tsx | 181 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.snippets.create | codebase/renderer/features/snippets/SnippetsView.tsx | 193 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.add | codebase/renderer/features/snippets/SnippetsView.tsx | 196 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.snippets.duplicate | codebase/renderer/features/snippets/SnippetsView.tsx | 201 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.snippets.replacementPlaceholder | codebase/renderer/features/snippets/SnippetsView.tsx | 216 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | common.cancel | codebase/renderer/features/snippets/SnippetsView.tsx | 231 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.snippets.create | codebase/renderer/features/snippets/SnippetsView.tsx | 234 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.snippets.title | codebase/renderer/features/snippets/SnippetsView.tsx | 246 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.snippets.emptyTitle | codebase/renderer/features/snippets/SnippetsView.tsx | 256 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.snippets.emptyTitleAccent | codebase/renderer/features/snippets/SnippetsView.tsx | 257 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.snippets.emptyDescription | codebase/renderer/features/snippets/SnippetsView.tsx | 260 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.snippets.new | codebase/renderer/features/snippets/SnippetsView.tsx | 264 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.noMatches | codebase/renderer/features/snippets/SnippetsView.tsx | 284 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.snippets.edit | codebase/renderer/features/snippets/SnippetsView.tsx | 301 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | dictionary.snippets.remove | codebase/renderer/features/snippets/SnippetsView.tsx | 308 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | languageSelector.searchPlaceholder | codebase/renderer/features/transcription/components/LanguageSelector.tsx | 210 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | languageSelector.noLanguagesFound | codebase/renderer/features/transcription/components/LanguageSelector.tsx | 230 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | transcriptionPreview.ready | codebase/renderer/features/transcription/TranscriptionPreviewOverlay.tsx | 226 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | transcriptionPreview.polishing | codebase/renderer/features/transcription/TranscriptionPreviewOverlay.tsx | 228 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | transcriptionPreview.listening | codebase/renderer/features/transcription/TranscriptionPreviewOverlay.tsx | 229 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | transcriptionPreview.copied | codebase/renderer/features/transcription/TranscriptionPreviewOverlay.tsx | 294 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | transcriptionPreview.copy | codebase/renderer/features/transcription/TranscriptionPreviewOverlay.tsx | 295 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | transcriptionPreview.waitingForInput | codebase/renderer/features/transcription/TranscriptionPreviewOverlay.tsx | 348 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | controlPanel.history.dateGroups.today | codebase/renderer/shared/utilities/dateFormatting.ts | 14 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | upcoming.tomorrow | codebase/renderer/shared/utilities/dateFormatting.ts | 15 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | controlPanel.history.dateGroups.today | codebase/renderer/shared/utilities/dateFormatting.ts | 27 | EXTRACTED SOURCE ANCHOR; registry-linked |
| Translation key | controlPanel.history.dateGroups.yesterday | codebase/renderer/shared/utilities/dateFormatting.ts | 29 | EXTRACTED SOURCE ANCHOR; registry-linked |

## Build and packaging inclusion

- Package/build authority: `codebase/package.json`; lock authority: `codebase/package-lock.json`.
- Offline asset inclusion and verification: `codebase/scripts/packaging/prepare-offline-assets.js`, `codebase/scripts/verification/verify-offline-assets.js`, and `codebase/resources/bin/asset-manifest.json`.
- Installer inclusion: electron-builder configuration in `codebase/package.json`; generated copies are inventory evidence, never source authority.
- Historical migration references remain mapped in `DATABASE_AND_DATA_GRAPH.md` and are not active runtime edges merely because old terms appear.
