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
import hy from "../locales/hy/common.json";
import yo from "../locales/yo/common.json";
import ig from "../locales/ig/common.json";
import mr from "../locales/mr/common.json";
import km from "../locales/km/common.json";
import el from "../locales/el/common.json";
import nl from "../locales/nl/common.json";
import ro from "../locales/ro/common.json";
import ms from "../locales/ms/common.json";
import sr from "../locales/sr/common.json";
import hr from "../locales/hr/common.json";
import bs from "../locales/bs/common.json";
import ti from "../locales/ti/common.json";
import om from "../locales/om/common.json";
import ha from "../locales/ha/common.json";
import zu from "../locales/zu/common.json";
import lo from "../locales/lo/common.json";
import ilo from "../locales/ilo/common.json";
import ceb from "../locales/ceb/common.json";
import sm from "../locales/sm/common.json";
import jv from "../locales/jv/common.json";
import tw from "../locales/tw/common.json";
import rw from "../locales/rw/common.json";
import ps from "../locales/ps/common.json";
import prs from "../locales/prs/common.json";
import sv from "../locales/sv/common.json";
import hu from "../locales/hu/common.json";
import cs from "../locales/cs/common.json";
import bg from "../locales/bg/common.json";
import sk from "../locales/sk/common.json";
import fi from "../locales/fi/common.json";
import da from "../locales/da/common.json";
import l_no from "../locales/no/common.json";
import lt from "../locales/lt/common.json";
import lv from "../locales/lv/common.json";
import et from "../locales/et/common.json";
import sl from "../locales/sl/common.json";
import sq from "../locales/sq/common.json";
import mk from "../locales/mk/common.json";
import ka from "../locales/ka/common.json";
import az from "../locales/az/common.json";
import kk from "../locales/kk/common.json";
import uz from "../locales/uz/common.json";
import si from "../locales/si/common.json";
import ln from "../locales/ln/common.json";
import rn from "../locales/rn/common.json";
import wo from "../locales/wo/common.json";

// English is the source copy. Other locales carry English values until translated
// by a human (crisis/safety copy especially must be reviewed, not machine-only —
// see docs/open-questions.md item 9).
export const LANGS = ["en", "es", "fr", "hi", "vi", "ar", "tl", "ht", "zh", "ko", "pt", "ru", "so", "ur", "bn", "pa", "fa", "am", "my", "ne", "sw", "te", "ja", "de", "gu", "ta", "yue", "id", "tr", "it", "pl", "uk", "ml", "kn", "th", "he", "hy", "yo", "ig", "mr", "km", "el", "nl", "ro", "ms", "sr", "hr", "bs", "ti", "om", "ha", "zu", "lo", "ilo", "ceb", "sm", "jv", "tw", "rw", "ps", "prs", "sv", "hu", "cs", "bg", "sk", "fi", "da", "no", "lt", "lv", "et", "sl", "sq", "mk", "ka", "az", "kk", "uz", "si", "ln", "rn", "wo"];
export const RTL_LANGS = ["ar", "ur", "fa", "he", "ps", "prs"];
export const LANGUAGE_LABELS = { en: "English", es: "Español", fr: "Français", hi: "हिन्दी", vi: "Tiếng Việt", ar: "العربية", tl: "Tagalog", ht: "Kreyòl ayisyen", zh: "简体中文", ko: "한국어", pt: "Português", ru: "Русский", so: "Soomaali", ur: "اردو", bn: "বাংলা", pa: "ਪੰਜਾਬੀ", fa: "فارسی", am: "አማርኛ", my: "မြန်မာ", ne: "नेपाली", sw: "Kiswahili", "te": "తెలుగు", "ja": "日本語", "de": "Deutsch", "gu": "ગુજરાતી", "ta": "தமிழ்", "yue": "粵語", "id": "Bahasa Indonesia", "tr": "Türkçe", "it": "Italiano", "pl": "Polski", "uk": "Українська", "ml": "മലയാളം", "kn": "ಕನ್ನಡ", "th": "ไทย", "he": "עברית", "hy": "Հայերեն", "yo": "Yorùbá", "ig": "Igbo", "mr": "मराठी", "km": "ខ្មែរ", "el": "Ελληνικά", "nl": "Nederlands", "ro": "Română", "ms": "Bahasa Melayu", "sr": "Српски", "hr": "Hrvatski", "bs": "Bosanski", "ti": "ትግርኛ", "om": "Afaan Oromoo", "ha": "Hausa", "zu": "isiZulu", "lo": "ລາວ", "ilo": "Ilokano", "ceb": "Cebuano", "sm": "Gagana Sāmoa", "jv": "Basa Jawa", "tw": "Twi", "rw": "Kinyarwanda", "ps": "پښتو", "prs": "دری", "sv": "Svenska", "hu": "Magyar", "cs": "Čeština", "bg": "Български", "sk": "Slovenčina", "fi": "Suomi", "da": "Dansk", "no": "Norsk", "lt": "Lietuvių", "lv": "Latviešu", "et": "Eesti", "sl": "Slovenščina", "sq": "Shqip", "mk": "Македонски", "ka": "ქართული", "az": "Azərbaycanca", "kk": "Қазақ", "uz": "Oʻzbek", "si": "සිංහල", "ln": "Lingála", "rn": "Ikirundi", "wo": "Wolof" };

const ALL = { en, es, fr, hi, vi, ar, tl, ht, zh, ko, pt, ru, so, ur, bn, pa, fa, am, my, ne, sw, te, ja, de, gu, ta, yue, id, tr, it, pl, uk, ml, kn, th, he, hy, yo, ig, mr, km, el, nl, ro, ms, sr, hr, bs, ti, om, ha, zu, lo, ilo, ceb, sm, jv, tw, rw, ps, prs, sv, hu, cs, bg, sk, fi, da, "no": l_no, lt, lv, et, sl, sq, mk, ka, az, kk, uz, si, ln, rn, wo };

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
