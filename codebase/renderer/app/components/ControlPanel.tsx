import React, { Suspense, useCallback, useEffect, useState } from "react";
import { ChevronLeft } from "lucide-react";
import ControlPanelSidebar, { type ControlPanelView } from "./ControlPanelSidebar";
import HistoryView from "../../features/dictation/HistoryView";
import MeetingsView from "../../features/meetings/MeetingsView";
import SearchView from "../../features/search/SearchView";
import MeetingRecordingMount from "../../features/meetings/MeetingRecordingMount";
import MeetingRecordingPill from "../../features/notes/components/MeetingRecordingPill";
import PostMigrationOnboarding from "../../features/onboarding/PostMigrationOnboarding";
import WindowControls from "./WindowControls";
import { Button } from "../../shared/ui/button";
import { useToast } from "../../shared/ui/useToast";
import { getCachedPlatform } from "../../shared/utilities/platform";
import { isAccessibilitySkipped } from "../../shared/utilities/permissions";
import {
  setActiveFolderId,
  setActiveNoteId,
  useActiveNoteId,
  initializeNotes,
} from "../../features/notes/noteStore";
import {
  useIsMeetingMode,
  useIsNarrowWindow,
  useMeetingRecordingStore,
} from "../../features/meetings/meetingRecordingStore";
import { useSettingsStore } from "../../features/settings/settingsStore";

const PersonalNotesView = React.lazy(
  () => import("../../features/notes/components/PersonalNotesView")
);
const UploadAudioView = React.lazy(() => import("../../features/notes/components/UploadAudioView"));
const SettingsPage = React.lazy(() => import("../../features/settings/SettingsPage"));
const platform = getCachedPlatform();

interface Props {
  initialSettingsSection?: string;
}

export default function ControlPanel({ initialSettingsSection }: Props = {}) {
  const [activeView, setActiveView] = useState<ControlPanelView>(
    initialSettingsSection ? "settings" : "home"
  );
  const [settingsSection, setSettingsSection] = useState(initialSettingsSection);
  const [showPostMigration, setShowPostMigration] = useState(false);
  const [meetingRequest, setMeetingRequest] = useState<{
    noteId: number;
    folderId: number;
    event: unknown;
  } | null>(null);
  const activeNoteId = useActiveNoteId();
  const isMeetingMode = useIsMeetingMode();
  const isNarrowWindow = useIsNarrowWindow();
  const recordingNoteId = useMeetingRecordingStore((state) => state.recordingNoteId);
  const recordingFolderId = useMeetingRecordingStore((state) => state.recordingFolderId);
  const sidePanel =
    isMeetingMode || (isNarrowWindow && activeView === "notes" && activeNoteId != null);
  const { toast } = useToast();

  const openNote = useCallback((id: number, folderId: number | null) => {
    if (folderId != null) {
      setActiveFolderId(folderId);
      void initializeNotes(null, 50, folderId);
    }
    setActiveNoteId(id);
    setActiveView("notes");
  }, []);

  const openSettings = useCallback((section?: string) => {
    setSettingsSection(section);
    setActiveView("settings");
  }, []);

  useEffect(() => {
    const { noteFilesEnabled, noteFilesPath } = useSettingsStore.getState();
    if (noteFilesEnabled) {
      void window.electronAPI?.noteFilesSetEnabled?.(true, noteFilesPath || undefined, {
        skipRebuild: true,
      });
    }
  }, []);

  useEffect(() => {
    if (platform !== "darwin") return;
    void window.electronAPI?.getPostMigrationState?.().then((state) => {
      if (state?.justMigrated) setShowPostMigration(true);
    });
  }, []);

  useEffect(() => {
    const drainMeetingNavigation = async () => {
      const data = await window.electronAPI?.getPendingMeetingNoteNavigation?.();
      if (!data) return;
      openNote(data.noteId, data.folderId);
      setMeetingRequest({ noteId: data.noteId, folderId: data.folderId, event: data.event });
      if (
        data.trigger === "hotkey" &&
        useSettingsStore.getState().meetingHotkeyLayoutMode === "side-panel"
      ) {
        void window.electronAPI?.snapToMeetingMode?.();
      }
    };
    void drainMeetingNavigation();
    const disposePending =
      window.electronAPI?.onMeetingNoteNavigationPending?.(drainMeetingNavigation);
    const disposeNote = window.electronAPI?.onNavigateToNote?.(({ noteId, folderId }) =>
      openNote(noteId, folderId)
    );
    return () => {
      disposePending?.();
      disposeNote?.();
    };
  }, [openNote]);

  useEffect(() => {
    const disposeSettings = window.electronAPI?.onShowSettings?.(() => openSettings());
    const disposeAccessibility = window.electronAPI?.onAccessibilityMissing?.(async () => {
      if (isAccessibilitySkipped()) return;
      const migration = await window.electronAPI?.getPostMigrationState?.();
      if (migration?.justMigrated) return;
      openSettings("privacy");
      toast({
        title: "Accessibility permission needed",
        description: "Enable accessibility access to paste dictation into other apps.",
        duration: 10000,
      });
    });
    return () => {
      disposeSettings?.();
      disposeAccessibility?.();
    };
  }, [openSettings, toast]);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      const modifier = platform === "darwin" ? event.metaKey : event.ctrlKey;
      if (modifier && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setActiveView("search");
      } else if (modifier && event.key === ",") {
        event.preventDefault();
        openSettings();
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [openSettings]);

  return (
    <div className="h-screen bg-background flex flex-col">
      <MeetingRecordingMount />
      <MeetingRecordingPill
        activeView={activeView}
        activeNoteId={activeNoteId}
        onReturnToNote={() => {
          if (recordingFolderId != null) setActiveFolderId(recordingFolderId);
          if (recordingNoteId != null) setActiveNoteId(recordingNoteId);
          setActiveView("notes");
        }}
      />
      <PostMigrationOnboarding
        open={showPostMigration}
        onOpenChange={setShowPostMigration}
        onDone={async () => {
          await window.electronAPI?.markBundleMigrated?.();
          setShowPostMigration(false);
        }}
      />
      <div className="flex flex-1 overflow-hidden">
        <div
          className="shrink-0 overflow-hidden transition-[width] duration-200"
          style={{ width: sidePanel ? 0 : undefined }}
        >
          <ControlPanelSidebar activeView={activeView} onViewChange={setActiveView} />
        </div>
        <main className="flex-1 min-w-0 flex flex-col overflow-hidden">
          <div
            className="h-10 shrink-0 flex items-center"
            style={{ WebkitAppRegion: "drag" } as React.CSSProperties}
          >
            {sidePanel && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => void window.electronAPI?.restoreFromMeetingMode?.()}
                className={platform === "darwin" ? "ml-20" : "ml-2"}
                style={{ WebkitAppRegion: "no-drag" } as React.CSSProperties}
              >
                <ChevronLeft size={14} /> Back
              </Button>
            )}
            <div className="flex-1" />
            {platform !== "darwin" && (
              <div style={{ WebkitAppRegion: "no-drag" } as React.CSSProperties}>
                <WindowControls />
              </div>
            )}
          </div>
          <div className="flex-1 overflow-y-auto">
            {activeView === "home" && <HistoryView onOpenSettings={openSettings} />}
            {activeView === "meetings" && <MeetingsView onOpenNote={openNote} />}
            {activeView === "search" && (
              <SearchView onOpenNote={openNote} onOpenDictation={() => setActiveView("home")} />
            )}
            {activeView === "notes" && (
              <Suspense fallback={null}>
                <PersonalNotesView
                  onOpenSettings={openSettings}
                  onOpenSearch={() => setActiveView("search")}
                  meetingRecordingRequest={meetingRequest}
                  onMeetingRecordingRequestHandled={() => setMeetingRequest(null)}
                />
              </Suspense>
            )}
            {activeView === "import" && (
              <Suspense fallback={null}>
                <UploadAudioView onNoteCreated={openNote} onOpenSettings={openSettings} />
              </Suspense>
            )}
            {activeView === "settings" && (
              <Suspense fallback={null}>
                <SettingsPage initialSection={settingsSection} />
              </Suspense>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
