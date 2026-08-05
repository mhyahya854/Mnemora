import { useSettingsStore } from "../settings/settingsStore";
import { getDefaultHotkey } from "./hotkeys";

export const useHotkey = () => {
  // Prefer the hotkeys the main process actually registered over the stored
  // preference (they diverge on partial registration and DE-native backends).
  const hotkey =
    useSettingsStore((s) => s.activeDictationKey || s.dictationKey) || getDefaultHotkey();
  const setHotkey = useSettingsStore((s) => s.setDictationKey);

  return {
    hotkey,
    setHotkey,
  };
};
