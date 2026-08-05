const crypto = require("crypto");
const fs = require("fs");
const { promises: fsPromises } = require("fs");
const path = require("path");
const { pipeline } = require("stream/promises");
const debugLogger = require("../../infrastructure/runtime/debugLogger");

const STALE_TMP_AGE_MS = 24 * 60 * 60 * 1000;

function createImportSignal() {
  const signal = { aborted: false, onAbort: null };
  return {
    signal,
    abort() {
      signal.aborted = true;
      if (typeof signal.onAbort === "function") signal.onAbort();
    },
  };
}

async function validateFileSize(filePath, expectedSizeBytes, tolerancePercent = 10) {
  const stats = await fsPromises.stat(filePath);
  const minSize = expectedSizeBytes * (1 - tolerancePercent / 100);
  if (stats.size < minSize) {
    await fsPromises.unlink(filePath).catch(() => {});
    throw Object.assign(
      new Error(
        `Imported file is too small: ${Math.round(stats.size / 1_000_000)}MB; ` +
          `expected at least ${Math.round(minSize / 1_000_000)}MB`
      ),
      { code: "ERR_FILE_TOO_SMALL" }
    );
  }
  return stats.size;
}

async function cleanupStaleImports(directory) {
  try {
    const entries = await fsPromises.readdir(directory);
    const now = Date.now();
    for (const entry of entries) {
      if (!entry.endsWith(".tmp") && !entry.startsWith("temp-extract-")) continue;
      const fullPath = path.join(directory, entry);
      try {
        const stats = await fsPromises.stat(fullPath);
        if (now - stats.mtimeMs <= STALE_TMP_AGE_MS) continue;
        if (stats.isDirectory()) await fsPromises.rm(fullPath, { recursive: true, force: true });
        else await fsPromises.unlink(fullPath);
        debugLogger.info("Cleaned up stale local import artifact", { path: fullPath });
      } catch {
        // A concurrent operation may have removed the temporary path.
      }
    }
  } catch {
    // The model directory may not exist on a clean install.
  }
}

async function checkDiskSpace(directory, requiredBytes) {
  try {
    await fsPromises.mkdir(directory, { recursive: true });
    const stats = await fsPromises.statfs(directory);
    const availableBytes = stats.bavail * stats.bsize;
    return { ok: availableBytes >= requiredBytes, availableBytes };
  } catch {
    return { ok: true, availableBytes: Infinity };
  }
}

function isSafeArchivePath(value) {
  if (typeof value !== "string" || value.includes("\0")) return false;
  const normalized = value.replace(/\\/g, "/");
  if (!normalized || normalized.startsWith("/") || /^[A-Za-z]:/.test(normalized)) return false;
  return !normalized.split("/").some((part) => part === "..");
}

function assertSafeTarEntry(entry) {
  if (!isSafeArchivePath(entry.path)) {
    throw new Error(`Archive contains an unsafe path: ${entry.path}`);
  }
  if (["SymbolicLink", "Link"].includes(entry.type)) {
    throw new Error(`Archive links are not allowed: ${entry.path}`);
  }
}

async function inspectTarArchive(archivePath, isBzip2) {
  const tar = require("tar");
  let inspectionError = null;
  const inspector = tar.t({
    strict: true,
    onentry(entry) {
      try {
        assertSafeTarEntry(entry);
      } catch (error) {
        inspectionError ||= error;
      }
      entry.resume();
    },
  });

  if (isBzip2) {
    const unbzip2 = require("unbzip2-stream");
    await pipeline(fs.createReadStream(archivePath), unbzip2(), inspector);
  } else {
    await pipeline(fs.createReadStream(archivePath), inspector);
  }
  if (inspectionError) throw inspectionError;
}

async function extractArchive(archivePath, destDir) {
  await fsPromises.mkdir(destDir, { recursive: true });
  const lower = archivePath.toLowerCase();
  const isTar = /\.(?:tar|tar\.gz|tgz|tar\.bz2|tbz2)$/.test(lower);
  if (isTar) {
    const isBzip2 = /\.(?:tar\.bz2|tbz2)$/.test(lower);
    await inspectTarArchive(archivePath, isBzip2);
    const tar = require("tar");
    const options = {
      cwd: destDir,
      strict: true,
      preservePaths: false,
      filter: (entryPath, entry) => {
        assertSafeTarEntry(entry);
        return true;
      },
    };
    if (isBzip2) {
      const unbzip2 = require("unbzip2-stream");
      await pipeline(fs.createReadStream(archivePath), unbzip2(), tar.x(options));
    } else {
      await tar.x({ ...options, file: archivePath });
    }
    return;
  }

  const handle = await fsPromises.open(archivePath, "r");
  const signature = Buffer.alloc(2);
  try {
    await handle.read(signature, 0, signature.length, 0);
  } finally {
    await handle.close();
  }
  if (signature[0] !== 0x50 || signature[1] !== 0x4b) {
    throw new Error("Zip extraction failed: invalid ZIP archive");
  }

  const unzipper = require("unzipper");
  let directory;
  try {
    directory = await unzipper.Open.file(archivePath);
  } catch (error) {
    throw new Error(`Zip extraction failed: ${error.message}`);
  }
  for (const entry of directory.files) {
    if (!isSafeArchivePath(entry.path)) {
      throw new Error(`Archive contains an unsafe path: ${entry.path}`);
    }
    if (entry.type !== "File" && entry.type !== "Directory") {
      throw new Error(`Archive links are not allowed: ${entry.path}`);
    }
  }
  await directory.extract({ path: destDir });
}

async function sha256(filePath) {
  const hash = crypto.createHash("sha256");
  await pipeline(fs.createReadStream(filePath), hash);
  return hash.digest("hex");
}

async function validateExpectedFiles(rootDir, expectedFiles = []) {
  for (const relativePath of expectedFiles) {
    if (!isSafeArchivePath(relativePath)) throw new Error(`Unsafe expected path: ${relativePath}`);
    const filePath = path.resolve(rootDir, ...relativePath.split("/"));
    const root = path.resolve(rootDir);
    if (!filePath.startsWith(`${root}${path.sep}`)) throw new Error(`Unsafe expected path: ${relativePath}`);
    const stats = await fsPromises.stat(filePath).catch(() => null);
    if (!stats?.isFile() || stats.size === 0) {
      throw new Error(`Imported package is incomplete: missing ${relativePath}`);
    }
  }
}

async function verifyPackManifest(rootDir) {
  const candidates = ["model-pack.json", "manifest.json"];
  const manifestName = candidates.find((name) => fs.existsSync(path.join(rootDir, name)));
  if (!manifestName) return { verified: false, files: 0 };

  const manifest = JSON.parse(await fsPromises.readFile(path.join(rootDir, manifestName), "utf8"));
  if (!Array.isArray(manifest.assets) || manifest.assets.length === 0) {
    throw new Error(`${manifestName} does not contain a non-empty assets list`);
  }
  for (const asset of manifest.assets) {
    if (!isSafeArchivePath(asset.path) || !/^[a-f0-9]{64}$/i.test(asset.sha256 || "")) {
      throw new Error(`Invalid checksum entry in ${manifestName}`);
    }
    const filePath = path.resolve(rootDir, ...asset.path.split("/"));
    if (!filePath.startsWith(`${path.resolve(rootDir)}${path.sep}`)) {
      throw new Error(`Unsafe checksum path in ${manifestName}: ${asset.path}`);
    }
    const stats = await fsPromises.stat(filePath).catch(() => null);
    if (!stats?.isFile() || (asset.size != null && stats.size !== asset.size)) {
      throw new Error(`Model-pack file is missing or has the wrong size: ${asset.path}`);
    }
    if ((await sha256(filePath)) !== asset.sha256.toLowerCase()) {
      throw new Error(`Model-pack checksum mismatch: ${asset.path}`);
    }
  }
  return { verified: true, files: manifest.assets.length };
}

async function findFile(dir, name, maxDepth = 5, depth = 0) {
  if (depth >= maxDepth) return null;
  const entries = await fsPromises.readdir(dir, { withFileTypes: true });
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      const found = await findFile(full, name, maxDepth, depth + 1);
      if (found) return found;
    } else if (entry.name === name) {
      return full;
    }
  }
  return null;
}

async function findFiles(dir, pattern, maxDepth = 5, depth = 0) {
  if (depth >= maxDepth) return [];
  const results = [];
  const entries = await fsPromises.readdir(dir, { withFileTypes: true });
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) results.push(...(await findFiles(full, pattern, maxDepth, depth + 1)));
    else if (pattern.test(entry.name)) results.push(full);
  }
  return results;
}

async function copyFileWithProgress(sourcePath, destPath, expectedSize, onProgress, signal) {
  const sourceStats = await fsPromises.stat(sourcePath);
  if (expectedSize > 0 && sourceStats.size < expectedSize * 0.9) {
    throw Object.assign(
      new Error(
        `Selected file is too small. Expected at least ${Math.round((expectedSize * 0.9) / 1_000_000)}MB, ` +
          `got ${Math.round(sourceStats.size / 1_000_000)}MB`
      ),
      { code: "ERR_FILE_TOO_SMALL" }
    );
  }

  await fsPromises.mkdir(path.dirname(destPath), { recursive: true });
  const tempPath = `${destPath}.tmp`;
  const readStream = fs.createReadStream(sourcePath);
  const writeStream = fs.createWriteStream(tempPath);
  let copiedBytes = 0;

  return new Promise((resolve, reject) => {
    const abort = () => {
      const error = Object.assign(new Error("Import cancelled by user"), { isAbort: true });
      readStream.destroy(error);
      writeStream.destroy(error);
      fsPromises.unlink(tempPath).catch(() => {});
    };
    if (signal) {
      if (signal.aborted) return abort();
      signal.onAbort = abort;
    }
    readStream.on("data", (chunk) => {
      copiedBytes += chunk.length;
      onProgress?.(copiedBytes, sourceStats.size);
    });
    readStream.on("error", (error) => {
      if (signal) signal.onAbort = null;
      writeStream.destroy();
      reject(error);
    });
    writeStream.on("error", (error) => {
      if (signal) signal.onAbort = null;
      readStream.destroy();
      reject(error);
    });
    writeStream.on("finish", async () => {
      if (signal) signal.onAbort = null;
      try {
        await fsPromises.rename(tempPath, destPath);
      } catch (error) {
        if (error.code !== "EXDEV") return reject(error);
        try {
          await fsPromises.copyFile(tempPath, destPath);
          await fsPromises.unlink(tempPath).catch(() => {});
        } catch (copyError) {
          return reject(copyError);
        }
      }
      resolve({ size: sourceStats.size });
    });
    readStream.pipe(writeStream);
  });
}

async function importLocalFile(destPath, options = {}) {
  const { dialog } = require("electron");
  const {
    title,
    filters,
    expectedSize,
    onProgress,
    isArchive,
    extractDir,
    signal,
    expectedFiles = [],
    validateExtracted,
  } = options;
  const result = await dialog.showOpenDialog({
    title: title || "Select File to Import",
    properties: ["openFile"],
    filters: filters || [{ name: "All Files", extensions: ["*"] }],
  });
  if (result.canceled || !result.filePaths.length) {
    throw Object.assign(new Error("Import cancelled by user"), { isAbort: true });
  }

  const sourcePath = result.filePaths[0];
  if (isArchive && extractDir) {
    debugLogger.info("Extracting local archive", { sourcePath, extractDir });
    const stagingDir = `${extractDir}.import-${process.pid}-${Date.now()}`;
    const previousDir = `${extractDir}.previous-${process.pid}-${Date.now()}`;
    await fsPromises.rm(stagingDir, { recursive: true, force: true });
    await fsPromises.mkdir(path.dirname(extractDir), { recursive: true });
    try {
      if (signal?.aborted) {
        throw Object.assign(new Error("Import cancelled by user"), { isAbort: true });
      }
      onProgress?.(10, 100);
      await extractArchive(sourcePath, stagingDir);
      await validateExpectedFiles(stagingDir, expectedFiles);
      const manifest = await verifyPackManifest(stagingDir);
      await validateExtracted?.(stagingDir, manifest);
      if (signal?.aborted) throw Object.assign(new Error("Import cancelled by user"), { isAbort: true });
      onProgress?.(90, 100);

      const hadPrevious = fs.existsSync(extractDir);
      if (hadPrevious) await fsPromises.rename(extractDir, previousDir);
      try {
        await fsPromises.rename(stagingDir, extractDir);
      } catch (error) {
        if (hadPrevious && fs.existsSync(previousDir)) {
          await fsPromises.rename(previousDir, extractDir).catch(() => {});
        }
        throw error;
      }
      await fsPromises.rm(previousDir, { recursive: true, force: true });
      onProgress?.(100, 100);
      return extractDir;
    } finally {
      await fsPromises.rm(stagingDir, { recursive: true, force: true }).catch(() => {});
      if (!fs.existsSync(extractDir) && fs.existsSync(previousDir)) {
        await fsPromises.rename(previousDir, extractDir).catch(() => {});
      }
    }
  }
  return copyFileWithProgress(sourcePath, destPath, expectedSize, onProgress, signal);
}

module.exports = {
  createImportSignal,
  validateFileSize,
  cleanupStaleImports,
  checkDiskSpace,
  extractArchive,
  isSafeArchivePath,
  validateExpectedFiles,
  verifyPackManifest,
  findFile,
  findFiles,
  copyFileWithProgress,
  importLocalFile,
};
