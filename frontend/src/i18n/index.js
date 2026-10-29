import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import en from "../locales/en/common.json";
import es from "../locales/es/common.json";
import fr from "../locales/fr/common.json";
import hi from "../locales/hi/common.json";
import vi from "../locales/vi/common.json";
import ar from "../locales/ar/common.json";
import tl from "../locales/tl/common.json";
import ht from "../locales/ht/common.json";

// English is the source copy. Other locales are stubbed ({}) and fall back to English
// until translated by a human (crisis copy especially must be reviewed, not machine-only).
export const LANGS = ["en", "es", "fr", "hi", "vi", "ar", "tl", "ht"];
export const RTL_LANGS = ["ar"];
export const LANGUAGE_LABELS = { en: "English", es: "Español", fr: "Français", hi: "हिन्दी", vi: "Tiếng Việt", ar: "العربية", tl: "Tagalog", ht: "Kreyòl ayisyen" };

export function dirFor(lng) {
  return RTL_LANGS.includes(lng) ? "rtl" : "ltr";
}

function applyDir(lng) {
  if (typeof document !== "undefined") {
    document.documentElement.lang = lng;
    document.documentElement.dir = dirFor(lng);
  }
}

i18n.use(initReactI18next).init({
  resources: Object.fromEntries(
    Object.entries({ en, es, fr, hi, vi, ar, tl, ht }).map(([k, v]) => [k, { common: v }]),
  ),
  lng: "en",
  fallbackLng: "en",
  supportedLngs: LANGS,
  ns: ["common"],
  defaultNS: "common",
  interpolation: { escapeValue: false },
});
i18n.on("languageChanged", applyDir);
applyDir(i18n.language);

export default i18n;
