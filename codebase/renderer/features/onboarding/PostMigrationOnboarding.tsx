import { useTranslation } from "react-i18next";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "../../shared/ui/dialog";
import { Button } from "../../shared/ui/button";
import PermissionsSection from "../settings/components/PermissionsSection";
import { usePermissions } from "../settings/usePermissions";
import { useSystemAudioPermission } from "../meetings/useSystemAudioPermission";

interface PostMigrationOnboardingProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onDone: () => void;
}

export default function PostMigrationOnboarding({
  open,
  onOpenChange,
  onDone,
}: PostMigrationOnboardingProps) {
  const { t } = useTranslation();
  const permissions = usePermissions();
  const systemAudio = useSystemAudioPermission();

  const remindLater = () => {
    window.electronAPI?.markBundleMigrationDismissed?.();
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{t("postMigration.title")}</DialogTitle>
          <DialogDescription>{t("postMigration.description")}</DialogDescription>
        </DialogHeader>

        <PermissionsSection permissions={permissions} systemAudio={systemAudio} />

        <DialogFooter>
          <Button variant="ghost" onClick={remindLater}>
            {t("postMigration.remindLater")}
          </Button>
          <Button onClick={onDone} disabled={!permissions.micPermissionGranted}>
            {t("postMigration.done")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
