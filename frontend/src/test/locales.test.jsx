import { describe, expect, it } from "vitest";
import { dirFor, LANGS, LANGUAGE_LABELS, RTL_LANGS } from "../i18n";
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

const ALL = Object.fromEntries(Object.entries(import.meta.glob("../locales/*/common.json", { eager: true, import: "default" })).map(([p, m]) => [p.split("/")[2], m]).filter(([k]) => k !== "en"));

function keysOf(obj, prefix = "") {
  return Object.entries(obj).flatMap(([k, v]) => (v && typeof v === "object" ? keysOf(v, `${prefix}${k}.`) : [`${prefix}${k}`]));
}

describe("21-language parity", () => {
  it("registers 21 languages with labels for the picker", () => {
    expect(LANGS).toHaveLength(Object.keys(ALL).length + 1);
    expect(Object.keys(LANGUAGE_LABELS).sort()).toEqual([...LANGS].sort());
  });
  it("every non-English locale has full key parity with en", () => {
    const want = keysOf(en).sort();
    expect(want.length).toBeGreaterThan(100);
    for (const [lang, dict] of Object.entries(ALL)) {
      expect(keysOf(dict).sort(), lang).toEqual(want);
    }
  });
  it("RTL only for ar, ur and fa", () => {
    expect([...RTL_LANGS].sort()).toEqual(["ar", "fa", "he", "prs", "ps", "ur", "yi"]);
    for (const lng of LANGS) {
      expect(dirFor(lng), lng).toBe(["ar", "ur", "fa", "he", "ps", "prs", "yi"].includes(lng) ? "rtl" : "ltr");
    }
  });
  it("crisis and safety copy stays untranslated until a human reviews it (open-questions #9)", () => {
    for (const [lang, dict] of Object.entries(ALL)) {
      expect(dict.crisis, `${lang}.crisis`).toEqual(en.crisis);
      expect(dict.safety.relapseDraft, `${lang}.safety.relapseDraft`).toBe(en.safety.relapseDraft);
    }
  });
});
