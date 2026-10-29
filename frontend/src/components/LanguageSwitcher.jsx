import { useTranslation } from "react-i18next";
import { LANGS, LANGUAGE_LABELS } from "../i18n";

export default function LanguageSwitcher() {
  const { t, i18n } = useTranslation();
  return (
    <label>
      {t("lang.label")}{" "}
      <select value={i18n.language} onChange={(e) => i18n.changeLanguage(e.target.value)}>
        {LANGS.map((l) => <option key={l} value={l}>{LANGUAGE_LABELS[l]}</option>)}
      </select>
    </label>
  );
}
