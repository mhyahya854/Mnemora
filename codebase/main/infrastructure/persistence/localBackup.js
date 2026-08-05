const crypto = require("node:crypto");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const Database = require("better-sqlite3");
const tar = require("tar");

const FORMAT = "mnemora-local-backup";
const FORMAT_VERSION = 1;
const DATABASE_ENTRY = "data/mnemora.sqlite";

function timestamp() {
  return new Date().toISOString().replace(/[:.]/g, "-");
}

function validateRelativePath(value) {
  if (
    typeof value !== "string" ||
    !value ||
    value.includes("\0") ||
    value.includes("\\") ||
    value.includes(":")
  ) {
    throw new Error("Backup manifest contains an unsafe path");
  }
  const normalized = path.posix.normalize(value);
  if (
    normalized !== value ||
    normalized === "." ||
    normalized === ".." ||
    normalized.startsWith("../") ||
    path.posix.isAbsolute(normalized) ||
    /^[A-Za-z]:/.test(normalized)
  ) {
    throw new Error("Backup manifest contains an unsafe path");
  }
  return normalized;
}

function safeJoin(root, relativePath) {
  const safe = validateRelativePath(relativePath);
  const resolvedRoot = path.resolve(root);
  const resolved = path.resolve(resolvedRoot, ...safe.split("/"));
  if (resolved !== resolvedRoot && !resolved.startsWith(`${resolvedRoot}${path.sep}`)) {
    throw new Error("Backup manifest path escapes the bundle");
  }
  return resolved;
}

function isInside(parent, child) {
  const root = path.resolve(parent);
  const target = path.resolve(child);
  return target === root || target.startsWith(`${root}${path.sep}`);
}

function sha256(filePath) {
  const hash = crypto.createHash("sha256");
  const handle = fs.openSync(filePath, "r");
  const buffer = Buffer.allocUnsafe(1024 * 1024);
  try {
    let read;
    while ((read = fs.readSync(handle, buffer, 0, buffer.length, null)) > 0) {
      hash.update(buffer.subarray(0, read));
    }
  } finally {
    fs.closeSync(handle);
  }
  return hash.digest("hex");
}

function listFiles(root, prefix = "") {
  if (!fs.existsSync(root)) return [];
  const files = [];
  for (const entry of fs.readdirSync(root, { withFileTypes: true })) {
    const absolute = path.join(root, entry.name);
    const relative = prefix ? `${prefix}/${entry.name}` : entry.name;
    if (entry.isSymbolicLink()) throw new Error("Backup source cannot contain symbolic links");
    if (entry.isDirectory()) files.push(...listFiles(absolute, relative));
    else if (entry.isFile()) files.push(relative);
  }
  return files.sort();
}

function openBackup(sourcePath) {
  const source = path.resolve(sourcePath);
  const stat = fs.lstatSync(source);
  if (stat.isSymbolicLink()) throw new Error("Backup source cannot be a symbolic link");
  if (stat.isDirectory()) return { root: source, cleanup: () => {} };
  if (!stat.isFile()) throw new Error("Backup source must be a Mnemora archive");

  const root = fs.mkdtempSync(path.join(os.tmpdir(), "mnemora-backup-read-"));
  try {
    let totalSize = 0;
    tar.t({
      file: source,
      sync: true,
      strict: true,
      onentry: (entry) => {
        const entryPath = entry.path.replace(/\/$/, "");
        validateRelativePath(entryPath);
        if (!new Set(["File", "OldFile", "Directory"]).has(entry.type)) {
          throw new Error("Backup archive contains a non-regular entry");
        }
        totalSize += Number(entry.size) || 0;
        if (totalSize > 100 * 1024 * 1024 * 1024) {
          throw new Error("Backup archive is too large");
        }
      },
    });
    tar.x({ file: source, cwd: root, sync: true, strict: true, preservePaths: false });
    return {
      root,
      cleanup: () => fs.rmSync(root, { recursive: true, force: true, maxRetries: 5 }),
    };
  } catch (error) {
    fs.rmSync(root, { recursive: true, force: true, maxRetries: 5 });
    throw error;
  }
}

function inspectDatabase(databasePath) {
  const db = new Database(databasePath, { readonly: true, fileMustExist: true });
  try {
    const quickCheck = db.pragma("quick_check", { simple: true });
    if (quickCheck !== "ok") throw new Error(`Backup database check failed: ${quickCheck}`);
    const tables = new Set(
      db
        .prepare("SELECT name FROM sqlite_master WHERE type = 'table'")
        .all()
        .map((row) => row.name)
    );
    const count = (table) =>
      tables.has(table) ? db.prepare(`SELECT COUNT(*) AS count FROM ${table}`).get().count : 0;
    return {
      schemaVersion: db.pragma("user_version", { simple: true }),
      counts: {
        notes: count("notes"),
        meetings: count("meetings"),
        recordings: count("recordings"),
        transcripts: count("transcripts"),
        tags: count("tags"),
      },
    };
  } finally {
    db.close();
  }
}

function writeManifest(bundlePath, metadata) {
  const files = [DATABASE_ENTRY, ...listFiles(path.join(bundlePath, "audio"), "audio")].map(
    (relativePath) => {
      const filePath = safeJoin(bundlePath, relativePath);
      const stat = fs.statSync(filePath);
      return { path: relativePath, size: stat.size, sha256: sha256(filePath) };
    }
  );
  const manifest = {
    format: FORMAT,
    formatVersion: FORMAT_VERSION,
    createdAt: new Date().toISOString(),
    appVersion: metadata.appVersion || "unknown",
    schemaVersion: Number(metadata.schemaVersion) || 0,
    includes: { database: true, audio: files.some((file) => file.path.startsWith("audio/")) },
    files,
  };
  fs.writeFileSync(path.join(bundlePath, "manifest.json"), JSON.stringify(manifest, null, 2));
  return manifest;
}

async function createBackup({
  database = null,
  databasePath,
  destinationPath,
  audioDirectory = null,
  includeAudio = false,
  appVersion = "unknown",
  schemaVersion = 0,
}) {
  if (!databasePath || !destinationPath) {
    throw new Error("databasePath and destinationPath are required");
  }
  const finalPath = path.resolve(destinationPath);
  if (includeAudio && audioDirectory && isInside(audioDirectory, finalPath)) {
    throw new Error("Backup destination cannot be inside the audio directory it contains");
  }
  if (fs.existsSync(finalPath)) throw new Error("Backup destination already exists");
  fs.mkdirSync(path.dirname(finalPath), { recursive: true });
  const stagingPath = `${finalPath}.tmp-${process.pid}-${Date.now()}`;
  fs.rmSync(stagingPath, { recursive: true, force: true });
  fs.mkdirSync(path.join(stagingPath, "data"), { recursive: true });

  try {
    const snapshotPath = safeJoin(stagingPath, DATABASE_ENTRY);
    if (database) await database.backup(snapshotPath);
    else fs.copyFileSync(databasePath, snapshotPath);

    if (includeAudio && audioDirectory && fs.existsSync(audioDirectory)) {
      fs.cpSync(audioDirectory, path.join(stagingPath, "audio"), {
        recursive: true,
        errorOnExist: true,
      });
      listFiles(path.join(stagingPath, "audio"));
    }

    const manifest = writeManifest(stagingPath, { appVersion, schemaVersion });
    readAndVerifyBundle(stagingPath);
    const entries = ["manifest.json", ...manifest.files.map((file) => file.path)];
    tar.c({ file: finalPath, cwd: stagingPath, gzip: true, sync: true, portable: true }, entries);
    previewBackup(finalPath);
    fs.rmSync(stagingPath, { recursive: true, force: true });
    return { path: finalPath, manifest };
  } catch (error) {
    try {
      fs.rmSync(stagingPath, { recursive: true, force: true });
    } catch {
      // Preserve the creation error; a stale temp directory can be cleaned later.
    }
    fs.rmSync(finalPath, { force: true });
    throw error;
  }
}

function readAndVerifyBundle(bundlePath) {
  const root = path.resolve(bundlePath);
  const manifestPath = path.join(root, "manifest.json");
  const manifestStat = fs.lstatSync(manifestPath);
  if (!manifestStat.isFile() || manifestStat.isSymbolicLink()) {
    throw new Error("Backup manifest is not a regular file");
  }
  const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  if (manifest.format !== FORMAT || manifest.formatVersion !== FORMAT_VERSION) {
    throw new Error("Unsupported Mnemora backup format");
  }
  if (!Array.isArray(manifest.files) || manifest.files.length === 0) {
    throw new Error("Backup manifest has no files");
  }

  const seen = new Set();
  for (const entry of manifest.files) {
    const relativePath = validateRelativePath(entry?.path);
    const pathKey = process.platform === "win32" ? relativePath.toLocaleLowerCase() : relativePath;
    if (seen.has(pathKey)) throw new Error("Backup manifest contains duplicate paths");
    seen.add(pathKey);
    const filePath = safeJoin(root, relativePath);
    const stat = fs.lstatSync(filePath);
    if (!stat.isFile() || stat.isSymbolicLink()) throw new Error("Backup entry is not a regular file");
    if (stat.size !== entry.size || sha256(filePath) !== entry.sha256) {
      throw new Error(`Backup checksum verification failed for ${relativePath}`);
    }
  }
  const databaseKey = process.platform === "win32" ? DATABASE_ENTRY.toLocaleLowerCase() : DATABASE_ENTRY;
  if (!seen.has(databaseKey)) throw new Error("Backup database is missing");
  const actualFiles = new Set(["manifest.json", ...listFiles(root)]);
  const expectedFiles = new Set(["manifest.json", ...seen]);
  if (
    actualFiles.size !== expectedFiles.size ||
    [...actualFiles].some((file) => !expectedFiles.has(file))
  ) {
    const extras = [...actualFiles].filter((file) => !expectedFiles.has(file));
    const missing = [...expectedFiles].filter((file) => !actualFiles.has(file));
    throw new Error(
      `Backup archive file list mismatch (extra: ${extras.join(", ") || "none"}; missing: ${missing.join(", ") || "none"})`
    );
  }
  const database = inspectDatabase(safeJoin(root, DATABASE_ENTRY));
  if (Number(manifest.schemaVersion) !== database.schemaVersion) {
    throw new Error("Backup manifest schema version does not match its database");
  }
  return { root, manifest, database };
}

function previewBackup(bundlePath) {
  const opened = openBackup(bundlePath);
  try {
    const verified = readAndVerifyBundle(opened.root);
    return {
      path: path.resolve(bundlePath),
      createdAt: verified.manifest.createdAt,
      appVersion: verified.manifest.appVersion,
      schemaVersion: verified.database.schemaVersion,
      includesAudio: verified.manifest.includes?.audio === true,
      counts: verified.database.counts,
      files: verified.manifest.files.map((file) => ({ ...file })),
    };
  } finally {
    opened.cleanup();
  }
}

async function restoreBackup({
  sourcePath,
  databasePath,
  audioDirectory = null,
  restoreAudio = false,
  preRestoreDirectory = null,
  appVersion = "unknown",
}) {
  if (!sourcePath || !databasePath) throw new Error("sourcePath and databasePath are required");
  if (restoreAudio && audioDirectory && isInside(audioDirectory, sourcePath)) {
    throw new Error("Backup source cannot be inside an audio directory being restored");
  }
  if (restoreAudio && audioDirectory && preRestoreDirectory && isInside(audioDirectory, preRestoreDirectory)) {
    throw new Error("Pre-restore snapshots cannot be stored inside an audio directory being restored");
  }
  const opened = openBackup(sourcePath);
  const source = readAndVerifyBundle(opened.root);
  const sourcePreview = {
    path: path.resolve(sourcePath),
    createdAt: source.manifest.createdAt,
    appVersion: source.manifest.appVersion,
    schemaVersion: source.database.schemaVersion,
    includesAudio: source.manifest.includes?.audio === true,
    counts: source.database.counts,
    files: source.manifest.files.map((file) => ({ ...file })),
  };
  const databaseDir = path.dirname(databasePath);
  fs.mkdirSync(databaseDir, { recursive: true });
  const stagingPath = fs.mkdtempSync(path.join(databaseDir, ".mnemora-restore-"));
  const token = `${process.pid}-${Date.now()}`;
  const incomingDatabase = `${databasePath}.restore-${token}.tmp`;
  const oldDatabase = `${databasePath}.restore-${token}.old`;
  let oldAudio = null;
  let installedDatabase = false;
  let installedAudio = false;
  let preRestorePath = null;

  try {
    fs.copyFileSync(path.join(source.root, "manifest.json"), path.join(stagingPath, "manifest.json"));
    for (const entry of source.manifest.files) {
      const from = safeJoin(source.root, entry.path);
      const to = safeJoin(stagingPath, entry.path);
      fs.mkdirSync(path.dirname(to), { recursive: true });
      fs.copyFileSync(from, to);
    }
    readAndVerifyBundle(stagingPath);

    if (fs.existsSync(databasePath)) {
      const snapshotRoot =
        preRestoreDirectory || path.join(databaseDir, "restore-snapshots");
      preRestorePath = path.join(snapshotRoot, `pre-restore-${timestamp()}`);
      const current = inspectDatabase(databasePath);
      await createBackup({
        databasePath,
        destinationPath: preRestorePath,
        audioDirectory,
        includeAudio: restoreAudio,
        appVersion,
        schemaVersion: current.schemaVersion,
      });
    }

    fs.copyFileSync(safeJoin(stagingPath, DATABASE_ENTRY), incomingDatabase);
    fs.rmSync(`${databasePath}-wal`, { force: true });
    fs.rmSync(`${databasePath}-shm`, { force: true });
    if (fs.existsSync(databasePath)) fs.renameSync(databasePath, oldDatabase);
    fs.renameSync(incomingDatabase, databasePath);
    installedDatabase = true;

    if (restoreAudio && source.manifest.includes?.audio && audioDirectory) {
      const incomingAudio = `${audioDirectory}.restore-${token}.tmp`;
      fs.rmSync(incomingAudio, { recursive: true, force: true });
      fs.cpSync(path.join(stagingPath, "audio"), incomingAudio, { recursive: true });
      if (fs.existsSync(audioDirectory)) {
        oldAudio = `${audioDirectory}.restore-${token}.old`;
        fs.renameSync(audioDirectory, oldAudio);
      }
      fs.renameSync(incomingAudio, audioDirectory);
      installedAudio = true;
    }

    try {
      fs.rmSync(oldDatabase, { force: true });
    } catch {
      // The restored database is already committed; a stale rollback file is safer than rollback.
    }
    if (oldAudio) {
      try {
        fs.rmSync(oldAudio, { recursive: true, force: true });
      } catch {
        // Same rule for audio: leave the old directory for later cleanup.
      }
    }
    return { success: true, preview: sourcePreview, preRestorePath };
  } catch (error) {
    if (installedAudio && audioDirectory) fs.rmSync(audioDirectory, { recursive: true, force: true });
    if (oldAudio && fs.existsSync(oldAudio)) fs.renameSync(oldAudio, audioDirectory);
    if (installedDatabase) fs.rmSync(databasePath, { force: true });
    if (fs.existsSync(oldDatabase)) fs.renameSync(oldDatabase, databasePath);
    throw error;
  } finally {
    try {
      fs.rmSync(incomingDatabase, { force: true });
      fs.rmSync(stagingPath, { recursive: true, force: true });
    } catch {
      // Never turn a committed restore into a reported failure because temp cleanup was blocked.
    }
    opened.cleanup();
  }
}

module.exports = {
  FORMAT,
  FORMAT_VERSION,
  createBackup,
  previewBackup,
  restoreBackup,
  validateRelativePath,
};
