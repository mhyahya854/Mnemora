const test = require("node:test");
const assert = require("node:assert/strict");
const { chunkText, documentText } = require("../../../main/features/search/vectorIndex");

test("semantic document text includes normalized meeting transcript edits", () => {
  const text = documentText({
    title: "اجتماع المشروع",
    content: "Local notes",
    transcript: JSON.stringify([
      { text: "original words" },
      { text: "old text", editedText: "corrected speaker words" },
    ]),
  });

  assert.match(text, /اجتماع المشروع/);
  assert.match(text, /original words/);
  assert.match(text, /corrected speaker words/);
  assert.doesNotMatch(text, /old text/);
});

test("semantic text chunking is bounded, overlapping, and lossless at the edges", () => {
  const source = `${"alpha ".repeat(180)}نهاية`;
  const chunks = chunkText(source);
  assert.ok(chunks.length > 1);
  assert.ok(chunks.every((chunk) => chunk.length <= 900));
  assert.match(chunks[0], /^alpha/);
  assert.match(chunks.at(-1), /نهاية$/);
  assert.ok(chunks[0].slice(-80).split(" ").some((word) => chunks[1].includes(word)));
});
