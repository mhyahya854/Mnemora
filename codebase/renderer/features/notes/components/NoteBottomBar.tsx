import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Mic, Square, Loader2 } from "lucide-react";
import { cn } from "../../../shared/ui/utils";
import { formatMmSs } from "../../../shared/utilities/formatDuration";

const BAR_COUNT = 5;

interface NoteBottomBarProps {
  isRecording: boolean;
  isProcessing: boolean;
  onStartRecording: () => void;
  onStopRecording: () => void;
}

export default function NoteBottomBar({
  isRecording,
  isProcessing,
  onStartRecording,
  onStopRecording,
}: NoteBottomBarProps) {
  const { t } = useTranslation();
  const [elapsed, setElapsed] = useState(0);
  const [wasRecording, setWasRecording] = useState(isRecording);

  if (isRecording !== wasRecording) {
    setWasRecording(isRecording);
    if (!isRecording) setElapsed(0);
  }

  useEffect(() => {
    if (!isRecording) return;
    const id = setInterval(() => setElapsed((s) => s + 1), 1000);
    return () => clearInterval(id);
  }, [isRecording]);

  const elapsedLabel = formatMmSs(elapsed);

  return (
    <div className="absolute bottom-0 left-0 right-0 z-10 px-5 pb-4 pt-3 flex justify-center pointer-events-none bg-background">
      <div className="flex items-center pointer-events-auto">
        {isRecording ? (
          <button
            onClick={onStopRecording}
            className={cn(
              "flex items-center gap-2 h-10 pl-3.5 pr-3 rounded-xl",
              "bg-primary/6 dark:bg-primary/10",
              "border border-primary/20 dark:border-primary/25",
              "transition-colors duration-150",
              "hover:bg-primary/10 dark:hover:bg-primary/15"
            )}
          >
            <div className="flex items-end gap-0.5 h-3.5">
              {Array.from({ length: BAR_COUNT }, (_, i) => (
                <div
                  key={i}
                  className="w-0.5 rounded-full bg-primary/60 dark:bg-primary/70 origin-bottom"
                  style={{
                    height: "100%",
                    animation: `waveform-bar ${0.5 + i * 0.07}s ease-in-out infinite`,
                    animationDelay: `${i * 0.04}s`,
                  }}
                />
              ))}
            </div>
            <span className="text-[11px] font-medium tabular-nums text-primary/60 dark:text-primary/70">
              {elapsedLabel}
            </span>
            <Square size={9} fill="currentColor" className="text-primary/50" />
          </button>
        ) : isProcessing ? (
          <div
            className={cn(
              "flex items-center justify-center w-10 h-10 rounded-xl",
              "bg-foreground/3 dark:bg-white/4",
              "border border-border/20 dark:border-white/6"
            )}
          >
            <Loader2 size={14} className="animate-spin text-foreground/25" />
          </div>
        ) : (
          <button
            onClick={onStartRecording}
            className={cn(
              "flex items-center justify-center w-10 h-10 rounded-xl",
              "bg-foreground/3 dark:bg-white/4",
              "border border-border/20 dark:border-white/6",
              "text-foreground/30 dark:text-foreground/20",
              "transition-all duration-200",
              "hover:bg-foreground/6 dark:hover:bg-white/8",
              "hover:text-foreground/50 dark:hover:text-foreground/35",
              "hover:border-border/30 dark:hover:border-white/10",
              "active:scale-95"
            )}
            aria-label={t("notes.editor.transcribe")}
          >
            <Mic size={15} />
          </button>
        )}
      </div>
    </div>
  );
}
