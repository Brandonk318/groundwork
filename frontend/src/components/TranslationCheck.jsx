import { useTranslation } from "react-i18next";

const FALLBACK = "Please double-check the translation to make sure it matches the English version.";

// Safeguard for crisis, legal and price lines (docs/open-questions.md #9). Display only: when the
// app is not in English AND a protected line has been translated, it shows the English original
// under it with a "double-check" notice. It never adds a step, a button or a link, never hides or
// delays anything, and only repeats text already on screen (no new phone numbers). Renders nothing
// in English or while the line is still English (today every protected line is kept in English).
// keys: "a.b" or ["a.b", "c.d"].
export default function TranslationCheck({ keys }) {
  const { t, i18n } = useTranslation();
  const lng = (i18n.resolvedLanguage || i18n.language || "en").slice(0, 2);
  if (lng === "en") return null;
  const en = i18n.getFixedT("en");
  const list = Array.isArray(keys) ? keys : [keys];
  const english = list.map((k) => en(k));
  if (list.every((k, i) => t(k) === english[i])) return null;
  return (
    <div className="translation-check" data-testid="translation-check" lang="en" dir="ltr">
      {english.map((s, i) => <p key={i}>{s}</p>)}
      <p lang={lng} dir="auto"><em>{t("translationCheck.notice", { defaultValue: FALLBACK })}</em></p>
    </div>
  );
}
