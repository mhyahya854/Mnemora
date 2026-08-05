const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const Module = require("node:module");
const BetterSqlite = require("better-sqlite3");

let userDataDir = fs.mkdtempSync(path.join(os.tmpdir(), "mnemora-local-data-"));
const originalLoad = Module._load;
Module._load = function patchedLoad(request, parent, isMain) {
  if (request === "electron") {
    return {
      app: {
        getPath: () => userDataDir,
        getAppPath: () => process.cwd(),
        getVersion: () => "test",
        isReady: () => false,
      },
    };
  }
  return originalLoad.call(this, request, parent, isMain);
};

process.env.NODE_ENV = "test";
const DatabaseManager = require("../../../main/infrastructure/persistence/database.js");
const debugLogger = require("../../../main/infrastructure/runtime/debugLogger.js");

function createManager(t) {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "mnemora-local-data-"));
  userDataDir = directory;
  const manager = new DatabaseManager();
  t.after(() => {
    if (manager.db?.open) manager.db.close();
    fs.rmSync(directory, { recursive: true, force: true });
  });
  return { manager, directory };
}

test("fresh schema supports local graphs, Unicode search, tags, settings, and cascades", (t) => {
  const { manager } = createManager(t);
  const tables = new Set(
    manager.db
      .prepare("SELECT name FROM sqlite_master WHERE type IN ('table', 'view')")
      .all()
      .map((row) => row.name)
  );
  for (const table of [
    "local_settings",
    "tags",
    "note_tags",
    "meetings",
    "meeting_tags",
    "recordings",
    "transcripts",
    "transcript_segments",
    "attachments",
    "backups",
    "semantic_index_state",
  ]) {
    assert.ok(tables.has(table), `${table} should exist`);
  }
  for (const removedTable of [
    "actions",
    "agent_conversations",
    "agent_messages",
    "google_calendar_tokens",
    "google_calendars",
    "calendar_events",
  ]) {
    assert.ok(!tables.has(removedTable), `${removedTable} should be removed`);
  }
  const noteColumns = new Set(manager.db.pragma("table_info(notes)").map((column) => column.name));
  for (const removedColumn of [
    "enhanced_content",
    "enhancement_prompt",
    "enhanced_at_content_hash",
    "calendar_event_id",
  ]) {
    assert.ok(!noteColumns.has(removedColumn), `${removedColumn} should be removed`);
  }
  assert.equal(DatabaseManager.SCHEMA_VERSION, 4);
  assert.equal(manager.db.pragma("user_version", { simple: true }), 4);
  assert.equal(manager.db.pragma("foreign_keys", { simple: true }), 1);

  manager.setLocalSetting("retention", { enabled: false, days: null });
  assert.deepEqual(manager.getLocalSetting("retention"), { enabled: false, days: null });

  const note = manager.saveNote("خطة المشروع", "تفاصيل محلية", "meeting").note;
  const tag = manager.createTag("重要", "#123456").tag;
  manager.setNoteTags(note.id, [tag.id]);
  const meeting = manager.getMeetingByNoteId(note.id);
  manager.setMeetingTags(meeting.id, [tag.id]);
  const recording = manager.createRecording({
    meetingId: meeting.id,
    noteId: note.id,
    filePath: "audio/meeting.wav",
    durationMs: 2_000,
  }).recording;
  const transcript = manager.createTranscript({
    meetingId: meeting.id,
    recordingId: recording.id,
    noteId: note.id,
    language: "ja",
    rawText: "顧客要件を確認",
    segments: [
      {
        startMs: 0,
        endMs: 2_000,
        originalText: "顧客要件を確認",
        speakerId: "speaker-1",
      },
    ],
  }).transcript;
  manager.createAttachment({ noteId: note.id, meetingId: meeting.id, filePath: "files/a.txt" });
  manager.setSpeakerMapping(note.id, "speaker-1", null, "Alice");

  assert.equal(manager.searchNotes("المشروع")[0].id, note.id);
  assert.equal(manager.searchNotes("顧客")[0].id, note.id);
  assert.equal(manager.searchTranscripts("要件")[0].id, transcript.id);
  assert.equal(manager.searchNotes("重要", 10, { tagIds: [tag.id] })[0].id, note.id);
  assert.deepEqual(manager.getTagsForNote(note.id).map((item) => item.id), [tag.id]);

  const semantic = manager.updateSemanticIndexState({
    status: "ready",
    modelId: "minilm",
    lastIndexedAt: "2026-07-13T00:00:00.000Z",
  });
  assert.equal(semantic.status, "ready");

  assert.equal(manager.deleteNote(note.id).success, true);
  assert.equal(manager.getMeeting(meeting.id), null);
  assert.equal(manager.getRecording(recording.id), null);
  assert.equal(manager.getTranscript(transcript.id), null);
  assert.equal(manager.db.prepare("SELECT COUNT(*) AS count FROM attachments").get().count, 0);
  assert.equal(manager.db.prepare("SELECT COUNT(*) AS count FROM speaker_mappings").get().count, 0);
  assert.equal(manager.getTags().length, 1, "deleting a note must not delete reusable tags");
  assert.deepEqual(manager.db.pragma("foreign_key_check"), []);
});

test("legacy adoption is backed up, transactional, lossless, and restart-idempotent", (t) => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "mnemora-legacy-data-"));
  userDataDir = directory;
  const databasePath = path.join(directory, "mnemora.sqlite");
  const legacy = new BetterSqlite(databasePath);
  const rawTranscript = JSON.stringify([
    {
      text: "محضر محفوظ",
      source: "system",
      timestamp: 1_700_000_000_000,
      speaker: "speaker-1",
      speakerName: "ليلى",
      speakerLocked: true,
    },
    { text: "続き", source: "mic", timestamp: 1_700_000_002_000 },
  ]);
  legacy.exec(`
    CREATE TABLE folders (
      id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, is_default INTEGER NOT NULL DEFAULT 0,
      sort_order INTEGER NOT NULL DEFAULT 0, created_at TEXT, updated_at TEXT,
      client_folder_id TEXT, cloud_id TEXT, sync_status TEXT, deleted_at TEXT
    );
    INSERT INTO folders VALUES
      (1, 'Personal', 1, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL, NULL, NULL, NULL),
      (2, 'Meetings', 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL, NULL, NULL, NULL),
      (3, 'Archived local', 0, 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'local-3', 'cloud-3', 'deleted', CURRENT_TIMESTAMP);

    CREATE TABLE notes (
      id INTEGER PRIMARY KEY, title TEXT NOT NULL, content TEXT NOT NULL, note_type TEXT NOT NULL,
      source_file TEXT, audio_duration_seconds REAL, folder_id INTEGER, transcript TEXT,
      enhanced_content TEXT, enhancement_prompt TEXT, enhanced_at_content_hash TEXT,
      calendar_event_id TEXT,
      created_at TEXT, updated_at TEXT, client_note_id TEXT, cloud_id TEXT,
      sync_status TEXT, deleted_at TEXT
    );
    INSERT INTO notes VALUES (
      7, 'Legacy meeting', '', 'meeting', NULL, NULL, 2, '${rawTranscript.replace(/'/g, "''")}',
      'discard cloud enhancement', 'cloud prompt', 'cloud hash', 'cloud event',
      CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'local-7', 'cloud-7', 'deleted', CURRENT_TIMESTAMP
    );

    CREATE TABLE actions (id INTEGER PRIMARY KEY, name TEXT);
    CREATE TABLE agent_conversations (id INTEGER PRIMARY KEY, title TEXT);
    CREATE TABLE agent_messages (id INTEGER PRIMARY KEY, conversation_id INTEGER, content TEXT);
    CREATE TABLE google_calendar_tokens (id INTEGER PRIMARY KEY, access_token TEXT);
    CREATE TABLE google_calendars (id TEXT PRIMARY KEY, summary TEXT);
    CREATE TABLE calendar_events (id TEXT PRIMARY KEY, summary TEXT);

    CREATE TABLE transcriptions (
      id INTEGER PRIMARY KEY, text TEXT NOT NULL, timestamp TEXT, created_at TEXT,
      client_transcription_id TEXT, cloud_id TEXT, sync_status TEXT, deleted_at TEXT
    );
    INSERT INTO transcriptions VALUES
      (8, 'preserve me', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'local-8', 'cloud-8', 'deleted', CURRENT_TIMESTAMP);

    CREATE TABLE snippets (
      id INTEGER PRIMARY KEY, trigger TEXT NOT NULL, replacement TEXT NOT NULL,
      created_at TEXT, updated_at TEXT, client_snippet_id TEXT, cloud_id TEXT,
      sync_status TEXT, deleted_at TEXT
    );
    INSERT INTO snippets VALUES
      (9, 'legacy', 'kept', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'local-9', 'cloud-9', 'deleted', CURRENT_TIMESTAMP);

    CREATE TABLE custom_dictionary (
      id INTEGER PRIMARY KEY, word TEXT NOT NULL UNIQUE, source TEXT, created_at TEXT, updated_at TEXT,
      client_dict_id TEXT, cloud_id TEXT, sync_status TEXT, deleted_at TEXT
    );
    INSERT INTO custom_dictionary VALUES
      (10, 'Mnemora', 'manual', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'local-10', 'cloud-10', 'deleted', CURRENT_TIMESTAMP);

    CREATE TABLE speaker_profiles (
      id INTEGER PRIMARY KEY, display_name TEXT NOT NULL, email TEXT, embedding BLOB NOT NULL,
      sample_count INTEGER, created_at TEXT, updated_at TEXT
    );
    CREATE TABLE speaker_mappings (
      note_id INTEGER NOT NULL, speaker_id TEXT NOT NULL, profile_id INTEGER,
      display_name TEXT NOT NULL, PRIMARY KEY (note_id, speaker_id)
    );
    INSERT INTO speaker_mappings VALUES
      (999, 'orphan-note', NULL, 'Orphan'),
      (7, 'orphan-profile', 999, 'Preserved');
    CREATE TABLE note_speaker_embeddings (
      note_id INTEGER NOT NULL, speaker_id TEXT NOT NULL, embedding BLOB NOT NULL,
      PRIMARY KEY (note_id, speaker_id)
    );
    INSERT INTO note_speaker_embeddings VALUES (999, 'orphan-note', X'01');
  `);
  legacy.close();

  const manager = new DatabaseManager();
  t.after(() => {
    if (manager.db?.open) manager.db.close();
    fs.rmSync(directory, { recursive: true, force: true });
  });

  assert.equal(manager.db.pragma("user_version", { simple: true }), 4);
  assert.equal(manager.db.pragma("foreign_keys", { simple: true }), 1);
  assert.equal(manager.getNote(7).title, "Legacy meeting");
  assert.equal(manager.getTranscriptionById(8).text, "preserve me");
  assert.equal(manager.db.prepare("SELECT replacement FROM snippets WHERE id = 9").get().replacement, "kept");
  assert.equal(manager.db.prepare("SELECT word FROM custom_dictionary WHERE id = 10").get().word, "Mnemora");
  assert.equal(manager.db.prepare("SELECT name FROM folders WHERE id = 3").get().name, "Archived local");
  assert.equal(manager.db.prepare("SELECT COUNT(*) AS count FROM note_speaker_embeddings").get().count, 0);
  assert.equal(manager.db.prepare("SELECT COUNT(*) AS count FROM speaker_mappings").get().count, 1);
  assert.equal(
    manager.db.prepare("SELECT profile_id FROM speaker_mappings WHERE note_id = 7").get().profile_id,
    null
  );
  for (const table of ["notes", "folders", "transcriptions", "snippets", "custom_dictionary"]) {
    assert.ok(!manager.db.pragma(`table_info(${table})`).some((column) => column.name === "deleted_at"));
  }
  for (const table of [
    "actions",
    "agent_conversations",
    "agent_messages",
    "google_calendar_tokens",
    "google_calendars",
    "calendar_events",
  ]) {
    assert.equal(
      manager.db.prepare("SELECT COUNT(*) AS count FROM sqlite_master WHERE name = ?").get(table)
        .count,
      0
    );
  }
  for (const column of [
    "enhanced_content",
    "enhancement_prompt",
    "enhanced_at_content_hash",
    "calendar_event_id",
  ]) {
    assert.ok(!manager.db.pragma("table_info(notes)").some((entry) => entry.name === column));
  }

  const meeting = manager.getMeetingByNoteId(7);
  const transcript = manager.getTranscripts({ noteId: 7 })[0];
  const segments = manager.getTranscript(transcript.id).segments;
  assert.equal(transcript.raw_text, rawTranscript);
  assert.equal(meeting.title, "Legacy meeting");
  assert.deepEqual(segments.map((segment) => segment.start_ms), [0, 2_000]);
  assert.equal(JSON.parse(segments[0].metadata_json).speakerName, "ليلى");

  assert.ok(manager.lastMigrationBackupPath);
  assert.ok(fs.existsSync(manager.lastMigrationBackupPath));
  const snapshot = new BetterSqlite(manager.lastMigrationBackupPath, {
    readonly: true,
    fileMustExist: true,
  });
  assert.equal(snapshot.prepare("SELECT COUNT(*) AS count FROM notes WHERE id = 7").get().count, 1);
  assert.ok(snapshot.pragma("table_info(notes)").some((column) => column.name === "deleted_at"));
  snapshot.close();

  const backupCount = fs.readdirSync(path.join(directory, "migration-backups")).length;
  manager.db.close();
  const reopened = new DatabaseManager();
  assert.equal(reopened.lastMigrationBackupPath, null);
  assert.equal(fs.readdirSync(path.join(directory, "migration-backups")).length, backupCount);
  assert.equal(reopened.getTranscripts({ noteId: 7 }).length, 1);
  reopened.db.close();
});

test("a failed ordered migration rolls back its schema version and destructive cleanup", (t) => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "mnemora-failed-migration-"));
  userDataDir = directory;
  const databasePath = path.join(directory, "mnemora.sqlite");
  const legacy = new BetterSqlite(databasePath);
  legacy.exec(`
    CREATE TABLE notes (
      id INTEGER PRIMARY KEY,
      title TEXT NOT NULL,
      content TEXT NOT NULL,
      note_type TEXT NOT NULL,
      source_file TEXT,
      audio_duration_seconds REAL,
      created_at TEXT,
      updated_at TEXT,
      deleted_at TEXT
    );
    INSERT INTO notes VALUES (
      1, 'Keep me', 'Legacy content', 'personal', NULL, NULL,
      CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
    );
  `);
  legacy.close();

  let failedInstance = null;
  class FailingMigrationManager extends DatabaseManager {
    _migrateLegacyMeetingNotes() {
      failedInstance = this;
      throw new Error("injected migration failure");
    }
  }

  const originalError = debugLogger.error;
  debugLogger.error = () => {};
  try {
    assert.throws(() => new FailingMigrationManager(), /injected migration failure/);
  } finally {
    debugLogger.error = originalError;
  }
  if (failedInstance?.db?.open) failedInstance.db.close();
  const probe = new BetterSqlite(databasePath);
  assert.equal(probe.pragma("user_version", { simple: true }), 0);
  assert.ok(probe.pragma("table_info(notes)").some((column) => column.name === "deleted_at"));
  assert.equal(probe.prepare("SELECT title FROM notes WHERE id = 1").get().title, "Keep me");
  assert.equal(
    probe
      .prepare("SELECT COUNT(*) AS count FROM sqlite_master WHERE type = 'table' AND name = 'meetings'")
      .get().count,
    0
  );
  probe.close();
  assert.equal(fs.readdirSync(path.join(directory, "migration-backups")).length, 1);

  t.after(() => fs.rmSync(directory, { recursive: true, force: true }));
});

test("a newer database is rejected before the older app mutates it", (t) => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "mnemora-newer-schema-"));
  userDataDir = directory;
  const databasePath = path.join(directory, "mnemora.sqlite");
  const newer = new BetterSqlite(databasePath);
  newer.exec("CREATE TABLE future_data (value TEXT); INSERT INTO future_data VALUES ('kept')");
  newer.pragma("user_version = 999");
  newer.close();

  const originalError = debugLogger.error;
  debugLogger.error = () => {};
  try {
    assert.throws(() => new DatabaseManager(), /newer than supported/);
  } finally {
    debugLogger.error = originalError;
  }

  const probe = new BetterSqlite(databasePath);
  assert.equal(probe.pragma("user_version", { simple: true }), 999);
  assert.equal(probe.prepare("SELECT value FROM future_data").get().value, "kept");
  assert.equal(
    probe.prepare("SELECT COUNT(*) AS count FROM sqlite_master WHERE name = 'notes'").get().count,
    0
  );
  probe.close();
  t.after(() => fs.rmSync(directory, { recursive: true, force: true }));
});
