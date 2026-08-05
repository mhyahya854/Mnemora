import { create } from "zustand";
import i18n, { normalizeUiLanguage } from "../../shared/i18n";
import whisperVadConstants from "../../../shared/config/whisperVad.json";
import logger from "../../shared/utilities/logger";
import type { Snippet } from "../snippets/snippets";

export type Theme = "light" | "dark" | "auto";
export type PanelStartPosition = "bottom-right" | "center" | "bottom-left";
export type MeetingLayoutMode = "side-panel" | "full-width";
export type ActivationMode = "tap" | "push";

const isBrowser = typeof window !== "undefined";

function readString(key: string, fallback: string): string {
  return isBrowser ? (localStorage.getItem(key) ?? fallback) : fallback;
}

function readBoolean(key: string, fallback: boolean): boolean {
  if (!isBrowser) return fallback;
  const value = localStorage.getItem(key);
  return value === null ? fallback : value === "true";
}

function readNumber(key: string, fallback: number): number {
  const value = Number(readString(key, String(fallback)));
  return Number.isFinite(value) ? value : fallback;
}

function readArray<T>(key: string): T[] {
  if (!isBrowser) return [];
  try {
    const value = JSON.parse(localStorage.getItem(key) ?? "[]");
    return Array.isArray(value) ? value : [];
  } catch {
    return [];
  }
}

function persist(key: string, value: unknown) {
  if (!isBrowser) return;
  localStorage.setItem(key, typeof value === "string" ? value : JSON.stringify(value));
}

const VAD_DEFAULTS = whisperVadConstants.DEFAULTS;
const VAD_LIMITS = whisperVadConstants.LIMITS;
type VadKey = keyof typeof VAD_DEFAULTS;

function clampVad(key: VadKey, value: number): number {
  const limits = VAD_LIMITS[key];
  const next = Number.isFinite(value) ? value : VAD_DEFAULTS[key];
  const clamped = Math.min(limits.max, Math.max(limits.min, next));
  return limits.round ? Math.round(clamped) : clamped;
}

export interface SettingsState {
  uiLanguage: string;
  useLocalWhisper: true;
  whisperModel: string;
  preferredLanguage: string;
  customDictionary: string[];
  snippets: Snippet[];

  dictationKey: string;
  activeDictationKey: string | null;
  meetingKey: string;
  meetingHotkeyLayoutMode: MeetingLayoutMode;
  activationMode: ActivationMode;

  preferBuiltInMic: boolean;
  selectedMicDeviceId: string;
  theme: Theme;
  audioRetentionDays: number;
  dataRetentionEnabled: boolean;
  saveDiscardedTranscriptions: boolean;
  audioCuesEnabled: boolean;
  pauseMediaOnDictation: boolean;
  floatingIconAutoHide: boolean;
  startMinimized: boolean;
  panelStartPosition: PanelStartPosition;
  showTranscriptionPreview: boolean;
  autoPasteEnabled: boolean;
  keepTranscriptionInClipboard: boolean;
  noteFilesEnabled: boolean;
  noteFilesPath: string;

  meetingProcessDetection: boolean;
  speakerDiarizationEnabled: boolean;
  dictationSileroEnabled: boolean;
  noteRecordingSileroEnabled: boolean;
  meetingSileroEnabled: boolean;
  whisperVadThreshold: number;
  whisperVadMinSpeechDurationMs: number;
  whisperVadMinSilenceDurationMs: number;
  whisperVadMaxSpeechDurationS: number;
  whisperVadSpeechPadMs: number;
  whisperVadSamplesOverlap: number;

  setUiLanguage: (language: string) => void;
  setWhisperModel: (model: string) => void;
  setPreferredLanguage: (language: string) => void;
  setCustomDictionary: (words: string[]) => void;
  applyCustomDictionaryFromExternal: (words: string[]) => void;
  setSnippets: (snippets: Snippet[]) => void;
  applySnippetsFromExternal: (snippets: Snippet[]) => void;
  setDictationKey: (key: string) => void;
  setMeetingKey: (key: string) => void;
  setMeetingHotkeyLayoutMode: (mode: MeetingLayoutMode) => void;
  setActivationMode: (mode: ActivationMode) => void;
  setPreferBuiltInMic: (value: boolean) => void;
  setSelectedMicDeviceId: (id: string) => void;
  setTheme: (theme: Theme) => void;
  setAudioRetentionDays: (days: number) => void;
  setDataRetentionEnabled: (value: boolean) => void;
  setSaveDiscardedTranscriptions: (value: boolean) => void;
  setAudioCuesEnabled: (value: boolean) => void;
  setPauseMediaOnDictation: (value: boolean) => void;
  setFloatingIconAutoHide: (value: boolean) => void;
  setStartMinimized: (value: boolean) => void;
  setPanelStartPosition: (value: PanelStartPosition) => void;
  setShowTranscriptionPreview: (value: boolean) => void;
  setAutoPasteEnabled: (value: boolean) => void;
  setKeepTranscriptionInClipboard: (value: boolean) => void;
  setNoteFilesEnabled: (value: boolean) => void;
  setNoteFilesPath: (value: string) => void;
  setMeetingProcessDetection: (value: boolean) => void;
  setSpeakerDiarizationEnabled: (value: boolean) => void;
  setDictationSileroEnabled: (value: boolean) => void;
  setNoteRecordingSileroEnabled: (value: boolean) => void;
  setMeetingSileroEnabled: (value: boolean) => void;
  setWhisperVadThreshold: (value: number) => void;
  setWhisperVadMinSpeechDurationMs: (value: number) => void;
  setWhisperVadMinSilenceDurationMs: (value: number) => void;
  setWhisperVadMaxSpeechDurationS: (value: number) => void;
  setWhisperVadSpeechPadMs: (value: number) => void;
  setWhisperVadSamplesOverlap: (value: number) => void;
}

const storedTheme = readString("theme", "auto");
const storedPanelPosition = readString("panelStartPosition", "bottom-right");
const storedLayout = readString("meetingHotkeyLayoutMode", "full-width");

export const useSettingsStore = create<SettingsState>()((set, get) => {
  const setBoolean = (key: keyof SettingsState, value: boolean) => {
    persist(String(key), value);
    set({ [key]: value } as Partial<SettingsState>);
  };
  const syncVad = (key: VadKey, storeKey: keyof SettingsState, raw: number) => {
    const value = clampVad(key, raw);
    persist(String(storeKey), value);
    set({ [storeKey]: value } as Partial<SettingsState>);
    window.electronAPI?.setWhisperVadConfig?.({ [key]: value });
  };

  return {
    uiLanguage: normalizeUiLanguage(readString("uiLanguage", "en")),
    useLocalWhisper: true,
    whisperModel: readString("whisperModel", "base"),
    preferredLanguage: readString("preferredLanguage", "auto"),
    customDictionary: readArray<string>("customDictionary"),
    snippets: readArray<Snippet>("snippets"),

    dictationKey: readString("dictationKey", ""),
    activeDictationKey: null,
    meetingKey: readString("meetingKey", ""),
    meetingHotkeyLayoutMode: storedLayout === "side-panel" ? "side-panel" : "full-width",
    activationMode: readString("activationMode", "tap") === "push" ? "push" : "tap",

    preferBuiltInMic: readBoolean("preferBuiltInMic", true),
    selectedMicDeviceId: readString("selectedMicDeviceId", ""),
    theme:
      storedTheme === "light" || storedTheme === "dark" || storedTheme === "auto"
        ? storedTheme
        : "auto",
    audioRetentionDays: Math.max(0, Math.round(readNumber("audioRetentionDays", 30))),
    dataRetentionEnabled: readBoolean("dataRetentionEnabled", false),
    saveDiscardedTranscriptions: readBoolean("saveDiscardedTranscriptions", false),
    audioCuesEnabled: readBoolean("audioCuesEnabled", true),
    pauseMediaOnDictation: readBoolean("pauseMediaOnDictation", false),
    floatingIconAutoHide: readBoolean("floatingIconAutoHide", false),
    startMinimized: readBoolean("startMinimized", false),
    panelStartPosition:
      storedPanelPosition === "center" || storedPanelPosition === "bottom-left"
        ? storedPanelPosition
        : "bottom-right",
    showTranscriptionPreview: readBoolean("showTranscriptionPreview", false),
    autoPasteEnabled: readBoolean("autoPasteEnabled", true),
    keepTranscriptionInClipboard: readBoolean("keepTranscriptionInClipboard", false),
    noteFilesEnabled: readBoolean("noteFilesEnabled", false),
    noteFilesPath: readString("noteFilesPath", ""),

    meetingProcessDetection: readBoolean("meetingProcessDetection", true),
    speakerDiarizationEnabled: readBoolean("speakerDiarizationEnabled", true),
    dictationSileroEnabled: readBoolean("dictationSileroEnabled", true),
    noteRecordingSileroEnabled: readBoolean("noteRecordingSileroEnabled", true),
    meetingSileroEnabled: readBoolean("meetingSileroEnabled", true),
    whisperVadThreshold: clampVad("threshold", readNumber("whisperVadThreshold", 0.5)),
    whisperVadMinSpeechDurationMs: clampVad(
      "minSpeechDurationMs",
      readNumber("whisperVadMinSpeechDurationMs", 250)
    ),
    whisperVadMinSilenceDurationMs: clampVad(
      "minSilenceDurationMs",
      readNumber("whisperVadMinSilenceDurationMs", 200)
    ),
    whisperVadMaxSpeechDurationS: clampVad(
      "maxSpeechDurationS",
      readNumber("whisperVadMaxSpeechDurationS", 30)
    ),
    whisperVadSpeechPadMs: clampVad("speechPadMs", readNumber("whisperVadSpeechPadMs", 100)),
    whisperVadSamplesOverlap: clampVad(
      "samplesOverlap",
      readNumber("whisperVadSamplesOverlap", 0.5)
    ),

    setUiLanguage: (language) => {
      const value = normalizeUiLanguage(language);
      persist("uiLanguage", value);
      set({ uiLanguage: value });
      void i18n.changeLanguage(value);
      void window.electronAPI?.setUiLanguage?.(value);
    },
    setWhisperModel: (whisperModel) => {
      persist("whisperModel", whisperModel);
      set({ whisperModel });
    },
    setPreferredLanguage: (preferredLanguage) => {
      persist("preferredLanguage", preferredLanguage);
      set({ preferredLanguage });
    },
    setCustomDictionary: (customDictionary) => {
      persist("customDictionary", customDictionary);
      set({ customDictionary });
      void window.electronAPI
        ?.setDictionary?.(customDictionary)
        .catch((error) =>
          logger.warn("Failed to save dictionary", { error: String(error) }, "settings")
        );
    },
    applyCustomDictionaryFromExternal: (customDictionary) => {
      persist("customDictionary", customDictionary);
      set({ customDictionary });
    },
    setSnippets: (snippets) => {
      persist("snippets", snippets);
      set({ snippets });
      void window.electronAPI
        ?.setSnippets?.(snippets)
        .catch((error) =>
          logger.warn("Failed to save snippets", { error: String(error) }, "settings")
        );
    },
    applySnippetsFromExternal: (snippets) => {
      persist("snippets", snippets);
      set({ snippets });
    },
    setDictationKey: (dictationKey) => {
      persist("dictationKey", dictationKey);
      set({ dictationKey });
      window.electronAPI?.notifyHotkeyChanged?.(dictationKey);
      void window.electronAPI?.saveDictationKey?.(dictationKey);
    },
    setMeetingKey: (meetingKey) => {
      persist("meetingKey", meetingKey);
      set({ meetingKey });
    },
    setMeetingHotkeyLayoutMode: (meetingHotkeyLayoutMode) => {
      persist("meetingHotkeyLayoutMode", meetingHotkeyLayoutMode);
      set({ meetingHotkeyLayoutMode });
    },
    setActivationMode: (activationMode) => {
      persist("activationMode", activationMode);
      set({ activationMode });
      window.electronAPI?.notifyActivationModeChanged?.(activationMode);
    },
    setPreferBuiltInMic: (value) => setBoolean("preferBuiltInMic", value),
    setSelectedMicDeviceId: (selectedMicDeviceId) => {
      persist("selectedMicDeviceId", selectedMicDeviceId);
      set({ selectedMicDeviceId });
    },
    setTheme: (theme) => {
      persist("theme", theme);
      set({ theme });
    },
    setAudioRetentionDays: (audioRetentionDays) => {
      const value = Math.max(0, Math.round(audioRetentionDays));
      persist("audioRetentionDays", value);
      set({ audioRetentionDays: value });
    },
    setDataRetentionEnabled: (value) => setBoolean("dataRetentionEnabled", value),
    setSaveDiscardedTranscriptions: (value) => setBoolean("saveDiscardedTranscriptions", value),
    setAudioCuesEnabled: (value) => setBoolean("audioCuesEnabled", value),
    setPauseMediaOnDictation: (value) => setBoolean("pauseMediaOnDictation", value),
    setFloatingIconAutoHide: (floatingIconAutoHide) => {
      if (get().floatingIconAutoHide === floatingIconAutoHide) return;
      persist("floatingIconAutoHide", floatingIconAutoHide);
      set({ floatingIconAutoHide });
      window.electronAPI?.notifyFloatingIconAutoHideChanged?.(floatingIconAutoHide);
    },
    setStartMinimized: (startMinimized) => {
      persist("startMinimized", startMinimized);
      set({ startMinimized });
      window.electronAPI?.notifyStartMinimizedChanged?.(startMinimized);
    },
    setPanelStartPosition: (panelStartPosition) => {
      persist("panelStartPosition", panelStartPosition);
      set({ panelStartPosition });
      window.electronAPI?.notifyPanelStartPositionChanged?.(panelStartPosition);
    },
    setShowTranscriptionPreview: (value) => setBoolean("showTranscriptionPreview", value),
    setAutoPasteEnabled: (value) => setBoolean("autoPasteEnabled", value),
    setKeepTranscriptionInClipboard: (value) => setBoolean("keepTranscriptionInClipboard", value),
    setNoteFilesEnabled: (value) => setBoolean("noteFilesEnabled", value),
    setNoteFilesPath: (noteFilesPath) => {
      persist("noteFilesPath", noteFilesPath);
      set({ noteFilesPath });
    },
    setMeetingProcessDetection: (meetingProcessDetection) => {
      persist("meetingProcessDetection", meetingProcessDetection);
      set({ meetingProcessDetection });
      void window.electronAPI?.meetingDetectionSetPreferences?.({
        processDetection: meetingProcessDetection,
      });
    },
    setSpeakerDiarizationEnabled: (speakerDiarizationEnabled) => {
      persist("speakerDiarizationEnabled", speakerDiarizationEnabled);
      set({ speakerDiarizationEnabled });
      void window.electronAPI?.setSpeakerDiarizationEnabled?.(speakerDiarizationEnabled);
    },
    setDictationSileroEnabled: (value) => {
      setBoolean("dictationSileroEnabled", value);
      void window.electronAPI?.setWhisperVadConfig?.({ dictationSileroEnabled: value });
    },
    setNoteRecordingSileroEnabled: (value) => {
      setBoolean("noteRecordingSileroEnabled", value);
      void window.electronAPI?.setWhisperVadConfig?.({ noteRecordingSileroEnabled: value });
    },
    setMeetingSileroEnabled: (value) => {
      setBoolean("meetingSileroEnabled", value);
      void window.electronAPI?.setWhisperVadConfig?.({ meetingSileroEnabled: value });
    },
    setWhisperVadThreshold: (value) => syncVad("threshold", "whisperVadThreshold", value),
    setWhisperVadMinSpeechDurationMs: (value) =>
      syncVad("minSpeechDurationMs", "whisperVadMinSpeechDurationMs", value),
    setWhisperVadMinSilenceDurationMs: (value) =>
      syncVad("minSilenceDurationMs", "whisperVadMinSilenceDurationMs", value),
    setWhisperVadMaxSpeechDurationS: (value) =>
      syncVad("maxSpeechDurationS", "whisperVadMaxSpeechDurationS", value),
    setWhisperVadSpeechPadMs: (value) => syncVad("speechPadMs", "whisperVadSpeechPadMs", value),
    setWhisperVadSamplesOverlap: (value) =>
      syncVad("samplesOverlap", "whisperVadSamplesOverlap", value),
  };
});

export function getSettings(): SettingsState {
  return useSettingsStore.getState();
}

export const selectResolvedMeetingTranscription = (state: SettingsState) => ({
  useLocalWhisper: true as const,
  localTranscriptionProvider: "whisper" as const,
  whisperModel: state.whisperModel || "base",
});

export const selectResolvedUploadTranscription = selectResolvedMeetingTranscription;

let initialized = false;

export async function initializeSettings(): Promise<void> {
  if (initialized || !isBrowser) return;
  initialized = true;

  const state = useSettingsStore.getState();
  try {
    const [dictationKey, activeDictationKey, activationMode, uiLanguage, dictionary, snippets] =
      await Promise.all([
        state.dictationKey ? Promise.resolve(null) : window.electronAPI?.getDictationKey?.(),
        window.electronAPI?.getActiveDictationKey?.(),
        window.electronAPI?.getActivationMode?.(),
        window.electronAPI?.getUiLanguage?.(),
        window.electronAPI?.getDictionary?.(),
        window.electronAPI?.getSnippets?.(),
      ]);

    if (dictationKey) state.setDictationKey(dictationKey);
    if (activeDictationKey) useSettingsStore.setState({ activeDictationKey });
    if (activationMode === "tap" || activationMode === "push") {
      persist("activationMode", activationMode);
      useSettingsStore.setState({ activationMode });
    }
    if (uiLanguage) state.setUiLanguage(uiLanguage);
    else void i18n.changeLanguage(state.uiLanguage);

    if (dictionary?.length) state.applyCustomDictionaryFromExternal(dictionary);
    else if (state.customDictionary.length)
      await window.electronAPI?.setDictionary?.(state.customDictionary);

    if (snippets?.length) state.applySnippetsFromExternal(snippets);
    else if (state.snippets.length) await window.electronAPI?.setSnippets?.(state.snippets);
  } catch (error) {
    logger.warn("Failed to initialize local settings", { error: String(error) }, "settings");
  }

  const current = useSettingsStore.getState();
  await Promise.allSettled([
    window.electronAPI?.syncStartupPreferences?.({
      localTranscriptionProvider: "whisper",
      model: current.whisperModel || "base",
    }),
    window.electronAPI?.meetingDetectionSetPreferences?.({
      processDetection: current.meetingProcessDetection,
    }),
    window.electronAPI?.setSpeakerDiarizationEnabled?.(current.speakerDiarizationEnabled),
    window.electronAPI?.setWhisperVadConfig?.({
      dictationSileroEnabled: current.dictationSileroEnabled,
      noteRecordingSileroEnabled: current.noteRecordingSileroEnabled,
      meetingSileroEnabled: current.meetingSileroEnabled,
      threshold: current.whisperVadThreshold,
      minSpeechDurationMs: current.whisperVadMinSpeechDurationMs,
      minSilenceDurationMs: current.whisperVadMinSilenceDurationMs,
      maxSpeechDurationS: current.whisperVadMaxSpeechDurationS,
      speechPadMs: current.whisperVadSpeechPadMs,
      samplesOverlap: current.whisperVadSamplesOverlap,
    }),
  ]);

  window.electronAPI?.onDictationKeyActive?.((key: string) => {
    useSettingsStore.setState({ activeDictationKey: key });
  });
  window.electronAPI?.onSettingUpdated?.(({ key, value }) => {
    if (key === "dictationKey" && typeof value === "string") {
      persist(key, value);
      useSettingsStore.setState({ dictationKey: value });
    }
  });
}
