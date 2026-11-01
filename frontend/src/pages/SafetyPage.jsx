import { useEffect, useState } from "react";
import CrisisNotice from "../components/CrisisNotice";
import { useTranslation } from "react-i18next";
import { api } from "../api";
import TranslationCheck from "../components/TranslationCheck";
export default function SafetyPage() {
  const { t } = useTranslation();
  const [msg, setMsg] = useState("");
  const [confirm, setConfirm] = useState(false);
  const [inbox, setInbox] = useState([]);
  useEffect(() => { api("/api/safety/private_inbox").then((d) => setInbox(d.messages || [])).catch(() => {}); }, []);
  async function wipe() { try { await api("/api/safety/data_wipe", { method: "POST" }); setMsg(t("safety.wiped")); } catch (e) { setMsg(e.message); } }
  return (
    <section>
      <h1>{t("nav.safety")}</h1>
      <h2>{t("safety.relapseTitle")}</h2>
      <p>{t("safety.relapseDraft")}</p>
      <p><a href="tel:988">{t("crisis.call988")}</a> · <a href="tel:911">{t("crisis.call911")}</a></p>
      <TranslationCheck keys={["safety.relapseDraft", "crisis.call988", "crisis.call911"]} />
      {inbox.length > 0 && <div data-testid="private-inbox"><h2>{t("crisisReply.inboxTitle")}</h2>{inbox.map((m) => <CrisisNotice key={m.id} notice={m.message} />)}</div>}
      <h2 id="safe-contacts">{t("safety.safeContactsTitle")}</h2>
      <p>{t("safety.safeContactsHelp")}</p>
      <h2>{t("safety.vaultTitle")}</h2>
      <p>{t("safety.vaultHelp")}</p>
      <TranslationCheck keys="safety.vaultHelp" />
      <h2>{t("safety.wipeTitle")}</h2>
      <p>{t("safety.wipeHelp")}</p>
      <label><input type="checkbox" checked={confirm} onChange={(e) => setConfirm(e.target.checked)} /> {t("safety.wipeConfirm")}</label>
      <button type="button" disabled={!confirm} onClick={wipe}>{t("safety.wipeButton")}</button>
      {msg && <p role="status">{msg}</p>}
    </section>
  );
}
