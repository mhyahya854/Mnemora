#!/usr/bin/env node

const path = require("path");
const fs = require("fs");
const { spawnSync } = require("child_process");

const root = path.join(__dirname, "..", "..");
const run = (script, args = []) => {
  const result = spawnSync(process.execPath, [path.join(__dirname, script), ...args], {
    cwd: root,
    env: process.env,
    stdio: "inherit",
  });
  if (result.error) throw result.error;
  if (result.status !== 0) process.exit(result.status || 1);
};

const ffmpegBinary = path.join(
  root,
  "node_modules",
  "ffmpeg-static",
  process.platform === "win32" ? "ffmpeg.exe" : "ffmpeg"
);
if (!fs.existsSync(ffmpegBinary)) run("../../node_modules/ffmpeg-static/install.js");

run("../downloads/download-whisper-cpp.js", ["--current"]);
run("../downloads/download-whisper-model.js");
run("../downloads/download-sherpa-onnx.js", ["--current"]);
run("../downloads/download-qdrant.js", ["--current"]);
run("../downloads/download-meeting-aec-helper.js", ["--current"]);
run("../downloads/download-whisper-vad-model.js");
run("../downloads/download-minilm.js", ["--for-build"]);
run("../downloads/download-diarization-models.js", [
  "--output-dir",
  path.join(root, "resources", "bin", "diarization-models"),
]);

if (process.platform === "win32") {
  run("../downloads/download-nircmd.js");
  run("../downloads/download-windows-fast-paste.js");
  run("../downloads/download-windows-key-listener.js");
  run("../downloads/download-windows-system-audio-helper.js");
}

run("../verification/verify-offline-assets.js", ["--write-manifest"]);
