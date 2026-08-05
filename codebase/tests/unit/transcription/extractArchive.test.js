const test = require("node:test");
const assert = require("node:assert/strict");
const crypto = require("crypto");
const fs = require("fs");
const os = require("os");
const path = require("path");
const {
  extractArchive,
  isSafeArchivePath,
  validateExpectedFiles,
  verifyPackManifest,
} = require("../../../main/features/transcription/downloadUtils");

// One stored ZIP entry named "test-file.txt" containing "hello from test\n".
const ZIP_FIXTURE = Buffer.from(
  "UEsDBAoAAAAAAEwFr1xBZFoiEAAAABAAAAANABwAdGVzdC1maWxlLnR4dFVUCQADz08G" +
    "as9PBmp1eAsAAQToAwAABOgDAABoZWxsbyBmcm9tIHRlc3QKUEsBAh4DCgAAAAAATAWv" +
    "XEFkWiIQAAAAEAAAAA0AGAAAAAAAAQAAAKSBAAAAAHRlc3QtZmlsZS50eHRVVAUAA89P" +
    "Bmp1eAsAAQToAwAABOgDAABQSwUGAAAAAAEAAQBTAAAAVwAAAAAA",
  "base64"
);

function temporaryDirectory() {
  return fs.mkdtempSync(path.join(os.tmpdir(), "mnemora-archive-test-"));
}

async function removeTemporaryDirectory(root) {
  // Windows can briefly retain the ZIP handle after yauzl closes it.
  await new Promise((resolve) => setTimeout(resolve, 25));
  await fs.promises.rm(root, { recursive: true, force: true, maxRetries: 10, retryDelay: 50 });
}

test("extractArchive extracts a valid ZIP without platform shell tools", async () => {
  const root = temporaryDirectory();
  try {
    const archive = path.join(root, "pack.zip");
    const output = path.join(root, "output");
    fs.writeFileSync(archive, ZIP_FIXTURE);
    await extractArchive(archive, output);
    assert.equal(fs.readFileSync(path.join(output, "test-file.txt"), "utf8").trim(), "hello from test");
  } finally {
    await removeTemporaryDirectory(root);
  }
});

test("extractArchive rejects ZIP path traversal before writing any entry", async () => {
  const root = temporaryDirectory();
  try {
    const archive = path.join(root, "unsafe.zip");
    const output = path.join(root, "output");
    const unsafe = Buffer.from(ZIP_FIXTURE);
    let offset = 0;
    while ((offset = unsafe.indexOf("test-file.txt", offset)) !== -1) {
      unsafe.write("../escape.txt", offset, "ascii");
      offset += 13;
    }
    fs.writeFileSync(archive, unsafe);
    await assert.rejects(() => extractArchive(archive, output), /unsafe path/i);
    assert.equal(fs.existsSync(path.join(root, "escape.txt")), false);
  } finally {
    await removeTemporaryDirectory(root);
  }
});

test("extractArchive rejects corrupt ZIP data", async () => {
  const root = temporaryDirectory();
  try {
    const archive = path.join(root, "corrupt.zip");
    fs.writeFileSync(archive, "not a zip file");
    await assert.rejects(() => extractArchive(archive, path.join(root, "output")), /zip extraction failed/i);
  } finally {
    await removeTemporaryDirectory(root);
  }
});

test("archive path validation rejects absolute, parent, drive, UNC, and NUL paths", () => {
  for (const value of ["model/model.onnx", "nested\\file.bin", "manifest.json"]) {
    assert.equal(isSafeArchivePath(value), true, value);
  }
  for (const value of ["../file", "a/../../file", "/root/file", "C:\\file", "\\\\server\\share", "a\0b"]) {
    assert.equal(isSafeArchivePath(value), false, value);
  }
});

test("model-pack validation checks required files and supplied SHA-256 manifest", async () => {
  const root = temporaryDirectory();
  try {
    const model = Buffer.from("offline model bytes");
    fs.mkdirSync(path.join(root, "models"));
    fs.writeFileSync(path.join(root, "models", "model.bin"), model);
    fs.writeFileSync(
      path.join(root, "model-pack.json"),
      JSON.stringify({
        assets: [
          {
            path: "models/model.bin",
            size: model.length,
            sha256: crypto.createHash("sha256").update(model).digest("hex"),
          },
        ],
      })
    );

    await validateExpectedFiles(root, ["models/model.bin"]);
    assert.deepEqual(await verifyPackManifest(root), { verified: true, files: 1 });

    fs.appendFileSync(path.join(root, "models", "model.bin"), "changed");
    await assert.rejects(() => verifyPackManifest(root), /wrong size|checksum mismatch/i);
  } finally {
    await removeTemporaryDirectory(root);
  }
});
