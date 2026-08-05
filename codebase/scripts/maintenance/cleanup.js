const fs = require("fs");
const os = require("os");
const path = require("path");

for (const directory of ["build-output", path.join("node_modules", ".cache")]) {
  if (fs.existsSync(directory)) {
    fs.rmSync(directory, { recursive: true, force: true });
    console.log(`Cleaned ${directory}`);
  }
}

const userDataPath =
  process.platform === "darwin"
    ? path.join(os.homedir(), "Library", "Application Support", "Mnemora-dev")
    : process.platform === "win32"
      ? path.join(process.env.APPDATA || os.homedir(), "Mnemora-dev")
      : path.join(os.homedir(), ".config", "Mnemora-dev");
const devDatabase = path.join(userDataPath, "transcriptions-dev.db");

if (fs.existsSync(devDatabase)) {
  fs.unlinkSync(devDatabase);
  console.log(`Cleaned development database ${devDatabase}`);
}
