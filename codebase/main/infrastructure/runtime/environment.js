const path = require("node:path");
const fs = require("node:fs");
const fsPromises = require("node:fs/promises");
const { app } = require("electron");
const { normalizeUiLanguage } = require("./i18nMain");

const PERSISTED_KEYS = [
  "LOCAL_WHISPER_MODEL",
  "DICTATION_KEY",
  "MEETING_KEY",
  "ACTIVATION_MODE",
  "FLOATING_ICON_AUTO_HIDE",
  "PANEL_START_POSITION",
  "START_MINIMIZED",
  "UI_LANGUAGE",
  "WHISPER_CUDA_ENABLED",
  "WHISPER_THREADS",
  "TRANSCRIPTION_GPU_UUID",
];

let envWriteQueue = Promise.resolve();

class EnvironmentManager {
  constructor() {
    const envPath = path.join(app.getPath("userData"), ".env");
    if (fs.existsSync(envPath)) require("dotenv").config({ path: envPath, override: true });
  }

  async init() {}

  _getKey(name) {
    return process.env[name] || "";
  }

  _save(name, value) {
    if (value === undefined || value === null || value === "") delete process.env[name];
    else process.env[name] = String(value);
    this.saveAllKeysToEnvFile().catch(() => {});
    return { success: true };
  }

  getDictationKey() { return this._getKey("DICTATION_KEY"); }
  saveDictationKey(value) { return this._save("DICTATION_KEY", value); }
  getMeetingKey() { return this._getKey("MEETING_KEY"); }
  saveMeetingKey(value) { return this._save("MEETING_KEY", value); }

  getActivationMode() {
    return this._getKey("ACTIVATION_MODE") === "push" ? "push" : "tap";
  }
  saveActivationMode(value) {
    return this._save("ACTIVATION_MODE", value === "push" ? "push" : "tap");
  }

  getFloatingIconAutoHide() { return this._getKey("FLOATING_ICON_AUTO_HIDE") === "true"; }
  saveFloatingIconAutoHide(value) { return this._save("FLOATING_ICON_AUTO_HIDE", Boolean(value)); }
  getStartMinimized() { return this._getKey("START_MINIMIZED") === "true"; }
  saveStartMinimized(value) { return this._save("START_MINIMIZED", Boolean(value)); }

  getPanelStartPosition() {
    const value = this._getKey("PANEL_START_POSITION");
    return ["bottom-right", "center", "bottom-left"].includes(value) ? value : "bottom-right";
  }
  savePanelStartPosition(value) {
    const valid = ["bottom-right", "center", "bottom-left"].includes(value)
      ? value
      : "bottom-right";
    return this._save("PANEL_START_POSITION", valid);
  }

  getUiLanguage() { return normalizeUiLanguage(this._getKey("UI_LANGUAGE")); }
  saveUiLanguage(value) {
    const language = normalizeUiLanguage(value);
    return { ...this._save("UI_LANGUAGE", language), language };
  }

  async saveAllKeysToEnvFile() {
    const envPath = path.join(app.getPath("userData"), ".env");
    envWriteQueue = envWriteQueue.catch(() => {}).then(async () => {
      await fsPromises.mkdir(path.dirname(envPath), { recursive: true });
      const lines = ["# Mnemora local settings"];
      for (const key of PERSISTED_KEYS) {
        if (process.env[key]) lines.push(`${key}=${process.env[key]}`);
      }
      const temporaryPath = `${envPath}.tmp`;
      await fsPromises.writeFile(temporaryPath, `${lines.join("\n")}\n`, "utf8");
      await fsPromises.rename(temporaryPath, envPath);
    });
    await envWriteQueue;
    return { success: true, path: envPath };
  }
}

module.exports = EnvironmentManager;
