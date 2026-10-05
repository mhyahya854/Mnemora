const test = require("node:test");
const assert = require("node:assert/strict");
const crypto = require("node:crypto");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const Module = require("node:module");

let userDataDir = fs.mkdtempSync(path.join(os.tmpdir(), "mnemora-data-safety-bootstrap-"));
const originalLoad = Module._load;
Module._load = function patchedLoad(request, parent, isMain) {
  if (request === "electron") {
    return {
      app: {
        getPath: () => userDataDir,
        getAppPath: () => process.cwd(),
        getVersion: () => "data-safety-test",
        isReady: () => false,
      },
    };
  }
  return originalLoad.call(this, request, parent, isMain);
};

process.env.NODE_ENV = "test";
const DatabaseManager = require("../../main/infrastructure/persistence/database.js");
const AudioStorageManager = require("../../main/infrastructure/persistence/audioStorage.js");
const { migrateUserData } = require("../../main/infrastructure/persistence/dataMigration.js");

function sha256(filePath) {
  return crypto.createHash("sha256").update(fs.readFileSync(filePath)).digest("hex");
}

test("real SQLite and filesystem boundary preserves every disposable user-data class", async (t) => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "mnemora-data-safety-real-"));
  const appDataPath = path.join(root, "app-data");
  const seedPath = path.join(root, "seed");
  const legacyPath = path.join(appDataPath, "OpenWhispr");
  const destination = path.join(appDataPath, "Mnemora");
  fs.mkdirSync(seedPath, { recursive: true });
  fs.mkdirSync(legacyPath, { recursive: true });
  userDataDir = seedPath;

  const seed = new DatabaseManager();
  const seedNote = seed.saveNote("Legacy meeting", "preserved note", "meeting").note;
  const seedMeeting = seed.getMeetingByNoteId(seedNote.id);
  const seedRecording = seed.createRecording({
    meetingId: seedMeeting.id,
    noteId: seedNote.id,
    filePath: "audio/legacy-recording.webm",
    sha256: "legacy-recording-hash",
  }).recording;
  seed.createTranscript({
    meetingId: seedMeeting.id,
    recordingId: seedRecording.id,
    noteId: seedNote.id,
    rawText: "legacy transcript",
    segments: [{ startMs: 0, endMs: 1000, originalText: "legacy transcript", speakerId: "s1" }],
  });
  const tag = seed.createTag("retained").tag;
  seed.setNoteTags(seedNote.id, [tag.id]);
  seed.setMeetingTags(seedMeeting.id, [tag.id]);
  seed.createAttachment({ noteId: seedNote.id, filePath: "attachments/legacy.txt" });
  seed.setLocalSetting("offline", true);
  seed.recordBackup({ path: "legacy-backup.mnemora-backup" });
  seed.updateSemanticIndexState({ status: "needs_rebuild" });
  seed.db.exec("DROP TABLE migration_journal");
  seed.db.pragma("user_version = 4");
  seed.db.pragma("wal_checkpoint(TRUNCATE)");
  seed.db.close();

  const legacyDatabase = path.join(legacyPath, "transcriptions.db");
  fs.renameSync(path.join(seedPath, "mnemora.sqlite"), legacyDatabase);
  const legacyAudio = path.join(legacyPath, "audio", "legacy-recording.webm");
  const legacyExport = path.join(legacyPath, "exports", "legacy-export.txt");
  const legacyBackup = path.join(legacyPath, "backups", "legacy-backup.bin");
  for (const file of [legacyAudio, legacyExport, legacyBackup]) {
    fs.mkdirSync(path.dirname(file), { recursive: true });
  }
  fs.writeFileSync(legacyAudio, "legacy audio bytes");
  fs.writeFileSync(legacyExport, "legacy export bytes");
  fs.writeFileSync(legacyBackup, "legacy backup bytes");
  const legacyHashesBefore = Object.fromEntries(
    [legacyDatabase, legacyAudio, legacyExport, legacyBackup].map((file) => [path.basename(file), sha256(file)])
  );

  const copied = migrateUserData({
    appDataPath,
    newUserDataPath: destination,
    channel: "production",
  });
  assert.equal(copied.status, "completed");
  assert.equal(copied.journal.files[0].sourceSchemaVersion, 4);
  assert.equal(copied.journal.files[0].destinationSchemaVersion, 4);
  assert.equal(sha256(legacyDatabase), legacyHashesBefore["transcriptions.db"]);

  userDataDir = destination;
  const manager = new DatabaseManager();
  t.after(() => {
    if (manager.db?.open) manager.db.close();
    fs.rmSync(root, { recursive: true, force: true });
  });
  assert.equal(manager.db.pragma("user_version", { simple: true }), 5);
  assert.ok(fs.existsSync(manager.lastMigrationBackupPath));
  assert.match(manager.lastMigrationBackupDetails.sourceSha256, /^[0-9a-f]{64}$/);
  assert.match(manager.lastMigrationBackupDetails.backupSha256, /^[0-9a-f]{64}$/);
  const migrationBackupSha256 = manager.lastMigrationBackupDetails.backupSha256;

  const audio = new AudioStorageManager();
  const saved = audio.saveAudio(777, Buffer.from("atomic recording"), "2026-08-20T00:00:00.000Z");
  assert.equal(saved.success, true);
  const audioHash = sha256(saved.path);
  const overwrite = audio.saveAudio(777, Buffer.from("must not overwrite"), "2026-08-20T00:00:00.000Z");
  assert.deepEqual(overwrite, { success: false, reason: "already_exists", path: saved.path });
  assert.equal(sha256(saved.path), audioHash);

  const note = manager.saveNote("Safety fixture", "original note", "meeting").note;
  const meeting = manager.getMeetingByNoteId(note.id);
  const recording = manager.createRecording({
    meetingId: meeting.id,
    noteId: note.id,
    filePath: saved.path,
    sha256: audioHash,
  }).recording;
  manager.createTranscript({
    meetingId: meeting.id,
    recordingId: recording.id,
    noteId: note.id,
    rawText: "preserved transcript",
    segments: [{ segmentIndex: 0, startMs: 0, endMs: 1000, originalText: "preserved transcript" }],
  });
  const exportPath = path.join(destination, "exports", "safety-export.txt");
  fs.mkdirSync(path.dirname(exportPath), { recursive: true });
  fs.writeFileSync(exportPath, "preserved export");
  const exportHash = sha256(exportPath);

  const before = manager.getDataSafetySnapshot();
  assert.equal(before.quickCheck, "ok");
  assert.deepEqual(before.foreignKeyViolations, []);
  assert.equal(before.recordingReferences.find((entry) => entry.id === recording.id).observedSha256, audioHash);
  const backupPath = path.join(destination, "backups", "safety.mnemora-backup");
  const backup = await manager.createLocalBackup(backupPath, {
    includeAudio: true,
    audioDirectory: audio.audioDir,
  });
  assert.equal(backup.success, true);
  const backupHash = sha256(backupPath);

  manager.updateNote(note.id, { title: "temporary mutation" });
  await manager.restoreLocalBackup(backupPath, {
    restoreAudio: true,
    audioDirectory: audio.audioDir,
    preRestoreDirectory: path.join(destination, "restore-snapshots"),
  });
  const after = manager.getDataSafetySnapshot();
  assert.equal(manager.getNote(note.id).title, "Safety fixture");
  assert.equal(after.quickCheck, "ok");
  assert.deepEqual(after.foreignKeyViolations, []);
  for (const table of [
    "meetings",
    "recordings",
    "transcripts",
    "transcript_segments",
    "notes",
    "folders",
    "tags",
    "snippets",
    "attachments",
    "local_settings",
    "semantic_index_state",
  ]) {
    assert.equal(after.counts[table], before.counts[table], `${table} count changed across restore`);
  }
  assert.equal(sha256(saved.path), audioHash);
  assert.equal(sha256(exportPath), exportHash);
  assert.equal(sha256(backupPath), backupHash);
  const legacyHashesAfter = Object.fromEntries(
    [legacyDatabase, legacyAudio, legacyExport, legacyBackup].map((file) => [path.basename(file), sha256(file)])
  );
  assert.deepEqual(legacyHashesAfter, legacyHashesBefore);

  const evidence = {
    sourceSchemaVersion: copied.journal.files[0].sourceSchemaVersion,
    destinationSchemaVersion: after.schemaVersion,
    legacyHashesBefore,
    legacyHashesAfter,
    beforeCounts: before.counts,
    afterCounts: after.counts,
    databaseSha256: after.databaseSha256,
    recordingSha256: audioHash,
    exportSha256: exportHash,
    backupSha256: backupHash,
    migrationBackupSha256,
    migrationStatus: after.migrationJournal.at(-1).status,
    foreignKeyViolations: after.foreignKeyViolations.length,
    quickCheck: after.quickCheck,
  };
  console.log(`DATA_SAFETY_EVIDENCE=${JSON.stringify(evidence)}`);

  assert.deepEqual(manager.cleanup(), { success: true });
  assert.equal(fs.existsSync(path.join(destination, "mnemora.sqlite")), true);
});
