const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const Module = require("node:module");
const tar = require("tar");

let userDataDir = fs.mkdtempSync(path.join(os.tmpdir(), "mnemora-backup-"));
const originalLoad = Module._load;
Module._load = function patchedLoad(request, parent, isMain) {
  if (request === "electron") {
    return {
      app: {
        getPath: () => userDataDir,
        getAppPath: () => process.cwd(),
        getVersion: () => "1.0.0-test",
        isReady: () => false,
      },
    };
  }
  return originalLoad.call(this, request, parent, isMain);
};

process.env.NODE_ENV = "test";
const DatabaseManager = require("../../../main/infrastructure/persistence/database.js");

test("verified backup round-trips the database and optional audio with a pre-restore snapshot", async (t) => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "mnemora-backup-"));
  userDataDir = directory;
  const manager = new DatabaseManager();
  t.after(() => {
    if (manager.db?.open) manager.db.close();
    fs.rmSync(directory, { recursive: true, force: true });
  });

  const note = manager.saveNote("Backup meeting", "before restore", "meeting").note;
  manager.updateNote(note.id, {
    transcript: JSON.stringify([{ text: "نسخة احتياطية", source: "mic", timestamp: 3 }]),
  });
  manager.setLocalSetting("backup-test", { value: 42 });
  const audioDirectory = path.join(directory, "audio");
  fs.mkdirSync(audioDirectory, { recursive: true });
  fs.writeFileSync(path.join(audioDirectory, "sample.wav"), "original audio");

  const backupPath = path.join(directory, "exports", "first.mnemora-backup");
  const created = await manager.createLocalBackup(backupPath, {
    includeAudio: true,
    audioDirectory,
  });
  assert.equal(created.success, true);
  const preview = manager.previewLocalBackup(backupPath);
  assert.equal(preview.compatible, true);
  assert.equal(preview.includesAudio, true);
  assert.equal(preview.counts.notes, 1);
  assert.equal(preview.counts.meetings, 1);
  assert.equal(preview.counts.transcripts, 1);

  manager.updateNote(note.id, { title: "Mutated", content: "after backup" });
  manager.setLocalSetting("backup-test", { value: 99 });
  fs.writeFileSync(path.join(audioDirectory, "sample.wav"), "mutated audio");

  const restored = await manager.restoreLocalBackup(backupPath, {
    restoreAudio: true,
    audioDirectory,
    preRestoreDirectory: path.join(directory, "restore-snapshots"),
  });
  assert.equal(restored.success, true);
  assert.ok(restored.preRestorePath);
  assert.ok(fs.statSync(restored.preRestorePath).isFile());
  assert.equal(manager.getNote(note.id).title, "Backup meeting");
  assert.deepEqual(manager.getLocalSetting("backup-test"), { value: 42 });
  assert.equal(fs.readFileSync(path.join(audioDirectory, "sample.wav"), "utf8"), "original audio");
  assert.equal(manager.searchTranscripts("احتياطية").length, 1);
  assert.equal(manager.db.pragma("foreign_keys", { simple: true }), 1);

  const preRestorePreview = manager.previewLocalBackup(restored.preRestorePath);
  assert.equal(preRestorePreview.counts.notes, 1);
  assert.equal(preRestorePreview.includesAudio, true);
});

test("preview rejects checksum corruption and path traversal before restore", async (t) => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "mnemora-backup-invalid-"));
  userDataDir = directory;
  const manager = new DatabaseManager();
  t.after(() => {
    if (manager.db?.open) manager.db.close();
    fs.rmSync(directory, { recursive: true, force: true });
  });
  manager.saveNote("Safe", "data");

  const cleanPath = path.join(directory, "clean.mnemora-backup");
  await manager.createLocalBackup(cleanPath);

  const corruptPath = path.join(directory, "corrupt.mnemora-backup");
  fs.mkdirSync(corruptPath);
  tar.x({ file: cleanPath, cwd: corruptPath, sync: true });
  fs.appendFileSync(path.join(corruptPath, "data", "mnemora.sqlite"), "tampered");
  assert.throws(() => manager.previewLocalBackup(corruptPath), /checksum verification failed/);

  const traversalPath = path.join(directory, "traversal.mnemora-backup");
  fs.mkdirSync(traversalPath);
  tar.x({ file: cleanPath, cwd: traversalPath, sync: true });
  const manifestPath = path.join(traversalPath, "manifest.json");
  const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  manifest.files.push({ path: "../escape", size: 0, sha256: "0".repeat(64) });
  fs.writeFileSync(manifestPath, JSON.stringify(manifest));
  assert.throws(() => manager.previewLocalBackup(traversalPath), /unsafe path/);

  assert.equal(manager.getNotes()[0].title, "Safe", "invalid bundles must not mutate live data");
});
