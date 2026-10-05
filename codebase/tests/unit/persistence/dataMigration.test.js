const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const Database = require("better-sqlite3");
const { migrateUserData } = require("../../../main/infrastructure/persistence/dataMigration");

function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "mnemora-user-data-migration-"));
  const appDataPath = path.join(root, "app-data");
  const legacyPath = path.join(appDataPath, "OpenWhispr");
  const destination = path.join(appDataPath, "Mnemora");
  fs.mkdirSync(legacyPath, { recursive: true });
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  return { root, appDataPath, legacyPath, destination };
}

function createLegacyDatabase(filePath) {
  const database = new Database(filePath);
  database.exec("CREATE TABLE retained (id INTEGER PRIMARY KEY, value TEXT); INSERT INTO retained VALUES (1, 'keep')");
  database.pragma("user_version = 3");
  database.close();
}

test("skips migration if new location is not empty", (t) => {
  const paths = fixture(t);
  fs.mkdirSync(paths.destination, { recursive: true });
  fs.writeFileSync(path.join(paths.destination, "existing.txt"), "keep");

  const result = migrateUserData({
    appDataPath: paths.appDataPath,
    newUserDataPath: paths.destination,
    channel: "production",
  });

  assert.deepEqual(result, { status: "skipped", reason: "new_location_not_empty" });
  assert.equal(fs.readFileSync(path.join(paths.destination, "existing.txt"), "utf8"), "keep");
});

test("skips migration if legacy data doesn't exist", (t) => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "mnemora-user-data-no-legacy-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const result = migrateUserData({
    appDataPath: root,
    newUserDataPath: path.join(root, "Mnemora"),
    channel: "production",
  });

  assert.deepEqual(result, { status: "skipped", reason: "no_legacy_data" });
});

test("copies verified legacy files atomically and records an idempotent journal", (t) => {
  const paths = fixture(t);
  createLegacyDatabase(path.join(paths.legacyPath, "transcriptions.db"));
  fs.writeFileSync(path.join(paths.legacyPath, ".env"), "LOCAL_ONLY=1");
  fs.mkdirSync(path.join(paths.legacyPath, "secure-keys"));
  fs.writeFileSync(path.join(paths.legacyPath, "secure-keys", "key1.enc"), "protected");

  const result = migrateUserData({
    appDataPath: paths.appDataPath,
    newUserDataPath: paths.destination,
    channel: "production",
  });

  assert.equal(result.status, "completed");
  assert.equal(result.journal.files.length, 3);
  assert.ok(result.journal.files.every((entry) => /^[0-9a-f]{64}$/.test(entry.sha256)));
  const databaseEntry = result.journal.files.find((entry) => entry.destination === "mnemora.sqlite");
  assert.equal(databaseEntry.sourceSchemaVersion, 3);
  assert.equal(databaseEntry.destinationSchemaVersion, 3);
  assert.equal(fs.readFileSync(path.join(paths.destination, ".env"), "utf8"), "LOCAL_ONLY=1");
  assert.equal(
    fs.readFileSync(path.join(paths.destination, "secure-keys", "key1.enc"), "utf8"),
    "protected"
  );
  assert.ok(fs.existsSync(path.join(paths.legacyPath, "transcriptions.db")));

  const journal = JSON.parse(
    fs.readFileSync(path.join(paths.destination, ".mnemora-migration-completed"), "utf8")
  );
  assert.equal(journal.status, "completed");
  assert.equal(journal.result, "verified copy committed atomically; source preserved");
  assert.deepEqual(
    migrateUserData({
      appDataPath: paths.appDataPath,
      newUserDataPath: paths.destination,
      channel: "production",
    }),
    { status: "skipped", reason: "new_location_not_empty" }
  );
});

test("an interrupted copy leaves no partial destination and retries safely", (t) => {
  const paths = fixture(t);
  createLegacyDatabase(path.join(paths.legacyPath, "transcriptions.db"));
  fs.writeFileSync(path.join(paths.legacyPath, ".env"), "PRESERVE=1");
  const sourceDatabase = fs.readFileSync(path.join(paths.legacyPath, "transcriptions.db"));
  let copies = 0;
  const failingFs = {
    ...fs,
    copyFileSync: (...args) => {
      copies += 1;
      if (copies === 2) throw new Error("injected copy interruption");
      return fs.copyFileSync(...args);
    },
  };

  const failed = migrateUserData({
    appDataPath: paths.appDataPath,
    newUserDataPath: paths.destination,
    channel: "production",
    fsMock: failingFs,
  });

  assert.deepEqual(failed, { status: "failed", error: "injected copy interruption" });
  assert.equal(fs.existsSync(paths.destination), false);
  assert.deepEqual(fs.readFileSync(path.join(paths.legacyPath, "transcriptions.db")), sourceDatabase);
  assert.equal(
    fs.readdirSync(paths.appDataPath).some((name) => name.startsWith("Mnemora.migration-")),
    false
  );

  const retried = migrateUserData({
    appDataPath: paths.appDataPath,
    newUserDataPath: paths.destination,
    channel: "production",
  });
  assert.equal(retried.status, "completed");
});
