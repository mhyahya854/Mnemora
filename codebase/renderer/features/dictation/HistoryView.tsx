import { useCallback, useEffect, useState } from "react";
import {
  Archive,
  Clipboard,
  FolderOpen,
  Loader2,
  Mic,
  RefreshCw,
  RotateCcw,
  Trash2,
} from "lucide-react";
import type { TranscriptionItem } from "../../shared/types/electron";
import { useHotkey } from "./useHotkey";
import { useSettingsStore } from "../settings/settingsStore";
import {
  clearTranscriptions,
  initializeTranscriptions,
  removeTranscription,
  updateTranscription,
  useShowDiscarded,
  useTranscriptions,
} from "../transcription/transcriptionStore";
import { Button } from "../../shared/ui/button";

interface Props {
  onOpenSettings: (section?: string) => void;
}

const formatWhen = (item: TranscriptionItem) => {
  const raw = item.timestamp || item.created_at;
  const date = new Date(raw.endsWith("Z") ? raw : `${raw}Z`);
  return Number.isNaN(date.getTime())
    ? ""
    : new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(date);
};

export default function HistoryView({ onOpenSettings }: Props) {
  const history = useTranscriptions();
  const showDiscarded = useShowDiscarded();
  const dataRetentionEnabled = useSettingsStore((state) => state.dataRetentionEnabled);
  const { hotkey } = useHotkey();
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<number | null>(null);

  const load = useCallback(
    async (includeDiscarded = showDiscarded) => {
      setLoading(true);
      try {
        await initializeTranscriptions(100, includeDiscarded);
      } finally {
        setLoading(false);
      }
    },
    [showDiscarded]
  );

  useEffect(() => {
    void load();
  }, [load]);

  const retry = async (item: TranscriptionItem) => {
    setBusyId(item.id);
    try {
      const settings = useSettingsStore.getState();
      const result = await (
        window.electronAPI.retryTranscription as unknown as (
          id: number,
          options: Record<string, unknown>
        ) => Promise<{ success: boolean; transcription?: TranscriptionItem }>
      )(item.id, {
        useLocalWhisper: true,
        localTranscriptionProvider: "whisper",
        whisperModel: settings.whisperModel || "base",
        preferredLanguage: settings.preferredLanguage,
      });
      if (result.success && result.transcription) updateTranscription(result.transcription);
    } finally {
      setBusyId(null);
    }
  };

  const remove = async (id: number) => {
    if (!window.confirm("Delete this dictation and its saved audio?")) return;
    const result = await window.electronAPI.deleteTranscription(id);
    if (result.success) removeTranscription(id);
  };

  const clear = async () => {
    if (!window.confirm("Delete all saved dictations and their audio?")) return;
    const result = await window.electronAPI.clearTranscriptions();
    if (result.success) clearTranscriptions();
  };

  return (
    <section className="max-w-4xl mx-auto p-6">
      <header className="flex items-start justify-between gap-4 mb-5">
        <div>
          <h1 className="text-xl font-semibold">Home</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Press <kbd className="rounded border bg-muted px-1.5 py-0.5 text-xs">{hotkey}</kbd> to
            dictate anywhere.
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => void load(!showDiscarded)}
            title={showDiscarded ? "Hide discarded recordings" : "Show discarded recordings"}
          >
            <Archive size={14} /> {showDiscarded ? "Hide discarded" : "Discarded"}
          </Button>
          {history.length > 0 && (
            <Button variant="outline" size="sm" onClick={() => void clear()}>
              <Trash2 size={14} /> Clear all
            </Button>
          )}
        </div>
      </header>

      {!dataRetentionEnabled && (
        <button
          type="button"
          onClick={() => onOpenSettings("data")}
          className="w-full mb-4 rounded-lg border border-amber-500/25 bg-amber-500/5 px-4 py-3 text-left text-xs text-amber-700 dark:text-amber-300"
        >
          History is off. Dictation still works, but text and audio are not retained. Open Data
          settings to opt in.
        </button>
      )}

      {loading && history.length === 0 ? (
        <div className="py-20 flex justify-center">
          <Loader2 className="animate-spin text-muted-foreground" />
        </div>
      ) : history.length === 0 ? (
        <div className="rounded-xl border border-dashed border-border p-14 text-center">
          <Mic className="mx-auto text-muted-foreground/50" size={32} />
          <h2 className="mt-3 text-sm font-medium">Your dictation history is empty</h2>
          <p className="mt-1 text-xs text-muted-foreground">
            New entries appear here when local retention is enabled.
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {history.map((item) => (
            <article key={item.id} className="rounded-xl border border-border/60 bg-card p-4">
              <div className="flex gap-4">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
                    <span>{formatWhen(item)}</span>
                    {item.status !== "completed" && (
                      <span className="rounded-full bg-muted px-2 py-0.5 capitalize">
                        {item.status}
                      </span>
                    )}
                    {item.model && <span className="ml-auto">Whisper {item.model}</span>}
                  </div>
                  <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">
                    {item.text || item.error_message || "Saved recording without text"}
                  </p>
                </div>
                <div className="flex shrink-0 items-start gap-1">
                  {!!item.text && (
                    <Button
                      variant="ghost"
                      size="icon"
                      title="Copy"
                      onClick={() => void navigator.clipboard.writeText(item.text)}
                    >
                      <Clipboard size={14} />
                    </Button>
                  )}
                  {item.has_audio === 1 && (
                    <>
                      <Button
                        variant="ghost"
                        size="icon"
                        title="Show audio"
                        onClick={() => void window.electronAPI.showAudioInFolder(item.id)}
                      >
                        <FolderOpen size={14} />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        title="Transcribe again"
                        disabled={busyId === item.id}
                        onClick={() => void retry(item)}
                      >
                        {busyId === item.id ? (
                          <Loader2 size={14} className="animate-spin" />
                        ) : (
                          <RotateCcw size={14} />
                        )}
                      </Button>
                    </>
                  )}
                  <Button
                    variant="ghost"
                    size="icon"
                    title="Delete"
                    onClick={() => void remove(item.id)}
                  >
                    <Trash2 size={14} />
                  </Button>
                </div>
              </div>
            </article>
          ))}
          <div className="flex justify-center pt-3">
            <Button variant="ghost" size="sm" onClick={() => void load()}>
              <RefreshCw size={14} /> Refresh
            </Button>
          </div>
        </div>
      )}
    </section>
  );
}
