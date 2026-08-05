const test = require("node:test");
const assert = require("node:assert/strict");
const { migrateUserData } = require("../../../main/infrastructure/persistence/dataMigration");

test("skips migration if new location is not empty", () => {
  const fsMock = {
    existsSync: (p) => {
      if (p.endsWith("mnemora.sqlite")) return true;
      return false;
    }
  };
  const pathMock = {
    join: (...args) => args.join("/")
  };

  const result = migrateUserData({
    appDataPath: "/appData",
    newUserDataPath: "/newUserData",
    channel: "production",
    fsMock,
    pathMock
  });

  assert.deepEqual(result, { status: "skipped", reason: "new_location_not_empty" });
});

test("skips migration if legacy data doesn't exist", () => {
  const fsMock = {
    existsSync: (p) => {
      if (
        p.endsWith("mnemora.sqlite") ||
        p.endsWith("mnemora-dev.sqlite") ||
        p.endsWith(".env")
      ) {
        return false;
      }
      if (p === "/appData/OpenWhispr") {
        return false;
      }
      return false;
    }
  };
  const pathMock = {
    join: (...args) => args.join("/")
  };

  const result = migrateUserData({
    appDataPath: "/appData",
    newUserDataPath: "/newUserData",
    channel: "production",
    fsMock,
    pathMock
  });

  assert.deepEqual(result, { status: "skipped", reason: "no_legacy_data" });
});

test("copies legacy files to new location successfully", () => {
  const dirsCreated = [];
  const filesCopied = [];
  const filesWritten = [];

  const fsMock = {
    existsSync: (p) => {
      if (p.includes("/newUserData")) return false;
      if (p === "/appData/OpenWhispr") return true;
      if (p.endsWith("transcriptions.db")) return true;
      if (p.endsWith("secure-keys")) return true;
      if (p.endsWith("key1.enc")) return true;
      if (p.endsWith(".env")) return true;
      return false;
    },
    mkdirSync: (p, _opts) => {
      dirsCreated.push(p);
    },
    copyFileSync: (src, dest) => {
      filesCopied.push({ src, dest });
    },
    readdirSync: (p) => {
      if (p.endsWith("secure-keys")) return ["key1.enc"];
      return [];
    },
    writeFileSync: (p, content) => {
      filesWritten.push({ path: p, content });
    }
  };

  const pathMock = {
    join: (...args) => args.join("/"),
    dirname: (p) => p.split("/").slice(0, -1).join("/")
  };

  const result = migrateUserData({
    appDataPath: "/appData",
    newUserDataPath: "/newUserData",
    channel: "production",
    fsMock,
    pathMock
  });

  assert.equal(result.status, "completed");
  assert.ok(dirsCreated.includes("/newUserData"));
  assert.ok(dirsCreated.includes("/newUserData/secure-keys"));

  const envCopy = filesCopied.find((c) => c.src.endsWith(".env"));
  assert.equal(envCopy.dest, "/newUserData/.env");

  const dbCopy = filesCopied.find((c) => c.src.endsWith("transcriptions.db"));
  assert.equal(dbCopy.dest, "/newUserData/mnemora.sqlite");

  const keyCopy = filesCopied.find((c) => c.src.includes("key1.enc"));
  assert.equal(keyCopy.dest, "/newUserData/secure-keys/key1.enc");

  const sentinel = filesWritten.find((w) =>
    w.path.endsWith(".mnemora-migration-completed")
  );
  assert.ok(sentinel);
});
