import { TFunction } from "i18next";

type RecordingError = {
  code?: string;
  title: string;
  description?: string;
  messageKey?: string;
};

export function getRecordingErrorTitle(error: RecordingError, t: TFunction): string {
  return error.title;
}

export function getRecordingErrorDescription(error: RecordingError, t: TFunction): string {
  if (error.messageKey) return t(error.messageKey);
  return error.description ?? "";
}
