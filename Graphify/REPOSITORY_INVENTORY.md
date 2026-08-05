# Repository Inventory

## Root and provenance

- Root: `C:\Users\mhyah\Downloads\Code\Mnemora`.
- Current application folder: `codebase/`; planned `Codebase` spelling is not a completed move.
- Derived planning folder: `Graphify/`.
- Git: present; details are in `RUN_STATE.md` and the 2026-08-05 audit baseline in `PLANNING_BASELINE.md`.
- Authoritative inventory: 24842 files in `REPOSITORY_FILE_INVENTORY.json`; derived Graphify outputs are validated separately.

## Application roots

- Package root: `codebase/package.json`; npm lock: `codebase/package-lock.json`.
- Main process: `codebase/main/`; Electron entry: `codebase/main/index.js`.
- Renderer: `codebase/renderer/`; app entry: `codebase/renderer/app/main.jsx`; route owner: `codebase/renderer/app/AppRouter.jsx::AppRouter`.
- Preload: `codebase/preload/index.js`; renderer contract: `codebase/renderer/shared/types/electron.ts`.
- IPC: `codebase/main/ipc/ipcHandlers.js::setupIpcHandlers` plus preload exposures and renderer declarations.
- Features: `codebase/main/features/{dictation,meetings,notes,search,transcription}/` and matching renderer feature folders.
- Persistence/migrations/backup: `codebase/main/infrastructure/persistence/`.
- Runtime/network/process ownership: `codebase/main/infrastructure/runtime/`.
- Native/platform source: `codebase/native/` and `codebase/main/platform/`.
- Bundled binaries/models: `codebase/resources/bin/`; manifest: `codebase/resources/bin/asset-manifest.json`.
- Build and packaging: `codebase/scripts/{build,packaging,verification,downloads}/`, `codebase/electron-builder.json`, `codebase/packaging/`.
- Tests and fixtures: `codebase/tests/unit/`, `codebase/tests/fixtures/`; planned real integration additions are in the task contracts.
- Generated/vendor roots: `codebase/node_modules/` and `codebase/build-output/`; inventoried but not application source authority.
