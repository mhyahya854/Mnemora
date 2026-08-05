import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Archive,
  BookOpen,
  CheckCircle2,
  Database,
  FolderOpen,
  HardDrive,
  Info,
  Keyboard,
  Loader2,
  Mic,
  RefreshCw,
  Search,
  Shield,
  Users,
} from "lucide-react";
import type { WhisperModelsListResult } from "../../shared/types/electron";
import { useSettings } from "./useSettings";
import DictionaryView from "../dictation/DictionaryView";
import { Button } from "../../shared/ui/button";
import { Input } from "../../shared/ui/input";
import { cn } from "../../shared/ui/utils";

type SectionId =
  | "general"
  | "dictation"
  | "meetings"
  | "models"
  | "search"
  | "data"
  | "backup"
  | "privacy"
  | "about";

interface Props {
  initialSection?: string;
}

interface OfflineBridge {
  importWhisperModelPack?: () => Promise<{ success: boolean; model?: string; error?: string }>;
  selectWhisperModelPack?: () => Promise<{ success: boolean; model?: string; error?: string }>;
}

const sections: Array<{
  id: SectionId;
  label: string;
  icon: typeof Info;
}> = [
  { id: "general", label: "General", icon: HardDrive },
  { id: "dictation", label: "Dictation", icon: Mic },
  { id: "meetings", label: "Meetings", icon: Users },
  { id: "models", label: "Models", icon: Database },
  { id: "search", label: "Search", icon: Search },
  { id: "data", label: "Data", icon: Archive },
  { id: "backup", label: "Backup & Export", icon: FolderOpen },
  { id: "privacy", label: "Privacy", icon: Shield },
  { id: "about", label: "About", icon: Info },
];

function normalizeSection(value?: string): SectionId {
  if (value === "backupExport" || value === "backup-export") return "backup";
  if (value === "privacyData") return "privacy";
  return sections.some((section) => section.id === value) ? (value as SectionId) : "general";
}

function SettingsCard({
  title,
  description,
  children,
}: {
  title: string;
  description?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-border/60 bg-card p-4">
      <h2 className="text-sm font-medium">{title}</h2>
      {description && (
        <p className="mt-1 text-xs leading-relaxed text-muted-foreground">{description}</p>
      )}
      <div className="mt-4 space-y-3">{children}</div>
    </div>
  );
}

function ToggleRow({
  label,
  description,
  checked,
  onChange,
}: {
  label: string;
  description?: string;
  checked: boolean;
  onChange: (value: boolean) => void;
}) {
  return (
    <label className="flex items-center justify-between gap-4 py-1 cursor-pointer">
      <span>
        <span className="block text-sm">{label}</span>
        {description && (
          <span className="block mt-0.5 text-xs text-muted-foreground">{description}</span>
        )}
      </span>
      <input
        type="checkbox"
        checked={checked}
        onChange={(event) => onChange(event.target.checked)}
        className="h-4 w-4 accent-primary"
      />
    </label>
  );
}

export default function SettingsPage({ initialSection }: Props) {
  const settings = useSettings();
  const [active, setActive] = useState<SectionId>(() => normalizeSection(initialSection));
  const [models, setModels] = useState<WhisperModelsListResult | null>(null);
  const [modelsBusy, setModelsBusy] = useState(false);
  const [modelMessage, setModelMessage] = useState("");
  const [reindexing, setReindexing] = useState(false);
  const [reindexProgress, setReindexProgress] = useState<{ done: number; total: number } | null>(
    null
  );
  const [storage, setStorage] = useState<{ fileCount: number; totalBytes: number } | null>(null);
  const [appVersion, setAppVersion] = useState("");
  const [backupMessage, setBackupMessage] = useState("");
  const [backupAudio, setBackupAudio] = useState(false);
  const [backupBusy, setBackupBusy] = useState(false);

  useEffect(() => setActive(normalizeSection(initialSection)), [initialSection]);

  const refreshModels = useCallback(async () => {
    setModelsBusy(true);
    try {
      const result = await window.electronAPI.listWhisperModels();
      setModels(result);
      const currentAvailable = result.models.some(
        (model) => model.model === settings.whisperModel && model.installed
      );
      if (!currentAvailable) {
        const first = result.models.find((model) => model.installed);
        if (first) settings.setWhisperModel(first.model);
      }
    } catch (error) {
      setModelMessage(`Could not inspect local models: ${String(error)}`);
    } finally {
      setModelsBusy(false);
    }
  }, [settings.setWhisperModel, settings.whisperModel]);

  useEffect(() => {
    if (active === "models") void refreshModels();
    if (active === "data") void window.electronAPI.getAudioStorageUsage().then(setStorage);
    if (active === "about")
      void window.electronAPI.getAppVersion().then(({ version }) => setAppVersion(version));
  }, [active, refreshModels]);

  useEffect(
    () =>
      window.electronAPI.onSemanticReindexProgress?.((progress) => setReindexProgress(progress)),
    []
  );

  const installedModels = useMemo(
    () => models?.models.filter((model) => model.installed) ?? [],
    [models]
  );

  const importModelPack = async () => {
    const bridge = window.electronAPI as unknown as OfflineBridge;
    const importer = bridge.importWhisperModelPack ?? bridge.selectWhisperModelPack;
    if (!importer) {
      setModelMessage("Place a compatible GGML Whisper model in the models folder, then refresh.");
      await window.electronAPI.openMnemoraModelsFolder?.();
      return;
    }
    setModelsBusy(true);
    try {
      const result = await importer();
      setModelMessage(
        result.success
          ? `Imported ${result.model ?? "model pack"}.`
          : (result.error ?? "Import failed.")
      );
      if (result.success) await refreshModels();
    } finally {
      setModelsBusy(false);
    }
  };

  const reindex = async () => {
    setReindexing(true);
    setReindexProgress(null);
    try {
      await window.electronAPI.semanticReindexAll();
    } finally {
      setReindexing(false);
    }
  };

  const runBackupAction = async (action: "create" | "restore") => {
    setBackupBusy(true);
    setBackupMessage("");
    try {
      const result =
        action === "create"
          ? await window.electronAPI.createLocalBackup({ includeAudio: backupAudio })
          : await window.electronAPI.restoreLocalBackup({ restoreAudio: backupAudio });
      if (result.canceled) return;
      if (!result.success) {
        setBackupMessage(result.error ?? "Backup action failed.");
        return;
      }
      if (action === "create") {
        setBackupMessage(`Verified backup created at ${result.path}.`);
      } else {
        setBackupMessage("Backup restored. Reloading local data…");
        window.setTimeout(() => window.location.reload(), 500);
      }
    } finally {
      setBackupBusy(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto p-6 flex gap-6">
      <aside className="w-44 shrink-0">
        <h1 className="text-xl font-semibold mb-4">Settings</h1>
        <nav className="space-y-0.5">
          {sections.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              type="button"
              onClick={() => setActive(id)}
              className={cn(
                "w-full rounded-lg px-3 py-2 flex items-center gap-2 text-left text-xs transition-colors",
                active === id
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <Icon size={14} /> {label}
            </button>
          ))}
        </nav>
      </aside>

      <div className="min-w-0 flex-1 space-y-4 pb-10">
        {active === "general" && (
          <>
            <SettingsCard title="Appearance">
              <label className="block text-xs text-muted-foreground">
                Theme
                <select
                  value={settings.theme}
                  onChange={(event) =>
                    settings.setTheme(event.target.value as "light" | "dark" | "auto")
                  }
                  className="mt-1 block w-full rounded border border-border bg-background px-3 py-2 text-sm text-foreground"
                >
                  <option value="auto">Use system theme</option>
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                </select>
              </label>
              <label className="block text-xs text-muted-foreground">
                Dictation panel position
                <select
                  value={settings.panelStartPosition}
                  onChange={(event) =>
                    settings.setPanelStartPosition(
                      event.target.value as "bottom-right" | "center" | "bottom-left"
                    )
                  }
                  className="mt-1 block w-full rounded border border-border bg-background px-3 py-2 text-sm text-foreground"
                >
                  <option value="bottom-right">Bottom right</option>
                  <option value="center">Center</option>
                  <option value="bottom-left">Bottom left</option>
                </select>
              </label>
            </SettingsCard>
            <SettingsCard title="Startup">
              <ToggleRow
                label="Start minimized"
                checked={settings.startMinimized}
                onChange={settings.setStartMinimized}
              />
              <ToggleRow
                label="Auto-hide floating dictation panel"
                checked={settings.floatingIconAutoHide}
                onChange={settings.setFloatingIconAutoHide}
              />
            </SettingsCard>
          </>
        )}

        {active === "dictation" && (
          <>
            <SettingsCard
              title="Keyboard and capture"
              description="Dictation is always transcribed by local Whisper."
            >
              <label className="block text-xs text-muted-foreground">
                Dictation shortcut
                <Input
                  value={settings.dictationKey}
                  onChange={(event) => settings.setDictationKey(event.target.value)}
                  placeholder="Ctrl+Shift+Space"
                  className="mt-1"
                />
              </label>
              <label className="block text-xs text-muted-foreground">
                Spoken language
                <select
                  value={settings.preferredLanguage}
                  onChange={(event) => settings.setPreferredLanguage(event.target.value)}
                  className="mt-1 block w-full rounded border border-border bg-background px-3 py-2 text-sm text-foreground"
                >
                  <option value="auto">Detect automatically</option>
                  <option value="en">English</option>
                  <option value="ar">Arabic</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                  <option value="it">Italian</option>
                  <option value="pt">Portuguese</option>
                  <option value="zh">Chinese</option>
                  <option value="ja">Japanese</option>
                </select>
              </label>
              <ToggleRow
                label="Paste after transcription"
                checked={settings.autoPasteEnabled}
                onChange={settings.setAutoPasteEnabled}
              />
              <ToggleRow
                label="Keep text in clipboard"
                checked={settings.keepTranscriptionInClipboard}
                onChange={settings.setKeepTranscriptionInClipboard}
              />
              <ToggleRow
                label="Pause media while dictating"
                checked={settings.pauseMediaOnDictation}
                onChange={settings.setPauseMediaOnDictation}
              />
              <ToggleRow
                label="Audio start and stop cues"
                checked={settings.audioCuesEnabled}
                onChange={settings.setAudioCuesEnabled}
              />
              <ToggleRow
                label="Prefer built-in microphone"
                checked={settings.preferBuiltInMic}
                onChange={settings.setPreferBuiltInMic}
              />
            </SettingsCard>
            <SettingsCard
              title="Dictionary and snippets"
              description="Local hints improve proper nouns; snippets expand spoken triggers after transcription."
            >
              <DictionaryView />
            </SettingsCard>
          </>
        )}

        {active === "meetings" && (
          <>
            <SettingsCard
              title="Meeting capture"
              description="Meetings combine microphone and system audio and persist the transcript in a note."
            >
              <label className="block text-xs text-muted-foreground">
                Meeting shortcut
                <Input
                  value={settings.meetingKey}
                  onChange={(event) => settings.setMeetingKey(event.target.value)}
                  placeholder="Ctrl+Shift+M"
                  className="mt-1"
                />
              </label>
              <label className="block text-xs text-muted-foreground">
                Shortcut layout
                <select
                  value={settings.meetingHotkeyLayoutMode}
                  onChange={(event) =>
                    settings.setMeetingHotkeyLayoutMode(
                      event.target.value as "side-panel" | "full-width"
                    )
                  }
                  className="mt-1 block w-full rounded border border-border bg-background px-3 py-2 text-sm text-foreground"
                >
                  <option value="full-width">Full window</option>
                  <option value="side-panel">Side panel</option>
                </select>
              </label>
              <ToggleRow
                label="Detect meeting apps"
                checked={settings.meetingProcessDetection}
                onChange={settings.setMeetingProcessDetection}
              />
              <ToggleRow
                label="Speaker diarization"
                description="Assign local speaker labels to the system-audio transcript."
                checked={settings.speakerDiarizationEnabled}
                onChange={settings.setSpeakerDiarizationEnabled}
              />
              <ToggleRow
                label="Voice activity detection"
                checked={settings.meetingSileroEnabled}
                onChange={settings.setMeetingSileroEnabled}
              />
            </SettingsCard>
            <SettingsCard title="System permissions">
              <div className="flex flex-wrap gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => void window.electronAPI.requestMicrophoneAccess?.()}
                >
                  <Mic size={14} /> Request microphone
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => void window.electronAPI.requestSystemAudioAccess?.()}
                >
                  <Users size={14} /> Request system audio
                </Button>
              </div>
            </SettingsCard>
          </>
        )}

        {active === "models" && (
          <SettingsCard
            title="Bundled local Whisper"
            description="Mnemora never downloads a model at runtime. Import a model pack from disk or place it in the local models folder."
          >
            <div className="flex flex-wrap gap-2">
              <Button onClick={() => void importModelPack()} disabled={modelsBusy}>
                <Database size={14} /> Import model pack
              </Button>
              <Button
                variant="outline"
                onClick={() => void window.electronAPI.openMnemoraModelsFolder?.()}
              >
                <FolderOpen size={14} /> Open models folder
              </Button>
              <Button variant="ghost" onClick={() => void refreshModels()} disabled={modelsBusy}>
                {modelsBusy ? (
                  <Loader2 size={14} className="animate-spin" />
                ) : (
                  <RefreshCw size={14} />
                )}{" "}
                Refresh
              </Button>
            </div>
            {modelMessage && <p className="text-xs text-muted-foreground">{modelMessage}</p>}
            {installedModels.length === 0 && !modelsBusy ? (
              <p className="rounded-lg border border-amber-500/20 bg-amber-500/5 p-3 text-xs text-amber-700 dark:text-amber-300">
                No local model was detected.
              </p>
            ) : (
              <div className="space-y-2">
                {installedModels.map((model) => (
                  <label
                    key={model.model}
                    className="flex items-center gap-3 rounded-lg border border-border/60 p-3 cursor-pointer"
                  >
                    <input
                      type="radio"
                      name="whisper-model"
                      checked={settings.whisperModel === model.model}
                      onChange={() => settings.setWhisperModel(model.model)}
                    />
                    <span className="flex-1 text-sm">Whisper {model.model}</span>
                    <span className="text-xs text-muted-foreground">
                      {model.size_mb ? `${model.size_mb.toFixed(0)} MB` : "Installed"}
                    </span>
                    {settings.whisperModel === model.model && (
                      <CheckCircle2 size={15} className="text-emerald-500" />
                    )}
                  </label>
                ))}
              </div>
            )}
          </SettingsCard>
        )}

        {active === "search" && (
          <SettingsCard
            title="On-device semantic index"
            description="Embeddings and indexes stay in the app data directory."
          >
            <Button onClick={() => void reindex()} disabled={reindexing}>
              {reindexing ? (
                <Loader2 size={14} className="animate-spin" />
              ) : (
                <RefreshCw size={14} />
              )}{" "}
              Rebuild search index
            </Button>
            {reindexProgress && (
              <p className="text-xs text-muted-foreground">
                Indexed {reindexProgress.done} of {reindexProgress.total}
              </p>
            )}
          </SettingsCard>
        )}

        {active === "data" && (
          <>
            <SettingsCard
              title="Local retention"
              description="Retention is opt-in. Turning it off stops future dictation text and audio from being saved."
            >
              <ToggleRow
                label="Save dictation history"
                checked={settings.dataRetentionEnabled}
                onChange={settings.setDataRetentionEnabled}
              />
              <label className="block text-xs text-muted-foreground">
                Keep audio for this many days (0 keeps no audio)
                <Input
                  type="number"
                  min={0}
                  max={3650}
                  value={settings.audioRetentionDays}
                  onChange={(event) => settings.setAudioRetentionDays(Number(event.target.value))}
                  className="mt-1"
                />
              </label>
              <ToggleRow
                label="Keep canceled recordings"
                checked={settings.saveDiscardedTranscriptions}
                onChange={settings.setSaveDiscardedTranscriptions}
              />
              {storage && (
                <p className="text-xs text-muted-foreground">
                  {storage.fileCount} audio files · {(storage.totalBytes / 1024 / 1024).toFixed(1)}{" "}
                  MB
                </p>
              )}
              <Button
                variant="outline"
                onClick={async () => {
                  if (window.confirm("Delete all retained audio?")) {
                    await window.electronAPI.deleteAllAudio();
                    setStorage(await window.electronAPI.getAudioStorageUsage());
                  }
                }}
              >
                <Archive size={14} /> Delete retained audio
              </Button>
            </SettingsCard>
            <SettingsCard
              title="Markdown note mirror"
              description="Optionally mirror notes to a folder on this device."
            >
              <ToggleRow
                label="Mirror notes as Markdown"
                checked={settings.noteFilesEnabled}
                onChange={(enabled) => {
                  settings.setNoteFilesEnabled(enabled);
                  void window.electronAPI.noteFilesSetEnabled?.(
                    enabled,
                    settings.noteFilesPath || undefined
                  );
                }}
              />
              <div className="flex gap-2">
                <Input
                  value={settings.noteFilesPath}
                  readOnly
                  placeholder="Default local notes folder"
                />
                <Button
                  variant="outline"
                  onClick={async () => {
                    const result = await window.electronAPI.noteFilesPickFolder?.();
                    if (!result?.canceled && result?.path) {
                      settings.setNoteFilesPath(result.path);
                      await window.electronAPI.noteFilesSetPath?.(result.path);
                    }
                  }}
                >
                  <FolderOpen size={14} />
                </Button>
              </div>
            </SettingsCard>
          </>
        )}

        {active === "backup" && (
          <SettingsCard
            title="Backup and restore"
            description="Backup archives are local files. Restoring may replace current local data."
          >
            <div className="space-y-3">
              <ToggleRow
                label="Include retained audio when creating or restoring"
                checked={backupAudio}
                onChange={setBackupAudio}
              />
              <div className="grid grid-cols-2 gap-2">
                <Button
                  variant="outline"
                  disabled={backupBusy}
                  onClick={() => void runBackupAction("create")}
                >
                  {backupBusy ? (
                    <Loader2 size={14} className="animate-spin" />
                  ) : (
                    <Archive size={14} />
                  )}{" "}
                  Export verified backup
                </Button>
                <Button
                  variant="outline"
                  disabled={backupBusy}
                  onClick={() => void runBackupAction("restore")}
                >
                  <RefreshCw size={14} /> Import and restore
                </Button>
              </div>
            </div>
            {backupMessage && <p className="text-xs text-muted-foreground">{backupMessage}</p>}
          </SettingsCard>
        )}

        {active === "privacy" && (
          <>
            <SettingsCard
              title="Offline by design"
              description="Mnemora does not send audio, transcripts, notes, searches, or model prompts to a remote service."
            >
              <div className="rounded-lg border border-emerald-500/20 bg-emerald-500/5 p-3 text-xs leading-relaxed text-emerald-700 dark:text-emerald-300">
                Local Whisper performs transcription. The semantic index and speaker diarization are
                also on-device.
              </div>
            </SettingsCard>
            <SettingsCard
              title="System access"
              description="These permissions enable microphone capture, paste, and meeting system audio."
            >
              <div className="flex flex-wrap gap-2">
                <Button
                  variant="outline"
                  onClick={() => void window.electronAPI.openMicrophoneSettings?.()}
                >
                  Microphone settings
                </Button>
                <Button
                  variant="outline"
                  onClick={() => void window.electronAPI.openAccessibilitySettings?.()}
                >
                  Accessibility settings
                </Button>
                <Button
                  variant="outline"
                  onClick={() => void window.electronAPI.openSystemAudioSettings?.()}
                >
                  System audio settings
                </Button>
              </div>
            </SettingsCard>
          </>
        )}

        {active === "about" && (
          <SettingsCard
            title="Mnemora"
            description="A private, offline dictation and meeting-memory app."
          >
            <p className="text-sm">Version {appVersion || "…"}</p>
            <p className="text-xs leading-relaxed text-muted-foreground">
              All core workflows are designed to work without an account or network connection.
            </p>
            <Button variant="outline" onClick={() => void window.electronAPI.openLogsFolder?.()}>
              <Keyboard size={14} /> Open diagnostic logs
            </Button>
          </SettingsCard>
        )}
      </div>
    </div>
  );
}
