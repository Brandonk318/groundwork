import { useState } from "react";
import { useTranslation } from "react-i18next";
import ReadAloud from "../components/ReadAloud";
import { negotiate } from "../data/phase3";
import { api } from "../api";
export default function MatchPage() {
  const { t } = useTranslation();
  const [interests, setInterests] = useState("music, walking");
  const [results, setResults] = useState([]);
  const [msg, setMsg] = useState("");
  async function run() {
    try { const r = await api("/api/matching/ai_matching/run", { method: "POST" }); setResults(r.results || []); } catch (e) {
      // local deterministic preview so the page still explains the flow offline
      const demo = negotiate({ interests: interests.split(",").map((s) => s.trim()), dealbreakers: [] }, { interests: ["music"], attributes: {} });
      setResults([{ candidate: { handle: "demo" }, ...demo }]); setMsg(e.message);
    }
  }
  async function override(h) { try { await api("/api/matching/ai_matching/override", { method: "POST", body: { candidate_handle: h } }); setMsg(t("phase3.override")); } catch (e) { setMsg(e.message); } }
  return <section><h1>{t("nav.matching")}</h1><h2>{t("phase3.matchTitle")}</h2><p>{t("phase3.matchHelp")}</p><p>{t("phase3.datingOff")}</p><ReadAloud text={t("phase3.matchHelp")} />
    <label>{t("phase3.interests")} <input value={interests} onChange={(e) => setInterests(e.target.value)} /></label>
    <button type="button" onClick={run}>{t("phase3.findMatches")}</button>
    <button type="button" onClick={run}>{t("phase3.rematch")}</button>
    <ul>{results.map((r, i) => <li key={i}>{r.candidate?.handle} — {r.fit} ({r.score}) {(r.reasons || []).join(" ")} {r.fit === "reject" && <button type="button" onClick={() => override(r.candidate?.handle)}>{t("phase3.override")}</button>}</li>)}</ul>
    {msg && <p role="status">{msg}</p>}</section>;
}
