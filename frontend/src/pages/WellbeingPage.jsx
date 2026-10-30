import { useState } from "react";
import { useTranslation } from "react-i18next";
import { api } from "../api";
import { isRough, suggestFilters } from "../lib/mood";
import ReadAloud from "../components/ReadAloud";
const MOODS = ["good", "okay", "rough", "struggling", "craving"];
export default function WellbeingPage() {
  const { t } = useTranslation();
  const [mood, setMood] = useState("okay");
  const [msg, setMsg] = useState("");
  const [lockTarget, setLockTarget] = useState("community_feed");
  const suggested = suggestFilters(mood);
  async function submit() {
    try { const r = await api("/api/wellbeing/mood_checkins", { method: "POST", body: { mood } }); setMsg(r.show_crisis ? t("wellbeing.roughHelp") : t("wellbeing.saved")); }
    catch { setMsg(t("wellbeing.loginNeeded")); }
  }
  async function addLock() {
    try { await api("/api/wellbeing/locks", { method: "POST", body: { target: lockTarget, kind: "week" } }); setMsg(t("wellbeing.lockSaved")); } catch (e) { setMsg(e.message); }
  }
  return (
    <section>
      <h1>{t("nav.wellbeing")}</h1>
      <h2>{t("wellbeing.checkinTitle")}</h2>
      <div role="radiogroup" aria-label={t("wellbeing.checkinTitle")}>{MOODS.map((m) => <label key={m}><input type="radio" name="mood" checked={mood === m} onChange={() => setMood(m)} /> {t(`wellbeing.mood.${m}`)}</label>)}</div>
      <button type="button" onClick={submit}>{t("wellbeing.save")}</button>
      {isRough(mood) && <div data-testid="filter-suggestion"><p>{t("wellbeing.suggestFilters")}: {suggested.join(", ")}</p><p>{t("wellbeing.roughHelp")}</p></div>}
      <ReadAloud text={t("wellbeing.checkinTitle")} />
      <h2>{t("wellbeing.locksTitle")}</h2>
      <p>{t("wellbeing.locksHelp")}</p>
      <label>{t("wellbeing.lockTarget")} <select value={lockTarget} onChange={(e) => setLockTarget(e.target.value)}><option value="community_feed">community_feed</option><option value="peer_messaging">peer_messaging</option><option value="ai_matching">ai_matching</option></select></label>
      <button type="button" onClick={addLock}>{t("wellbeing.addLock")}</button>
      {msg && <p role="status">{msg}</p>}
    </section>
  );
}
