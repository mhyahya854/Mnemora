import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import english from "../../shared/i18n/en/translation.json";

export const SUPPORTED_UI_LANGUAGES = ["en"] as const;
export type UiLanguage = (typeof SUPPORTED_UI_LANGUAGES)[number];

export function normalizeUiLanguage(_language?: string | null): UiLanguage {
  return "en";
}

void i18n.use(initReactI18next).init({
  resources: { en: { translation: english } },
  lng: "en",
  fallbackLng: "en",
  supportedLngs: ["en"],
  defaultNS: "translation",
  interpolation: { escapeValue: false },
  returnEmptyString: true,
  returnNull: false,
});

export default i18n;
