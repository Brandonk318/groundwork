import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
// Private crisis auto-reply (Brann 2026-10-31). Shown only to the author; text comes from the
// server in English pending human review of other locales (open question #9).
export default function CrisisNotice({ notice }) {
  const { t } = useTranslation();
  if (!notice) return null;
  return (
    <div role="alert" data-testid="crisis-notice" lang={notice.locale || "en"}>
      <h3>{notice.title}</h3>
      <p>{notice.body}</p>
      <p>{t("crisisReply.onlyYou")}</p>
      <ul>{(notice.resources || []).map((r) => <li key={r.id}><a href={r.tel || r.sms}>{r.label}</a></li>)}</ul>
      <Link to={notice.links?.crisis_button || "/safety"}>{t("crisisReply.openCrisis")}</Link>
    </div>
  );
}
