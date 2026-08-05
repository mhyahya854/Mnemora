import { useEffect, useState } from "react";
import {
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Database,
  FolderOpen,
  Keyboard,
  Mic,
  MonitorSpeaker,
  Shield,
} from "lucide-react";
import { useSettings } from "../settings/useSettings";
import { getDefaultHotkey } from "../dictation/hotkeys";
import { Button } from "../../shared/ui/button";
import { Input } from "../../shared/ui/input";
import WindowControls from "../../app/components/WindowControls";

interface Props {
  onComplete: (options?: { openSettings?: boolean }) => void;
}

const steps = ["Welcome", "Local model", "Permissions", "Shortcuts & storage", "Ready"];

export default function OnboardingFlow({ onComplete }: Props) {
  const settings = useSettings();
  const [step, setStep] = useState(() =>
    Math.min(Number(localStorage.getItem("onboardingCurrentStep") || 0), steps.length - 1)
  );
  const [models, setModels] = useState<Array<{ model: string; installed: boolean }>>([]);
  const [checkingModels, setCheckingModels] = useState(false);
  const [micGranted, setMicGranted] = useState(false);
  const [accessibilityGranted, setAccessibilityGranted] = useState(false);
  const [systemAudioGranted, setSystemAudioGranted] = useState(false);
  const [permissionMessage, setPermissionMessage] = useState("");

  const loadModels = async () => {
    setCheckingModels(true);
    try {
      const result = await window.electronAPI.listWhisperModels();
      const installed = result.models.filter((model) => model.installed);
      setModels(installed);
      if (installed.length && !installed.some((model) => model.model === settings.whisperModel)) {
        settings.setWhisperModel(installed[0].model);
      }
    } finally {
      setCheckingModels(false);
    }
  };

  useEffect(() => {
    localStorage.setItem("onboardingCurrentStep", String(step));
    if (step === 1) void loadModels();
    if (step === 2) {
      void window.electronAPI
        .checkMicrophoneAccess?.()
        .then((result) => setMicGranted(Boolean(result?.granted)));
      void window.electronAPI.checkAccessibilityPermission?.(true).then(setAccessibilityGranted);
    }
  }, [step]);

  useEffect(() => {
    if (!settings.dictationKey) settings.setDictationKey(getDefaultHotkey());
  }, [settings.dictationKey, settings.setDictationKey]);

  const requestMicrophone = async () => {
    try {
      const result = await window.electronAPI.requestMicrophoneAccess?.();
      if (!result?.granted) throw new Error("Microphone permission was not granted.");
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach((track) => track.stop());
      setMicGranted(true);
      setPermissionMessage("");
    } catch (error) {
      setPermissionMessage(String(error));
    }
  };

  const requestAccessibility = async () => {
    const granted = await window.electronAPI.checkAccessibilityPermission?.(true);
    if (granted) {
      setAccessibilityGranted(true);
      return;
    }
    await window.electronAPI.openAccessibilitySettings?.();
    setPermissionMessage(
      "Enable accessibility access in system settings to paste dictation automatically."
    );
  };

  const requestSystemAudio = async () => {
    const result = await window.electronAPI.requestSystemAudioAccess?.();
    setSystemAudioGranted(Boolean(result?.granted));
    if (!result?.granted) {
      setPermissionMessage(
        result?.error || "System audio can also be granted later from Settings."
      );
    }
  };

  const finish = () => {
    localStorage.setItem("onboardingCompleted", "true");
    localStorage.removeItem("onboardingCurrentStep");
    onComplete();
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <div
        className="h-10 flex items-center"
        style={{ WebkitAppRegion: "drag" } as React.CSSProperties}
      >
        <div className="flex-1" />
        {window.electronAPI.getPlatform() !== "darwin" && (
          <div style={{ WebkitAppRegion: "no-drag" } as React.CSSProperties}>
            <WindowControls />
          </div>
        )}
      </div>
      <div className="mx-auto w-full max-w-3xl px-6 pt-5 pb-10 flex-1 flex flex-col">
        <div
          className="flex items-center gap-2 mb-8"
          aria-label={`Step ${step + 1} of ${steps.length}`}
        >
          {steps.map((label, index) => (
            <div key={label} className="flex-1">
              <div className={`h-1 rounded-full ${index <= step ? "bg-primary" : "bg-muted"}`} />
              <span
                className={`mt-1.5 block text-[10px] ${index === step ? "text-foreground" : "text-muted-foreground"}`}
              >
                {label}
              </span>
            </div>
          ))}
        </div>

        <div className="flex-1 rounded-2xl border border-border/60 bg-card p-8 shadow-sm">
          {step === 0 && (
            <div className="max-w-xl">
              <div className="w-12 h-12 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
                <Shield size={24} />
              </div>
              <h1 className="mt-5 text-3xl font-semibold tracking-tight">
                Your voice, kept private.
              </h1>
              <p className="mt-3 text-base leading-relaxed text-muted-foreground">
                Mnemora captures dictation, meetings, notes, and imported media entirely on this
                device. No account, API key, or network service is required.
              </p>
              <div className="mt-6 grid grid-cols-3 gap-3 text-xs">
                <div className="rounded-lg border p-3">
                  <Mic size={16} className="text-primary mb-2" />
                  Local dictation
                </div>
                <div className="rounded-lg border p-3">
                  <MonitorSpeaker size={16} className="text-primary mb-2" />
                  Meeting audio
                </div>
                <div className="rounded-lg border p-3">
                  <Database size={16} className="text-primary mb-2" />
                  Local memory
                </div>
              </div>
            </div>
          )}

          {step === 1 && (
            <div>
              <Database size={28} className="text-primary" />
              <h1 className="mt-4 text-2xl font-semibold">Local Whisper model</h1>
              <p className="mt-2 text-sm text-muted-foreground">
                Mnemora uses only models already bundled with, or imported into, this installation.
              </p>
              <div className="mt-6 space-y-2">
                {checkingModels ? (
                  <p className="text-sm text-muted-foreground">Checking this device…</p>
                ) : models.length ? (
                  models.map((model) => (
                    <label
                      key={model.model}
                      className="flex items-center gap-3 rounded-xl border p-4 cursor-pointer"
                    >
                      <input
                        type="radio"
                        checked={settings.whisperModel === model.model}
                        onChange={() => settings.setWhisperModel(model.model)}
                      />
                      <span className="flex-1 text-sm font-medium">Whisper {model.model}</span>
                      <CheckCircle2 size={17} className="text-emerald-500" />
                    </label>
                  ))
                ) : (
                  <div className="rounded-xl border border-amber-500/25 bg-amber-500/5 p-4">
                    <p className="text-sm font-medium text-amber-700 dark:text-amber-300">
                      No model detected
                    </p>
                    <p className="mt-1 text-xs text-muted-foreground">
                      Open the local models folder and add a compatible GGML Whisper model pack.
                    </p>
                    <Button
                      className="mt-3"
                      variant="outline"
                      size="sm"
                      onClick={() => void window.electronAPI.openMnemoraModelsFolder?.()}
                    >
                      <FolderOpen size={14} /> Open models folder
                    </Button>
                  </div>
                )}
              </div>
            </div>
          )}

          {step === 2 && (
            <div>
              <Shield size={28} className="text-primary" />
              <h1 className="mt-4 text-2xl font-semibold">System permissions</h1>
              <p className="mt-2 text-sm text-muted-foreground">
                Grant only the access needed for the workflows you use.
              </p>
              <div className="mt-6 space-y-2">
                {[
                  {
                    title: "Microphone",
                    description: "Required for dictation and your side of meetings.",
                    granted: micGranted,
                    action: requestMicrophone,
                    icon: Mic,
                  },
                  {
                    title: "Accessibility",
                    description: "Recommended for pasting text into other apps.",
                    granted: accessibilityGranted,
                    action: requestAccessibility,
                    icon: Keyboard,
                  },
                  {
                    title: "System audio",
                    description: "Optional; captures other speakers in meetings.",
                    granted: systemAudioGranted,
                    action: requestSystemAudio,
                    icon: MonitorSpeaker,
                  },
                ].map(({ title, description, granted, action, icon: Icon }) => (
                  <div key={title} className="rounded-xl border p-4 flex items-center gap-4">
                    <Icon size={20} className="text-primary" />
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium">{title}</p>
                      <p className="text-xs text-muted-foreground">{description}</p>
                    </div>
                    {granted ? (
                      <span className="text-xs text-emerald-600 flex items-center gap-1">
                        <CheckCircle2 size={14} /> Granted
                      </span>
                    ) : (
                      <Button variant="outline" size="sm" onClick={() => void action()}>
                        Grant
                      </Button>
                    )}
                  </div>
                ))}
              </div>
              {permissionMessage && (
                <p className="mt-3 text-xs text-muted-foreground">{permissionMessage}</p>
              )}
            </div>
          )}

          {step === 3 && (
            <div>
              <Keyboard size={28} className="text-primary" />
              <h1 className="mt-4 text-2xl font-semibold">Shortcuts and storage</h1>
              <div className="mt-6 space-y-5">
                <label className="block text-xs text-muted-foreground">
                  Dictation shortcut
                  <Input
                    className="mt-1"
                    value={settings.dictationKey}
                    onChange={(event) => settings.setDictationKey(event.target.value)}
                  />
                </label>
                <label className="block text-xs text-muted-foreground">
                  Meeting shortcut
                  <Input
                    className="mt-1"
                    value={settings.meetingKey}
                    onChange={(event) => settings.setMeetingKey(event.target.value)}
                    placeholder="Control+Shift+M"
                  />
                </label>
                <label className="flex gap-3 rounded-xl border p-4 cursor-pointer">
                  <input
                    type="checkbox"
                    className="mt-0.5"
                    checked={settings.dataRetentionEnabled}
                    onChange={(event) => settings.setDataRetentionEnabled(event.target.checked)}
                  />
                  <span>
                    <span className="block text-sm font-medium">
                      Save dictation history locally
                    </span>
                    <span className="block mt-1 text-xs text-muted-foreground">
                      Optional. When off, completed dictations are pasted but not stored.
                    </span>
                  </span>
                </label>
              </div>
            </div>
          )}

          {step === 4 && (
            <div className="text-center max-w-lg mx-auto py-8">
              <div className="mx-auto w-14 h-14 rounded-full bg-emerald-500/10 text-emerald-600 flex items-center justify-center">
                <CheckCircle2 size={28} />
              </div>
              <h1 className="mt-5 text-2xl font-semibold">Mnemora is ready</h1>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                Dictate with your shortcut, create a meeting note for system-and-mic capture, or
                import an audio or video file. Everything stays local.
              </p>
            </div>
          )}
        </div>

        <div className="mt-5 flex items-center justify-between">
          <Button
            variant="ghost"
            onClick={() => setStep((value) => Math.max(0, value - 1))}
            disabled={step === 0}
          >
            <ChevronLeft size={15} /> Back
          </Button>
          {step < steps.length - 1 ? (
            <Button onClick={() => setStep((value) => Math.min(steps.length - 1, value + 1))}>
              Continue <ChevronRight size={15} />
            </Button>
          ) : (
            <Button onClick={finish}>
              Open Mnemora <ChevronRight size={15} />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
