import logger from "../../shared/utilities/logger";
import { isBuiltInMicrophone } from "../transcription/audioDeviceUtils";
import { getBaseLanguageCode } from "../transcription/languageSupport";
import { getDictionaryHintWords } from "../snippets/snippets";
import { matchesDictionaryPrompt } from "./dictionaryEchoFilter.js";
import {
  createLocalSpeechGateState,
  getLocalSpeechGateDecision,
  recordLocalSpeechWindow,
} from "./localSpeechGate";
import { reacquireIfDead } from "./micTrackHealth";
import { isStaleDeviceError } from "./staleMicDevice";
import { shouldSaveDiscardedRecording } from "./discardedRecording";
import { evaluateFinishedRecording } from "./recordingValidation";
import { getSettings } from "../settings/settingsStore";

const RECORDING_TIMESLICE_MS = 250;

class AudioManager {
  constructor() {
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.isRecording = false;
    this.isProcessing = false;
    this.recordingStartTime = null;
    this.recordingMimeType = "audio/webm";
    this.cachedMicDeviceId = null;
    this.micDriverWarmedUp = false;
    this.lastAudioBlob = null;
    this.lastAudioMetadata = null;
    this._receivedAudioData = false;
    this._localSpeechGateState = null;
    this._silenceCtx = null;
    this._silenceAnalyser = null;
    this._silenceInterval = null;
    this._processingGeneration = 0;
    this.onStateChange = null;
    this.onError = null;
    this.onTranscriptionComplete = null;

    this._onDeviceChange = () => {
      this.cachedMicDeviceId = null;
      this.micDriverWarmedUp = false;
    };
    navigator.mediaDevices?.addEventListener?.("devicechange", this._onDeviceChange);
  }

  setCallbacks({ onStateChange, onError, onTranscriptionComplete }) {
    this.onStateChange = onStateChange;
    this.onError = onError;
    this.onTranscriptionComplete = onTranscriptionComplete;
  }

  getCustomDictionaryPrompt() {
    const words = getDictionaryHintWords(getSettings());
    return words.length ? words.join(", ") : null;
  }

  async getAudioConstraints(forceDefaultMic = false) {
    const { preferBuiltInMic, selectedMicDeviceId } = getSettings();
    const audio = {
      echoCancellation: false,
      noiseSuppression: false,
      autoGainControl: false,
      channelCount: 2,
    };

    if (forceDefaultMic) return { audio };
    if (preferBuiltInMic) {
      if (!this.cachedMicDeviceId) {
        try {
          const devices = await navigator.mediaDevices.enumerateDevices();
          this.cachedMicDeviceId =
            devices.find(
              (device) => device.kind === "audioinput" && isBuiltInMicrophone(device.label)
            )?.deviceId ?? null;
        } catch (error) {
          logger.debug("Could not enumerate microphones", { error: String(error) }, "audio");
        }
      }
      if (this.cachedMicDeviceId) {
        return { audio: { ...audio, deviceId: { exact: this.cachedMicDeviceId } } };
      }
    }
    if (!preferBuiltInMic && selectedMicDeviceId) {
      return { audio: { ...audio, deviceId: { exact: selectedMicDeviceId } } };
    }
    return { audio };
  }

  async warmupMicDriver() {
    if (this.micDriverWarmedUp || this.isRecording || this.isProcessing) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia(await this.getAudioConstraints());
      stream.getTracks().forEach((track) => track.stop());
      this.micDriverWarmedUp = true;
    } catch (error) {
      logger.debug("Microphone warmup skipped", { error: String(error) }, "audio");
    }
  }

  setupSpeechGate(stream) {
    try {
      this._silenceCtx = new AudioContext();
      void this._silenceCtx.resume().catch(() => {});
      this._silenceAnalyser = this._silenceCtx.createAnalyser();
      this._silenceAnalyser.fftSize = 2048;
      this._silenceCtx.createMediaStreamSource(stream).connect(this._silenceAnalyser);
      this._localSpeechGateState = createLocalSpeechGateState();
      const samples = new Uint8Array(this._silenceAnalyser.fftSize);
      this._silenceInterval = setInterval(() => {
        if (this._silenceCtx?.state !== "running") return;
        this._silenceAnalyser.getByteTimeDomainData(samples);
        let energy = 0;
        let peak = 0;
        for (const sample of samples) {
          const value = (sample - 128) / 128;
          energy += value * value;
          peak = Math.max(peak, Math.abs(value));
        }
        recordLocalSpeechWindow(
          this._localSpeechGateState,
          Math.sqrt(energy / samples.length),
          peak
        );
      }, 100);
    } catch (error) {
      logger.debug("Speech gate unavailable", { error: String(error) }, "audio");
      this._localSpeechGateState = null;
    }
  }

  teardownSpeechGate() {
    if (this._silenceInterval) clearInterval(this._silenceInterval);
    this._silenceInterval = null;
    void this._silenceCtx?.close().catch(() => {});
    this._silenceCtx = null;
    this._silenceAnalyser = null;
  }

  async startRecording(forceDefaultMic = false) {
    if (this.isRecording || this.isProcessing || this.mediaRecorder?.state === "recording") {
      return false;
    }

    try {
      const stream = await reacquireIfDead(
        await navigator.mediaDevices.getUserMedia(await this.getAudioConstraints(forceDefaultMic)),
        () => {
          this.cachedMicDeviceId = null;
          return this.getAudioConstraints(true);
        },
        logger
      );

      this.setupSpeechGate(stream);
      this.mediaRecorder = new MediaRecorder(stream);
      this.recordingMimeType = this.mediaRecorder.mimeType || "audio/webm";
      this.audioChunks = [];
      this._receivedAudioData = false;
      this.recordingStartTime = Date.now();

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data?.size) {
          this._receivedAudioData = true;
          this.audioChunks.push(event.data);
        }
      };

      this.mediaRecorder.onstop = async () => {
        this.teardownSpeechGate();
        this.isRecording = false;
        const durationSeconds = this.recordingStartTime
          ? (Date.now() - this.recordingStartTime) / 1000
          : 0;
        this.recordingStartTime = null;
        const blob = new Blob(this.audioChunks, { type: this.recordingMimeType });
        const check = evaluateFinishedRecording({
          blobSize: blob.size,
          receivedAudioData: this._receivedAudioData,
        });

        if (!check.usable) {
          stream.getTracks().forEach((track) => track.stop());
          this.onStateChange?.({ isRecording: false, isProcessing: false, isStreaming: false });
          this.onTranscriptionComplete?.({ success: true, text: "" });
          return;
        }

        this.isProcessing = true;
        this.lastAudioBlob = blob;
        this.onStateChange?.({ isRecording: false, isProcessing: true, isStreaming: false });
        await this.processAudio(blob, { durationSeconds });
        stream.getTracks().forEach((track) => track.stop());
      };

      this.mediaRecorder.start(RECORDING_TIMESLICE_MS);
      this.isRecording = true;
      this.onStateChange?.({ isRecording: true, isProcessing: false, isStreaming: false });
      return true;
    } catch (error) {
      if (isStaleDeviceError(error) && !forceDefaultMic) {
        this.cachedMicDeviceId = null;
        return this.startRecording(true);
      }

      const denied = error?.name === "NotAllowedError" || error?.name === "PermissionDeniedError";
      this.onError?.({
        title: denied ? "Microphone Access Denied" : "Recording Error",
        description: denied
          ? "Grant microphone permission in system settings, then try again."
          : `Failed to access the microphone: ${error?.message ?? String(error)}`,
      });
      return false;
    }
  }

  stopRecording() {
    if (this.mediaRecorder?.state !== "recording") return false;
    this.mediaRecorder.stop();
    return true;
  }

  cancelRecording() {
    if (this.mediaRecorder?.state !== "recording") return false;
    const recorder = this.mediaRecorder;
    recorder.onstop = () => {
      this.teardownSpeechGate();
      const durationSeconds = this.recordingStartTime
        ? (Date.now() - this.recordingStartTime) / 1000
        : 0;
      const blob = shouldSaveDiscardedRecording(getSettings(), durationSeconds)
        ? new Blob(this.audioChunks, { type: this.recordingMimeType })
        : null;
      recorder.stream.getTracks().forEach((track) => track.stop());
      this.audioChunks = [];
      this.recordingStartTime = null;
      this.isRecording = false;
      this.isProcessing = false;
      this.onStateChange?.({ isRecording: false, isProcessing: false, isStreaming: false });
      if (blob?.size) void this.saveDiscardedTranscription(blob, durationSeconds);
    };
    recorder.stop();
    return true;
  }

  cancelProcessing() {
    if (!this.isProcessing) return false;
    this._processingGeneration += 1;
    this.isProcessing = false;
    this.lastAudioBlob = null;
    this.lastAudioMetadata = null;
    this.onStateChange?.({ isRecording: false, isProcessing: false, isStreaming: false });
    return true;
  }

  async processAudio(audioBlob, { durationSeconds = 0 } = {}) {
    const generation = ++this._processingGeneration;
    const speechDecision = getLocalSpeechGateDecision(this._localSpeechGateState);
    this._localSpeechGateState = null;

    try {
      if (speechDecision.skip) {
        this.onTranscriptionComplete?.({ success: true, text: "" });
        return;
      }

      const settings = getSettings();
      const arrayBuffer = await audioBlob.arrayBuffer();
      const language = getBaseLanguageCode(settings.preferredLanguage);
      const options = { model: settings.whisperModel || "base" };
      if (language) options.language = language;
      const initialPrompt = this.getCustomDictionaryPrompt();
      if (initialPrompt) options.initialPrompt = initialPrompt;

      const result = await window.electronAPI.transcribeLocalWhisper(arrayBuffer, options);
      if (generation !== this._processingGeneration) return;
      if (!result?.success) {
        if (result?.message === "No audio detected") {
          this.onTranscriptionComplete?.({ success: true, text: "" });
          return;
        }
        throw new Error(result?.message || result?.error || "Local Whisper transcription failed");
      }

      const text = String(result.text ?? "").trim();
      if (!text || matchesDictionaryPrompt(text, initialPrompt)) {
        this.onTranscriptionComplete?.({ success: true, text: "" });
        return;
      }

      this.lastAudioMetadata = {
        durationMs: Math.round(durationSeconds * 1000),
        provider: "local-whisper",
        model: options.model,
      };
      this.onTranscriptionComplete?.({
        success: true,
        text,
        rawText: text,
        source: "local-whisper",
      });
    } catch (error) {
      if (generation !== this._processingGeneration) return;
      const message = error?.message ?? String(error);
      this.onError?.({
        title: "Transcription Error",
        description: `Local transcription failed: ${message}`,
      });
      if (this.lastAudioBlob) void this.saveFailedTranscription(message, null, { durationSeconds });
    } finally {
      if (generation === this._processingGeneration) {
        this.isProcessing = false;
        this.onStateChange?.({ isRecording: false, isProcessing: false, isStreaming: false });
      }
    }
  }

  async safePaste(text, options = {}) {
    try {
      await window.electronAPI.pasteText(text, options);
      return true;
    } catch (error) {
      this.onError?.({
        title: "Paste Error",
        description: `Could not paste the text: ${error?.message ?? String(error)}`,
      });
      return false;
    }
  }

  async saveTranscription(text, rawText = null, { clientTranscriptionId } = {}) {
    if (!getSettings().dataRetentionEnabled) {
      this.lastAudioBlob = null;
      this.lastAudioMetadata = null;
      return true;
    }
    try {
      const result = await window.electronAPI.saveTranscription(text, rawText, {
        clientTranscriptionId,
      });
      if (result?.id && this.lastAudioBlob) {
        const audio = await this.lastAudioBlob.arrayBuffer();
        await window.electronAPI.saveTranscriptionAudio(result.id, audio, this.lastAudioMetadata);
      }
      this.lastAudioBlob = null;
      this.lastAudioMetadata = null;
      return true;
    } catch (error) {
      logger.warn("Failed to save transcription", { error: String(error) }, "audio");
      return false;
    }
  }

  async saveFailedTranscription(errorMessage, errorCode = null, metadata = {}) {
    if (!getSettings().dataRetentionEnabled || !this.lastAudioBlob) return;
    try {
      const result = await window.electronAPI.saveTranscription("", null, {
        status: "failed",
        errorMessage,
        errorCode,
      });
      if (result?.id) {
        await window.electronAPI.saveTranscriptionAudio(
          result.id,
          await this.lastAudioBlob.arrayBuffer(),
          {
            durationMs: metadata.durationSeconds
              ? Math.round(metadata.durationSeconds * 1000)
              : undefined,
            provider: "local-whisper",
            model: getSettings().whisperModel || "base",
          }
        );
      }
    } catch (error) {
      logger.warn("Failed to preserve failed dictation", { error: String(error) }, "audio");
    } finally {
      this.lastAudioBlob = null;
      this.lastAudioMetadata = null;
    }
  }

  async saveDiscardedTranscription(blob, durationSeconds) {
    let id = null;
    try {
      const result = await window.electronAPI.saveTranscription("", null, { status: "discarded" });
      id = result?.id ?? null;
      if (id) {
        await window.electronAPI.saveTranscriptionAudio(id, await blob.arrayBuffer(), {
          durationMs: Math.round(durationSeconds * 1000),
        });
      }
    } catch (error) {
      logger.warn("Failed to preserve discarded recording", { error: String(error) }, "audio");
      if (id) void window.electronAPI.deleteTranscription(id);
    }
  }

  getState() {
    return {
      isRecording: this.isRecording,
      isProcessing: this.isProcessing,
      isStreaming: false,
      isStreamingStartInProgress: false,
    };
  }

  shouldUseStreaming() {
    return false;
  }

  cleanup() {
    this._processingGeneration += 1;
    this.teardownSpeechGate();
    if (this.mediaRecorder?.state === "recording") this.cancelRecording();
    navigator.mediaDevices?.removeEventListener?.("devicechange", this._onDeviceChange);
    this.onStateChange = null;
    this.onError = null;
    this.onTranscriptionComplete = null;
  }
}

export default AudioManager;
