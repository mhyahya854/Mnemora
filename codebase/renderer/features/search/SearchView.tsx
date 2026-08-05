import { useCallback, useMemo, useState } from "react";
import { FileAudio, Loader2, NotebookPen, Search, Sparkles, Users } from "lucide-react";
import type { NoteItem, TranscriptionItem } from "../../shared/types/electron";
import { Button } from "../../shared/ui/button";
import { Input } from "../../shared/ui/input";
import { cn } from "../../shared/ui/utils";

type Filter = "all" | "notes" | "meetings" | "imports" | "dictations";
type Result =
  | { kind: "note"; note: NoteItem; semantic: boolean }
  | { kind: "dictation"; transcription: TranscriptionItem };

interface Props {
  onOpenNote: (id: number, folderId: number | null) => void;
  onOpenDictation?: (id: number) => void;
}

const filters: Array<{ id: Filter; label: string }> = [
  { id: "all", label: "All" },
  { id: "notes", label: "Notes" },
  { id: "meetings", label: "Meetings" },
  { id: "imports", label: "Imports" },
  { id: "dictations", label: "Dictations" },
];

export default function SearchView({ onOpenNote, onOpenDictation }: Props) {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<Filter>("all");
  const [results, setResults] = useState<Result[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const runSearch = useCallback(async () => {
    const value = query.trim();
    if (!value) {
      setResults([]);
      setSearched(false);
      return;
    }
    setLoading(true);
    setSearched(true);
    try {
      const api = window.electronAPI;
      const [exact, semantic, dictations] = await Promise.all([
        api.searchNotes(value, 100),
        api.semanticSearchNotes
          ? api.semanticSearchNotes(value, 100).catch(() => [] as NoteItem[])
          : Promise.resolve([] as NoteItem[]),
        api.getTranscriptions(500).catch(() => [] as TranscriptionItem[]),
      ]);
      const exactIds = new Set(exact.map((note) => note.id));
      const noteResults: Result[] = [
        ...exact.map((note) => ({ kind: "note" as const, note, semantic: false })),
        ...semantic
          .filter((note) => !exactIds.has(note.id))
          .map((note) => ({ kind: "note" as const, note, semantic: true })),
      ];
      const needle = value.toLocaleLowerCase();
      const transcriptionResults: Result[] = dictations
        .filter((item) => item.text?.toLocaleLowerCase().includes(needle))
        .map((transcription) => ({ kind: "dictation" as const, transcription }));
      setResults([...noteResults, ...transcriptionResults]);
    } finally {
      setLoading(false);
    }
  }, [query]);

  const visible = useMemo(
    () =>
      results.filter((result) => {
        if (filter === "all") return true;
        if (result.kind === "dictation") return filter === "dictations";
        if (filter === "notes") return result.note.note_type === "personal";
        if (filter === "meetings") return result.note.note_type === "meeting";
        return result.note.note_type === "upload";
      }),
    [filter, results]
  );

  return (
    <section className="max-w-4xl mx-auto p-6">
      <h1 className="text-xl font-semibold">Search</h1>
      <p className="text-sm text-muted-foreground mt-1">
        Search exact text and the on-device semantic index together.
      </p>
      <form
        className="mt-5 flex gap-2"
        onSubmit={(event) => {
          event.preventDefault();
          void runSearch();
        }}
      >
        <div className="relative flex-1">
          <Search
            size={16}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
          />
          <Input
            autoFocus
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search notes, meetings, imports, and dictations"
            className="pl-9"
          />
        </div>
        <Button type="submit" disabled={loading || !query.trim()}>
          {loading ? <Loader2 size={15} className="animate-spin" /> : "Search"}
        </Button>
      </form>
      <div className="mt-3 flex flex-wrap gap-1.5">
        {filters.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => setFilter(item.id)}
            className={cn(
              "rounded-full border px-3 py-1 text-[11px] transition-colors",
              filter === item.id
                ? "border-primary/30 bg-primary/10 text-primary"
                : "border-border text-muted-foreground hover:text-foreground"
            )}
          >
            {item.label}
          </button>
        ))}
      </div>

      <div className="mt-6 space-y-2">
        {!loading && searched && visible.length === 0 && (
          <div className="rounded-xl border border-dashed p-10 text-center text-sm text-muted-foreground">
            No local results found.
          </div>
        )}
        {visible.map((result) => {
          if (result.kind === "dictation") {
            return (
              <button
                key={`dictation-${result.transcription.id}`}
                type="button"
                onClick={() => onOpenDictation?.(result.transcription.id)}
                className="w-full rounded-xl border border-border/60 bg-card p-4 text-left hover:border-primary/30 transition-colors"
              >
                <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
                  <FileAudio size={13} /> Dictation
                </div>
                <p className="mt-2 text-sm line-clamp-3">{result.transcription.text}</p>
              </button>
            );
          }
          const Icon = result.note.note_type === "meeting" ? Users : NotebookPen;
          return (
            <button
              key={`note-${result.note.id}`}
              type="button"
              onClick={() => onOpenNote(result.note.id, result.note.folder_id)}
              className="w-full rounded-xl border border-border/60 bg-card p-4 text-left hover:border-primary/30 transition-colors"
            >
              <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
                <Icon size={13} />
                {result.note.note_type === "meeting"
                  ? "Meeting"
                  : result.note.note_type === "upload"
                    ? "Import"
                    : "Note"}
                {result.semantic && (
                  <span className="ml-auto inline-flex items-center gap-1 text-primary">
                    <Sparkles size={12} /> Semantic match
                  </span>
                )}
              </div>
              <h2 className="mt-2 text-sm font-medium">{result.note.title || "Untitled"}</h2>
              <p className="mt-1 text-xs text-muted-foreground line-clamp-3">
                {result.note.transcript || result.note.content || "Empty note"}
              </p>
            </button>
          );
        })}
      </div>
    </section>
  );
}
