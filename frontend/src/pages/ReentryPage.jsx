import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { api } from "../api";
import ReadAloud from "../components/ReadAloud";
import { REENTRY_SECTIONS, REENTRY_STEPS, celebrationsFor, sectionProgress } from "../data/reentrySteps";
import TranslationCheck from "../components/TranslationCheck";

export default function ReentryPage() {
  const { t } = useTranslation();
  const [done, setDone] = useState(new Set());
  const [meta, setMeta] = useState({}); // id -> {due_date, priority, notes}
  const [custom, setCustom] = useState([]);
  const [customTitle, setCustomTitle] = useState("");
  const [tipText, setTipText] = useState({});
  const [tips, setTips] = useState({});
  const [openTips, setOpenTips] = useState({});
  const [serverMsg, setServerMsg] = useState("");

  useEffect(() => {
    api("/api/reentry/reentry_checklist").then((d) => {
      if (d.steps) {
        setDone(new Set(d.steps.filter((s) => s.status === "done").map((s) => s.id)));
        const m = {};
        d.steps.forEach((s) => { m[s.id] = { due_date: s.due_date || "", priority: s.priority || "normal", notes: s.notes || "" }; });
        setMeta(m);
      }
      if (d.custom_steps) setCustom(d.custom_steps);
    }).catch(() => {});
  }, []);

  const sections = useMemo(() => sectionProgress([...done]), [done]);
  const celebrations = useMemo(() => celebrationsFor([...done]), [done]);
  const totalDone = REENTRY_STEPS.filter((s) => done.has(s.id)).length;

  async function toggle(step) {
    const next = new Set(done);
    const willDone = !next.has(step.id);
    willDone ? next.add(step.id) : next.delete(step.id);
    setDone(next);
    try { await api("/api/reentry/reentry_checklist/progress", { method: "POST", body: { step_id: step.id, status: willDone ? "done" : "not_started", ...(meta[step.id] || {}) } }); } catch {}
  }
  function updateMeta(id, patch) { setMeta((m) => ({ ...m, [id]: { ...(m[id] || { due_date: "", priority: "normal", notes: "" }), ...patch } })); }
  async function saveMeta(step) { try { await api("/api/reentry/reentry_checklist/progress", { method: "POST", body: { step_id: step.id, status: done.has(step.id) ? "done" : "not_started", ...(meta[step.id] || {}) } }); setServerMsg(t("reentry.save")); } catch {} }
  async function addCustom() {
    if (!customTitle.trim()) return;
    const title = customTitle;
    const local = { _id: `local-${Date.now()}`, title, status: "not_started", is_custom: true };
    setCustom((c) => [...c, local]);
    setCustomTitle("");
    try { await api("/api/reentry/reentry_checklist/custom_steps", { method: "POST", body: { title } }); } catch {}
  }
  async function loadTips(stepId) {
    setOpenTips((o) => ({ ...o, [stepId]: !o[stepId] }));
    try { const d = await api(`/api/reentry/reentry_checklist/steps/${stepId}/tips`); setTips((x) => ({ ...x, [stepId]: d.tips || [] })); } catch {}
  }
  async function sendTip(stepId) {
    const body = (tipText[stepId] || "").trim();
    if (!body) return;
    try {
      const r = await api(`/api/reentry/reentry_checklist/steps/${stepId}/tips`, { method: "POST", body: { body } });
      if (r.status === "published") setTips((x) => ({ ...x, [stepId]: [...(x[stepId] || []), r] }));
      setServerMsg(r.moderation?.reply || "");
    } catch (e) { setServerMsg(e.message); }
    setTipText((x) => ({ ...x, [stepId]: "" }));
  }

  return (
    <section>
      <h1>{t("nav.reentry")}</h1>
      <h2>{t("reentry.checklistTitle")}</h2>
      <div data-testid="checklist-crisis">
        <p>{t("reentry.crisisStep")}</p>
        <a href="tel:988">{t("crisis.call988")}</a>{" · "}<a href="sms:988">{t("crisis.text988")}</a>{" · "}<a href="tel:911">{t("crisis.call911")}</a>
        <TranslationCheck keys={["reentry.crisisStep", "crisis.call988", "crisis.text988", "crisis.call911"]} />
      </div>
      <p data-testid="overall-progress">{t("reentry.progress")}: {totalDone}/33</p>
      {celebrations.length > 0 && (
        <div data-testid="celebrations" role="status">
          {celebrations.map((c, i) => <p key={i}>{c.type === "first_step" ? t("reentry.celebrationFirst") : c.type === "all_complete" ? t("reentry.celebrationAll") : `${t("reentry.celebrationSection")}: ${t(`reentry.sections.${c.section}`)}`}</p>)}
        </div>
      )}
      {REENTRY_SECTIONS.map((sec) => {
        const sp = sections.find((s) => s.id === sec.id);
        return (
          <div key={sec.id} data-testid={`section-${sec.id}`}>
            <h3>{t(`reentry.sections.${sec.id}`)} — {sp.done}/{sp.total} ({sp.percent}%)</h3>
            <ul>
              {REENTRY_STEPS.filter((s) => s.section === sec.id).map((step) => {
                const m = meta[step.id] || { due_date: "", priority: "normal", notes: "" };
                const stepTips = tips[step.id] || [];
                return (
                  <li key={step.id} data-testid={`step-${step.id}`}>
                    <span>{step.id}. {t(`reentry.steps.step${step.id}`)}</span>
                    <ReadAloud text={t(`reentry.steps.step${step.id}`)} />
                    <button type="button" onClick={() => toggle(step)}>{done.has(step.id) ? t("reentry.done") : t("reentry.markDone")}</button>
                    <label>{t("reentry.dueDate")} <input type="date" aria-label={`${t("reentry.dueDate")} ${step.id}`} value={m.due_date} onChange={(e) => updateMeta(step.id, { due_date: e.target.value })} /></label>
                    <label>{t("reentry.priority")} <select aria-label={`${t("reentry.priority")} ${step.id}`} value={m.priority} onChange={(e) => updateMeta(step.id, { priority: e.target.value })}><option value="low">{t("reentry.priorityLow")}</option><option value="normal">{t("reentry.priorityNormal")}</option><option value="high">{t("reentry.priorityHigh")}</option></select></label>
                    <label>{t("reentry.notes")} <input aria-label={`${t("reentry.notes")} ${step.id}`} value={m.notes} onChange={(e) => updateMeta(step.id, { notes: e.target.value })} /></label>
                    <button type="button" onClick={() => saveMeta(step)}>{t("reentry.save")}</button>
                    {step.resource_pointer && <p>{t("reentry.resourceOnly")} <a href="tel:211">{t("reentry.call211")}</a></p>}
                    {step.resource_pointer && <TranslationCheck keys="reentry.call211" />}
                    {step.id === 11 && <p data-testid="step11-crisis"><a href="tel:988">{t("crisis.call988")}</a>{" · "}<a href="tel:911">{t("crisis.call911")}</a></p>}
                    {step.id === 11 && <TranslationCheck keys={["crisis.call988", "crisis.call911"]} />}
                    <button type="button" onClick={() => loadTips(step.id)}>{t("reentry.tipsTitle")}</button>
                    {openTips[step.id] && (
                      <div data-testid={`tips-${step.id}`}>
                        <p>{t("reentry.tipsAnonymous")}</p>
                        {stepTips.length === 0 ? <p>{t("reentry.noTips")}</p> : <ul>{stepTips.map((tip, i) => <li key={tip._id || i}>{tip.body} — Anonymous</li>)}</ul>}
                        <label>{t("reentry.addTip")} <input aria-label={`${t("reentry.addTip")} ${step.id}`} value={tipText[step.id] || ""} onChange={(e) => setTipText((x) => ({ ...x, [step.id]: e.target.value }))} placeholder={t("reentry.tipPlaceholder")} /></label>
                        <button type="button" onClick={() => sendTip(step.id)}>{t("reentry.sendTip")}</button>
                      </div>
                    )}
                  </li>
                );
              })}
            </ul>
          </div>
        );
      })}
      <h3>{t("reentry.mySteps")}</h3>
      <label>{t("reentry.addStep")} <input value={customTitle} onChange={(e) => setCustomTitle(e.target.value)} placeholder={t("reentry.addStepPlaceholder")} /></label>
      <button type="button" onClick={addCustom}>{t("reentry.addStep")}</button>
      <ul>{custom.map((c) => <li key={c._id}>{c.title}</li>)}</ul>
      <p>{t("reentry.milestones")}: 30, 60, 90, 180, 365</p>
      {serverMsg && <p role="status">{serverMsg}</p>}
    </section>
  );
}
