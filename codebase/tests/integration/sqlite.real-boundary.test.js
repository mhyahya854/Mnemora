const test = require("node:test");
const assert = require("node:assert/strict");
const crypto = require("node:crypto");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const Module = require("node:module");
const BetterSqlite = require("better-sqlite3");

let userDataDir = fs.mkdtempSync(path.join(os.tmpdir(), "mnemora-sqlite-bootstrap-"));
const originalLoad = Module._load;
Module._load = function patchedLoad(request, parent, isMain) {
  if (request === "electron") {
    return {
      app: {
        getPath: () => userDataDir,
        getAppPath: () => process.cwd(),
        getVersion: () => "sqlite-real-boundary-test",
        isReady: () => false,
      },
    };
  }
  return originalLoad.call(this, request, parent, isMain);
};

process.env.NODE_ENV = "test";
const DatabaseManager = require("../../main/infrastructure/persistence/database.js");

function sha256(filePath) {
  return crypto.createHash("sha256").update(fs.readFileSync(filePath)).digest("hex");
}

function createIsolatedEnvironment(t, prefix = "mnemora-sqlite-test-") {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), prefix));
  userDataDir = root;
  const manager = new DatabaseManager();
  t.after(() => {
    if (manager.db?.open) {
      try {
        manager.db.close();
      } catch {}
    }
    try {
      fs.rmSync(root, { recursive: true, force: true, maxRetries: 5, retryDelay: 50 });
    } catch {}
  });
  return { root, manager };
}

test("real SQLite native boundary enforces schema v5, WAL mode, foreign keys, and local tables", (t) => {
  const { root, manager } = createIsolatedEnvironment(t, "mnemora-sqlite-schema-");
  const dbFile = path.join(root, "mnemora.sqlite");
  assert.ok(fs.existsSync(dbFile), "mnemora.sqlite database file must be created on disk");

  // Pragmas
  assert.equal(manager.db.pragma("user_version", { simple: true }), 5, "schema version must be 5");
  assert.equal(manager.db.pragma("foreign_keys", { simple: true }), 1, "foreign keys must be enabled");
  assert.equal(manager.db.pragma("journal_mode", { simple: true }).toLowerCase(), "wal", "journal mode must be WAL");
  assert.equal(manager.db.pragma("busy_timeout", { simple: true }), 5000, "busy_timeout must be 5000ms");

  // Required local tables
  const tables = new Set(
    manager.db
      .prepare("SELECT name FROM sqlite_master WHERE type IN ('table', 'view')")
      .all()
      .map((row) => row.name)
  );

  const requiredTables = [
    "meetings",
    "recordings",
    "transcripts",
    "transcript_segments",
    "notes",
    "folders",
    "tags",
    "note_tags",
    "meeting_tags",
    "attachments",
    "backups",
    "migration_journal",
    "semantic_index_state",
    "snippets",
    "custom_dictionary",
    "speaker_profiles",
    "speaker_mappings",
    "note_speaker_embeddings",
    "local_settings",
    "notes_fts",
    "transcript_segments_fts",
  ];
  for (const tbl of requiredTables) {
    assert.ok(tables.has(tbl), `Required table/view '${tbl}' must be present in SQLite schema`);
  }

  // Forbidden cloud/agent tables
  const forbiddenTables = [
    "actions",
    "agent_conversations",
    "agent_messages",
    "google_calendar_tokens",
    "google_calendars",
    "calendar_events",
  ];
  for (const forbidden of forbiddenTables) {
    assert.ok(!tables.has(forbidden), `Forbidden cloud/agent table '${forbidden}' must not exist`);
  }

  // Foreign key check on clean schema
  const fkViolations = manager.db.pragma("foreign_key_check");
  assert.deepEqual(fkViolations, [], "foreign_key_check must report zero violations on fresh database");
});

test("real SQLite boundary guarantees transaction atomicity and rollback on error", (t) => {
  const { manager } = createIsolatedEnvironment(t, "mnemora-sqlite-tx-");

  // Pre-condition count
  const initialNoteCount = manager.db.prepare("SELECT COUNT(*) AS count FROM notes").get().count;
  assert.equal(initialNoteCount, 0);

  // Successful transaction commits atomically
  manager.db.transaction(() => {
    manager.db.prepare("INSERT INTO notes (title, content, note_type) VALUES (?, ?, ?)").run("Note 1", "Content 1", "notes");
    manager.db.prepare("INSERT INTO notes (title, content, note_type) VALUES (?, ?, ?)").run("Note 2", "Content 2", "notes");
  })();
  const afterCommitCount = manager.db.prepare("SELECT COUNT(*) AS count FROM notes").get().count;
  assert.equal(afterCommitCount, 2, "Both notes must be persisted after successful transaction");

  // Failed transaction rolls back completely without partial state
  assert.throws(
    () => {
      manager.db.transaction(() => {
        manager.db.prepare("INSERT INTO notes (title, content, note_type) VALUES (?, ?, ?)").run("Note 3", "Content 3", "notes");
        throw new Error("Simulated failure inside transaction");
      })();
    },
    /Simulated failure inside transaction/
  );

  const afterRollbackCount = manager.db.prepare("SELECT COUNT(*) AS count FROM notes").get().count;
  assert.equal(afterRollbackCount, 2, "Rolled-back note must not exist; transaction must be completely atomic");
});

test("real SQLite boundary enforces foreign key constraints and cascading deletes", (t) => {
  const { manager } = createIsolatedEnvironment(t, "mnemora-sqlite-cascade-");

  // Create full relational entity graph
  const folder = manager.createFolder("Test Project").folder;
  const tag1 = manager.createTag("Urgent", "#ff0000").tag;
  const tag2 = manager.createTag("Client", "#00ff00").tag;

  const note = manager.saveNote("Strategy Session", "Q4 Planning details", "meeting", folder.id).note;
  manager.setNoteTags(note.id, [tag1.id, tag2.id]);

  const meeting = manager.getMeetingByNoteId(note.id);
  assert.ok(meeting, "Meeting should be linked to note");
  manager.setMeetingTags(meeting.id, [tag1.id]);

  const recording = manager.createRecording({
    meetingId: meeting.id,
    noteId: note.id,
    filePath: "audio/q4-strategy.webm",
    durationMs: 30000,
    sha256: "dummy-hash-123",
  }).recording;

  const transcript = manager.createTranscript({
    meetingId: meeting.id,
    recordingId: recording.id,
    noteId: note.id,
    language: "en",
    rawText: "Discussion on strategy and planning",
    segments: [
      { startMs: 0, endMs: 5000, originalText: "Discussion on strategy and planning", speakerId: "spk-1" },
    ],
  }).transcript;

  const attachment = manager.createAttachment({
    noteId: note.id,
    meetingId: meeting.id,
    filePath: "docs/agenda.pdf",
    fileName: "agenda.pdf",
  });
  assert.ok(attachment, "Attachment must be created");

  manager.setSpeakerMapping(note.id, "spk-1", null, "Chief Architect");

  // Constraint check: invalid foreign key insertion fails
  assert.throws(() => {
    manager.db.prepare("INSERT INTO note_tags (note_id, tag_id) VALUES (?, ?)").run(note.id, 99999);
  }, /FOREIGN KEY constraint failed/);

  // Assert referential integrity before delete
  assert.deepEqual(manager.db.pragma("foreign_key_check"), []);

  // Cascading delete: deleting note removes associated meeting, recordings, transcripts, attachments, mappings
  const deleteResult = manager.deleteNote(note.id);
  assert.equal(deleteResult.success, true);

  assert.equal(manager.getNote(note.id), null, "Note must be deleted");
  assert.equal(manager.getMeeting(meeting.id), null, "Meeting must be deleted by cascade");
  assert.equal(manager.getRecording(recording.id), null, "Recording must be deleted by cascade");
  assert.equal(manager.getTranscript(transcript.id), null, "Transcript must be deleted by cascade");
  assert.equal(manager.db.prepare("SELECT COUNT(*) AS count FROM transcript_segments WHERE transcript_id = ?").get(transcript.id).count, 0);
  assert.equal(manager.db.prepare("SELECT COUNT(*) AS count FROM attachments WHERE note_id = ?").get(note.id).count, 0);
  assert.equal(manager.db.prepare("SELECT COUNT(*) AS count FROM note_tags WHERE note_id = ?").get(note.id).count, 0);
  assert.equal(manager.db.prepare("SELECT COUNT(*) AS count FROM speaker_mappings WHERE note_id = ?").get(note.id).count, 0);

  // Reusable entities must be preserved!
  assert.ok(manager.getFolders().find((f) => f.id === folder.id), "Folder must be preserved after note deletion");
  assert.equal(manager.getTags().length, 2, "Reusable tags must be preserved after note deletion");

  // Integrity remains clean
  assert.deepEqual(manager.db.pragma("foreign_key_check"), []);
});

test("real FTS5 full-text search triggers and multilingual Unicode search across notes and transcripts", (t) => {
  const { manager } = createIsolatedEnvironment(t, "mnemora-sqlite-fts-");

  // Multilingual content: Arabic, Japanese, Turkish, English
  const arabicNote = manager.saveNote("خطة المشروع السنوية", "مناقشة متقدمة حول معمارية البيانات", "notes").note;
  const japaneseNote = manager.saveNote("年次プロジェクト計画", "データ永続性と同期アーキテクチャの要件", "notes").note;
  const turkishNote = manager.saveNote("Yıllık Proje Planı", "Veri güvenliği ve yerel veritabanı değerlendirmesi", "notes").note;
  const englishNote = manager.saveNote("Annual Architecture Review", "Deep dive into SQLite WAL mode performance", "notes").note;

  // Search Notes via FTS
  const searchArabic = manager.searchNotes("المشروع");
  assert.ok(searchArabic.length > 0 && searchArabic[0].id === arabicNote.id, "Arabic FTS search must match note");

  const searchJapanese = manager.searchNotes("同期アーキテクチャ");
  assert.ok(searchJapanese.length > 0 && searchJapanese[0].id === japaneseNote.id, "Japanese FTS search must match note");

  const searchTurkish = manager.searchNotes("değerlendirmesi");
  assert.ok(searchTurkish.length > 0 && searchTurkish[0].id === turkishNote.id, "Turkish FTS search must match note");

  const searchEnglish = manager.searchNotes("SQLite WAL");
  assert.ok(searchEnglish.length > 0 && searchEnglish[0].id === englishNote.id, "English FTS search must match note");

  // Verify triggers on UPDATE
  manager.updateNote(englishNote.id, { content: "Updated content covering FTS5 trigger synchronization" });
  assert.equal(manager.searchNotes("synchronization")[0].id, englishNote.id, "FTS update trigger must re-index updated content");

  // Verify triggers on DELETE
  manager.deleteNote(arabicNote.id);
  assert.equal(manager.searchNotes("المشروع").length, 0, "FTS delete trigger must remove indexed entries on note deletion");

  // Transcripts FTS
  const meeting = manager.getMeetingByNoteId(englishNote.id) || { id: null };
  const recording = manager.createRecording({
    meetingId: meeting.id,
    noteId: englishNote.id,
    filePath: "audio/test.webm",
  }).recording;

  const transcript = manager.createTranscript({
    meetingId: meeting.id,
    recordingId: recording.id,
    noteId: englishNote.id,
    language: "tr",
    rawText: "Türkçe transkript metni burada yer almaktadır",
    segments: [
      { startMs: 0, endMs: 3000, originalText: "Türkçe transkript metni burada yer almaktadır", speakerId: "spk-1" },
    ],
  }).transcript;

  const transcriptResults = manager.searchTranscripts("transkript");
  assert.ok(transcriptResults.length > 0 && transcriptResults[0].id === transcript.id, "Transcript FTS must match indexed segment");
});

test("real SQLite migration journaling and pre-migration backup on disposable legacy copy", (t) => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "mnemora-sqlite-mig-"));
  userDataDir = root;
  const dbFile = path.join(root, "mnemora.sqlite");

  // Create legacy database with schema version 4 in WAL mode
  const legacyDb = new BetterSqlite(dbFile);
  legacyDb.pragma("journal_mode = WAL");
  legacyDb.exec(`
    CREATE TABLE folders (
      id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, is_default INTEGER NOT NULL DEFAULT 0,
      sort_order INTEGER NOT NULL DEFAULT 0, created_at TEXT, updated_at TEXT,
      client_folder_id TEXT, cloud_id TEXT, sync_status TEXT, deleted_at TEXT
    );
    CREATE TABLE notes (
      id INTEGER PRIMARY KEY, title TEXT NOT NULL, content TEXT NOT NULL, note_type TEXT NOT NULL,
      source_file TEXT, audio_duration_seconds REAL, folder_id INTEGER, transcript TEXT,
      enhanced_content TEXT, enhancement_prompt TEXT, enhanced_at_content_hash TEXT,
      calendar_event_id TEXT,
      created_at TEXT, updated_at TEXT, client_note_id TEXT, cloud_id TEXT,
      sync_status TEXT, deleted_at TEXT
    );
    INSERT INTO notes (id, title, content, note_type, created_at, updated_at) VALUES (1, 'Legacy Note', 'Preserved Content', 'notes', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
  `);
  legacyDb.pragma("user_version = 4");
  legacyDb.pragma("wal_checkpoint(TRUNCATE)");
  legacyDb.close();

  const legacyHash = sha256(dbFile);

  // Instantiating DatabaseManager performs migration to schema version 5
  const manager = new DatabaseManager();
  t.after(() => {
    if (manager.db?.open) {
      try {
        manager.db.close();
      } catch {}
    }
    try {
      fs.rmSync(root, { recursive: true, force: true, maxRetries: 5, retryDelay: 50 });
    } catch {}
  });

  assert.equal(manager.db.pragma("user_version", { simple: true }), 5, "Migrated database must have user_version = 5");
  assert.ok(fs.existsSync(manager.lastMigrationBackupPath), "Pre-migration backup file must exist");
  assert.equal(manager.lastMigrationBackupDetails.sourceSha256, legacyHash, "Backup record must match pre-migration source SHA-256");

  // Check migration_journal table
  const journalEntries = manager.db.prepare("SELECT * FROM migration_journal ORDER BY id DESC").all();
  assert.ok(journalEntries.length > 0, "Migration journal must record migration attempt");
  const latestJournal = journalEntries[0];
  assert.equal(latestJournal.source_schema_version, 4);
  assert.equal(latestJournal.destination_schema_version, 5);
  assert.equal(latestJournal.status, "completed");
  assert.equal(latestJournal.source_sha256, legacyHash);

  // Legacy data remains completely preserved
  assert.equal(manager.getNote(1).title, "Legacy Note");
  assert.equal(manager.getNote(1).content, "Preserved Content");
});

test("real SQLite WAL checkpointing and safe connection release", (t) => {
  const { root, manager } = createIsolatedEnvironment(t, "mnemora-sqlite-wal-");
  const dbFile = path.join(root, "mnemora.sqlite");

  for (let i = 0; i < 50; i++) {
    manager.saveNote(`Concurrent Note ${i}`, `Content ${i}`, "notes");
  }

  // WAL checkpoint executes cleanly
  const checkpoint = manager.db.pragma("wal_checkpoint(TRUNCATE)");
  assert.ok(Array.isArray(checkpoint) && checkpoint.length > 0, "wal_checkpoint must succeed");

  // Close connection cleanly
  manager.db.close();
  assert.equal(manager.db.open, false);

  // Verify file on disk is accessible without lock conflicts
  const hash = sha256(dbFile);
  assert.match(hash, /^[0-9a-f]{64}$/, "Database file must be readable after close");
});
