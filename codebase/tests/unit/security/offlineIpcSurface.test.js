const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.join(__dirname, "..", "..", "..");
const read = (file) => fs.readFileSync(path.join(root, file), "utf8");

test("preload exposes local transcription without remote or arbitrary URL bridges", () => {
  const preload = read("preload/index.js");

  for (const forbidden of [
    "open-external",
    "cloud-transcribe",
    "cloud-reason",
    "cloud-api-request",
    "transcribe-audio-file-byok",
    "dictation-realtime",
    "assemblyai-streaming",
    "deepgram-streaming",
    "corti-streaming",
    "transcribe-local-parakeet",
    "db-update-note-cloud-id",
    "db-create-action",
  ]) {
    assert.doesNotMatch(preload, new RegExp(forbidden), forbidden);
  }

  assert.match(preload, /transcribe-local-whisper/);
  assert.match(preload, /meeting-transcription-start/);
  assert.match(preload, /dictation-preview-audio/);
});

test("main IPC keeps retry and live capture on local Whisper", () => {
  const ipc = read("main/ipc/ipcHandlers.js");

  assert.match(ipc, /ipcMain\.handle\("retry-transcription"/);
  assert.match(ipc, /ipcMain\.handle\("meeting-transcription-start"/);
  assert.match(ipc, /transcribeLocalWhisper/);
  assert.doesNotMatch(ipc, /net\.fetch|open-external|cloud-transcribe|parakeetManager/);
});

test("Whisper server cannot switch away from loopback", () => {
  const server = read("main/features/transcription/whisperServer.js");

  assert.match(server, /const LOOPBACK_HOST = "127\.0\.0\.1"/);
  assert.doesNotMatch(server, /connectRemote|isRemote|this\.hostname/);
});
