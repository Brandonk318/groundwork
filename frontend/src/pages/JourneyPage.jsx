import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { api } from "../api";
import ReadAloud from "../components/ReadAloud";
import { MILESTONE_DAYS } from "../lib/mood";
export default function JourneyPage() {
  const { t } = useTranslation();
  const [start, setStart] = useState("2024-01-01");
  const [result, setResult] = useState(null);
  const [balance, setBalance] = useState(0);
  const [merch, setMerch] = useState([]);
  const [items, setItems] = useState([]);
  const [suggest, setSuggest] = useState([]);
  const [title, setTitle] = useState("");
  const [story, setStory] = useState("");
  const [vis, setVis] = useState("private");
  const [editing, setEditing] = useState(null);
  const [sharing, setSharing] = useState(null);
  const localSeq = useRef(0);
  const [shareUrl, setShareUrl] = useState("");
  const [goals, setGoals] = useState([]);
  const [gname, setGname] = useState("");
  const [target, setTarget] = useState("");
  const [monthly, setMonthly] = useState("");
  const [calc, setCalc] = useState(null);
  const [plan, setPlan] = useState([]);
  const [msg, setMsg] = useState("");
  async function loadPortfolio() {
    try { setItems((await api("/api/journey/journey_portfolio/items")).items || []); } catch {}
    try { setSuggest((await api("/api/journey/journey_portfolio/suggestions")).suggestions || []); } catch {}
  }
  useEffect(() => {
    loadPortfolio();
    api("/api/journey/token_rewards").then((d) => setBalance(d.balance ?? 0)).catch(() => {});
    api("/api/journey/merch_rewards").then((d) => setMerch(d.items || [])).catch(() => {});
    api("/api/journey/housing_savings/goals").then((d) => setGoals(d.goals || [])).catch(() => {});
    api("/api/journey/housing_savings/plan").then((d) => setPlan(d.steps || [])).catch(() => {});
  }, []);
  async function save() { try { setResult(await api("/api/journey/milestone_celebrations", { method: "POST", body: { kind: "sobriety", start_date: start } })); } catch {} }
  async function earn() { try { const r = await api("/api/journey/token_rewards/earn", { method: "POST", body: { reason: "checkin", points: 10 } }); setBalance(r.balance); } catch (e) { setMsg(e.message); } }
  async function addGoal() {
    try { const g = await api("/api/journey/housing_savings/goals", { method: "POST", body: { name: gname, target_cents: Math.round(Number(target || 0) * 100), saved_cents: 0 } }); setGoals((x) => [...x, g]); setGname(""); setTarget(""); }
    catch (e) { setMsg(e.message); }
  }
  async function runCalc() {
    try { setCalc(await api("/api/journey/housing_savings/calculator", { method: "POST", body: { target_cents: Math.round(Number(target || 0) * 100), saved_cents: 0, monthly_cents: Math.round(Number(monthly || 1) * 100) } })); }
    catch { const tc = Number(target || 0), mc = Number(monthly || 1); setCalc({ months: mc > 0 ? Math.ceil(tc / mc) : 0 }); }
  }
  async function checkStep(id, done) { try { await api("/api/journey/housing_savings/plan/check", { method: "POST", body: { step_id: id, done: !done } }); setPlan((p) => p.map((s) => s.id === id ? { ...s, done: !done } : s)); } catch {} }
  async function addItem() {
    if (!title.trim()) return;
    try { await api("/api/journey/journey_portfolio/items", { method: "POST", body: { title, story, visibility: vis } }); }
    catch { localSeq.current += 1; const lid = `local-${Date.now()}-${localSeq.current}`; setItems((x) => [...x, { _id: lid, title, story, visibility: vis, position: x.length }]); }
    setTitle(""); setStory(""); loadPortfolio();
  }
  async function saveEdit() {
    if (!editing) return;
    const snapshot = { ...editing };
    try { await api(`/api/journey/journey_portfolio/items/${editing._id}`, { method: "PATCH", body: { title: editing.title, story: editing.story, visibility: editing.visibility } }); }
    catch { setItems((x) => x.map((it) => it._id === snapshot._id ? { ...it, ...snapshot } : it)); }
    setEditing(null); loadPortfolio();
  }
  async function delItem(id) { try { await api(`/api/journey/journey_portfolio/items/${id}`, { method: "DELETE" }); } catch {} loadPortfolio(); }
  async function move(id, dir) {
    const order = items.map((x) => x._id);
    const i = order.indexOf(id);
    const j = i + dir;
    if (i < 0 || j < 0 || j >= order.length) return;
    [order[i], order[j]] = [order[j], order[i]];
    setItems(order.map((oid) => items.find((x) => x._id === oid)));
    try { await api("/api/journey/journey_portfolio/reorder", { method: "POST", body: { order } }); } catch {}
  }
  async function mint(item) {
    try { const r = await api("/api/journey/journey_portfolio/share", { method: "POST", body: { item_id: item._id } }); setShareUrl(r.url); }
    catch (e) { setMsg(e.message); }
    setSharing(item);
  }
  async function revoke(item) {
    try { await api("/api/journey/journey_portfolio/share", { method: "POST", body: { item_id: item._id, revoke: true } }); setShareUrl(""); } catch (e) { setMsg(e.message); }
    loadPortfolio();
  }
  return (
    <section>
      <h1>{t("nav.journey")}</h1>
      <h2>{t("journey.milestonesTitle")}</h2>
      <p>{t("journey.milestoneDays")}: {MILESTONE_DAYS.join(", ")}</p>
      <label>{t("journey.startDate")} <input type="date" value={start} onChange={(e) => setStart(e.target.value)} /></label>
      <button type="button" onClick={save}>{t("journey.save")}</button>
      {result && <p role="status">{t("journey.days")}: {result.days} — {t("journey.reached")}: {(result.reached || []).join(", ") || "—"}</p>}
      <div data-testid="portfolio-section"><h2>{t("journey.portfolioTitle")}</h2>
      <p>{t("journey.portfolioPrivate")}</p><ReadAloud text={t("journey.portfolioPrivate")} />
      {suggest.length > 0 && (<div data-testid="portfolio-suggest"><h3>{t("phase3.suggestTitle")}</h3><p>{t("phase3.suggestHelp")}</p>
        <ul>{suggest.map((s) => <li key={s.milestone_day}>Day {s.milestone_day}</li>)}</ul></div>)}
      <label>{t("phase3.portfolioTitle")} <input value={title} onChange={(e) => setTitle(e.target.value)} /></label>
      <label>{t("phase3.portfolioStory")} <textarea value={story} onChange={(e) => setStory(e.target.value)} /></label>
      <label>{t("phase3.portfolioVisibility")} <select value={vis} onChange={(e) => setVis(e.target.value)}>
        <option value="private">{t("phase3.visPrivate")}</option><option value="family">{t("phase3.visFamily")}</option>
        <option value="members">{t("phase3.visMembers")}</option><option value="link">{t("phase3.visLink")}</option></select></label>
      <button type="button" onClick={addItem}>{t("phase3.portfolioAdd")}</button>
      <ul>{items.map((it) => (
        <li key={it._id} data-testid={`portfolio-${it._id}`}>
          {editing?._id === it._id ? (<span>
            <input aria-label="edit title" value={editing.title} onChange={(e) => setEditing({ ...editing, title: e.target.value })} />
            <button type="button" onClick={saveEdit}>{t("phase3.save")}</button>
            <button type="button" onClick={() => setEditing(null)}>{t("phase3.cancel")}</button>
          </span>) : (<span><strong>{it.title}</strong> ({it.visibility}) <ReadAloud text={it.title} />
            <button type="button" onClick={() => setEditing(it)}>{t("phase3.portfolioEdit")}</button>
            <button type="button" onClick={() => move(it._id, -1)}>{t("phase3.moveUp")}</button>
            <button type="button" onClick={() => move(it._id, 1)}>{t("phase3.moveDown")}</button>
            <button type="button" onClick={() => mint(it)}>{t("phase3.shareDialog")}</button>
            <button type="button" onClick={() => delItem(it._id)}>{t("phase3.portfolioDelete")}</button>
          </span>)}
        </li>))}
      </ul>
      {sharing && (<div role="dialog" aria-label={t("phase3.shareDialog")} data-testid="share-dialog">
        <p>{t("phase3.shareWho")}</p>
        {shareUrl && <p>{shareUrl}</p>}
        <button type="button" onClick={() => mint(sharing)}>{t("phase3.mintLink")}</button>
        <button type="button" onClick={() => revoke(sharing)}>{t("phase3.revokeLink")}</button>
        <button type="button" onClick={() => { setSharing(null); setShareUrl(""); }}>{t("phase3.cancel")}</button>
      </div>)}
      </div>
      <div data-testid="tokens-section"><h2>{t("phase3.tokensTitle")}</h2><p>{t("phase3.tokensHelp")}</p><ReadAloud text={t("phase3.tokensHelp")} />
        <p>{t("phase3.balance")}: {balance}</p><button type="button" onClick={earn}>{t("phase3.earn")}</button></div>
      <div data-testid="merch-section"><h2>{t("phase3.merchTitle")}</h2><p>{t("phase3.merchHelp")}</p><ReadAloud text={t("phase3.merchHelp")} />
        <ul>{merch.map((m) => <li key={m.id}>{m.name} — {m.code}</li>)}</ul></div>
      <div data-testid="share-section"><h2>{t("phase3.shareTitle")}</h2><p>{t("phase3.shareHelp")}</p><ReadAloud text={t("phase3.shareHelp")} /></div>
      <div data-testid="archive-section"><h2>{t("phase3.archiveTitle")}</h2><p>{t("phase3.archiveHelp")}</p><ReadAloud text={t("phase3.archiveHelp")} /></div>
      <div data-testid="housing-section"><h2>{t("phase3.housingTitle")}</h2><p>{t("phase3.housingHelp")}</p><ReadAloud text={t("phase3.housingHelp")} />
        <h3>{t("phase3.calcTitle")}</h3>
        <label>{t("phase3.goalTarget")} <input value={target} onChange={(e) => setTarget(e.target.value)} inputMode="decimal" /></label>
        <label>{t("phase3.calcMonthly")} <input value={monthly} onChange={(e) => setMonthly(e.target.value)} inputMode="decimal" /></label>
        <button type="button" onClick={runCalc}>{t("phase3.calcRun")}</button>
        {calc && <p role="status">{calc.months} {t("phase3.calcResult")}</p>}
        <h3>{t("phase3.goalName")}</h3>
        <label>{t("phase3.goalName")} <input value={gname} onChange={(e) => setGname(e.target.value)} /></label>
        <button type="button" onClick={addGoal}>{t("phase3.addGoal")}</button>
        <ul>{goals.map((g) => <li key={g._id}>{g.name}</li>)}</ul>
        <h3>{t("phase3.planTitle")}</h3>
        <ul>{plan.map((s) => <li key={s.id}><label><input type="checkbox" checked={!!s.done} onChange={() => checkStep(s.id, s.done)} /> {s.title}</label></li>)}</ul>
        <p><a href="tel:211">{t("phase3.call211")}</a></p></div>
      {msg && <p role="status">{msg}</p>}
    </section>
  );
}
