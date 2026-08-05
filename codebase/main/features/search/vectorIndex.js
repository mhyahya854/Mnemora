const { QdrantClient } = require("@qdrant/js-client-rest");
const debugLogger = require("../../infrastructure/runtime/debugLogger");
const localEmbeddings = require("./localEmbeddings");

const COLLECTION = "mnemora_documents_v1";
const VECTOR_SIZE = 384;
const INDEX_VERSION = 1;
const CHUNK_SIZE = 900;
const CHUNK_OVERLAP = 120;

function transcriptText(value) {
  if (!value) return "";
  let parsed = value;
  if (typeof value === "string") {
    try {
      parsed = JSON.parse(value);
    } catch {
      return value;
    }
  }
  if (!Array.isArray(parsed)) return "";
  return parsed
    .map((segment) =>
      typeof segment === "string"
        ? segment
        : segment?.editedText || segment?.edited_text || segment?.text || segment?.originalText || ""
    )
    .filter(Boolean)
    .join("\n");
}

function documentText(note) {
  return [
    note?.title,
    note?.content,
    transcriptText(note?.transcript),
    transcriptText(note?.transcript_segments),
  ]
    .filter(Boolean)
    .join("\n\n")
    .trim();
}

function chunkText(text) {
  const normalized = String(text || "").replace(/\r\n/g, "\n").trim();
  if (!normalized) return [];
  const chunks = [];
  let start = 0;
  while (start < normalized.length) {
    let end = Math.min(start + CHUNK_SIZE, normalized.length);
    if (end < normalized.length) {
      const boundary = Math.max(
        normalized.lastIndexOf("\n", end),
        normalized.lastIndexOf(" ", end)
      );
      if (boundary > start + CHUNK_SIZE / 2) end = boundary;
    }
    chunks.push(normalized.slice(start, end).trim());
    if (end >= normalized.length) break;
    start = Math.max(start + 1, end - CHUNK_OVERLAP);
  }
  return chunks.filter(Boolean);
}

function pointId(noteId, chunkIndex) {
  const numericId = Number(noteId);
  if (!Number.isSafeInteger(numericId) || numericId < 0 || chunkIndex >= 10000) {
    throw new Error(`Cannot create stable semantic point id for note ${noteId}`);
  }
  const id = numericId * 10000 + chunkIndex;
  if (!Number.isSafeInteger(id)) throw new Error(`Semantic point id overflow for note ${noteId}`);
  return id;
}

class VectorIndex {
  constructor() {
    this.client = null;
    this.collectionName = COLLECTION;
  }

  init(port) {
    this.client = new QdrantClient({ host: "127.0.0.1", port });
  }

  async _createCollection() {
    await this.client.createCollection(this.collectionName, {
      vectors: { size: VECTOR_SIZE, distance: "Cosine" },
    });
  }

  async ensureCollection() {
    if (!this.client) return false;
    try {
      const info = await this.client.getCollection(this.collectionName);
      const size = info?.config?.params?.vectors?.size;
      if (size && size !== VECTOR_SIZE) {
        await this.recreateCollection();
      }
    } catch {
      await this._createCollection();
    }
    return true;
  }

  async recreateCollection() {
    if (!this.client) return false;
    try {
      await this.client.deleteCollection(this.collectionName);
    } catch {
      // A clean install has no collection yet.
    }
    await this._createCollection();
    return true;
  }

  async upsertNote(noteOrId, text = "") {
    if (!this.client) return false;
    const note =
      typeof noteOrId === "object" && noteOrId !== null
        ? noteOrId
        : { id: noteOrId, content: text };
    const chunks = chunkText(documentText(note));
    await this.deleteNote(note.id);
    if (!chunks.length) return true;

    const vectors = await localEmbeddings.embedTexts(chunks);
    const points = chunks.map((chunk, index) => ({
      id: pointId(note.id, index),
      vector: Array.from(vectors[index]),
      payload: {
        note_id: Number(note.id),
        chunk_index: index,
        note_type: note.note_type || note.noteType || "note",
        text_preview: chunk.slice(0, 180),
        index_version: INDEX_VERSION,
      },
    }));
    await this.client.upsert(this.collectionName, { points, wait: true });
    return true;
  }

  async deleteNote(noteId) {
    if (!this.client) return false;
    await this.client.delete(this.collectionName, {
      filter: { must: [{ key: "note_id", match: { value: Number(noteId) } }] },
      wait: true,
    });
    return true;
  }

  async search(queryText, limit = 5) {
    if (!this.client || !String(queryText || "").trim()) return [];
    try {
      const vector = await localEmbeddings.embedText(queryText);
      const results = await this.client.search(this.collectionName, {
        vector: Array.from(vector),
        limit: Math.max(limit * 4, 20),
        with_payload: true,
      });
      const best = new Map();
      for (const result of results) {
        const noteId = Number(result.payload?.note_id);
        if (!Number.isSafeInteger(noteId)) continue;
        if (!best.has(noteId) || result.score > best.get(noteId)) best.set(noteId, result.score);
      }
      return [...best.entries()]
        .sort((a, b) => b[1] - a[1])
        .slice(0, limit)
        .map(([noteId, score]) => ({ noteId, score }));
    } catch (error) {
      debugLogger.warn("Local semantic search failed", { error: error.message });
      return [];
    }
  }

  async reindexAll(notes, onProgress) {
    if (!this.client) throw new Error("Vector index is not initialized");
    await this.recreateCollection();
    let completed = 0;
    for (const note of notes) {
      await this.upsertNote(note);
      completed += 1;
      onProgress?.(completed, notes.length);
    }
    return { indexed: completed, version: INDEX_VERSION };
  }

  async getStatus() {
    if (!this.client) return { ready: false, version: INDEX_VERSION, points: 0 };
    try {
      const info = await this.client.getCollection(this.collectionName);
      return {
        ready: true,
        version: INDEX_VERSION,
        points: info.points_count || 0,
        status: info.status || "unknown",
      };
    } catch (error) {
      return { ready: false, version: INDEX_VERSION, points: 0, error: error.message };
    }
  }

  isReady() {
    return this.client !== null;
  }
}

const instance = new VectorIndex();
module.exports = instance;
module.exports.VectorIndex = VectorIndex;
module.exports.chunkText = chunkText;
module.exports.documentText = documentText;
module.exports.INDEX_VERSION = INDEX_VERSION;
