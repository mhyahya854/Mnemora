const Database = require("better-sqlite3");
const path = require("path");
const fs = require("fs");
const debugLogger = require("../runtime/debugLogger");
const localBackup = require("./localBackup");
const { app } = require("electron");

const SCHEMA_VERSION = 4;

class DatabaseManager {
  constructor() {
    this.db = null;
    this.dbPath = null;
    this.lastMigrationBackupPath = null;
    this.initDatabase();
  }

  _runMigrations({ dbPath, hadSchema }) {
    const currentVersion = this.db.pragma("user_version", { simple: true });
    if (currentVersion > SCHEMA_VERSION) {
      throw new Error(
        `Database schema ${currentVersion} is newer than supported schema ${SCHEMA_VERSION}`
      );
    }

    const migrations = [
      {
        version: 1,
        run: () => {
          this._removeDictionaryAndSnippetSyncMetadata();
          this._removeLocalRecordSyncMetadata();
          this._cleanLegacyOrphans();
          this.db.exec(
            "CREATE INDEX IF NOT EXISTS idx_snippets_trigger_lower ON snippets(lower(trigger))"
          );
        },
      },
      { version: 2, run: () => this._createLocalDataSchema() },
      {
        version: 3,
        run: () => {
          this._createTranscriptSearchSchema();
          this._migrateLegacyMeetingNotes();
        },
      },
      { version: 4, run: () => this._removeCloudAndAgentSchema() },
    ];
    const pending = migrations.filter((migration) => migration.version > currentVersion);

    if (pending.length > 0 && hadSchema && !this.lastMigrationBackupPath) {
      this.lastMigrationBackupPath = this._createPreMigrationBackup(
        dbPath,
        currentVersion,
        SCHEMA_VERSION
      );
    }

    if (pending.length > 0) {
      this.db.transaction(() => {
        for (const migration of pending) {
          migration.run();
          this.db.pragma(`user_version = ${migration.version}`);
        }
        const violations = this.db.pragma("foreign_key_check");
        if (violations.length > 0) {
          throw new Error(`Database migration left ${violations.length} foreign-key violation(s)`);
        }
      })();
    }

    this.db.pragma("foreign_keys = ON");
    if (this.db.pragma("foreign_keys", { simple: true }) !== 1) {
      throw new Error("Failed to enable SQLite foreign-key enforcement");
    }
  }

  _createPreMigrationBackup(dbPath, fromVersion, toVersion) {
    const backupDir = path.join(path.dirname(dbPath), "migration-backups");
    fs.mkdirSync(backupDir, { recursive: true });
    const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
    const backupPath = path.join(
      backupDir,
      `mnemora-pre-migration-v${fromVersion}-to-v${toVersion}-${timestamp}.sqlite`
    );
    this.db.pragma("wal_checkpoint(FULL)");
    this.db.prepare("VACUUM INTO ?").run(backupPath);
    return backupPath;
  }

  _cleanLegacyOrphans() {
    this.db.exec(`
      UPDATE notes
      SET folder_id = NULL
      WHERE folder_id IS NOT NULL AND folder_id NOT IN (SELECT id FROM folders);

      DELETE FROM speaker_mappings
      WHERE note_id NOT IN (SELECT id FROM notes);
      UPDATE speaker_mappings
      SET profile_id = NULL
      WHERE profile_id IS NOT NULL AND profile_id NOT IN (SELECT id FROM speaker_profiles);
      DELETE FROM note_speaker_embeddings
      WHERE note_id NOT IN (SELECT id FROM notes);
    `);

  }

  _createNoteSearchSchema() {
    this.db.exec(`
      CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(
        title,
        content,
        content='notes',
        content_rowid='id'
      );

      CREATE TRIGGER IF NOT EXISTS notes_fts_insert AFTER INSERT ON notes BEGIN
        INSERT INTO notes_fts(rowid, title, content) VALUES (new.id, new.title, new.content);
      END;

      CREATE TRIGGER IF NOT EXISTS notes_fts_update AFTER UPDATE ON notes BEGIN
        INSERT INTO notes_fts(notes_fts, rowid, title, content)
        VALUES ('delete', old.id, old.title, old.content);
        INSERT INTO notes_fts(rowid, title, content) VALUES (new.id, new.title, new.content);
      END;

      CREATE TRIGGER IF NOT EXISTS notes_fts_delete AFTER DELETE ON notes BEGIN
        INSERT INTO notes_fts(notes_fts, rowid, title, content)
        VALUES ('delete', old.id, old.title, old.content);
      END;

      INSERT OR IGNORE INTO notes_fts(rowid, title, content)
      SELECT id, COALESCE(title, ''), COALESCE(content, '') FROM notes;
    `);
  }

  _removeCloudAndAgentSchema() {
    this.db.exec(`
      DROP TRIGGER IF EXISTS notes_fts_insert;
      DROP TRIGGER IF EXISTS notes_fts_update;
      DROP TRIGGER IF EXISTS notes_fts_delete;
      DROP TABLE IF EXISTS notes_fts;
      DROP TABLE IF EXISTS agent_messages;
      DROP TABLE IF EXISTS agent_conversations;
      DROP TABLE IF EXISTS actions;
      DROP TABLE IF EXISTS calendar_events;
      DROP TABLE IF EXISTS google_calendars;
      DROP TABLE IF EXISTS google_calendar_tokens;
    `);
    const noteColumns = new Set(this.db.pragma("table_info(notes)").map((column) => column.name));
    for (const column of [
      "enhanced_content",
      "enhancement_prompt",
      "enhanced_at_content_hash",
      "calendar_event_id",
    ]) {
      if (noteColumns.has(column)) this.db.exec(`ALTER TABLE notes DROP COLUMN ${column}`);
    }
    this._createNoteSearchSchema();
  }

  _createLocalDataSchema() {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS local_settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL COLLATE NOCASE UNIQUE,
        color TEXT,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS note_tags (
        note_id INTEGER NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
        tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
        PRIMARY KEY (note_id, tag_id)
      );

      CREATE TABLE IF NOT EXISTS meetings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        note_id INTEGER UNIQUE REFERENCES notes(id) ON DELETE CASCADE,
        title TEXT NOT NULL DEFAULT 'Untitled Meeting',
        started_at DATETIME,
        ended_at DATETIME,
        status TEXT NOT NULL DEFAULT 'completed',
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS meeting_tags (
        meeting_id INTEGER NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
        tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
        PRIMARY KEY (meeting_id, tag_id)
      );

      CREATE TABLE IF NOT EXISTS recordings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        meeting_id INTEGER REFERENCES meetings(id) ON DELETE CASCADE,
        note_id INTEGER REFERENCES notes(id) ON DELETE CASCADE,
        kind TEXT NOT NULL DEFAULT 'meeting',
        file_path TEXT NOT NULL,
        source_name TEXT,
        mime_type TEXT,
        duration_ms INTEGER,
        sample_rate INTEGER,
        channels INTEGER,
        size_bytes INTEGER,
        sha256 TEXT,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS transcripts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        meeting_id INTEGER REFERENCES meetings(id) ON DELETE CASCADE,
        recording_id INTEGER REFERENCES recordings(id) ON DELETE SET NULL,
        note_id INTEGER REFERENCES notes(id) ON DELETE CASCADE,
        language TEXT,
        source TEXT NOT NULL DEFAULT 'local',
        status TEXT NOT NULL DEFAULT 'completed',
        raw_text TEXT NOT NULL DEFAULT '',
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
      );

      CREATE UNIQUE INDEX IF NOT EXISTS idx_transcripts_legacy_note
      ON transcripts(note_id) WHERE source = 'legacy_note';

      CREATE TABLE IF NOT EXISTS transcript_segments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transcript_id INTEGER NOT NULL REFERENCES transcripts(id) ON DELETE CASCADE,
        segment_index INTEGER NOT NULL,
        start_ms INTEGER,
        end_ms INTEGER,
        speaker_id TEXT,
        speaker_name TEXT,
        speaker_profile_id INTEGER REFERENCES speaker_profiles(id) ON DELETE SET NULL,
        original_text TEXT NOT NULL DEFAULT '',
        edited_text TEXT,
        confidence REAL,
        language TEXT,
        source TEXT,
        status TEXT NOT NULL DEFAULT 'final',
        speaker_status TEXT,
        speaker_locked INTEGER NOT NULL DEFAULT 0,
        metadata_json TEXT,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (transcript_id, segment_index)
      );

      CREATE INDEX IF NOT EXISTS idx_transcript_segments_transcript
      ON transcript_segments(transcript_id, segment_index);

      CREATE TABLE IF NOT EXISTS attachments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        note_id INTEGER REFERENCES notes(id) ON DELETE CASCADE,
        meeting_id INTEGER REFERENCES meetings(id) ON DELETE CASCADE,
        file_path TEXT NOT NULL,
        display_name TEXT,
        mime_type TEXT,
        size_bytes INTEGER,
        sha256 TEXT,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS backups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT NOT NULL UNIQUE,
        kind TEXT NOT NULL DEFAULT 'manual',
        status TEXT NOT NULL DEFAULT 'completed',
        includes_audio INTEGER NOT NULL DEFAULT 0,
        manifest_json TEXT,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        completed_at DATETIME
      );

      CREATE TABLE IF NOT EXISTS semantic_index_state (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        schema_version INTEGER NOT NULL DEFAULT 1,
        model_id TEXT,
        model_sha256 TEXT,
        status TEXT NOT NULL DEFAULT 'not_built',
        last_indexed_at DATETIME,
        last_error TEXT,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
      );

      INSERT OR IGNORE INTO semantic_index_state (id) VALUES (1);
    `);
  }

  _createTranscriptSearchSchema() {
    this.db.exec(`
      CREATE VIRTUAL TABLE IF NOT EXISTS transcript_segments_fts USING fts5(
        original_text,
        edited_text,
        content='transcript_segments',
        content_rowid='id',
        tokenize='unicode61'
      );

      CREATE TRIGGER IF NOT EXISTS transcript_segments_fts_insert
      AFTER INSERT ON transcript_segments BEGIN
        INSERT INTO transcript_segments_fts(rowid, original_text, edited_text)
        VALUES (new.id, new.original_text, new.edited_text);
      END;

      CREATE TRIGGER IF NOT EXISTS transcript_segments_fts_update
      AFTER UPDATE ON transcript_segments BEGIN
        INSERT INTO transcript_segments_fts(
          transcript_segments_fts, rowid, original_text, edited_text
        ) VALUES ('delete', old.id, old.original_text, old.edited_text);
        INSERT INTO transcript_segments_fts(rowid, original_text, edited_text)
        VALUES (new.id, new.original_text, new.edited_text);
      END;

      CREATE TRIGGER IF NOT EXISTS transcript_segments_fts_delete
      AFTER DELETE ON transcript_segments BEGIN
        INSERT INTO transcript_segments_fts(
          transcript_segments_fts, rowid, original_text, edited_text
        ) VALUES ('delete', old.id, old.original_text, old.edited_text);
      END;

      INSERT OR IGNORE INTO transcript_segments_fts(rowid, original_text, edited_text)
      SELECT id, COALESCE(original_text, ''), COALESCE(edited_text, '')
      FROM transcript_segments;
    `);
  }

  _migrateLegacyMeetingNotes() {
    const notes = this.db
      .prepare(
        `SELECT * FROM notes
         WHERE note_type = 'meeting'
         ORDER BY id`
      )
      .all();
    for (const note of notes) {
      this._syncLegacyNoteTranscript(note.id, note);
    }
  }

  _syncLegacyNoteTranscript(noteId, existingNote = null) {
    const note = existingNote || this.db.prepare("SELECT * FROM notes WHERE id = ?").get(noteId);
    if (!note || note.note_type !== "meeting") return null;

    this.db
      .prepare(
        `INSERT INTO meetings (note_id, title, created_at, updated_at)
         VALUES (?, ?, COALESCE(?, CURRENT_TIMESTAMP), COALESCE(?, CURRENT_TIMESTAMP))
         ON CONFLICT(note_id) DO UPDATE SET
           title = excluded.title,
           updated_at = excluded.updated_at`
      )
      .run(note.id, note.title || "Untitled Meeting", note.created_at, note.updated_at);
    const meeting = this.db.prepare("SELECT * FROM meetings WHERE note_id = ?").get(note.id);
    const raw = typeof note.transcript === "string" ? note.transcript : "";
    if (!raw.trim()) {
      this.db
        .prepare("DELETE FROM transcripts WHERE note_id = ? AND source = 'legacy_note'")
        .run(note.id);
      return { meeting, transcript: null };
    }

    this.db
      .prepare(
        `INSERT INTO transcripts (
           meeting_id, note_id, source, status, raw_text, created_at, updated_at
         ) VALUES (?, ?, 'legacy_note', 'completed', ?, COALESCE(?, CURRENT_TIMESTAMP), COALESCE(?, CURRENT_TIMESTAMP))
         ON CONFLICT(note_id) WHERE source = 'legacy_note' DO UPDATE SET
           meeting_id = excluded.meeting_id,
           raw_text = excluded.raw_text,
           updated_at = excluded.updated_at`
      )
      .run(meeting.id, note.id, raw, note.created_at, note.updated_at);
    const transcript = this.db
      .prepare("SELECT * FROM transcripts WHERE note_id = ? AND source = 'legacy_note'")
      .get(note.id);

    let segments;
    try {
      const parsed = JSON.parse(raw);
      segments = Array.isArray(parsed) ? parsed : [{ text: raw, source: "legacy" }];
    } catch {
      segments = [{ text: raw, source: "legacy" }];
    }

    const timestamps = segments
      .map((segment) => Number(segment?.timestamp))
      .filter(Number.isFinite);
    const minimumTimestamp = timestamps.length > 0 ? Math.min(...timestamps) : null;
    const timestampScale = minimumTimestamp !== null && minimumTimestamp > 100_000_000_000 ? 1 : 1000;
    const epochBase = minimumTimestamp !== null && minimumTimestamp > 100_000_000
      ? minimumTimestamp
      : null;
    const remove = this.db.prepare("DELETE FROM transcript_segments WHERE transcript_id = ?");
    const insert = this.db.prepare(
      `INSERT INTO transcript_segments (
         transcript_id, segment_index, start_ms, end_ms, speaker_id, speaker_name,
         original_text, edited_text, confidence, language, source, status,
         speaker_status, speaker_locked, metadata_json
       ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
    );
    remove.run(transcript.id);
    segments.forEach((segment, index) => {
      const value = segment && typeof segment === "object" ? segment : { text: String(segment) };
      const timestamp = Number(value.timestamp);
      const startMs = Number.isFinite(timestamp)
        ? Math.max(
            0,
            Math.round((timestamp - (epochBase === null ? 0 : epochBase)) * timestampScale)
          )
        : null;
      const end = Number(value.end_ms ?? value.endMs);
      insert.run(
        transcript.id,
        index,
        startMs,
        Number.isFinite(end) ? Math.max(startMs || 0, Math.round(end)) : null,
        value.speaker ?? null,
        value.speakerName ?? null,
        value.text == null ? "" : String(value.text),
        value.editedText == null ? null : String(value.editedText),
        Number.isFinite(Number(value.confidence)) ? Number(value.confidence) : null,
        value.language ?? null,
        value.source ?? null,
        value.status ?? "final",
        value.speakerStatus ?? null,
        value.speakerLocked ? 1 : 0,
        JSON.stringify(value)
      );
    });
    return { meeting, transcript };
  }

  _ftsQuery(query) {
    const tokens = String(query || "")
      .normalize("NFKC")
      .match(/[\p{L}\p{N}_]+/gu);
    if (!tokens || tokens.length === 0) return null;
    return tokens.map((token) => `"${token.replace(/"/g, '""')}"*`).join(" AND ");
  }

  _writeTranscriptSegments(transcriptId, segments) {
    this.db.prepare("DELETE FROM transcript_segments WHERE transcript_id = ?").run(transcriptId);
    const insert = this.db.prepare(
      `INSERT INTO transcript_segments (
         transcript_id, segment_index, start_ms, end_ms, speaker_id, speaker_name,
         speaker_profile_id, original_text, edited_text, confidence, language, source,
         status, speaker_status, speaker_locked, metadata_json
       ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
    );
    (Array.isArray(segments) ? segments : []).forEach((segment, index) => {
      const startMs = Number(segment?.startMs ?? segment?.start_ms);
      const endMs = Number(segment?.endMs ?? segment?.end_ms);
      const confidence = Number(segment?.confidence);
      const normalizedStart = Number.isFinite(startMs) ? Math.max(0, Math.round(startMs)) : null;
      const normalizedEnd = Number.isFinite(endMs)
        ? Math.max(normalizedStart || 0, Math.round(endMs))
        : null;
      insert.run(
        transcriptId,
        Number.isInteger(segment?.segmentIndex) ? segment.segmentIndex : index,
        normalizedStart,
        normalizedEnd,
        segment?.speakerId ?? segment?.speaker_id ?? segment?.speaker ?? null,
        segment?.speakerName ?? segment?.speaker_name ?? null,
        segment?.speakerProfileId ?? segment?.speaker_profile_id ?? null,
        String(segment?.originalText ?? segment?.original_text ?? segment?.text ?? ""),
        segment?.editedText ?? segment?.edited_text ?? null,
        Number.isFinite(confidence) ? confidence : null,
        segment?.language ?? null,
        segment?.source ?? null,
        segment?.status ?? "final",
        segment?.speakerStatus ?? segment?.speaker_status ?? null,
        segment?.speakerLocked || segment?.speaker_locked ? 1 : 0,
        typeof segment?.metadataJson === "string"
          ? segment.metadataJson
          : JSON.stringify(segment || {})
      );
    });
  }

  initDatabase() {
    try {
      this.lastMigrationBackupPath = null;
      const dbFileName =
        process.env.NODE_ENV === "development" ? "mnemora-dev.sqlite" : "mnemora.sqlite";

      const dbPath = path.join(app.getPath("userData"), dbFileName);
      this.dbPath = dbPath;

      this.db = new Database(dbPath);
      this.db.pragma("journal_mode = WAL");
      this.db.pragma("busy_timeout = 5000");
      this.db.pragma("foreign_keys = OFF");
      const hadSchema =
        this.db
          .prepare("SELECT COUNT(*) AS count FROM sqlite_master WHERE type = 'table'")
          .get().count > 0;
      const startingVersion = this.db.pragma("user_version", { simple: true });
      if (startingVersion > SCHEMA_VERSION) {
        throw new Error(
          `Database schema ${startingVersion} is newer than supported schema ${SCHEMA_VERSION}`
        );
      }
      if (hadSchema && startingVersion < SCHEMA_VERSION) {
        this.lastMigrationBackupPath = this._createPreMigrationBackup(
          dbPath,
          startingVersion,
          SCHEMA_VERSION
        );
      }

      this.db.transaction(() => {
      this.db.exec(`
        CREATE TABLE IF NOT EXISTS transcriptions (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          text TEXT NOT NULL,
          timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `);

      // Audio retention columns
      try {
        this.db.exec("ALTER TABLE transcriptions ADD COLUMN raw_text TEXT");
      } catch (err) {
        if (!err.message.includes("duplicate column")) throw err;
      }
      try {
        this.db.exec("ALTER TABLE transcriptions ADD COLUMN has_audio INTEGER NOT NULL DEFAULT 0");
      } catch (err) {
        if (!err.message.includes("duplicate column")) throw err;
      }
      try {
        this.db.exec("ALTER TABLE transcriptions ADD COLUMN audio_duration_ms INTEGER");
      } catch (err) {
        if (!err.message.includes("duplicate column")) throw err;
      }
      try {
        this.db.exec("ALTER TABLE transcriptions ADD COLUMN provider TEXT");
      } catch (err) {
        if (!err.message.includes("duplicate column")) throw err;
      }
      try {
        this.db.exec("ALTER TABLE transcriptions ADD COLUMN model TEXT");
      } catch (err) {
        if (!err.message.includes("duplicate column")) throw err;
      }
      try {
        this.db.exec(
          "ALTER TABLE transcriptions ADD COLUMN status TEXT NOT NULL DEFAULT 'completed'"
        );
      } catch (err) {
        if (!err.message.includes("duplicate column")) throw err;
      }
      try {
        this.db.exec("ALTER TABLE transcriptions ADD COLUMN error_message TEXT");
      } catch (err) {
        if (!err.message.includes("duplicate column")) throw err;
      }
      try {
        this.db.exec("ALTER TABLE transcriptions ADD COLUMN error_code TEXT");
      } catch (err) {
        if (!err.message.includes("duplicate column")) throw err;
      }

      this.db.exec(`
        CREATE TABLE IF NOT EXISTS custom_dictionary (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          word TEXT NOT NULL UNIQUE,
          source TEXT NOT NULL DEFAULT 'manual',
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `);

      this.db.exec(`
        CREATE TABLE IF NOT EXISTS snippets (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          trigger TEXT NOT NULL,
          replacement TEXT NOT NULL,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `);

      this.db.exec(`
        CREATE TABLE IF NOT EXISTS notes (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          title TEXT NOT NULL DEFAULT 'Untitled Note',
          content TEXT NOT NULL DEFAULT '',
          note_type TEXT NOT NULL DEFAULT 'personal',
          source_file TEXT,
          audio_duration_seconds REAL,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `);

      this.db.exec(`
        CREATE TABLE IF NOT EXISTS folders (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL UNIQUE,
          is_default INTEGER NOT NULL DEFAULT 0,
          sort_order INTEGER NOT NULL DEFAULT 0,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `);

      const seedFolder = this.db.prepare(
        "INSERT OR IGNORE INTO folders (name, is_default, sort_order) VALUES (?, 1, ?)"
      );
      seedFolder.run("Personal", 0);
      seedFolder.run("Meetings", 1);

      try {
        this.db.exec("ALTER TABLE notes ADD COLUMN folder_id INTEGER REFERENCES folders(id)");
      } catch (err) {
        if (!err.message.includes("duplicate column")) throw err;
      }

      const personalFolder = this.db
        .prepare("SELECT id FROM folders WHERE name = 'Personal' AND is_default = 1")
        .get();
      const meetingsFolder = this.db
        .prepare("SELECT id FROM folders WHERE name = 'Meetings' AND is_default = 1")
        .get();
      if (meetingsFolder) {
        this.db
          .prepare("UPDATE notes SET folder_id = ? WHERE folder_id IS NULL AND note_type = 'meeting'")
          .run(meetingsFolder.id);
      }
      if (personalFolder) {
        this.db
          .prepare("UPDATE notes SET folder_id = ? WHERE folder_id IS NULL AND note_type != 'meeting'")
          .run(personalFolder.id);
      }

      try {
        this.db.exec("ALTER TABLE notes ADD COLUMN transcript TEXT");
      } catch (err) {
        if (!err.message.includes("duplicate column")) throw err;
      }
      try {
        this.db.exec("ALTER TABLE notes ADD COLUMN participants TEXT");
      } catch (err) {
        if (!err.message.includes("duplicate column")) throw err;
      }
      try {
        this.db.exec("ALTER TABLE notes ADD COLUMN diarization_enabled INTEGER");
      } catch (err) {
        if (!err.message.includes("duplicate column")) throw err;
      }
      try {
        this.db.exec("ALTER TABLE notes ADD COLUMN expected_speaker_count INTEGER");
      } catch (err) {
        if (!err.message.includes("duplicate column")) throw err;
      }

      this.db.exec(`
        CREATE TABLE IF NOT EXISTS contacts (
          email TEXT PRIMARY KEY,
          display_name TEXT,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `);

      this.db.exec(`
        CREATE TABLE IF NOT EXISTS speaker_profiles (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          display_name TEXT NOT NULL,
          email TEXT,
          embedding BLOB NOT NULL,
          sample_count INTEGER DEFAULT 1,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `);

      this.db.exec(`
        CREATE TABLE IF NOT EXISTS speaker_mappings (
          note_id INTEGER NOT NULL,
          speaker_id TEXT NOT NULL,
          profile_id INTEGER,
          display_name TEXT NOT NULL,
          PRIMARY KEY (note_id, speaker_id),
          FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE,
          FOREIGN KEY (profile_id) REFERENCES speaker_profiles(id) ON DELETE SET NULL
        )
      `);

      this.db.exec(`
        CREATE TABLE IF NOT EXISTS note_speaker_embeddings (
          note_id INTEGER NOT NULL,
          speaker_id TEXT NOT NULL,
          embedding BLOB NOT NULL,
          PRIMARY KEY (note_id, speaker_id),
          FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
        )
      `);

      try {
        this.db.exec("ALTER TABLE folders ADD COLUMN updated_at DATETIME");
        this.db.exec("UPDATE folders SET updated_at = created_at WHERE updated_at IS NULL");
      } catch (err) {
        if (!err.message.includes("duplicate column")) throw err;
      }

      // Local dictionary metadata. Existing installations may predate these fields.
      try {
        this.db.exec(
          "ALTER TABLE custom_dictionary ADD COLUMN source TEXT NOT NULL DEFAULT 'manual'"
        );
      } catch (err) {
        if (!err.message.includes("duplicate column")) throw err;
      }
      try {
        this.db.exec("ALTER TABLE custom_dictionary ADD COLUMN updated_at DATETIME");
        this.db.exec(
          "UPDATE custom_dictionary SET updated_at = created_at WHERE updated_at IS NULL"
        );
      } catch (err) {
        if (!err.message.includes("duplicate column")) throw err;
      }

      })();
      this._runMigrations({ dbPath, hadSchema });

      return true;
    } catch (error) {
      debugLogger.error("Database initialization failed", { error: error.message }, "database");
      if (this.db?.open) this.db.close();
      this.db = null;
      throw error;
    }
  }

  _removeDictionaryAndSnippetSyncMetadata() {
    const hasColumn = (table, column) =>
      this.db.pragma(`table_info(${table})`).some((entry) => entry.name === column);
    const dropColumn = (table, column) => {
      if (hasColumn(table, column)) {
        this.db.exec(`ALTER TABLE ${table} DROP COLUMN ${column}`);
      }
    };

    this.db.exec("DROP INDEX IF EXISTS idx_custom_dictionary_client_id");
    this.db.exec("DROP INDEX IF EXISTS idx_snippets_client_id");
    this.db.exec("DROP INDEX IF EXISTS idx_snippets_trigger_lower_active");
    this.db.exec("DROP INDEX IF EXISTS idx_snippets_pending_sync");

    for (const column of ["client_dict_id", "cloud_id", "sync_status", "deleted_at"]) {
      dropColumn("custom_dictionary", column);
    }
    for (const column of ["client_snippet_id", "cloud_id", "sync_status", "deleted_at"]) {
      dropColumn("snippets", column);
    }
  }

  _removeLocalRecordSyncMetadata() {
    const hasColumn = (table, column) =>
      this.db.pragma(`table_info(${table})`).some((entry) => entry.name === column);
    const dropColumn = (table, column) => {
      if (hasColumn(table, column)) {
        this.db.exec(`ALTER TABLE ${table} DROP COLUMN ${column}`);
      }
    };

    this.db.exec("DROP INDEX IF EXISTS idx_notes_client_note_id");
    this.db.exec("DROP INDEX IF EXISTS idx_folders_client_folder_id");
    this.db.exec("DROP INDEX IF EXISTS idx_transcriptions_client_id");

    for (const column of ["client_note_id", "cloud_id", "sync_status", "deleted_at"]) {
      dropColumn("notes", column);
    }
    for (const column of ["client_folder_id", "cloud_id", "sync_status", "deleted_at"]) {
      dropColumn("folders", column);
    }
    for (const column of ["client_transcription_id", "cloud_id", "sync_status", "deleted_at"]) {
      dropColumn("transcriptions", column);
    }
  }

  saveTranscription(
    text,
    rawText = null,
    {
      status = "completed",
      errorMessage = null,
      errorCode = null,
    } = {}
  ) {
    try {
      if (!this.db) {
        throw new Error("Database not initialized");
      }
      const stmt = this.db.prepare(
        "INSERT INTO transcriptions (text, raw_text, status, error_message, error_code) VALUES (?, ?, ?, ?, ?)"
      );
      const result = stmt.run(
        text,
        rawText,
        status,
        errorMessage,
        errorCode
      );

      const fetchStmt = this.db.prepare("SELECT * FROM transcriptions WHERE id = ?");
      const transcription = fetchStmt.get(result.lastInsertRowid);

      return { id: result.lastInsertRowid, success: true, transcription };
    } catch (error) {
      debugLogger.error("Error saving transcription", { error: error.message }, "database");
      throw error;
    }
  }

  getTranscriptions(limit = 50, { includeDiscarded = false } = {}) {
    try {
      if (!this.db) {
        throw new Error("Database not initialized");
      }
      const statusFilter = includeDiscarded ? "" : " AND status != 'discarded'";
      const stmt = this.db.prepare(
        `SELECT * FROM transcriptions WHERE 1 = 1${statusFilter} ORDER BY timestamp DESC LIMIT ?`
      );
      const transcriptions = stmt.all(limit);
      return transcriptions;
    } catch (error) {
      debugLogger.error("Error getting transcriptions", { error: error.message }, "database");
      throw error;
    }
  }

  clearTranscriptions() {
    try {
      if (!this.db) {
        throw new Error("Database not initialized");
      }
      const result = this.db.prepare("DELETE FROM transcriptions").run();
      return { cleared: result.changes, success: true };
    } catch (error) {
      debugLogger.error("Error clearing transcriptions", { error: error.message }, "database");
      throw error;
    }
  }

  deleteTranscription(id) {
    try {
      if (!this.db) {
        throw new Error("Database not initialized");
      }
      const result = this.db.prepare("DELETE FROM transcriptions WHERE id = ?").run(id);
      return { success: result.changes > 0, id };
    } catch (error) {
      debugLogger.error("Error deleting transcription", { error: error.message }, "database");
      throw error;
    }
  }

  updateTranscriptionAudio(id, { hasAudio, audioDurationMs, provider, model }) {
    try {
      if (!this.db) throw new Error("Database not initialized");
      const stmt = this.db.prepare(
        "UPDATE transcriptions SET has_audio = ?, audio_duration_ms = ?, provider = ?, model = ? WHERE id = ?"
      );
      stmt.run(hasAudio, audioDurationMs, provider, model, id);
      return { success: true };
    } catch (error) {
      debugLogger.error("Error updating transcription audio", { error: error.message }, "database");
      throw error;
    }
  }

  updateTranscriptionText(id, text, rawText) {
    try {
      if (!this.db) throw new Error("Database not initialized");
      const stmt = this.db.prepare("UPDATE transcriptions SET text = ?, raw_text = ? WHERE id = ?");
      stmt.run(text, rawText, id);
      return { success: true };
    } catch (error) {
      debugLogger.error("Error updating transcription text", { error: error.message }, "database");
      throw error;
    }
  }

  updateTranscriptionStatus(id, status, errorMessage = null, errorCode = null) {
    try {
      if (!this.db) throw new Error("Database not initialized");
      const stmt = this.db.prepare(
        "UPDATE transcriptions SET status = ?, error_message = ?, error_code = ? WHERE id = ?"
      );
      stmt.run(status, errorMessage, errorCode, id);
      return { success: true };
    } catch (error) {
      debugLogger.error(
        "Error updating transcription status",
        { error: error.message },
        "database"
      );
      throw error;
    }
  }

  getTranscriptionById(id) {
    try {
      if (!this.db) throw new Error("Database not initialized");
      const stmt = this.db.prepare("SELECT * FROM transcriptions WHERE id = ?");
      return stmt.get(id) || null;
    } catch (error) {
      debugLogger.error("Error getting transcription by id", { error: error.message }, "database");
      throw error;
    }
  }

  clearAudioFlags(ids) {
    try {
      if (!this.db) throw new Error("Database not initialized");
      if (!ids || ids.length === 0) return { success: true };
      const transaction = this.db.transaction((idList) => {
        const stmt = this.db.prepare("UPDATE transcriptions SET has_audio = 0 WHERE id = ?");
        for (const id of idList) {
          stmt.run(id);
        }
      });
      transaction(ids);
      return { success: true };
    } catch (error) {
      debugLogger.error("Error clearing audio flags", { error: error.message }, "database");
      throw error;
    }
  }

  getDictionary() {
    try {
      if (!this.db) {
        throw new Error("Database not initialized");
      }
      const rows = this.db
        .prepare("SELECT word FROM custom_dictionary ORDER BY id ASC")
        .all();
      return rows.map((row) => row.word);
    } catch (error) {
      debugLogger.error("Error getting dictionary", { error: error.message }, "database");
      throw error;
    }
  }

  // Diff-based update so unchanged rows retain their local source and timestamps.
  // `sourceForNewWords` tags additions ('manual' for user-typed, 'learned' for auto-learn).
  setDictionary(words, sourceForNewWords = "manual") {
    try {
      if (!this.db) {
        throw new Error("Database not initialized");
      }
      // Dedupe input by lower(word), keeping the first occurrence's casing, so
      // the diff loop sees at most one incoming entry per word.
      const incomingByLower = new Map();
      for (const raw of Array.isArray(words) ? words : []) {
        if (typeof raw !== "string") continue;
        const trimmed = raw.trim();
        if (!trimmed) continue;
        const lower = trimmed.toLowerCase();
        if (!incomingByLower.has(lower)) incomingByLower.set(lower, trimmed);
      }
      const cleaned = Array.from(incomingByLower.values());
      const incomingLower = new Set(incomingByLower.keys());

      const existingRows = this.db.prepare("SELECT id, word, source FROM custom_dictionary").all();
      const existingByLower = new Map(existingRows.map((r) => [r.word.toLowerCase(), r]));

      const remove = this.db.prepare("DELETE FROM custom_dictionary WHERE id = ?");
      const promoteSource = this.db.prepare(
        "UPDATE custom_dictionary SET word = ?, source = 'manual', updated_at = datetime('now') WHERE id = ? AND source = 'learned'"
      );
      // Guard unchanged values so no-op saves do not touch local timestamps.
      const updateWord = this.db.prepare(
        "UPDATE custom_dictionary SET word = ?, updated_at = datetime('now') WHERE id = ? AND word != ?"
      );
      const insert = this.db.prepare(
        "INSERT OR IGNORE INTO custom_dictionary (word, source, updated_at) VALUES (?, ?, datetime('now'))"
      );

      this.db.transaction(() => {
        for (const existing of existingRows) {
          if (incomingLower.has(existing.word.toLowerCase())) continue;
          remove.run(existing.id);
        }
        for (const word of cleaned) {
          const existing = existingByLower.get(word.toLowerCase());
          if (existing) {
            if (sourceForNewWords === "manual" && existing.source === "learned") {
              promoteSource.run(word, existing.id);
            } else {
              updateWord.run(word, existing.id, word);
            }
            continue;
          }
          insert.run(word, sourceForNewWords);
        }
      })();

      return { success: true };
    } catch (error) {
      debugLogger.error("Error setting dictionary", { error: error.message }, "database");
      throw error;
    }
  }

  getSnippets() {
    try {
      if (!this.db) {
        throw new Error("Database not initialized");
      }
      return this.db
        .prepare("SELECT trigger, replacement FROM snippets ORDER BY id ASC")
        .all();
    } catch (error) {
      debugLogger.error("Error getting snippets", { error: error.message }, "database");
      throw error;
    }
  }

  setSnippets(snippets) {
    try {
      if (!this.db) {
        throw new Error("Database not initialized");
      }

      const incomingByLower = new Map();
      for (const raw of Array.isArray(snippets) ? snippets : []) {
        if (!raw || typeof raw !== "object") continue;
        const trigger = typeof raw.trigger === "string" ? raw.trigger.trim() : "";
        const replacement = typeof raw.replacement === "string" ? raw.replacement.trim() : "";
        if (!trigger || !replacement) continue;
        const lower = trigger.toLowerCase();
        if (!incomingByLower.has(lower)) incomingByLower.set(lower, { trigger, replacement });
      }
      const cleaned = Array.from(incomingByLower.values());
      const incomingLower = new Set(incomingByLower.keys());

      const existingRows = this.db.prepare("SELECT id, trigger, replacement FROM snippets").all();
      const existingByLower = new Map(existingRows.map((row) => [row.trigger.toLowerCase(), row]));
      const remove = this.db.prepare("DELETE FROM snippets WHERE id = ?");
      const updateActive = this.db.prepare(
        "UPDATE snippets SET trigger = ?, replacement = ?, updated_at = datetime('now') WHERE id = ? AND (trigger != ? OR replacement != ?)"
      );
      const insert = this.db.prepare(
        "INSERT OR IGNORE INTO snippets (trigger, replacement, updated_at) VALUES (?, ?, datetime('now'))"
      );

      this.db.transaction(() => {
        for (const existing of existingRows) {
          if (incomingLower.has(existing.trigger.toLowerCase())) continue;
          remove.run(existing.id);
        }

        for (const snippet of cleaned) {
          const existing = existingByLower.get(snippet.trigger.toLowerCase());
          if (existing) {
            updateActive.run(
              snippet.trigger,
              snippet.replacement,
              existing.id,
              snippet.trigger,
              snippet.replacement
            );
            continue;
          }
          insert.run(snippet.trigger, snippet.replacement);
        }
      })();

      return { success: true };
    } catch (error) {
      debugLogger.error("Error setting snippets", { error: error.message }, "database");
      throw error;
    }
  }

  saveNote(
    title,
    content,
    noteType = "personal",
    sourceFile = null,
    audioDuration = null,
    folderId = null
  ) {
    try {
      if (!this.db) {
        throw new Error("Database not initialized");
      }
      if (!folderId) {
        const defaultFolderName = noteType === "meeting" ? "Meetings" : "Personal";
        const defaultFolder = this.db
          .prepare("SELECT id FROM folders WHERE name = ? AND is_default = 1")
          .get(defaultFolderName);
        folderId = defaultFolder?.id || null;
      }
      return this.db.transaction(() => {
        const result = this.db
          .prepare(
            "INSERT INTO notes (title, content, note_type, source_file, audio_duration_seconds, folder_id) VALUES (?, ?, ?, ?, ?, ?)"
          )
          .run(title, content, noteType, sourceFile, audioDuration, folderId);
        const note = this.db
          .prepare("SELECT * FROM notes WHERE id = ?")
          .get(result.lastInsertRowid);
        if (noteType === "meeting") this._syncLegacyNoteTranscript(note.id, note);
        return { success: true, note };
      })();
    } catch (error) {
      debugLogger.error("Error saving note", { error: error.message }, "notes");
      throw error;
    }
  }

  getNote(id) {
    try {
      if (!this.db) {
        throw new Error("Database not initialized");
      }
      const stmt = this.db.prepare("SELECT * FROM notes WHERE id = ?");
      return stmt.get(id) || null;
    } catch (error) {
      debugLogger.error("Error getting note", { error: error.message }, "notes");
      throw error;
    }
  }

  getNotes(noteType = null, limit = 100, folderId = null) {
    try {
      if (!this.db) {
        throw new Error("Database not initialized");
      }
      const conditions = [];
      const params = [];
      if (noteType) {
        conditions.push("note_type = ?");
        params.push(noteType);
      }
      if (folderId) {
        conditions.push("folder_id = ?");
        params.push(folderId);
      }
      const where = conditions.length > 0 ? `WHERE ${conditions.join(" AND ")}` : "";
      const stmt = this.db.prepare(`SELECT * FROM notes ${where} ORDER BY updated_at DESC LIMIT ?`);
      params.push(limit);
      return stmt.all(...params);
    } catch (error) {
      debugLogger.error("Error getting notes", { error: error.message }, "notes");
      throw error;
    }
  }

  updateNote(id, updates) {
    try {
      if (!this.db) throw new Error("Database not initialized");
      const allowedFields = [
        "title",
        "content",
        "folder_id",
        "transcript",
        "participants",
        "diarization_enabled",
        "expected_speaker_count",
      ];
      const fields = [];
      const values = [];
      for (const [key, value] of Object.entries(updates)) {
        if (allowedFields.includes(key) && value !== undefined) {
          fields.push(`${key} = ?`);
          values.push(value);
        }
      }
      if (fields.length === 0) return { success: false };
      fields.push("updated_at = CURRENT_TIMESTAMP");
      values.push(id);
      return this.db.transaction(() => {
        this.db.prepare(`UPDATE notes SET ${fields.join(", ")} WHERE id = ?`).run(...values);
        const note = this.db.prepare("SELECT * FROM notes WHERE id = ?").get(id);
        if (note?.note_type === "meeting" && updates.transcript !== undefined) {
          this._syncLegacyNoteTranscript(id, note);
        } else if (note?.note_type === "meeting" && updates.title !== undefined) {
          this.db
            .prepare("UPDATE meetings SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE note_id = ?")
            .run(note.title, id);
        }
        return { success: true, note };
      })();
    } catch (error) {
      debugLogger.error("Error updating note", { error: error.message }, "notes");
      throw error;
    }
  }

  getFolders() {
    try {
      if (!this.db) throw new Error("Database not initialized");
      return this.db
        .prepare("SELECT * FROM folders ORDER BY sort_order ASC, created_at ASC")
        .all();
    } catch (error) {
      debugLogger.error("Error getting folders", { error: error.message }, "notes");
      throw error;
    }
  }

  createFolder(name) {
    try {
      if (!this.db) throw new Error("Database not initialized");
      const trimmed = (name || "").trim();
      if (!trimmed) return { success: false, error: "Folder name is required" };
      const existing = this.db.prepare("SELECT id FROM folders WHERE name = ?").get(trimmed);
      if (existing) return { success: false, error: "A folder with that name already exists" };
      const maxOrder = this.db.prepare("SELECT MAX(sort_order) as max_order FROM folders").get();
      const sortOrder = (maxOrder?.max_order ?? 0) + 1;
      const result = this.db
        .prepare("INSERT INTO folders (name, sort_order) VALUES (?, ?)")
        .run(trimmed, sortOrder);
      const folder = this.db
        .prepare("SELECT * FROM folders WHERE id = ?")
        .get(result.lastInsertRowid);
      return { success: true, folder };
    } catch (error) {
      debugLogger.error("Error creating folder", { error: error.message }, "notes");
      throw error;
    }
  }

  deleteFolder(id) {
    try {
      if (!this.db) throw new Error("Database not initialized");
      const folder = this.db.prepare("SELECT * FROM folders WHERE id = ?").get(id);
      if (!folder) return { success: false, error: "Folder not found" };
      if (folder.is_default) return { success: false, error: "Cannot delete default folders" };
      const noteIds = this.db
        .prepare("SELECT id FROM notes WHERE folder_id = ?")
        .all(id)
        .map((row) => row.id);
      const hardDeleteNotes = this.db.prepare("DELETE FROM notes WHERE folder_id = ?");
      const hardDeleteFolder = this.db.prepare("DELETE FROM folders WHERE id = ?");
      this.db.transaction(() => {
        hardDeleteNotes.run(id);
        hardDeleteFolder.run(id);
      })();
      return { success: true, id, noteIds };
    } catch (error) {
      debugLogger.error("Error deleting folder", { error: error.message }, "notes");
      throw error;
    }
  }

  renameFolder(id, name) {
    try {
      if (!this.db) throw new Error("Database not initialized");
      const folder = this.db.prepare("SELECT * FROM folders WHERE id = ?").get(id);
      if (!folder) return { success: false, error: "Folder not found" };
      if (folder.is_default) return { success: false, error: "Cannot rename default folders" };
      const trimmed = (name || "").trim();
      if (!trimmed) return { success: false, error: "Folder name is required" };
      const existing = this.db
        .prepare("SELECT id FROM folders WHERE name = ? AND id != ?")
        .get(trimmed, id);
      if (existing) return { success: false, error: "A folder with that name already exists" };
      this.db
        .prepare(
          "UPDATE folders SET name = ?, updated_at = datetime('now') WHERE id = ?"
        )
        .run(trimmed, id);
      const updated = this.db.prepare("SELECT * FROM folders WHERE id = ?").get(id);
      return { success: true, folder: updated };
    } catch (error) {
      debugLogger.error("Error renaming folder", { error: error.message }, "notes");
      throw error;
    }
  }

  getFolderNoteCounts() {
    try {
      if (!this.db) throw new Error("Database not initialized");
      return this.db
        .prepare("SELECT folder_id, COUNT(*) as count FROM notes GROUP BY folder_id")
        .all();
    } catch (error) {
      debugLogger.error("Error getting folder note counts", { error: error.message }, "notes");
      throw error;
    }
  }

  setLocalSetting(key, value) {
    const normalizedKey = String(key || "").trim();
    if (!normalizedKey || value === undefined) throw new Error("Setting key and value are required");
    this.db
      .prepare(
        `INSERT INTO local_settings (key, value, updated_at)
         VALUES (?, ?, CURRENT_TIMESTAMP)
         ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP`
      )
      .run(normalizedKey, JSON.stringify(value));
    return { success: true, key: normalizedKey, value };
  }

  getLocalSetting(key, fallback = null) {
    const row = this.db.prepare("SELECT value FROM local_settings WHERE key = ?").get(key);
    if (!row) return fallback;
    try {
      return JSON.parse(row.value);
    } catch {
      return row.value;
    }
  }

  getLocalSettings() {
    return Object.fromEntries(
      this.db.prepare("SELECT key, value FROM local_settings ORDER BY key").all().map((row) => {
        try {
          return [row.key, JSON.parse(row.value)];
        } catch {
          return [row.key, row.value];
        }
      })
    );
  }

  deleteLocalSetting(key) {
    return { success: this.db.prepare("DELETE FROM local_settings WHERE key = ?").run(key).changes > 0 };
  }

  getTags() {
    return this.db
      .prepare(
        `SELECT t.*, COUNT(DISTINCT nt.note_id) AS note_count,
                COUNT(DISTINCT mt.meeting_id) AS meeting_count
         FROM tags t
         LEFT JOIN note_tags nt ON nt.tag_id = t.id
         LEFT JOIN meeting_tags mt ON mt.tag_id = t.id
         GROUP BY t.id
         ORDER BY t.name COLLATE NOCASE`
      )
      .all();
  }

  createTag(name, color = null) {
    const normalized = String(name || "").trim();
    if (!normalized) return { success: false, error: "Tag name is required" };
    const folded = normalized.normalize("NFKC").toLocaleLowerCase();
    const duplicate = this.db
      .prepare("SELECT * FROM tags")
      .all()
      .find((tag) => tag.name.normalize("NFKC").toLocaleLowerCase() === folded);
    if (duplicate) return { success: false, error: "A tag with that name already exists", tag: duplicate };
    const result = this.db
      .prepare("INSERT INTO tags (name, color) VALUES (?, ?)")
      .run(normalized, color);
    return {
      success: true,
      tag: this.db.prepare("SELECT * FROM tags WHERE id = ?").get(result.lastInsertRowid),
    };
  }

  updateTag(id, updates = {}) {
    const tag = this.db.prepare("SELECT * FROM tags WHERE id = ?").get(id);
    if (!tag) return { success: false, error: "Tag not found" };
    const name = updates.name === undefined ? tag.name : String(updates.name).trim();
    if (!name) return { success: false, error: "Tag name is required" };
    const folded = name.normalize("NFKC").toLocaleLowerCase();
    const duplicate = this.db
      .prepare("SELECT id, name FROM tags WHERE id != ?")
      .all(id)
      .some((row) => row.name.normalize("NFKC").toLocaleLowerCase() === folded);
    if (duplicate) return { success: false, error: "A tag with that name already exists" };
    this.db
      .prepare("UPDATE tags SET name = ?, color = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?")
      .run(name, updates.color === undefined ? tag.color : updates.color, id);
    return { success: true, tag: this.db.prepare("SELECT * FROM tags WHERE id = ?").get(id) };
  }

  deleteTag(id) {
    return { success: this.db.prepare("DELETE FROM tags WHERE id = ?").run(id).changes > 0, id };
  }

  setNoteTags(noteId, tagIds = []) {
    const ids = [
      ...new Set((Array.isArray(tagIds) ? tagIds : []).map(Number).filter(Number.isInteger)),
    ];
    this.db.transaction(() => {
      this.db.prepare("DELETE FROM note_tags WHERE note_id = ?").run(noteId);
      const insert = this.db.prepare("INSERT INTO note_tags (note_id, tag_id) VALUES (?, ?)");
      ids.forEach((tagId) => insert.run(noteId, tagId));
    })();
    return { success: true, tags: this.getTagsForNote(noteId) };
  }

  getTagsForNote(noteId) {
    return this.db
      .prepare(
        `SELECT t.* FROM tags t
         JOIN note_tags nt ON nt.tag_id = t.id
         WHERE nt.note_id = ? ORDER BY t.name COLLATE NOCASE`
      )
      .all(noteId);
  }

  setMeetingTags(meetingId, tagIds = []) {
    const ids = [
      ...new Set((Array.isArray(tagIds) ? tagIds : []).map(Number).filter(Number.isInteger)),
    ];
    this.db.transaction(() => {
      this.db.prepare("DELETE FROM meeting_tags WHERE meeting_id = ?").run(meetingId);
      const insert = this.db.prepare("INSERT INTO meeting_tags (meeting_id, tag_id) VALUES (?, ?)");
      ids.forEach((tagId) => insert.run(meetingId, tagId));
    })();
    return { success: true, tags: this.getTagsForMeeting(meetingId) };
  }

  getTagsForMeeting(meetingId) {
    return this.db
      .prepare(
        `SELECT t.* FROM tags t
         JOIN meeting_tags mt ON mt.tag_id = t.id
         WHERE mt.meeting_id = ? ORDER BY t.name COLLATE NOCASE`
      )
      .all(meetingId);
  }

  createMeeting({
    noteId = null,
    title = "Untitled Meeting",
    startedAt = null,
    endedAt = null,
    status = "completed",
  } = {}) {
    const result = this.db
      .prepare(
        `INSERT INTO meetings (note_id, title, started_at, ended_at, status)
         VALUES (?, ?, ?, ?, ?)`
      )
      .run(noteId, String(title || "Untitled Meeting"), startedAt, endedAt, status);
    return { success: true, meeting: this.getMeeting(result.lastInsertRowid) };
  }

  getMeeting(id) {
    return this.db.prepare("SELECT * FROM meetings WHERE id = ?").get(id) || null;
  }

  getMeetingByNoteId(noteId) {
    return this.db.prepare("SELECT * FROM meetings WHERE note_id = ?").get(noteId) || null;
  }

  getMeetings(limit = 100) {
    return this.db
      .prepare("SELECT * FROM meetings ORDER BY COALESCE(started_at, created_at) DESC LIMIT ?")
      .all(limit);
  }

  updateMeeting(id, updates = {}) {
    const mapping = {
      noteId: "note_id",
      title: "title",
      startedAt: "started_at",
      endedAt: "ended_at",
      status: "status",
    };
    const fields = [];
    const values = [];
    for (const [key, column] of Object.entries(mapping)) {
      if (updates[key] !== undefined) {
        fields.push(`${column} = ?`);
        values.push(updates[key]);
      }
    }
    if (fields.length === 0) return { success: false, error: "No meeting updates provided" };
    values.push(id);
    const result = this.db
      .prepare(`UPDATE meetings SET ${fields.join(", ")}, updated_at = CURRENT_TIMESTAMP WHERE id = ?`)
      .run(...values);
    return { success: result.changes > 0, meeting: this.getMeeting(id) };
  }

  deleteMeeting(id) {
    return { success: this.db.prepare("DELETE FROM meetings WHERE id = ?").run(id).changes > 0, id };
  }

  createRecording({
    meetingId = null,
    noteId = null,
    kind = "meeting",
    filePath,
    sourceName = null,
    mimeType = null,
    durationMs = null,
    sampleRate = null,
    channels = null,
    sizeBytes = null,
    sha256 = null,
  } = {}) {
    if (!filePath) throw new Error("Recording filePath is required");
    const result = this.db
      .prepare(
        `INSERT INTO recordings (
           meeting_id, note_id, kind, file_path, source_name, mime_type, duration_ms,
           sample_rate, channels, size_bytes, sha256
         ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
      )
      .run(
        meetingId,
        noteId,
        kind,
        filePath,
        sourceName,
        mimeType,
        durationMs,
        sampleRate,
        channels,
        sizeBytes,
        sha256
      );
    return { success: true, recording: this.getRecording(result.lastInsertRowid) };
  }

  getRecording(id) {
    return this.db.prepare("SELECT * FROM recordings WHERE id = ?").get(id) || null;
  }

  getRecordings({ meetingId = null, noteId = null, limit = 100 } = {}) {
    const conditions = [];
    const values = [];
    if (meetingId !== null) {
      conditions.push("meeting_id = ?");
      values.push(meetingId);
    }
    if (noteId !== null) {
      conditions.push("note_id = ?");
      values.push(noteId);
    }
    values.push(limit);
    return this.db
      .prepare(
        `SELECT * FROM recordings ${conditions.length ? `WHERE ${conditions.join(" AND ")}` : ""}
         ORDER BY created_at DESC LIMIT ?`
      )
      .all(...values);
  }

  updateRecording(id, updates = {}) {
    const mapping = {
      meetingId: "meeting_id",
      noteId: "note_id",
      kind: "kind",
      filePath: "file_path",
      sourceName: "source_name",
      mimeType: "mime_type",
      durationMs: "duration_ms",
      sampleRate: "sample_rate",
      channels: "channels",
      sizeBytes: "size_bytes",
      sha256: "sha256",
    };
    const fields = [];
    const values = [];
    for (const [key, column] of Object.entries(mapping)) {
      if (updates[key] !== undefined) {
        fields.push(`${column} = ?`);
        values.push(updates[key]);
      }
    }
    if (fields.length === 0) return { success: false, error: "No recording updates provided" };
    values.push(id);
    const result = this.db
      .prepare(`UPDATE recordings SET ${fields.join(", ")}, updated_at = CURRENT_TIMESTAMP WHERE id = ?`)
      .run(...values);
    return { success: result.changes > 0, recording: this.getRecording(id) };
  }

  deleteRecording(id) {
    return { success: this.db.prepare("DELETE FROM recordings WHERE id = ?").run(id).changes > 0, id };
  }

  createTranscript({
    meetingId = null,
    recordingId = null,
    noteId = null,
    language = null,
    source = "local",
    status = "completed",
    rawText = "",
    segments = [],
  } = {}) {
    return this.db.transaction(() => {
      const result = this.db
        .prepare(
          `INSERT INTO transcripts (
             meeting_id, recording_id, note_id, language, source, status, raw_text
           ) VALUES (?, ?, ?, ?, ?, ?, ?)`
        )
        .run(meetingId, recordingId, noteId, language, source, status, String(rawText || ""));
      this._writeTranscriptSegments(result.lastInsertRowid, segments);
      return { success: true, transcript: this.getTranscript(result.lastInsertRowid) };
    })();
  }

  getTranscript(id) {
    const transcript = this.db.prepare("SELECT * FROM transcripts WHERE id = ?").get(id);
    if (!transcript) return null;
    return {
      ...transcript,
      segments: this.db
        .prepare("SELECT * FROM transcript_segments WHERE transcript_id = ? ORDER BY segment_index")
        .all(id),
    };
  }

  getTranscripts({ meetingId = null, recordingId = null, noteId = null, limit = 100 } = {}) {
    const conditions = [];
    const values = [];
    for (const [column, value] of [
      ["meeting_id", meetingId],
      ["recording_id", recordingId],
      ["note_id", noteId],
    ]) {
      if (value !== null) {
        conditions.push(`${column} = ?`);
        values.push(value);
      }
    }
    values.push(limit);
    return this.db
      .prepare(
        `SELECT * FROM transcripts ${conditions.length ? `WHERE ${conditions.join(" AND ")}` : ""}
         ORDER BY updated_at DESC LIMIT ?`
      )
      .all(...values);
  }

  updateTranscript(id, updates = {}) {
    return this.db.transaction(() => {
      const mapping = {
        meetingId: "meeting_id",
        recordingId: "recording_id",
        noteId: "note_id",
        language: "language",
        source: "source",
        status: "status",
        rawText: "raw_text",
      };
      const fields = [];
      const values = [];
      for (const [key, column] of Object.entries(mapping)) {
        if (updates[key] !== undefined) {
          fields.push(`${column} = ?`);
          values.push(updates[key]);
        }
      }
      if (fields.length > 0) {
        values.push(id);
        this.db
          .prepare(`UPDATE transcripts SET ${fields.join(", ")}, updated_at = CURRENT_TIMESTAMP WHERE id = ?`)
          .run(...values);
      }
      if (updates.segments !== undefined) this._writeTranscriptSegments(id, updates.segments);
      const transcript = this.getTranscript(id);
      return { success: !!transcript, transcript };
    })();
  }

  replaceTranscriptSegments(transcriptId, segments) {
    return this.db.transaction(() => {
      this._writeTranscriptSegments(transcriptId, segments);
      this.db
        .prepare("UPDATE transcripts SET updated_at = CURRENT_TIMESTAMP WHERE id = ?")
        .run(transcriptId);
      const transcript = this.getTranscript(transcriptId);
      return { success: !!transcript, transcript };
    })();
  }

  deleteTranscript(id) {
    return { success: this.db.prepare("DELETE FROM transcripts WHERE id = ?").run(id).changes > 0, id };
  }

  createAttachment({
    noteId = null,
    meetingId = null,
    filePath,
    displayName = null,
    mimeType = null,
    sizeBytes = null,
    sha256 = null,
  } = {}) {
    if (!filePath) throw new Error("Attachment filePath is required");
    const result = this.db
      .prepare(
        `INSERT INTO attachments (
           note_id, meeting_id, file_path, display_name, mime_type, size_bytes, sha256
         ) VALUES (?, ?, ?, ?, ?, ?, ?)`
      )
      .run(noteId, meetingId, filePath, displayName, mimeType, sizeBytes, sha256);
    return {
      success: true,
      attachment: this.db
        .prepare("SELECT * FROM attachments WHERE id = ?")
        .get(result.lastInsertRowid),
    };
  }

  getAttachments({ noteId = null, meetingId = null } = {}) {
    if (noteId !== null) {
      return this.db.prepare("SELECT * FROM attachments WHERE note_id = ? ORDER BY id").all(noteId);
    }
    if (meetingId !== null) {
      return this.db
        .prepare("SELECT * FROM attachments WHERE meeting_id = ? ORDER BY id")
        .all(meetingId);
    }
    return this.db.prepare("SELECT * FROM attachments ORDER BY id").all();
  }

  updateAttachment(id, updates = {}) {
    const mapping = {
      noteId: "note_id",
      meetingId: "meeting_id",
      filePath: "file_path",
      displayName: "display_name",
      mimeType: "mime_type",
      sizeBytes: "size_bytes",
      sha256: "sha256",
    };
    const fields = [];
    const values = [];
    for (const [key, column] of Object.entries(mapping)) {
      if (updates[key] !== undefined) {
        fields.push(`${column} = ?`);
        values.push(updates[key]);
      }
    }
    if (fields.length === 0) return { success: false, error: "No attachment updates provided" };
    values.push(id);
    const result = this.db
      .prepare(`UPDATE attachments SET ${fields.join(", ")} WHERE id = ?`)
      .run(...values);
    return {
      success: result.changes > 0,
      attachment: this.db.prepare("SELECT * FROM attachments WHERE id = ?").get(id) || null,
    };
  }

  deleteAttachment(id) {
    return { success: this.db.prepare("DELETE FROM attachments WHERE id = ?").run(id).changes > 0, id };
  }

  recordBackup({ path: backupPath, kind = "manual", status = "completed", includesAudio = false, manifest = null }) {
    this.db
      .prepare(
        `INSERT INTO backups (path, kind, status, includes_audio, manifest_json, completed_at)
         VALUES (?, ?, ?, ?, ?, CASE WHEN ? = 'completed' THEN CURRENT_TIMESTAMP END)
         ON CONFLICT(path) DO UPDATE SET
           kind = excluded.kind,
           status = excluded.status,
           includes_audio = excluded.includes_audio,
           manifest_json = excluded.manifest_json,
           completed_at = excluded.completed_at`
      )
      .run(
        backupPath,
        kind,
        status,
        includesAudio ? 1 : 0,
        manifest ? JSON.stringify(manifest) : null,
        status
      );
    return this.db.prepare("SELECT * FROM backups WHERE path = ?").get(backupPath);
  }

  getBackups(limit = 100) {
    return this.db.prepare("SELECT * FROM backups ORDER BY created_at DESC LIMIT ?").all(limit);
  }

  getSemanticIndexState() {
    return this.db.prepare("SELECT * FROM semantic_index_state WHERE id = 1").get();
  }

  updateSemanticIndexState(updates = {}) {
    const mapping = {
      schemaVersion: "schema_version",
      modelId: "model_id",
      modelSha256: "model_sha256",
      status: "status",
      lastIndexedAt: "last_indexed_at",
      lastError: "last_error",
    };
    const fields = [];
    const values = [];
    for (const [key, column] of Object.entries(mapping)) {
      if (updates[key] !== undefined) {
        fields.push(`${column} = ?`);
        values.push(updates[key]);
      }
    }
    if (fields.length === 0) return this.getSemanticIndexState();
    this.db
      .prepare(
        `UPDATE semantic_index_state
         SET ${fields.join(", ")}, updated_at = CURRENT_TIMESTAMP WHERE id = 1`
      )
      .run(...values);
    return this.getSemanticIndexState();
  }

  async createLocalBackup(destinationPath, options = {}) {
    const includeAudio = options.includeAudio === true;
    const result = await localBackup.createBackup({
      database: this.db,
      databasePath: this.dbPath,
      destinationPath,
      audioDirectory: options.audioDirectory || path.join(app.getPath("userData"), "audio"),
      includeAudio,
      appVersion: typeof app.getVersion === "function" ? app.getVersion() : "unknown",
      schemaVersion: this.db.pragma("user_version", { simple: true }),
    });
    try {
      this.recordBackup({
        path: result.path,
        kind: options.kind || "manual",
        includesAudio: result.manifest.includes.audio,
        manifest: result.manifest,
      });
    } catch (error) {
      debugLogger.warn("Backup created but history was not updated", { error: error.message }, "database");
    }
    return { success: true, ...result };
  }

  previewLocalBackup(sourcePath) {
    const preview = localBackup.previewBackup(sourcePath);
    return { ...preview, compatible: preview.schemaVersion <= SCHEMA_VERSION };
  }

  async restoreLocalBackup(sourcePath, options = {}) {
    const preview = this.previewLocalBackup(sourcePath);
    if (!preview.compatible) {
      throw new Error(`Backup schema ${preview.schemaVersion} is newer than this app supports`);
    }
    this.db.pragma("wal_checkpoint(TRUNCATE)");
    this.db.close();
    this.db = null;
    let restoreResult = null;
    try {
      restoreResult = await localBackup.restoreBackup({
        sourcePath,
        databasePath: this.dbPath,
        audioDirectory: options.audioDirectory || path.join(app.getPath("userData"), "audio"),
        restoreAudio: options.restoreAudio === true,
        preRestoreDirectory: options.preRestoreDirectory || null,
        appVersion: typeof app.getVersion === "function" ? app.getVersion() : "unknown",
      });
      this.initDatabase();
      try {
        this.recordBackup({
          path: sourcePath,
          kind: "restore",
          includesAudio: preview.includesAudio && options.restoreAudio === true,
          manifest: restoreResult.preview,
        });
      } catch (error) {
        debugLogger.warn(
          "Backup restored but history was not updated",
          { error: error.message },
          "database"
        );
      }
      return restoreResult;
    } catch (error) {
      if (restoreResult?.preRestorePath) error.preRestorePath = restoreResult.preRestorePath;
      if (!this.db) {
        try {
          this.initDatabase();
        } catch (reopenError) {
          error.reopenError = reopenError.message;
        }
      }
      throw error;
    }
  }

  deleteNote(id) {
    try {
      if (!this.db) {
        throw new Error("Database not initialized");
      }
      const result = this.db.prepare("DELETE FROM notes WHERE id = ?").run(id);
      return { success: result.changes > 0, id };
    } catch (error) {
      debugLogger.error("Error deleting note", { error: error.message }, "notes");
      throw error;
    }
  }

  searchNotes(query, limit = 50, options = {}) {
    try {
      if (!this.db) throw new Error("Database not initialized");
      const foldedQuery = String(query || "").trim().normalize("NFKC").toLocaleLowerCase();
      if (!foldedQuery) return [];
      const match = this._ftsQuery(query);
      const noteIds = match
        ? this.db
            .prepare(
              `SELECT rowid AS note_id
               FROM notes_fts
               WHERE notes_fts MATCH ?
               ORDER BY rank
               LIMIT ?`
            )
            .all(match, limit * 2)
            .map((row) => row.note_id)
        : [];
      // ponytail: linear fallback gives correct CJK/Unicode substring matching; add a
      // language-specific tokenizer only if local histories become large enough to need it.
      const substringNoteIds = this.db
        .prepare("SELECT id, title, content FROM notes")
        .all()
        .filter((note) =>
          [note.title, note.content].some((value) =>
            String(value || "").normalize("NFKC").toLocaleLowerCase().includes(foldedQuery)
          )
        )
        .map((note) => note.id);
      const transcriptNoteIds = this.searchTranscripts(query, limit * 2)
        .map((row) => row.resolved_note_id)
        .filter((id) => id !== null && id !== undefined);
      const matchingTagIds = this.db
        .prepare("SELECT id, name FROM tags")
        .all()
        .filter((tag) => tag.name.normalize("NFKC").toLocaleLowerCase().includes(foldedQuery))
        .map((tag) => tag.id);
      const tagNoteIds = matchingTagIds.length
        ? [
            ...this.db
              .prepare(
                `SELECT DISTINCT note_id FROM note_tags
                 WHERE tag_id IN (${matchingTagIds.map(() => "?").join(",")})`
              )
              .all(...matchingTagIds),
            ...this.db
              .prepare(
                `SELECT DISTINCT m.note_id
                 FROM meeting_tags mt JOIN meetings m ON m.id = mt.meeting_id
                 WHERE m.note_id IS NOT NULL
                   AND mt.tag_id IN (${matchingTagIds.map(() => "?").join(",")})`
              )
              .all(...matchingTagIds),
          ].map((row) => row.note_id)
        : [];

      let orderedIds = [
        ...new Set([...noteIds, ...substringNoteIds, ...transcriptNoteIds, ...tagNoteIds]),
      ];
      const requiredTagIds = Array.isArray(options)
        ? options
        : Array.isArray(options.tagIds)
          ? options.tagIds
          : [];
      if (requiredTagIds.length > 0 && orderedIds.length > 0) {
        const ids = [...new Set(requiredTagIds.map(Number).filter(Number.isInteger))];
        if (ids.length === 0) return [];
        const allowed = new Set(
          this.db
            .prepare(
              `SELECT note_id FROM note_tags
               WHERE tag_id IN (${ids.map(() => "?").join(",")})
               GROUP BY note_id HAVING COUNT(DISTINCT tag_id) = ?`
            )
            .all(...ids, ids.length)
            .map((row) => row.note_id)
        );
        orderedIds = orderedIds.filter((id) => allowed.has(id));
      }
      if (orderedIds.length === 0) return [];
      const rows = this.db
        .prepare(`SELECT * FROM notes WHERE id IN (${orderedIds.map(() => "?").join(",")})`)
        .all(...orderedIds);
      const byId = new Map(rows.map((row) => [row.id, row]));
      return orderedIds.map((id) => byId.get(id)).filter(Boolean).slice(0, limit);
    } catch (error) {
      debugLogger.error("Error searching notes", { error: error.message }, "database");
      throw error;
    }
  }

  searchTranscripts(query, limit = 50, options = {}) {
    const match = this._ftsQuery(query);
    const foldedQuery = String(query || "").trim().normalize("NFKC").toLocaleLowerCase();
    if (!foldedQuery) return [];
    const filters = [];
    const filterValues = [];
    if (options.meetingId !== undefined) {
      filters.push("t.meeting_id = ?");
      filterValues.push(options.meetingId);
    }
    if (options.noteId !== undefined) {
      filters.push("COALESCE(t.note_id, m.note_id) = ?");
      filterValues.push(options.noteId);
    }
    const select = `SELECT t.*, COALESCE(t.note_id, m.note_id) AS resolved_note_id,
                           s.id AS matched_segment_id,
                           COALESCE(s.edited_text, s.original_text) AS matched_text
                    FROM transcript_segments s
                    JOIN transcripts t ON t.id = s.transcript_id
                    LEFT JOIN meetings m ON m.id = t.meeting_id`;
    const results = [];
    const seen = new Set();
    if (match) {
      const ftsRows = this.db
        .prepare(
          `${select}
           JOIN transcript_segments_fts ON transcript_segments_fts.rowid = s.id
           WHERE transcript_segments_fts MATCH ?
             ${filters.length ? `AND ${filters.join(" AND ")}` : ""}
           ORDER BY t.updated_at DESC LIMIT ?`
        )
        .all(match, ...filterValues, limit);
      for (const row of ftsRows) {
        if (!seen.has(row.id)) {
          seen.add(row.id);
          results.push(row);
        }
      }
    }
    if (results.length < limit) {
      const scanRows = this.db
        .prepare(
          `${select} ${filters.length ? `WHERE ${filters.join(" AND ")}` : ""}
           ORDER BY t.updated_at DESC, s.segment_index`
        )
        .all(...filterValues);
      for (const row of scanRows) {
        if (
          results.length >= limit ||
          seen.has(row.id) ||
          !String(row.matched_text || "")
            .normalize("NFKC")
            .toLocaleLowerCase()
            .includes(foldedQuery)
        ) {
          continue;
        }
        seen.add(row.id);
        results.push(row);
      }
    }
    const requiredTagIds = Array.isArray(options.tagIds)
      ? [...new Set(options.tagIds.map(Number).filter(Number.isInteger))]
      : [];
    if (requiredTagIds.length === 0) return results;
    return results.filter((row) => {
      if (row.resolved_note_id === null || row.resolved_note_id === undefined) return false;
      const assigned = new Set([
        ...this.getTagsForNote(row.resolved_note_id).map((tag) => tag.id),
        ...(row.meeting_id ? this.getTagsForMeeting(row.meeting_id).map((tag) => tag.id) : []),
      ]);
      return requiredTagIds.every((tagId) => assigned.has(tagId));
    });
  }

  searchLocal(query, limit = 50, options = {}) {
    const folded = String(query || "").normalize("NFKC").toLocaleLowerCase();
    return {
      notes: this.searchNotes(query, limit, options),
      transcripts: this.searchTranscripts(query, limit, options),
      tags: this.getTags()
        .filter((tag) => tag.name.normalize("NFKC").toLocaleLowerCase().includes(folded))
        .slice(0, limit),
    };
  }

  upsertContacts(contacts) {
    try {
      if (!this.db) throw new Error("Database not initialized");
      const transaction = this.db.transaction((list) => {
        const stmt = this.db.prepare(
          "INSERT INTO contacts (email, display_name, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP) ON CONFLICT(email) DO UPDATE SET display_name = COALESCE(excluded.display_name, contacts.display_name), updated_at = CURRENT_TIMESTAMP"
        );
        for (const c of list) {
          if (c.email) stmt.run(c.email.toLowerCase().trim(), c.displayName || null);
        }
      });
      transaction(contacts);
      return { success: true };
    } catch (error) {
      debugLogger.error("Error upserting contacts", { error: error.message }, "database");
      throw error;
    }
  }

  searchContacts(query) {
    try {
      if (!this.db) throw new Error("Database not initialized");
      const pattern = `%${query || ""}%`;
      return this.db
        .prepare(
          "SELECT * FROM contacts WHERE email LIKE ? OR display_name LIKE ? ORDER BY display_name ASC, email ASC LIMIT 20"
        )
        .all(pattern, pattern);
    } catch (error) {
      debugLogger.error("Error searching contacts", { error: error.message }, "database");
      throw error;
    }
  }

  getMeetingsFolder() {
    try {
      if (!this.db) throw new Error("Database not initialized");
      return (
        this.db
          .prepare("SELECT id FROM folders WHERE name = 'Meetings' AND is_default = 1")
          .get() || null
      );
    } catch (error) {
      debugLogger.error("Error getting meetings folder", { error: error.message }, "gcal");
      throw error;
    }
  }

  cleanup() {
    try {
      if (this.db) {
        try {
          this.db.close();
        } catch (closeError) {
          debugLogger.error("Error closing database", { error: closeError.message }, "database");
        }
        this.db = null;
      }
      const dbPath = path.join(
        app.getPath("userData"),
        process.env.NODE_ENV === "development" ? "mnemora-dev.sqlite" : "mnemora.sqlite"
      );
      if (fs.existsSync(dbPath)) {
        fs.unlinkSync(dbPath);
      }
    } catch (error) {
      debugLogger.error("Error deleting database file", { error: error.message }, "database");
    }
  }
  _normalizeEmail(email) {
    const trimmed = (email || "").trim().toLowerCase();
    return trimmed || null;
  }

  _findProfileByEmail(email) {
    const normalized = this._normalizeEmail(email);
    if (!normalized) return null;
    return this.db.prepare("SELECT * FROM speaker_profiles WHERE lower(email) = ?").get(normalized);
  }

  upsertSpeakerProfile(name, email, embeddingBuffer, profileId = null) {
    try {
      if (!this.db) throw new Error("Database not initialized");
      const normalizedEmail = this._normalizeEmail(email);
      let existing = profileId
        ? this.db.prepare("SELECT * FROM speaker_profiles WHERE id = ?").get(profileId)
        : null;
      if (!existing && normalizedEmail) {
        existing = this._findProfileByEmail(normalizedEmail);
      }
      if (!existing) {
        existing = this.db
          .prepare("SELECT * FROM speaker_profiles WHERE display_name = ?")
          .get(name);
      }
      if (existing) {
        const stored = new Float32Array(
          existing.embedding.buffer,
          existing.embedding.byteOffset,
          existing.embedding.byteLength / 4
        );
        const incoming = new Float32Array(
          embeddingBuffer.buffer,
          embeddingBuffer.byteOffset,
          embeddingBuffer.byteLength / 4
        );
        const updated = new Float32Array(stored.length);
        for (let i = 0; i < stored.length; i++) {
          updated[i] = 0.3 * incoming[i] + 0.7 * stored[i];
        }
        const updatedBuf = Buffer.from(updated.buffer);
        const finalEmail = normalizedEmail || existing.email || null;
        this.db
          .prepare(
            "UPDATE speaker_profiles SET display_name = ?, email = ?, embedding = ?, sample_count = sample_count + 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
          )
          .run(name, finalEmail, updatedBuf, existing.id);
        const resolved = this.db
          .prepare("SELECT * FROM speaker_profiles WHERE id = ?")
          .get(existing.id);
        if (normalizedEmail) {
          const collision = this.db
            .prepare("SELECT * FROM speaker_profiles WHERE lower(email) = ? AND id != ?")
            .get(normalizedEmail, existing.id);
          if (collision) {
            return this.mergeSpeakerProfiles(resolved, collision);
          }
        }
        return resolved;
      }
      const result = this.db
        .prepare("INSERT INTO speaker_profiles (display_name, email, embedding) VALUES (?, ?, ?)")
        .run(name, normalizedEmail, embeddingBuffer);
      return this.db
        .prepare("SELECT * FROM speaker_profiles WHERE id = ?")
        .get(result.lastInsertRowid);
    } catch (error) {
      debugLogger.error("Error upserting speaker profile", { error: error.message }, "database");
      throw error;
    }
  }

  attachEmailToProfile(profileId, email) {
    try {
      if (!this.db) throw new Error("Database not initialized");
      const normalizedEmail = this._normalizeEmail(email);
      const profile = this.db.prepare("SELECT * FROM speaker_profiles WHERE id = ?").get(profileId);
      if (!profile) throw new Error(`Speaker profile ${profileId} not found`);

      if (!normalizedEmail) {
        this.db
          .prepare(
            "UPDATE speaker_profiles SET email = NULL, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
          )
          .run(profileId);
        return this.db.prepare("SELECT * FROM speaker_profiles WHERE id = ?").get(profileId);
      }

      const collision = this._findProfileByEmail(normalizedEmail);
      if (collision && collision.id !== profileId) {
        return this.mergeSpeakerProfiles(collision, profile);
      }

      this.db
        .prepare(
          "UPDATE speaker_profiles SET email = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        )
        .run(normalizedEmail, profileId);
      return this.db.prepare("SELECT * FROM speaker_profiles WHERE id = ?").get(profileId);
    } catch (error) {
      debugLogger.error(
        "Error attaching email to speaker profile",
        { error: error.message },
        "database"
      );
      throw error;
    }
  }

  mergeSpeakerProfiles(a, b) {
    const winner = (a.sample_count || 0) >= (b.sample_count || 0) ? a : b;
    const loser = winner === a ? b : a;

    const winnerEmb = new Float32Array(
      winner.embedding.buffer,
      winner.embedding.byteOffset,
      winner.embedding.byteLength / 4
    );
    const loserEmb = new Float32Array(
      loser.embedding.buffer,
      loser.embedding.byteOffset,
      loser.embedding.byteLength / 4
    );
    const wSamples = winner.sample_count || 1;
    const lSamples = loser.sample_count || 1;
    const total = wSamples + lSamples;
    const blended = new Float32Array(winnerEmb.length);
    for (let i = 0; i < winnerEmb.length; i++) {
      blended[i] = (winnerEmb[i] * wSamples + loserEmb[i] * lSamples) / total;
    }

    const finalEmail = winner.email || loser.email || null;
    const finalName = winner.display_name || loser.display_name;

    const tx = this.db.transaction(() => {
      this.db
        .prepare(
          "UPDATE speaker_profiles SET display_name = ?, email = ?, embedding = ?, sample_count = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        )
        .run(finalName, finalEmail, Buffer.from(blended.buffer), total, winner.id);
      this.db
        .prepare(
          "UPDATE speaker_mappings SET profile_id = ?, display_name = ? WHERE profile_id = ?"
        )
        .run(winner.id, finalName, loser.id);
      this.db.prepare("DELETE FROM speaker_profiles WHERE id = ?").run(loser.id);
    });
    tx();

    return this.db.prepare("SELECT * FROM speaker_profiles WHERE id = ?").get(winner.id);
  }

  getSpeakerProfiles(includeEmbedding = false) {
    try {
      if (!this.db) throw new Error("Database not initialized");
      const query = includeEmbedding
        ? "SELECT * FROM speaker_profiles"
        : `SELECT id, display_name, email, sample_count, created_at, updated_at
           FROM speaker_profiles`;
      return this.db.prepare(query).all();
    } catch (error) {
      debugLogger.error("Error getting speaker profiles", { error: error.message }, "database");
      throw error;
    }
  }

  setSpeakerMapping(noteId, speakerId, profileId, displayName) {
    try {
      if (!this.db) throw new Error("Database not initialized");
      this.db
        .prepare(
          "INSERT OR REPLACE INTO speaker_mappings (note_id, speaker_id, profile_id, display_name) VALUES (?, ?, ?, ?)"
        )
        .run(noteId, speakerId, profileId, displayName);
      return { success: true };
    } catch (error) {
      debugLogger.error("Error setting speaker mapping", { error: error.message }, "database");
      throw error;
    }
  }

  getSpeakerMappings(noteId) {
    try {
      if (!this.db) throw new Error("Database not initialized");
      return this.db.prepare("SELECT * FROM speaker_mappings WHERE note_id = ?").all(noteId);
    } catch (error) {
      debugLogger.error("Error getting speaker mappings", { error: error.message }, "database");
      throw error;
    }
  }

  saveNoteSpeakerEmbeddings(noteId, embeddings) {
    try {
      if (!this.db) throw new Error("Database not initialized");
      const transaction = this.db.transaction((entries) => {
        const stmt = this.db.prepare(
          "INSERT OR REPLACE INTO note_speaker_embeddings (note_id, speaker_id, embedding) VALUES (?, ?, ?)"
        );
        for (const [speakerId, buffer] of entries) {
          stmt.run(noteId, speakerId, buffer);
        }
      });
      transaction(Object.entries(embeddings));
      return { success: true };
    } catch (error) {
      debugLogger.error(
        "Error saving note speaker embeddings",
        { error: error.message },
        "database"
      );
      throw error;
    }
  }

  getNoteSpeakerEmbeddings(noteId) {
    try {
      if (!this.db) throw new Error("Database not initialized");
      return this.db.prepare("SELECT * FROM note_speaker_embeddings WHERE note_id = ?").all(noteId);
    } catch (error) {
      debugLogger.error(
        "Error getting note speaker embeddings",
        { error: error.message },
        "database"
      );
      throw error;
    }
  }

  getNotesWithUnmappedSpeakers() {
    try {
      if (!this.db) throw new Error("Database not initialized");
      return this.db
        .prepare(
          `SELECT DISTINCT nse.note_id
          FROM note_speaker_embeddings nse
          LEFT JOIN speaker_mappings sm ON nse.note_id = sm.note_id AND nse.speaker_id = sm.speaker_id
          WHERE sm.note_id IS NULL`
        )
        .all()
        .map((row) => row.note_id);
    } catch (error) {
      debugLogger.error(
        "Error getting notes with unmapped speakers",
        { error: error.message },
        "database"
      );
      throw error;
    }
  }

  removeSpeakerMapping(noteId, speakerId) {
    try {
      if (!this.db) throw new Error("Database not initialized");
      this.db
        .prepare("DELETE FROM speaker_mappings WHERE note_id = ? AND speaker_id = ?")
        .run(noteId, speakerId);
      return { success: true };
    } catch (error) {
      debugLogger.error("Error removing speaker mapping", { error: error.message }, "database");
      throw error;
    }
  }
}

DatabaseManager.SCHEMA_VERSION = SCHEMA_VERSION;
module.exports = DatabaseManager;
