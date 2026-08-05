const fs = require("fs");
const { promises: fsPromises } = require("fs");
const path = require("path");
const { app } = require("electron");
const debugLogger = require("../../infrastructure/runtime/debugLogger");
const {
  createImportSignal,
  cleanupStaleImports,
  extractArchive,
  findFile,
  findFiles,
  importLocalFile,
} = require("./downloadUtils");
const { getSafeTempDir } = require("../../infrastructure/runtime/safeTempDir");

const PLATFORM_BINARY_NAMES = {
  linux: "whisper-server-linux-x64-cuda",
  win32: "whisper-server-win32-x64-cuda.exe",
};

const PLATFORM_ASSET_NAMES = {
  linux: "whisper-server-linux-x64-cuda.zip",
  win32: "whisper-server-win32-x64-cuda.zip",
};

const COMPANION_PATTERNS = {
  linux: /\.so(\.\d+)*$/,
  win32: /\.dll$/i,
};

function isSupportedPlatform() {
  return process.platform === "linux" || process.platform === "win32";
}

class WhisperCudaManager {
  constructor() {
    this._binDir = null;
    this._importSignal = null;
    this._importing = false;
  }

  getCudaBinaryDir() {
    if (!this._binDir) {
      this._binDir = path.join(app.getPath("userData"), "bin");
      fs.mkdirSync(this._binDir, { recursive: true });
    }
    return this._binDir;
  }

  getCudaBinaryPath() {
    if (!isSupportedPlatform()) return null;

    const binaryName = PLATFORM_BINARY_NAMES[process.platform];
    const binaryPath = path.join(this.getCudaBinaryDir(), binaryName);
    return fs.existsSync(binaryPath) ? binaryPath : null;
  }

  isInstalled() {
    return !!this.getCudaBinaryPath();
  }

  isImporting() {
    return this._importing;
  }

  async importArchive(progressCallback) {
    if (this._importing) throw new Error("Import already in progress");
    if (!isSupportedPlatform()) {
      throw new Error(`CUDA binaries not available for ${process.platform}`);
    }

    this._importing = true;

    let zipPath = null;
    let extractDir = null;

    try {
      const assetName = PLATFORM_ASSET_NAMES[process.platform];
      const binDir = this.getCudaBinaryDir();

      await cleanupStaleImports(binDir);

      const tempDir = getSafeTempDir();
      zipPath = path.join(tempDir, `cuda-import-${Date.now()}.zip`);
      extractDir = path.join(tempDir, `temp-extract-${Date.now()}`);
      const { signal, abort } = createImportSignal();
      this._importSignal = { abort };

      await importLocalFile(zipPath, {
        title: `Select CUDA GPU Acceleration Binary Archive (${assetName})`,
        filters: [{ name: "CUDA Binary Archive (*.zip)", extensions: ["zip"] }],
        signal,
        onProgress: (imported, total) => {
          if (progressCallback) {
            progressCallback({
              type: "progress",
              imported_bytes: imported,
              total_bytes: total,
              percentage: total > 0 ? Math.round((imported / total) * 100) : 0,
            });
          }
        },
      });

      await fsPromises.mkdir(extractDir, { recursive: true });
      await extractArchive(zipPath, extractDir);

      const binaryName = PLATFORM_BINARY_NAMES[process.platform];
      const companionPattern = COMPANION_PATTERNS[process.platform];

      const binaryPath = await findFile(extractDir, binaryName);
      if (!binaryPath) {
        throw new Error(`Extraction completed but binary "${binaryName}" not found in archive`);
      }

      const dest = path.join(binDir, binaryName);
      await fsPromises.copyFile(binaryPath, dest);
      if (process.platform === "linux") {
        await fsPromises.chmod(dest, 0o755);
      }

      const libs = await findFiles(extractDir, companionPattern);
      for (const lib of libs) {
        const libDest = path.join(binDir, path.basename(lib));
        await fsPromises.copyFile(lib, libDest);
        if (process.platform === "linux") {
          await fsPromises.chmod(libDest, 0o755);
        }
      }

      debugLogger.info("CUDA binary import complete", {
        path: this.getCudaBinaryPath(),
      });

      if (progressCallback) {
        progressCallback({ type: "complete", percentage: 100 });
      }
    } catch (error) {
      if (error.isAbort || error.message?.includes("cancelled")) {
        throw new Error("Import cancelled by user");
      }
      throw error;
    } finally {
      this._importing = false;
      this._importSignal = null;
      if (zipPath) await fsPromises.unlink(zipPath).catch(() => {});
      if (extractDir)
        await fsPromises.rm(extractDir, { recursive: true, force: true }).catch(() => {});
    }
  }

  async cancelImport() {
    if (this._importSignal) {
      this._importSignal.abort();
      this._importSignal = null;
      return { success: true, message: "Import cancelled" };
    }
    return { success: false, error: "No active import to cancel" };
  }

  async delete() {
    if (!isSupportedPlatform()) {
      return { success: false, error: "Not supported on this platform" };
    }

    const binDir = this.getCudaBinaryDir();
    const binaryName = PLATFORM_BINARY_NAMES[process.platform];
    const companionPattern = COMPANION_PATTERNS[process.platform];

    let deletedCount = 0;
    let freedBytes = 0;

    try {
      const entries = await fsPromises.readdir(binDir);

      for (const entry of entries) {
        if (entry === binaryName || companionPattern.test(entry)) {
          const filePath = path.join(binDir, entry);
          try {
            const stats = await fsPromises.stat(filePath);
            await fsPromises.unlink(filePath);
            freedBytes += stats.size;
            deletedCount++;
          } catch {
            // Continue with remaining files
          }
        }
      }
    } catch {
      // Directory may not exist
    }

    debugLogger.info("CUDA binary deleted", { deletedCount, freedBytes });

    return {
      success: deletedCount > 0,
      deleted_count: deletedCount,
      freed_bytes: freedBytes,
      freed_mb: Math.round(freedBytes / (1024 * 1024)),
    };
  }
}

module.exports = WhisperCudaManager;
