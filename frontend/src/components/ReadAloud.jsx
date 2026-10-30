import { useTranslation } from "react-i18next";
export function speak(text, lang = "en") {
  if (typeof window === "undefined" || !("speechSynthesis" in window)) return false;
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = lang;
  window.speechSynthesis.speak(u);
  return true;
}
export default function ReadAloud({ text }) {
  const { t, i18n } = useTranslation();
  return <button type="button" className="read-aloud" onClick={() => speak(text, i18n.language)}>{t("readAloud.button")}</button>;
}
