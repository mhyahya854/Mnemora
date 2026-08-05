const { app } = require("electron");
const os = require("os");
const path = require("path");
const fs = require("fs");

function getCacheRoot() {
  const homeDir = app?.getPath?.("home") || os.homedir();
  const current = path.join(homeDir, ".cache", "mnemora");
  const legacy = path.join(homeDir, ".cache", "openwhispr");
  if (!fs.existsSync(current) && fs.existsSync(legacy)) {
    fs.mkdirSync(path.dirname(current), { recursive: true });
    try {
      fs.renameSync(legacy, current);
    } catch {
      // Existing legacy models remain readable through their original app version.
    }
  }
  return current;
}

function getModelsDirForService(service) {
  return path.join(getCacheRoot(), `${service}-models`);
}

module.exports = { getCacheRoot, getModelsDirForService };
