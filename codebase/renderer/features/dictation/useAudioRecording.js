import { useCallback, useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import AudioManager from "./audioManager";
import { playStartCue, playStopCue } from "./dictationCues";
import { getSettings } from "../settings/settingsStore";
import { expandSnippets } from "../snippets/snippets";
import {
  getRecordingErrorDescription,
  getRecordingErrorTitle,
} from "../transcription/recordingErrors";
import { isAccessibilitySkipped } from "../../shared/utilities/permissions";

export const useAudioRecording = (toast, options = {}) => {
  const { t } = useTranslation();
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcript, setTranscript] = useState("");
  const managerRef = useRef(null);
  const startLock = useRef(false);
  const stopLock = useRef(false);
  const wasRecording = useRef(false);
  const { onToggle } = options;

  const startRecording = useCallback(async () => {
    if (startLock.current || !managerRef.current) return false;
    startLock.current = true;
    try {
      if (managerRef.current.getState().isProcessing) return false;
      const started = await managerRef.current.startRecording();
      if (started) {
        if (getSettings().pauseMediaOnDictation) window.electronAPI?.pauseMediaPlayback?.();
        window.electronAPI?.registerCancelHotkey?.("Escape");
        void playStartCue();
      }
      return started;
    } finally {
      startLock.current = false;
    }
  }, []);

  const stopRecording = useCallback(async () => {
    if (stopLock.current || !managerRef.current) return false;
    stopLock.current = true;
    try {
      window.electronAPI?.unregisterCancelHotkey?.();
      const stopped = managerRef.current.stopRecording();
      if (stopped) void playStopCue();
      return stopped;
    } finally {
      stopLock.current = false;
    }
  }, []);

  useEffect(() => {
    const manager = new AudioManager();
    managerRef.current = manager;
    manager.setCallbacks({
      onStateChange: ({ isRecording: recording, isProcessing: processing }) => {
        if (!recording) {
          window.electronAPI?.unregisterCancelHotkey?.();
          if (wasRecording.current && getSettings().pauseMediaOnDictation) {
            window.electronAPI?.resumeMediaPlayback?.();
          }
        }
        wasRecording.current = recording;
        setIsRecording(recording);
        setIsProcessing(processing);
      },
      onError: (error) => {
        window.electronAPI?.hideDictationPreview?.();
        toast({
          title: getRecordingErrorTitle(error, t),
          description: getRecordingErrorDescription(error, t),
          variant: "destructive",
        });
      },
      onTranscriptionComplete: async (result) => {
        const rawText = result.text?.trim();
        if (!result.success || !rawText) {
          window.electronAPI?.hideDictationPreview?.();
          toast({
            title: t("hooks.audioRecording.noAudio.title"),
            description: t("hooks.audioRecording.noAudio.description"),
          });
          return;
        }

        const text = expandSnippets(rawText, getSettings().snippets);
        setTranscript(text);
        window.electronAPI?.completeDictationPreview?.({ text });
        const { autoPasteEnabled, keepTranscriptionInClipboard } = getSettings();
        if (autoPasteEnabled) {
          await manager.safePaste(text, {
            restoreClipboard: !keepTranscriptionInClipboard,
            allowClipboardFallback: isAccessibilitySkipped(),
          });
        } else if (keepTranscriptionInClipboard) {
          await navigator.clipboard.writeText(text);
        }
        void manager.saveTranscription(text, rawText);
      },
    });

    const toggle = async () => {
      const state = manager.getState();
      if (!state.isRecording && !state.isProcessing) await startRecording();
      else if (state.isRecording) await stopRecording();
      onToggle?.();
    };
    const disposeToggle = window.electronAPI.onToggleDictation(toggle);
    const disposeStart = window.electronAPI.onStartDictation?.(() => void startRecording());
    const disposeStop = window.electronAPI.onStopDictation?.(() => void stopRecording());
    const disposeNoAudio = window.electronAPI.onNoAudioDetected?.(() => {
      toast({
        title: t("hooks.audioRecording.noAudio.title"),
        description: t("hooks.audioRecording.noAudio.description"),
      });
    });

    return () => {
      disposeToggle?.();
      disposeStart?.();
      disposeStop?.();
      disposeNoAudio?.();
      manager.cleanup();
      managerRef.current = null;
    };
  }, [onToggle, startRecording, stopRecording, t, toast]);

  const cancelRecording = useCallback(() => {
    window.electronAPI?.unregisterCancelHotkey?.();
    if (getSettings().pauseMediaOnDictation) window.electronAPI?.resumeMediaPlayback?.();
    return managerRef.current?.cancelRecording() ?? false;
  }, []);

  const cancelProcessing = useCallback(() => managerRef.current?.cancelProcessing() ?? false, []);

  const toggleListening = useCallback(async () => {
    if (!isRecording && !isProcessing) return startRecording();
    if (isRecording) return stopRecording();
    return false;
  }, [isProcessing, isRecording, startRecording, stopRecording]);

  return {
    isRecording,
    isProcessing,
    isStreaming: false,
    transcript,
    partialTranscript: "",
    startRecording,
    stopRecording,
    cancelRecording,
    cancelProcessing,
    toggleListening,
  };
};
