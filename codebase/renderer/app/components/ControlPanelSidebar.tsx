import type React from "react";
import { FileAudio, Home, NotebookPen, Search, Settings, Users } from "lucide-react";
import logoIcon from "../../assets/icon.png";
import { cn } from "../../shared/ui/utils";

export type ControlPanelView = "home" | "meetings" | "notes" | "search" | "import" | "settings";

interface Props {
  activeView: ControlPanelView;
  onViewChange: (view: ControlPanelView) => void;
}

const items: Array<{
  id: ControlPanelView;
  label: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
}> = [
  { id: "home", label: "Home", icon: Home },
  { id: "meetings", label: "Meetings", icon: Users },
  { id: "notes", label: "Notes", icon: NotebookPen },
  { id: "search", label: "Search", icon: Search },
  { id: "import", label: "Import", icon: FileAudio },
  { id: "settings", label: "Settings", icon: Settings },
];

export default function ControlPanelSidebar({ activeView, onViewChange }: Props) {
  return (
    <aside className="w-52 h-full shrink-0 border-r border-border/40 bg-surface-1/70 flex flex-col">
      <div className="h-11 shrink-0" style={{ WebkitAppRegion: "drag" } as React.CSSProperties} />
      <div className="px-4 pb-4 flex items-center gap-2.5">
        <img src={logoIcon} alt="" className="w-7 h-7 rounded-lg" />
        <div>
          <p className="text-sm font-semibold leading-tight">Mnemora</p>
          <p className="text-[10px] text-muted-foreground">Private, on-device memory</p>
        </div>
      </div>
      <nav className="px-2 space-y-0.5">
        {items.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            type="button"
            onClick={() => onViewChange(id)}
            className={cn(
              "w-full h-9 px-3 rounded-lg flex items-center gap-2.5 text-left outline-none transition-colors",
              "focus-visible:ring-2 focus-visible:ring-primary/30",
              activeView === id
                ? "bg-primary/10 text-primary"
                : "text-foreground/70 hover:bg-foreground/5 hover:text-foreground"
            )}
          >
            <Icon size={16} />
            <span className="text-xs font-medium">{label}</span>
          </button>
        ))}
      </nav>
      <div className="flex-1" />
      <div className="m-3 rounded-lg border border-emerald-500/20 bg-emerald-500/5 px-3 py-2.5">
        <div className="flex items-center gap-2 text-[11px] font-medium text-emerald-700 dark:text-emerald-300">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
          Local only
        </div>
        <p className="mt-1 text-[10px] leading-relaxed text-muted-foreground">
          Audio and text stay on this device.
        </p>
      </div>
    </aside>
  );
}
