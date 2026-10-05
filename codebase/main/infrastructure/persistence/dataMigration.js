const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");
const Database = require("better-sqlite3");

function sha256(filePath, fsMock) {
  const hash = crypto.createHash("sha256");
  const handle = fsMock.openSync(filePath, "r");
  const buffer = Buffer.allocUnsafe(1024 * 1024);
  try {
    let read;
    while ((read = fsMock.readSync(handle, buffer, 0, buffer.length, null)) > 0) {
      hash.update(buffer.subarray(0, read));
    }
  } finally {
    fsMock.closeSync(handle);
  }
  return hash.digest("hex");
}

function inspectSqlite(filePath) {
  const database = new Database(filePath, { readonly: true, fileMustExist: true });
  try {
    return {
      schemaVersion: database.pragma("user_version", { simple: true }),
      quickCheck: database.pragma("quick_check", { simple: true }),
    };
  } finally {
    database.close();
  }
}

function migrateUserData({
  appDataPath,
  newUserDataPath,
  channel,
  fsMock = fs,
  pathMock = path,
}) {
  const destinationExists = fsMock.existsSync(newUserDataPath);
  if (destinationExists && fsMock.readdirSync(newUserDataPath).length > 0) {
    return { status: "skipped", reason: "new_location_not_empty" };
  }

  const oldUserDataPath = pathMock.join(
    appDataPath,
    channel === "production" ? "OpenWhispr" : `OpenWhispr-${channel}`
  );
  if (!fsMock.existsSync(oldUserDataPath)) {
    return { status: "skipped", reason: "no_legacy_data" };
  }

  const sourceFiles = [
    ["transcriptions.db", "mnemora.sqlite", true],
    ["transcriptions-dev.db", "mnemora-dev.sqlite", true],
    [".env", ".env", false],
    [".bundle-migrated", ".bundle-migrated", false],
  ].filter(([source]) => fsMock.existsSync(pathMock.join(oldUserDataPath, source)));
  const oldSecureKeys = pathMock.join(oldUserDataPath, "secure-keys");
  if (fsMock.existsSync(oldSecureKeys)) {
    for (const file of fsMock.readdirSync(oldSecureKeys)) {
      const source = pathMock.join(oldSecureKeys, file);
      const stat = fsMock.lstatSync(source);
      if (stat.isSymbolicLink()) {
        return { status: "failed", error: "legacy secure-keys cannot contain symbolic links" };
      }
      if (stat.isFile()) sourceFiles.push([`secure-keys/${file}`, `secure-keys/${file}`, false]);
    }
  }
  if (sourceFiles.length === 0) {
    return { status: "skipped", reason: "legacy_dir_empty" };
  }

  fsMock.mkdirSync(pathMock.dirname(newUserDataPath), { recursive: true });
  const stagingPath = fsMock.mkdtempSync(`${newUserDataPath}.migration-`);
  const startedAt = new Date().toISOString();
  try {
    const files = [];
    for (const [sourceRelative, destinationRelative, sqlite] of sourceFiles) {
      const source = pathMock.join(oldUserDataPath, ...sourceRelative.split("/"));
      const destination = pathMock.join(stagingPath, ...destinationRelative.split("/"));
      fsMock.mkdirSync(pathMock.dirname(destination), { recursive: true });
      fsMock.copyFileSync(source, destination, fs.constants.COPYFILE_EXCL);
      const sourceStat = fsMock.statSync(source);
      const destinationStat = fsMock.statSync(destination);
      const sourceSha256 = sha256(source, fsMock);
      const destinationSha256 = sha256(destination, fsMock);
      if (sourceStat.size !== destinationStat.size || sourceSha256 !== destinationSha256) {
        throw new Error(`verification failed for ${sourceRelative}`);
      }
      const database = sqlite ? inspectSqlite(destination) : null;
      if (database && database.quickCheck !== "ok") {
        throw new Error(`SQLite integrity check failed for ${sourceRelative}: ${database.quickCheck}`);
      }
      files.push({
        source: sourceRelative,
        destination: destinationRelative,
        size: sourceStat.size,
        sha256: sourceSha256,
        sourceSchemaVersion: database?.schemaVersion ?? null,
        destinationSchemaVersion: database?.schemaVersion ?? null,
      });
    }

    const journal = {
      format: "mnemora-user-data-migration",
      formatVersion: 1,
      status: "completed",
      startedAt,
      completedAt: new Date().toISOString(),
      sourcePath: oldUserDataPath,
      destinationPath: newUserDataPath,
      files,
      result: "verified copy committed atomically; source preserved",
    };
    fsMock.writeFileSync(
      pathMock.join(stagingPath, ".mnemora-migration-completed"),
      JSON.stringify(journal, null, 2),
      { flag: "wx" }
    );

    if (fsMock.existsSync(newUserDataPath)) {
      if (fsMock.readdirSync(newUserDataPath).length > 0) {
        throw new Error("new location became non-empty before migration commit");
      }
      fsMock.rmdirSync(newUserDataPath);
    }
    fsMock.renameSync(stagingPath, newUserDataPath);
    return { status: "completed", journal };
  } catch (error) {
    try {
      fsMock.rmSync(stagingPath, { recursive: true, force: true });
    } catch {
      // Preserve the migration failure; a staging directory contains copies only.
    }
    return { status: "failed", error: error.message };
  }
}

module.exports = {
  migrateUserData,
};
