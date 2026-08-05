const i18next = require("i18next");
const enTranslation = require("../../../shared/i18n/en/translation.json");

const SUPPORTED_UI_LANGUAGES = ["en"];
const normalizeUiLanguage = () => "en";
const i18nMain = i18next.createInstance();

void i18nMain.init({
  initAsync: false,
  resources: { en: { translation: enTranslation } },
  lng: "en",
  fallbackLng: "en",
  defaultNS: "translation",
  interpolation: { escapeValue: false },
  returnEmptyString: false,
  returnNull: false,
});

function changeLanguage() {
  if (i18nMain.language !== "en") void i18nMain.changeLanguage("en");
  return "en";
}

module.exports = {
  i18nMain,
  changeLanguage,
  normalizeUiLanguage,
  SUPPORTED_UI_LANGUAGES,
};
