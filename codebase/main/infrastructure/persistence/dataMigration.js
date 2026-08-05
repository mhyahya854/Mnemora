const fs = require("fs");
const path = require("path");

function migrateUserData({
  appDataPath,
  newUserDataPath,
  channel,
  fsMock = fs,
  pathMock = path
}) {
  // 1. Check whether the new Mnemora location already contains data (e.g. mnemora.sqlite or .env)
  const newDbPath = pathMock.join(newUserDataPath, "mnemora.sqlite");
  const newDbDevPath = pathMock.join(newUserDataPath, "mnemora-dev.sqlite");
  const newEnvPath = pathMock.join(newUserDataPath, ".env");

  const alreadyHasData =
    fsMock.existsSync(newDbPath) ||
    fsMock.existsSync(newDbDevPath) ||
    fsMock.existsSync(newEnvPath);

  if (alreadyHasData) {
    return { status: "skipped", reason: "new_location_not_empty" };
  }

  // 2. Identify the legacy OpenWhispr user-data path.
  let oldUserDataPath;
  if (channel === "production") {
    oldUserDataPath = pathMock.join(appDataPath, "OpenWhispr");
  } else {
    oldUserDataPath = pathMock.join(appDataPath, `OpenWhispr-${channel}`);
  }

  if (!fsMock.existsSync(oldUserDataPath)) {
    return { status: "skipped", reason: "no_legacy_data" };
  }

  // Check if legacy data exists (transcriptions.db, transcriptions-dev.db, or .env)
  const oldDbPath = pathMock.join(oldUserDataPath, "transcriptions.db");
  const oldDbDevPath = pathMock.join(oldUserDataPath, "transcriptions-dev.db");
  const oldEnvPath = pathMock.join(oldUserDataPath, ".env");

  const legacyExists =
    fsMock.existsSync(oldDbPath) ||
    fsMock.existsSync(oldDbDevPath) ||
    fsMock.existsSync(oldEnvPath);

  if (!legacyExists) {
    return { status: "skipped", reason: "legacy_dir_empty" };
  }

  try {
    // Ensure new directory exists
    fsMock.mkdirSync(newUserDataPath, { recursive: true });

    // Copy .env
    if (fsMock.existsSync(oldEnvPath)) {
      fsMock.copyFileSync(oldEnvPath, newEnvPath);
    }

    // Copy secure-keys directory
    const oldSecureKeys = pathMock.join(oldUserDataPath, "secure-keys");
    const newSecureKeys = pathMock.join(newUserDataPath, "secure-keys");
    if (fsMock.existsSync(oldSecureKeys)) {
      fsMock.mkdirSync(newSecureKeys, { recursive: true });
      const files = fsMock.readdirSync(oldSecureKeys);
      for (const file of files) {
        fsMock.copyFileSync(
          pathMock.join(oldSecureKeys, file),
          pathMock.join(newSecureKeys, file)
        );
      }
    }

    // Copy and rename database file(s)
    if (fsMock.existsSync(oldDbPath)) {
      fsMock.copyFileSync(oldDbPath, newDbPath);
    }
    if (fsMock.existsSync(oldDbDevPath)) {
      fsMock.copyFileSync(oldDbDevPath, newDbDevPath);
    }

    // Copy bundle-migrated sentinel if it exists
    const oldSentinel = pathMock.join(oldUserDataPath, ".bundle-migrated");
    const newSentinel = pathMock.join(newUserDataPath, ".bundle-migrated");
    if (fsMock.existsSync(oldSentinel)) {
      fsMock.copyFileSync(oldSentinel, newSentinel);
    }

    // Record that migration was completed
    fsMock.writeFileSync(
      pathMock.join(newUserDataPath, ".mnemora-migration-completed"),
      new Date().toISOString()
    );

    return { status: "completed" };
  } catch (err) {
    return { status: "failed", error: err.message };
  }
}

module.exports = {
  migrateUserData
};
