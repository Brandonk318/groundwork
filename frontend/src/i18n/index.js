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
import zh from "../locales/zh/common.json";
import ko from "../locales/ko/common.json";
import pt from "../locales/pt/common.json";
import ru from "../locales/ru/common.json";
import so from "../locales/so/common.json";
import ur from "../locales/ur/common.json";
import bn from "../locales/bn/common.json";
import pa from "../locales/pa/common.json";
import fa from "../locales/fa/common.json";
import am from "../locales/am/common.json";
import my from "../locales/my/common.json";
import ne from "../locales/ne/common.json";
import sw from "../locales/sw/common.json";
import te from "../locales/te/common.json";
import ja from "../locales/ja/common.json";
import de from "../locales/de/common.json";
import gu from "../locales/gu/common.json";
import ta from "../locales/ta/common.json";
import yue from "../locales/yue/common.json";
import id from "../locales/id/common.json";
import tr from "../locales/tr/common.json";
import it from "../locales/it/common.json";
import pl from "../locales/pl/common.json";
import uk from "../locales/uk/common.json";
import ml from "../locales/ml/common.json";
import kn from "../locales/kn/common.json";
import th from "../locales/th/common.json";
import he from "../locales/he/common.json";

// English is the source copy. Other locales carry English values until translated
// by a human (crisis/safety copy especially must be reviewed, not machine-only —
// see docs/open-questions.md item 9).
export const LANGS = ["en", "es", "fr", "hi", "vi", "ar", "tl", "ht", "zh", "ko", "pt", "ru", "so", "ur", "bn", "pa", "fa", "am", "my", "ne", "sw", "te", "ja", "de", "gu", "ta", "yue", "id", "tr", "it", "pl", "uk", "ml", "kn", "th", "he"];
export const RTL_LANGS = ["ar", "ur", "fa", "he"];
export const LANGUAGE_LABELS = { en: "English", es: "Español", fr: "Français", hi: "हिन्दी", vi: "Tiếng Việt", ar: "العربية", tl: "Tagalog", ht: "Kreyòl ayisyen", zh: "简体中文", ko: "한국어", pt: "Português", ru: "Русский", so: "Soomaali", ur: "اردو", bn: "বাংলা", pa: "ਪੰਜਾਬੀ", fa: "فارسی", am: "አማርኛ", my: "မြန်မာ", ne: "नेपाली", sw: "Kiswahili", "te": "తెలుగు", "ja": "日本語", "de": "Deutsch", "gu": "ગુજરાતી", "ta": "தமிழ்", "yue": "粵語", "id": "Bahasa Indonesia", "tr": "Türkçe", "it": "Italiano", "pl": "Polski", "uk": "Українська", "ml": "മലയാളം", "kn": "ಕನ್ನಡ", "th": "ไทย", "he": "עברית" };

const ALL = { en, es, fr, hi, vi, ar, tl, ht, zh, ko, pt, ru, so, ur, bn, pa, fa, am, my, ne, sw, te, ja, de, gu, ta, yue, id, tr, it, pl, uk, ml, kn, th, he };

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
    Object.entries(ALL).map(([k, v]) => [k, { common: v }]),
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
