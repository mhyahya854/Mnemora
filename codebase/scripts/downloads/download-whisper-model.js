#!/usr/bin/env node

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const { downloadFile } = require("../lib/download-utils");

const MODEL = {
  fileName: "ggml-base.bin",
  expectedSizeBytes: 147951465,
  sha256: "60ed5bc3dd14eea856493d334349b405782ddcaf0028d4b5df4088345fba2efe",
  url: "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin",
};
const outputDir = path.join(__dirname, "..", "..", "resources", "bin", "whisper-models");
const outputPath = path.join(outputDir, MODEL.fileName);

function checksum(filePath) {
  return crypto.createHash("sha256").update(fs.readFileSync(filePath)).digest("hex");
}

function isValid() {
  return (
    fs.existsSync(outputPath) &&
    fs.statSync(outputPath).size === MODEL.expectedSizeBytes &&
    checksum(outputPath) === MODEL.sha256
  );
}

async function main() {
  if (isValid()) {
    console.log(`[whisper-model] ${MODEL.fileName} already verified`);
    return;
  }

  fs.mkdirSync(outputDir, { recursive: true });
  await downloadFile(MODEL.url, outputPath);
  if (!isValid()) {
    fs.rmSync(outputPath, { force: true });
    throw new Error(`Bundled Whisper model failed size or SHA-256 verification: ${MODEL.fileName}`);
  }
  console.log(`[whisper-model] bundled and verified ${MODEL.fileName}`);
}

main().catch((error) => {
  console.error(`[whisper-model] ${error.message}`);
  process.exitCode = 1;
});
