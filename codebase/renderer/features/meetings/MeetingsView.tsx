import { useCallback, useEffect, useState } from "react";
import { CalendarDays, Loader2, Plus, RefreshCw } from "lucide-react";
import type { NoteItem } from "../../shared/types/electron";
import { Button } from "../../shared/ui/button";

interface Props {
  onOpenNote: (id: number, folderId: number | null) => void;
}

const formatDate = (value: string) =>
  new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(
    new Date(value)
  );

export default function MeetingsView({ onOpenNote }: Props) {
  const [meetings, setMeetings] = useState<NoteItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const notes = await window.electronAPI.getNotes("meeting", 200);
      setMeetings(notes.filter((note) => note.note_type === "meeting"));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
    const unsubscribeAdded = window.electronAPI.onNoteAdded?.(() => void load());
    const unsubscribeUpdated = window.electronAPI.onNoteUpdated?.(() => void load());
    const unsubscribeDeleted = window.electronAPI.onNoteDeleted?.(() => void load());
    return () => {
      unsubscribeAdded?.();
      unsubscribeUpdated?.();
      unsubscribeDeleted?.();
    };
  }, [load]);

  const createMeeting = async () => {
    setCreating(true);
    try {
      const title = `Meeting ${new Intl.DateTimeFormat(undefined, {
        dateStyle: "medium",
        timeStyle: "short",
      }).format(new Date())}`;
      const result = await window.electronAPI.saveNote(title, "", "meeting");
      if (result.success && result.note) onOpenNote(result.note.id, result.note.folder_id);
    } finally {
      setCreating(false);
    }
  };

  return (
    <section className="max-w-4xl mx-auto p-6">
      <header className="flex items-start justify-between gap-4 mb-6">
        <div>
          <h1 className="text-xl font-semibold">Meetings</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Capture system audio and microphone audio into a persistent meeting note.
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => void load()} aria-label="Refresh">
            <RefreshCw size={14} />
          </Button>
          <Button size="sm" onClick={() => void createMeeting()} disabled={creating}>
            {creating ? <Loader2 size={14} className="animate-spin" /> : <Plus size={14} />}
            New meeting
          </Button>
        </div>
      </header>

      {loading ? (
        <div className="py-20 flex justify-center">
          <Loader2 className="animate-spin text-muted-foreground" />
        </div>
      ) : meetings.length === 0 ? (
        <div className="rounded-xl border border-dashed border-border p-12 text-center">
          <CalendarDays className="mx-auto text-muted-foreground/60" size={30} />
          <h2 className="mt-3 text-sm font-medium">No meeting notes yet</h2>
          <p className="mt-1 text-xs text-muted-foreground">
            Create one, then start recording from its transcript panel.
          </p>
        </div>
      ) : (
        <div className="grid gap-2">
          {meetings.map((meeting) => (
            <button
              key={meeting.id}
              type="button"
              onClick={() => onOpenNote(meeting.id, meeting.folder_id)}
              className="rounded-xl border border-border/60 bg-card px-4 py-3 text-left hover:border-primary/30 hover:bg-primary/[0.02] transition-colors"
            >
              <div className="flex items-center justify-between gap-4">
                <span className="text-sm font-medium truncate">
                  {meeting.title || "Untitled meeting"}
                </span>
                <span className="text-[11px] text-muted-foreground shrink-0">
                  {formatDate(meeting.updated_at)}
                </span>
              </div>
              <p className="mt-1 text-xs text-muted-foreground line-clamp-2">
                {meeting.transcript || meeting.content || "No transcript yet"}
              </p>
            </button>
          ))}
        </div>
      )}
    </section>
  );
}
