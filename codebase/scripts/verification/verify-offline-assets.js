#!/usr/bin/env node

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const projectRoot = path.join(__dirname, "..", "..");
const binDir = path.join(projectRoot, "resources", "bin");
const manifestPath = path.join(binDir, "asset-manifest.json");
const platformArch = `${process.platform}-${process.arch}`;
const executableSuffix = process.platform === "win32" ? ".exe" : "";

const required = [
  `whisper-server-${platformArch}${executableSuffix}`,
  "whisper-models/ggml-base.bin",
  `qdrant-${platformArch}${executableSuffix}`,
  `sherpa-onnx-diarize-${platformArch}${executableSuffix}`,
  "all-MiniLM-L6-v2/model.onnx",
  "all-MiniLM-L6-v2/tokenizer.json",
  "diarization-models/sherpa-onnx-pyannote-segmentation-3-0/model.onnx",
  "diarization-models/3dspeaker_speech_campplus_sv_en_voxceleb_16k.onnx",
  "diarization-models/silero_vad.onnx",
  "whisper-vad/ggml-silero-v5.1.2.bin",
  `meeting-aec-helper-${platformArch}${executableSuffix}`,
];

if (process.platform === "win32") {
  required.push(
    "nircmd.exe",
    "windows-fast-paste.exe",
    "windows-key-listener.exe",
    "windows-system-audio-helper.exe",
    "cargs.dll",
    "onnxruntime.dll",
    "onnxruntime_providers_shared.dll",
    "sherpa-onnx-c-api.dll",
    "sherpa-onnx-cxx-api.dll"
  );
}

function hashFile(filePath) {
  const hash = crypto.createHash("sha256");
  const fd = fs.openSync(filePath, "r");
  const buffer = Buffer.allocUnsafe(1024 * 1024);
  try {
    let bytesRead;
    do {
      bytesRead = fs.readSync(fd, buffer, 0, buffer.length, null);
      if (bytesRead > 0) hash.update(buffer.subarray(0, bytesRead));
    } while (bytesRead > 0);
  } finally {
    fs.closeSync(fd);
  }
  return hash.digest("hex");
}

function collectAssets() {
  const missing = [];
  const assets = [];
  for (const relativePath of required) {
    const filePath = path.join(binDir, ...relativePath.split("/"));
    if (!fs.existsSync(filePath) || !fs.statSync(filePath).isFile()) {
      missing.push(relativePath);
      continue;
    }
    const size = fs.statSync(filePath).size;
    if (size === 0) {
      missing.push(`${relativePath} (empty)`);
      continue;
    }
    assets.push({ path: relativePath, size, sha256: hashFile(filePath) });
  }

  const forbidden = fs.existsSync(binDir)
    ? fs
        .readdirSync(binDir)
        .filter((name) => /parakeet|sherpa-onnx-ws/i.test(name))
    : [];

  if (missing.length || forbidden.length) {
    const details = [
      missing.length ? `Missing or invalid:\n  - ${missing.join("\n  - ")}` : "",
      forbidden.length ? `Forbidden network sidecars:\n  - ${forbidden.join("\n  - ")}` : "",
    ]
      .filter(Boolean)
      .join("\n");
    throw new Error(`Offline asset verification failed for ${platformArch}.\n${details}`);
  }
  return assets;
}

function writeManifest() {
  const packageJson = require(path.join(projectRoot, "package.json"));
  const manifest = {
    formatVersion: 1,
    appVersion: packageJson.version,
    platform: process.platform,
    arch: process.arch,
    assets: collectAssets(),
  };
  fs.writeFileSync(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`);
  console.log(`Wrote ${manifest.assets.length} verified assets to ${manifestPath}`);
}

function verifyManifest() {
  if (!fs.existsSync(manifestPath)) {
    throw new Error(`Offline asset manifest is missing: ${manifestPath}`);
  }
  const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  if (manifest.platform !== process.platform || manifest.arch !== process.arch) {
    throw new Error(
      `Offline asset manifest targets ${manifest.platform}-${manifest.arch}, not ${platformArch}`
    );
  }
  const actual = collectAssets();
  const expected = new Map(manifest.assets.map((asset) => [asset.path, asset]));
  for (const asset of actual) {
    const recorded = expected.get(asset.path);
    if (
      !recorded ||
      recorded.size !== asset.size ||
      recorded.sha256.toLowerCase() !== asset.sha256
    ) {
      throw new Error(`Offline asset checksum mismatch: ${asset.path}`);
    }
  }
  console.log(`Verified ${actual.length} offline assets for ${platformArch}`);
}

try {
  if (process.argv.includes("--write-manifest")) writeManifest();
  else verifyManifest();
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}

module.exports = { required, hashFile };
