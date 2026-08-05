const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const Module = require("node:module");

let userDataDir = fs.mkdtempSync(path.join(os.tmpdir(), "mnemora-snippets-db-"));
const originalLoad = Module._load;

Module._load = function patchedLoad(request, parent, isMain) {
  if (request === "electron") {
    return {
      app: {
        getPath: () => userDataDir,
        getAppPath: () => process.cwd(),
        isReady: () => false,
      },
    };
  }
  return originalLoad.call(this, request, parent, isMain);
};

process.env.NODE_ENV = "test";

const DatabaseManager = require("../../../main/infrastructure/persistence/database.js");

function createDb(t) {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "mnemora-snippets-db-"));
  userDataDir = directory;
  const manager = new DatabaseManager();
  t.after(() => {
    if (manager.db?.open) manager.db.close();
    fs.rmSync(directory, { recursive: true, force: true });
  });
  return manager;
}

test("snippets trim, dedupe, update, and retain their local identity", (t) => {
  const db = createDb(t);

  db.setSnippets([
    { trigger: "  signoff  ", replacement: "  Regards  " },
    { trigger: "SIGNOFF", replacement: "Ignored duplicate" },
  ]);
  assert.deepEqual(db.getSnippets(), [{ trigger: "signoff", replacement: "Regards" }]);

  const created = db.db.prepare("SELECT id FROM snippets WHERE trigger = ?").get("signoff");
  db.setSnippets([{ trigger: "signoff", replacement: "Best regards" }]);
  const updated = db.db
    .prepare("SELECT id, replacement FROM snippets WHERE trigger = ?")
    .get("signoff");

  assert.equal(updated.id, created.id);
  assert.equal(updated.replacement, "Best regards");
});

test("snippet removals delete local records without cloud tombstones", (t) => {
  const db = createDb(t);

  db.setSnippets([{ trigger: "temp", replacement: "Temporary" }]);
  db.setSnippets([]);

  assert.deepEqual(db.getSnippets(), []);
  assert.equal(db.db.prepare("SELECT COUNT(*) AS count FROM snippets").get().count, 0);
  const columns = db.db.pragma("table_info(snippets)").map((column) => column.name);
  assert.ok(!columns.includes("cloud_id"));
  assert.ok(!columns.includes("sync_status"));
  assert.ok(!columns.includes("deleted_at"));
});

test("local snippets persist after reopening and do not inherit the remote trigger cap", (t) => {
  const db = createDb(t);

  const longTrigger = "x".repeat(101);
  db.setSnippets([{ trigger: longTrigger, replacement: "Stored locally" }]);
  db.db.close();

  const reopened = new DatabaseManager();
  assert.deepEqual(reopened.getSnippets(), [{ trigger: longTrigger, replacement: "Stored locally" }]);
  reopened.db.close();
});

test("notes, folders, and transcription history use direct local persistence", (t) => {
  const db = createDb(t);

  const folder = db.createFolder("Project notes").folder;
  const note = db.saveNote("Offline note", "Stored only on this device", "personal", null, null, folder.id)
    .note;
  db.updateNote(note.id, { content: "Updated locally" });
  const transcription = db.saveTranscription("Local transcript").transcription;

  assert.equal(db.getNotes(null, 10, folder.id)[0].content, "Updated locally");
  assert.equal(db.getTranscriptionById(transcription.id).text, "Local transcript");
  assert.equal(db.deleteTranscription(transcription.id).success, true);
  assert.equal(db.getTranscriptionById(transcription.id), null);

  for (const table of ["notes", "folders", "transcriptions"]) {
    const columns = db.db.pragma(`table_info(${table})`).map((column) => column.name);
    assert.ok(!columns.includes("sync_status"));
    assert.ok(!columns.includes("deleted_at"));
  }
  assert.ok(!db.db.pragma("table_info(folders)").some((column) => column.name === "cloud_id"));
  assert.ok(
    !db.db.pragma("table_info(transcriptions)").some((column) => column.name === "cloud_id")
  );
});
