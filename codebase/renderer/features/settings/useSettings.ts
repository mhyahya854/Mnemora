import React, { createContext, useContext, useEffect, useMemo } from "react";
import { initializeSettings, useSettingsStore, type SettingsState } from "./settingsStore";
import { useLocalStorage } from "../../shared/hooks/useLocalStorage";
import logger from "../../shared/utilities/logger";

type SettingsValue = SettingsState & {
  autoLearnCorrections: boolean;
  setAutoLearnCorrections: (enabled: boolean) => void;
};

const SettingsContext = createContext<SettingsValue | null>(null);

export function SettingsProvider({ children }: { children: React.ReactNode }) {
  const store = useSettingsStore();
  const [autoLearnCorrections, setAutoLearnCorrectionsStored] = useLocalStorage(
    "autoLearnCorrections",
    true,
    {
      serialize: String,
      deserialize: (value: string) => value !== "false",
    }
  );

  useEffect(() => {
    void initializeSettings();
  }, []);

  useEffect(() => {
    return window.electronAPI?.onDictionaryUpdated?.((words) => {
      if (Array.isArray(words)) store.applyCustomDictionaryFromExternal(words);
    });
  }, [store.applyCustomDictionaryFromExternal]);

  useEffect(() => {
    return window.electronAPI?.onSnippetsUpdated?.((snippets) => {
      if (Array.isArray(snippets)) store.applySnippetsFromExternal(snippets);
    });
  }, [store.applySnippetsFromExternal]);

  useEffect(() => {
    window.electronAPI?.setAutoLearnEnabled?.(autoLearnCorrections);
  }, [autoLearnCorrections]);

  useEffect(() => {
    void window.electronAPI
      ?.syncStartupPreferences?.({
        localTranscriptionProvider: "whisper",
        model: store.whisperModel || "base",
      })
      .catch((error) =>
        logger.warn("Failed to warm local Whisper", { error: String(error) }, "settings")
      );
  }, [store.whisperModel]);

  const value = useMemo<SettingsValue>(
    () => ({
      ...store,
      autoLearnCorrections,
      setAutoLearnCorrections: setAutoLearnCorrectionsStored,
    }),
    [store, autoLearnCorrections, setAutoLearnCorrectionsStored]
  );

  return React.createElement(SettingsContext.Provider, { value }, children);
}

export function useSettings(): SettingsValue {
  const value = useContext(SettingsContext);
  if (!value) throw new Error("useSettings must be used within a SettingsProvider");
  return value;
}
