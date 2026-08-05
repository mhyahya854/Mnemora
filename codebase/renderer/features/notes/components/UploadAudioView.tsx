import { useEffect, useRef, useState } from "react";
import {
  CheckCircle2,
  FileAudio,
  FileVideo,
  FolderOpen,
  Loader2,
  RefreshCw,
  Upload,
  X,
} from "lucide-react";
import type { FolderItem } from "../../../shared/types/electron";
import { useSettings } from "../../settings/useSettings";
import { getBaseLanguageCode } from "../../transcription/languageSupport";
import { Button } from "../../../shared/ui/button";
import { cn } from "../../../shared/ui/utils";

type State = "idle" | "selected" | "transcribing" | "complete" | "error";

interface Props {
  onNoteCreated?: (noteId: number, folderId: number | null) => void;
  onOpenSettings?: (section: string) => void;
}

interface SelectedFile {
  name: string;
  path: string;
  sizeBytes: number;
  kind: "audio" | "video";
}

interface ImportBridge {
  cancelMediaImport?: () => Promise<unknown>;
  cancelAudioTranscription?: () => Promise<unknown>;
}

const supportedExtensions = new Set([
  "mp3",
  "wav",
  "m4a",
  "webm",
  "ogg",
  "oga",
  "flac",
  "aac",
  "mp4",
  "mov",
  "mkv",
  "avi",
  "mpeg",
  "mpg",
]);
const videoExtensions = new Set(["mp4", "mov", "mkv", "avi", "mpeg", "mpg"]);

const formatSize = (bytes: number) => {
  if (!bytes) return "";
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
};

const fileFromPath = async (path: string): Promise<SelectedFile> => {
  const name = path.split(/[/\\]/).pop() || "media";
  const extension = name.split(".").pop()?.toLowerCase() || "";
  return {
    name,
    path,
    sizeBytes: (await window.electronAPI.getFileSize?.(path)) ?? 0,
    kind: videoExtensions.has(extension) ? "video" : "audio",
  };
};

export default function UploadAudioView({ onNoteCreated, onOpenSettings }: Props) {
  const settings = useSettings();
  const inputRef = useRef<HTMLInputElement>(null);
  const runRef = useRef(0);
  const [state, setState] = useState<State>("idle");
  const [file, setFile] = useState<SelectedFile | null>(null);
  const [folders, setFolders] = useState<FolderItem[]>([]);
  const [folderId, setFolderId] = useState<number | null>(null);
  const [noteId, setNoteId] = useState<number | null>(null);
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState("");
  const [dragging, setDragging] = useState(false);
  const [modelAvailable, setModelAvailable] = useState<boolean | null>(null);

  useEffect(() => {
    void window.electronAPI.getFolders().then((items) => {
      setFolders(items);
      setFolderId(items.find((folder) => folder.is_default)?.id ?? items[0]?.id ?? null);
    });
    void window.electronAPI.listWhisperModels().then((result) => {
      setModelAvailable(result.success && result.models.some((model) => model.installed));
    });
  }, []);

  const choosePath = async (path: string) => {
    const selected = await fileFromPath(path);
    const extension = selected.name.split(".").pop()?.toLowerCase() || "";
    if (!supportedExtensions.has(extension)) {
      setError("Choose a supported audio or video file.");
      setState("error");
      return;
    }
    setFile(selected);
    setState("selected");
    setError("");
    setTranscript("");
    setNoteId(null);
  };

  const browse = async () => {
    const result = await window.electronAPI.selectAudioFile();
    if (!result.canceled && result.filePath) await choosePath(result.filePath);
  };

  const acceptBrowserFile = async (browserFile: File) => {
    const path = window.electronAPI.getPathForFile(browserFile);
    if (!path) return;
    await choosePath(path);
  };

  const transcribe = async () => {
    if (!file || modelAvailable === false) return;
    const run = ++runRef.current;
    setState("transcribing");
    setError("");
    try {
      const result = await window.electronAPI.transcribeAudioFile(file.path, {
        provider: "whisper",
        model: settings.whisperModel || "base",
        language: getBaseLanguageCode(settings.preferredLanguage) || undefined,
      });
      if (run !== runRef.current) return;
      const text = result.text?.trim();
      if (!result.success || !text) throw new Error(result.error || "No speech was detected.");

      const title = file.name.replace(/\.[^.]+$/, "") || "Imported transcript";
      const saved = await window.electronAPI.saveNote(
        title,
        text,
        "upload",
        file.path,
        null,
        folderId
      );
      if (run !== runRef.current) return;
      if (!saved.success || !saved.note) throw new Error("The transcript could not be saved.");
      setTranscript(text);
      setNoteId(saved.note.id);
      setState("complete");
    } catch (reason) {
      if (run !== runRef.current) return;
      setError(reason instanceof Error ? reason.message : String(reason));
      setState("error");
    }
  };

  const cancel = async () => {
    runRef.current += 1;
    const bridge = window.electronAPI as unknown as ImportBridge;
    await (bridge.cancelMediaImport?.() ??
      bridge.cancelAudioTranscription?.() ??
      Promise.resolve());
    setState(file ? "selected" : "idle");
  };

  const reset = () => {
    runRef.current += 1;
    setFile(null);
    setTranscript("");
    setNoteId(null);
    setError("");
    setState("idle");
    if (inputRef.current) inputRef.current.value = "";
  };

  return (
    <section className="max-w-3xl mx-auto p-6">
      <h1 className="text-xl font-semibold">Import</h1>
      <p className="mt-1 text-sm text-muted-foreground">
        Transcribe an audio or video file with local Whisper and save it as a note.
      </p>

      {modelAvailable === false && (
        <button
          type="button"
          onClick={() => onOpenSettings?.("models")}
          className="mt-5 w-full rounded-xl border border-amber-500/25 bg-amber-500/5 p-4 text-left text-sm text-amber-700 dark:text-amber-300"
        >
          A local Whisper model is required. Open Models settings to import one from disk.
        </button>
      )}

      {!file ? (
        <div
          onDragOver={(event) => {
            event.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(event) => {
            event.preventDefault();
            setDragging(false);
            const dropped = event.dataTransfer.files[0];
            if (dropped) void acceptBrowserFile(dropped);
          }}
          className={cn(
            "mt-6 rounded-2xl border-2 border-dashed p-14 text-center transition-colors",
            dragging ? "border-primary bg-primary/5" : "border-border hover:border-primary/30"
          )}
        >
          <Upload className="mx-auto text-primary" size={30} />
          <h2 className="mt-4 text-sm font-medium">Drop audio or video here</h2>
          <p className="mt-1 text-xs text-muted-foreground">
            MP3, WAV, M4A, WebM, OGG, FLAC, AAC, MP4, MOV, MKV, AVI, MPEG
          </p>
          <div className="mt-5 flex justify-center gap-2">
            <Button onClick={() => inputRef.current?.click()}>
              <FolderOpen size={14} /> Choose file
            </Button>
            <Button variant="outline" onClick={() => void browse()}>
              System picker
            </Button>
          </div>
          <input
            ref={inputRef}
            hidden
            type="file"
            accept="audio/*,video/*,.mkv"
            onChange={(event) => {
              const selected = event.target.files?.[0];
              if (selected) void acceptBrowserFile(selected);
            }}
          />
        </div>
      ) : (
        <div className="mt-6 rounded-2xl border border-border/60 bg-card p-5">
          <div className="flex items-start gap-4">
            <div className="w-11 h-11 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
              {file.kind === "video" ? <FileVideo size={21} /> : <FileAudio size={21} />}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium truncate">{file.name}</p>
              <p className="mt-1 text-xs text-muted-foreground">
                {formatSize(file.sizeBytes)} · Whisper {settings.whisperModel || "base"} · on device
              </p>
            </div>
            {state !== "transcribing" && (
              <Button variant="ghost" size="icon" onClick={reset}>
                <X size={15} />
              </Button>
            )}
          </div>

          <label className="mt-5 block text-xs text-muted-foreground">
            Save in folder
            <select
              value={folderId ?? ""}
              onChange={(event) =>
                setFolderId(event.target.value ? Number(event.target.value) : null)
              }
              className="mt-1 block w-full rounded border border-border bg-background px-3 py-2 text-sm text-foreground"
            >
              <option value="">No folder</option>
              {folders.map((folder) => (
                <option key={folder.id} value={folder.id}>
                  {folder.name}
                </option>
              ))}
            </select>
          </label>

          {state === "transcribing" && (
            <div className="mt-5 rounded-xl bg-muted/50 p-5 text-center">
              <Loader2 className="mx-auto animate-spin text-primary" size={22} />
              <p className="mt-3 text-sm font-medium">Transcribing locally…</p>
              <p className="mt-1 text-xs text-muted-foreground">
                Long media can take several minutes.
              </p>
              <Button className="mt-4" variant="outline" size="sm" onClick={() => void cancel()}>
                Cancel
              </Button>
            </div>
          )}

          {state === "error" && (
            <div className="mt-5 rounded-xl border border-destructive/20 bg-destructive/5 p-4">
              <p className="text-sm text-destructive">{error}</p>
              <Button
                className="mt-3"
                variant="outline"
                size="sm"
                onClick={() => void transcribe()}
              >
                <RefreshCw size={14} /> Try again
              </Button>
            </div>
          )}

          {state === "complete" && (
            <div className="mt-5 rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4">
              <div className="flex items-center gap-2 text-sm font-medium text-emerald-700 dark:text-emerald-300">
                <CheckCircle2 size={16} /> Saved as a local note
              </div>
              <p className="mt-3 max-h-40 overflow-y-auto whitespace-pre-wrap text-xs leading-relaxed text-foreground/80">
                {transcript}
              </p>
              {noteId != null && (
                <Button
                  className="mt-4"
                  size="sm"
                  onClick={() => onNoteCreated?.(noteId, folderId)}
                >
                  Open note
                </Button>
              )}
            </div>
          )}

          {(state === "selected" || state === "idle") && (
            <div className="mt-5 flex justify-end">
              <Button onClick={() => void transcribe()} disabled={modelAvailable === false}>
                <FileAudio size={14} /> Transcribe locally
              </Button>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
