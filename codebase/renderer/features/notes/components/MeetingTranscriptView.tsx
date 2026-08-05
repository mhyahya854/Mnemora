import { useState, useRef, useEffect, useLayoutEffect, useMemo, useCallback } from "react";
import { useTranslation } from "react-i18next";
import { Check, X, Loader2, Sparkles, User, Mail, Plus, UserCheck } from "lucide-react";
import { Button } from "../../../shared/ui/button";
import { Popover, PopoverTrigger, PopoverContent } from "../../../shared/ui/popover";
import { Toggle } from "../../../shared/ui/toggle";
import { cn } from "../../../shared/ui/utils";

// Check if email format is valid
const isValidEmail = (email: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim());
const getEmailPrefix = (email: string) => email.split("@")[0] || email;

// Speaker color palette
const SPEAKER_COLORS = [
  "text-blue-400 border-l-blue-400/50",
  "text-green-400 border-l-green-400/50",
  "text-purple-400 border-l-purple-400/50",
  "text-orange-400 border-l-orange-400/50",
  "text-pink-400 border-l-pink-400/50",
  "text-cyan-400 border-l-cyan-400/50",
  "text-yellow-400 border-l-yellow-400/50",
  "text-red-400 border-l-red-400/50",
];

// Helper to determine speaker color index
const getSpeakerColorClass = (speakerId: string, mappings: Record<string, string>) => {
  const name = mappings[speakerId] || speakerId;
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  const index = Math.abs(hash) % SPEAKER_COLORS.length;
  return SPEAKER_COLORS[index];
};

// Sub-component: Edit Contact Email Dialog
interface EditContactEmailProps {
  profile: { id: number; display_name: string };
  onAttachEmail: (profileId: number, email: string) => void;
  t: any;
}

function EditContactEmail({ profile, onAttachEmail, t }: EditContactEmailProps) {
  const [open, setOpen] = useState(false);
  const [email, setEmail] = useState("");
  const isEmailValid = isValidEmail(email);

  const handleSave = () => {
    if (isEmailValid) {
      onAttachEmail(profile.id, email.trim().toLowerCase());
      setOpen(false);
    }
  };

  return (
    <Popover
      open={open}
      onOpenChange={(val) => {
        setOpen(val);
        if (!val) setEmail("");
      }}
    >
      <PopoverTrigger asChild>
        <button className="inline-flex items-center mb-0.5 px-1.5 py-0.5 rounded-md text-[11px] outline-none cursor-pointer border border-dashed border-border/60 dark:border-white/15 text-foreground/50 hover:text-foreground hover:border-border/90 dark:hover:border-white/30 transition-colors duration-150 focus-visible:ring-1 focus-visible:ring-ring">
          {t("notes.speaker.addContact")}
        </button>
      </PopoverTrigger>
      <PopoverContent className="w-64 p-3 z-50">
        <div className="text-xs font-medium text-foreground truncate mb-2">
          {profile.display_name}
        </div>
        <input
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              handleSave();
            } else if (e.key === "Escape") {
              setOpen(false);
            }
          }}
          placeholder={t("notes.speaker.emailPlaceholder")}
          className="w-full px-2 py-1.5 rounded-md bg-transparent text-xs text-foreground placeholder:text-foreground/25 outline-none border border-border/50 focus:border-border/90 transition-colors"
          autoFocus
          type="email"
        />
        <div className="flex justify-end gap-1 mt-2">
          <button
            onClick={() => setOpen(false)}
            className="px-2 py-1 rounded text-[11px] text-foreground/50 hover:text-foreground hover:bg-foreground/5 transition-colors cursor-pointer"
          >
            {t("notes.speaker.cancel")}
          </button>
          <button
            onClick={handleSave}
            disabled={!isEmailValid}
            className="px-2 py-1 rounded text-[11px] font-medium transition-colors cursor-pointer bg-primary text-primary-foreground hover:bg-primary/90 disabled:bg-primary/20 disabled:text-primary-foreground/40 disabled:pointer-events-none"
          >
            {t("notes.speaker.save")}
          </button>
        </div>
      </PopoverContent>
    </Popover>
  );
}

// Sub-component: Name Selector List
interface NameSelectorListProps {
  speakerProfiles: any[];
  participants: any[];
  onSelectName: (name: string, email: string | null, profileId: number | null) => void;
  t: any;
}

function NameSelectorList({
  speakerProfiles,
  participants,
  onSelectName,
  t,
}: NameSelectorListProps) {
  const [search, setSearch] = useState("");
  const lowerSearch = search.toLowerCase();
  const searchTrimmed = search.trim();
  const lowerTrimmed = searchTrimmed.toLowerCase();

  const filteredParticipants = (participants || []).filter(
    (p) =>
      !search ||
      (p.displayName || "").toLowerCase().includes(lowerSearch) ||
      p.email.toLowerCase().includes(lowerSearch)
  );

  const filteredProfiles = (speakerProfiles || []).filter(
    (p) =>
      !search ||
      p.display_name.toLowerCase().includes(lowerSearch) ||
      (p.email && p.email.toLowerCase().includes(lowerSearch))
  );

  const isDuplicate =
    filteredParticipants.some(
      (p) =>
        (p.displayName || "").toLowerCase() === lowerTrimmed ||
        p.email.toLowerCase() === lowerTrimmed
    ) ||
    filteredProfiles.some(
      (p) =>
        p.display_name.toLowerCase() === lowerTrimmed ||
        (p.email && p.email.toLowerCase() === lowerTrimmed)
    );

  const canCreate = !!searchTrimmed && !isDuplicate;
  const isEmail = isValidEmail(searchTrimmed);

  const handleCreate = () => {
    if (canCreate) {
      if (isEmail) {
        const emailVal = searchTrimmed.toLowerCase();
        onSelectName(getEmailPrefix(emailVal), emailVal, null);
      } else {
        onSelectName(searchTrimmed, null, null);
      }
      setSearch("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && canCreate) {
      e.preventDefault();
      handleCreate();
    }
  };

  const hasNoResults = !filteredParticipants.length && !filteredProfiles.length && !canCreate;

  return (
    <div className="flex flex-col bg-popover text-popover-foreground">
      <div className="p-2 border-b border-border/50">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={t("notes.speaker.nameOrEmailPlaceholder")}
          className="w-full px-2 py-1.5 rounded-md bg-transparent text-xs text-foreground placeholder:text-foreground/20 outline-none border-none appearance-none"
          autoFocus
        />
      </div>
      <div className="max-h-52 overflow-y-auto">
        {filteredParticipants.length > 0 && (
          <div className="p-1 border-b border-border/30">
            <div className="px-2 py-1 text-[11px] font-medium text-muted-foreground">
              {t("notes.speaker.meetingAttendees")}
            </div>
            {filteredParticipants.slice(0, 5).map((p) => (
              <button
                key={p.email}
                onClick={() => onSelectName(p.displayName || p.email.split("@")[0], p.email, null)}
                className="flex items-center gap-2 w-full px-2 py-1.5 rounded-md text-xs text-foreground/70 hover:bg-foreground/5 transition-colors cursor-pointer text-left"
              >
                <span className="truncate flex-1 text-left">{p.displayName || p.email}</span>
                {p.displayName && (
                  <span className="text-foreground/30 truncate text-[11px]">{p.email}</span>
                )}
              </button>
            ))}
          </div>
        )}

        {filteredProfiles.length > 0 && (
          <div className="p-1 border-b border-border/30">
            <div className="px-2 py-1 text-[11px] font-medium text-muted-foreground">
              {t("notes.speaker.knownSpeakers")}
            </div>
            {filteredProfiles.slice(0, 5).map((p) => (
              <button
                key={p.id}
                onClick={() => onSelectName(p.display_name, p.email, p.id)}
                className="flex items-center gap-2 w-full px-2 py-1.5 rounded-md text-xs text-foreground/70 hover:bg-foreground/5 transition-colors cursor-pointer text-left"
              >
                <span className="truncate flex-1 text-left">{p.display_name}</span>
                {p.email && (
                  <span className="text-foreground/30 truncate text-[11px]">{p.email}</span>
                )}
              </button>
            ))}
          </div>
        )}

        {canCreate && (
          <div className="p-1">
            <button
              onClick={handleCreate}
              className="flex items-center gap-2 w-full px-2 py-1.5 rounded-md text-xs text-foreground/70 hover:bg-foreground/5 transition-colors cursor-pointer text-left"
            >
              <span className="text-foreground/50 shrink-0">
                {t("notes.speaker.createNewPrefix")}
              </span>
              {isEmail ? (
                <>
                  <span className="text-foreground truncate">{getEmailPrefix(searchTrimmed)}</span>
                  <span className="text-foreground/30 truncate text-[11px]">
                    {searchTrimmed.toLowerCase()}
                  </span>
                </>
              ) : (
                <span className="text-foreground truncate">{searchTrimmed}</span>
              )}
            </button>
          </div>
        )}

        {hasNoResults && (
          <div className="px-3 py-4 text-center text-[11px] text-foreground/30">
            {t("notes.speaker.nameOrEmailPlaceholder")}
          </div>
        )}
      </div>
    </div>
  );
}

// Sub-component: Speaker Badge with edit dropdown
interface SpeakerBadgeProps {
  speakerId: string;
  segment: any;
  mappedName: string | undefined;
  speakerProfiles: any[];
  participants: any[];
  colorClass: string;
  isOriginallyYou: boolean;
  onMapSpeaker: (
    speakerId: string,
    name: string,
    email: string | null,
    profileId: number | null
  ) => void;
  onConfirmSuggestion?: (speakerId: string, name: string, profileId: number | null) => void;
  onDismissSuggestion?: (speakerId: string) => void;
  t: any;
}

function SpeakerBadge({
  speakerId,
  segment,
  mappedName,
  speakerProfiles,
  participants,
  colorClass,
  isOriginallyYou,
  onMapSpeaker,
  onConfirmSuggestion,
  onDismissSuggestion,
  t,
}: SpeakerBadgeProps) {
  const [open, setOpen] = useState(false);

  const hasSuggestedName = segment.suggestedName && !mappedName;
  if (hasSuggestedName) {
    return (
      <span className="group inline-flex items-center gap-1 mb-0.5 px-1">
        <span className="text-[11px] font-medium italic text-muted-foreground/60">
          {segment.suggestedName}
        </span>
        <button
          onClick={() =>
            onConfirmSuggestion?.(speakerId, segment.suggestedName, segment.suggestedProfileId)
          }
          className="opacity-0 group-hover:opacity-100 p-0.5 rounded transition-opacity cursor-pointer text-muted-foreground hover:text-emerald-500"
        >
          <Check size={12} />
        </button>
        <button
          onClick={() => onDismissSuggestion?.(speakerId)}
          className="opacity-0 group-hover:opacity-100 p-0.5 rounded transition-opacity cursor-pointer text-muted-foreground hover:text-destructive"
        >
          <X size={12} />
        </button>
      </span>
    );
  }

  const name =
    mappedName ||
    segment.speakerName ||
    (isOriginallyYou ? t("notes.speaker.you") : t("notes.speaker.label", { n: speakerId }));
  const isUnnamed = !mappedName && !segment.speakerName;

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <button
          className={cn(
            "inline-flex items-center text-[11px] font-medium mb-0.5 px-1.5 py-0.5 rounded-md outline-none cursor-pointer border border-border/60 dark:border-white/20 hover:bg-foreground/5 hover:border-border/90 dark:hover:border-white/30 transition-colors duration-150 focus-visible:ring-1 focus-visible:ring-ring",
            colorClass,
            isUnnamed && "border-dashed"
          )}
        >
          {name}
        </button>
      </PopoverTrigger>
      <PopoverContent className="w-72 p-0 z-50">
        <NameSelectorList
          speakerProfiles={speakerProfiles}
          participants={participants}
          onSelectName={(chosenName, email, profileId) => {
            onMapSpeaker(speakerId, chosenName, email, profileId);
            setOpen(false);
          }}
          t={t}
        />
      </PopoverContent>
    </Popover>
  );
}

// Sub-component: Segment selection circle
interface SelectionIndicatorProps {
  isSelected: boolean;
  onToggle: () => void;
  className?: string;
}

function SelectionIndicator({ isSelected, onToggle, className }: SelectionIndicatorProps) {
  return (
    <button
      onClick={(e) => {
        e.stopPropagation();
        onToggle();
      }}
      aria-pressed={isSelected}
      className={cn(
        "w-4 h-4 rounded-full border flex items-center justify-center transition-all cursor-pointer",
        isSelected
          ? "border-primary bg-primary text-primary-foreground opacity-100"
          : "border-border/60 bg-background/80 opacity-0 group-hover:opacity-100 hover:border-foreground/50",
        className
      )}
    >
      {isSelected && <Check size={10} strokeWidth={3} />}
    </button>
  );
}

// Named Export: SelectionBar
export interface SelectionBarProps {
  count: number;
  onClear: () => void;
  speakerProfiles: any[];
  participants: any[];
  onAssignName: (name: string, email: string | null, profileId: number | null) => void;
  t: any;
}

export function SelectionBar({
  count,
  onClear,
  speakerProfiles,
  participants,
  onAssignName,
  t,
}: SelectionBarProps) {
  const [open, setOpen] = useState(false);

  return (
    <div
      className="flex items-center gap-3 rounded-md border border-border/40 bg-surface-2/95 backdrop-blur px-3 py-1.5 text-xs shadow-lg"
      style={{ animation: "agent-message-in 150ms ease-out both" }}
    >
      <span className="text-foreground/70 tabular-nums">
        {t("notes.speaker.selected", { n: count })}
      </span>
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <button className="inline-flex items-center gap-1 px-2 py-1 rounded text-foreground hover:bg-foreground/10 transition-colors cursor-pointer">
            <UserCheck size={12} />
            {t("notes.speaker.assignTo")}
          </button>
        </PopoverTrigger>
        <PopoverContent className="w-72 p-0 z-50">
          <NameSelectorList
            speakerProfiles={speakerProfiles}
            participants={participants}
            onSelectName={(chosenName, email, profileId) => {
              onAssignName(chosenName, email, profileId);
              setOpen(false);
            }}
            t={t}
          />
        </PopoverContent>
      </Popover>
      <button
        onClick={onClear}
        className="px-2 py-1 rounded text-muted-foreground hover:bg-foreground/5 hover:text-foreground transition-colors cursor-pointer"
      >
        {t("notes.speaker.deselectAll")}
      </button>
    </div>
  );
}

// Main Default Export: MeetingTranscriptView
interface MeetingTranscriptViewProps {
  segments: any[];
  micPartial?: string;
  systemPartial?: string;
  systemPartialSpeakerId?: string;
  systemPartialSpeakerName?: string;
  speakerMappings: Record<string, string>;
  speakerProfiles: any[];
  participants: any[];
  isRecording: boolean;
  isDiarizing: boolean;
  sessionDiarizationEnabled?: boolean;
  sessionExpectedCount?: number;
  userTouchedStepper?: boolean;
  onSetSessionDiarizationEnabled?: (enabled: boolean) => void;
  onSetSessionExpectedCount?: (count: number) => void;
  onMapSpeaker: (
    speakerId: string,
    name: string,
    email: string | null,
    profileId: number | null
  ) => void;
  onConfirmSuggestion?: (speakerId: string, name: string, profileId: number | null) => void;
  onDismissSuggestion?: (speakerId: string) => void;
  onAttachSpeakerEmail?: (profileId: number, email: string) => void;
  selectedSegmentIds?: Set<string>;
  onToggleSelect?: (segmentId: string) => void;
}

export function MeetingTranscriptView({
  segments,
  micPartial,
  systemPartial,
  systemPartialSpeakerId,
  systemPartialSpeakerName,
  speakerMappings,
  speakerProfiles,
  participants,
  isRecording,
  isDiarizing,
  sessionDiarizationEnabled = true,
  sessionExpectedCount = 2,
  userTouchedStepper = false,
  onSetSessionDiarizationEnabled,
  onSetSessionExpectedCount,
  onMapSpeaker,
  onConfirmSuggestion,
  onDismissSuggestion,
  onAttachSpeakerEmail,
  selectedSegmentIds,
  onToggleSelect,
}: MeetingTranscriptViewProps) {
  const { t } = useTranslation();
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const shouldAutoScrollRef = useRef(true);
  const [hideDiarizationPill, setHideDiarizationPill] = useState(false);

  // Monitor scroll height changes to keep scroll at bottom during live transcription
  useEffect(() => {
    const container = scrollContainerRef.current;
    if (!container) return;

    const handleScroll = () => {
      // Auto scroll if close to the bottom
      shouldAutoScrollRef.current =
        container.scrollHeight - container.scrollTop - container.clientHeight < 80;
    };

    handleScroll();
    container.addEventListener("scroll", handleScroll);
    return () => container.removeEventListener("scroll", handleScroll);
  }, []);

  useLayoutEffect(() => {
    const container = scrollContainerRef.current;
    if (container && shouldAutoScrollRef.current) {
      container.scrollTop = container.scrollHeight;
    }
  }, [segments, micPartial, systemPartial]);

  const hasSegments = segments.length > 0 || micPartial || systemPartial;

  if (!hasSegments) {
    return (
      <div className="h-full flex items-center justify-center px-5">
        <p className="text-xs text-muted-foreground/40 select-none">
          {t("notes.editor.conversationWillAppear")}
        </p>
      </div>
    );
  }

  const isInitiallyYou = (seg: any) => {
    const mapped = speakerMappings[seg.speaker];
    if (mapped) {
      return mapped.trim().toLowerCase() === t("notes.speaker.you").toLowerCase();
    }
    return seg.speaker === "you" || (!seg.speakerName && seg.source === "mic");
  };

  const othersCount = Math.max(0, sessionExpectedCount - 1);

  return (
    <div className="h-full relative flex flex-col min-h-0">
      {(isRecording || isDiarizing) && !hideDiarizationPill && (
        <div className="absolute top-2 left-1/2 -translate-x-1/2 z-10 flex items-center gap-2 px-2.5 py-1 rounded-md border border-border bg-background/95 backdrop-blur shadow-sm text-xs text-foreground">
          {isDiarizing ? (
            <Loader2 size={12} className="animate-spin text-muted-foreground" />
          ) : (
            <User
              size={12}
              className={cn(sessionDiarizationEnabled ? "text-primary" : "text-muted-foreground")}
            />
          )}
          <span>
            {isDiarizing
              ? t("notes.speaker.pill.finalizing")
              : sessionDiarizationEnabled
                ? othersCount === 1 &&
                  !(participants && participants.length > 0) &&
                  !userTouchedStepper
                  ? t("notes.speaker.pill.defaultingHint")
                  : t("notes.speaker.pill.identifying")
                : t("notes.speaker.pill.notLabeled")}
          </span>
          {!isDiarizing && sessionDiarizationEnabled && (
            <>
              <span className="text-muted-foreground">
                {othersCount === 0
                  ? t("notes.speaker.pill.justYou")
                  : t("notes.speaker.pill.othersInCall", { count: othersCount })}
              </span>
              <div className="flex items-center gap-0.5 rounded-md border border-border bg-surface-2/60">
                <button
                  onClick={() => onSetSessionExpectedCount?.(sessionExpectedCount - 1)}
                  disabled={othersCount <= 0}
                  className="px-1.5 py-0.5 rounded-l-md hover:bg-accent focus-visible:bg-accent focus-visible:outline-none disabled:opacity-30 disabled:pointer-events-none transition-colors"
                  aria-label={t("notes.speaker.pill.decAria")}
                >
                  âˆ’
                </button>
                <span className="px-1.5 tabular-nums">{othersCount}</span>
                <button
                  onClick={() => onSetSessionExpectedCount?.(sessionExpectedCount + 1)}
                  disabled={othersCount >= 7}
                  className="px-1.5 py-0.5 rounded-r-md hover:bg-accent focus-visible:bg-accent focus-visible:outline-none disabled:opacity-30 disabled:pointer-events-none transition-colors"
                  aria-label={t("notes.speaker.pill.incAria")}
                >
                  +
                </button>
              </div>
            </>
          )}

          <button
            onClick={() => setHideDiarizationPill(true)}
            className="text-foreground/40 hover:text-foreground/70 transition-colors ml-1"
          >
            <X size={12} />
          </button>
        </div>
      )}

      <div
        ref={scrollContainerRef}
        className="flex-1 overflow-y-auto px-4 pt-3 pb-24 flex flex-col gap-1.5 agent-chat-scroll min-h-0"
      >
        {segments.map((segment, index) => {
          const isYou = isInitiallyYou(segment);
          const isPrevSameSpeaker =
            index > 0 &&
            (segments[index - 1].speaker === segment.speaker ||
              (segments[index - 1].source === segment.source && !segment.speaker));

          const hasSpeaker = !!segment.speaker;
          const isExternalYou = segment.speaker === "you";
          const isSpeakerMapped = hasSpeaker && !isYou;

          const colorClass = getSpeakerColorClass(segment.speaker, speakerMappings);

          const isSelected = selectedSegmentIds?.has(segment.id) ?? false;
          const isSelectMode = !!selectedSegmentIds;

          const mappedName = speakerMappings[segment.speaker];
          const speakerName = mappedName || segment.speakerName;
          const matchedProfile =
            speakerName && speakerProfiles
              ? speakerProfiles.find((p) => p.id != null && p.display_name === speakerName)
              : undefined;
          const showAddEmail =
            !!matchedProfile &&
            matchedProfile.id != null &&
            !matchedProfile.email &&
            !!onAttachSpeakerEmail;

          const badgeElement = hasSpeaker && (
            <div className="flex items-center gap-1">
              <SpeakerBadge
                speakerId={segment.speaker}
                segment={segment}
                mappedName={mappedName}
                speakerProfiles={speakerProfiles}
                participants={participants}
                colorClass={colorClass}
                isOriginallyYou={isExternalYou}
                onMapSpeaker={onMapSpeaker}
                onConfirmSuggestion={onConfirmSuggestion}
                onDismissSuggestion={onDismissSuggestion}
                t={t}
              />
              {showAddEmail && (
                <EditContactEmail
                  profile={{ id: matchedProfile.id, display_name: matchedProfile.display_name }}
                  onAttachEmail={onAttachSpeakerEmail}
                  t={t}
                />
              )}
            </div>
          );

          return (
            <div
              key={segment.id}
              className={cn(
                "group flex flex-col",
                isYou ? "items-start" : "items-end",
                !isPrevSameSpeaker && index > 0 && "mt-2",
                isSelectMode && (isYou ? "pl-6" : "pr-6")
              )}
              style={{ animation: "agent-message-in 200ms ease-out both" }}
            >
              {badgeElement && !isPrevSameSpeaker && badgeElement}
              {badgeElement && isPrevSameSpeaker && (
                <div className="grid grid-rows-[0fr] opacity-0 pointer-events-none transition-[grid-template-rows,opacity] duration-150 ease-out group-hover:grid-rows-[1fr] group-hover:opacity-100 group-hover:pointer-events-auto">
                  <div className="overflow-hidden">{badgeElement}</div>
                </div>
              )}
              <div className="relative max-w-[80%]">
                <div
                  className={cn(
                    "px-3 py-1.5 cursor-default transition-colors text-[13px] leading-relaxed",
                    isYou
                      ? cn(
                          "bg-primary/90 text-primary-foreground",
                          isPrevSameSpeaker
                            ? "rounded-lg rounded-tl-sm"
                            : "rounded-lg rounded-bl-sm"
                        )
                      : cn(
                          "bg-surface-2 border border-border/30 text-foreground",
                          isPrevSameSpeaker
                            ? "rounded-lg rounded-tr-sm"
                            : "rounded-lg rounded-br-sm",
                          isSpeakerMapped && colorClass
                        ),
                    isSelected && "ring-2 ring-primary/60"
                  )}
                >
                  {segment.text}
                </div>
                {isSelectMode && (
                  <SelectionIndicator
                    isSelected={isSelected}
                    onToggle={() => onToggleSelect?.(segment.id)}
                    className={cn("absolute top-1.5", isYou ? "-left-6" : "-right-6")}
                  />
                )}
              </div>
            </div>
          );
        })}

        {/* Live partial transcripts */}
        {micPartial && (
          <div
            className="flex justify-start"
            style={{ animation: "agent-message-in 150ms ease-out both" }}
          >
            <div className="max-w-[80%] flex flex-col">
              <div className="px-3 py-1.5 rounded-lg rounded-bl-sm bg-primary/60 text-primary-foreground/80 text-[13px] leading-relaxed italic">
                {micPartial}
                <span
                  className="inline-block w-[2px] h-[13px] align-middle ml-0.5 bg-primary-foreground/60"
                  style={{ animation: "agent-cursor-blink 800ms steps(1) infinite" }}
                />
              </div>
            </div>
          </div>
        )}

        {systemPartial && (
          <div
            className="flex justify-end"
            style={{ animation: "agent-message-in 150ms ease-out both" }}
          >
            <div className="max-w-[80%] flex flex-col">
              {systemPartialSpeakerName && (
                <div className="mb-0.5 flex items-center gap-1 px-1 justify-end">
                  <span className="text-[11px] font-medium text-muted-foreground/70">
                    {systemPartialSpeakerName}
                  </span>
                </div>
              )}
              <div className="px-3 py-1.5 rounded-lg rounded-br-sm bg-surface-2/70 border border-border/20 text-foreground/80 text-[13px] leading-relaxed italic">
                {systemPartial}
                <span
                  className="inline-block w-[2px] h-[13px] align-middle ml-0.5 bg-foreground/40"
                  style={{ animation: "agent-cursor-blink 800ms steps(1) infinite" }}
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
