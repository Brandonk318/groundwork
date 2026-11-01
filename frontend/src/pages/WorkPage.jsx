import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { api } from "../api";
import ReadAloud from "../components/ReadAloud";
import { INTERVIEW_QUESTIONS, scoreInterview } from "../data/phase3";
import TranslationCheck from "../components/TranslationCheck";
export default function WorkPage() {
  const { t } = useTranslation();
  const [jobs, setJobs] = useState([]);
  const [name, setName] = useState("");
  const [resume, setResume] = useState(null);
  const [qid, setQid] = useState("q1");
  const [answer, setAnswer] = useState("");
  const [score, setScore] = useState(null);
  const [gig, setGig] = useState("");
  const [msg, setMsg] = useState("");
  useEffect(() => { api("/api/work/job_board?second_chance=true").then((d) => setJobs(d.jobs || [])).catch(() => {}); }, []);
  async function build() {
    try { setResume(await api("/api/work/resume_builder", { method: "POST", body: { full_name: name || "Alex", headline: "", summary: "", skills: [], experience: [] } })); }
    catch { setResume({ full_name: name || "Alex", text: `${name || "Alex"}` }); }
  }
  async function grade() {
    const local = scoreInterview(qid, answer);
    try { setScore(await api("/api/work/interview_coach/sessions", { method: "POST", body: { question_id: qid, answer } })); }
    catch { setScore(local); }
  }
  async function postGig() { try { await api("/api/work/micro_gigs", { method: "POST", body: { title: gig, description: gig } }); setMsg(gig); setGig(""); } catch (e) { setMsg(e.message); } }
  return (
    <section>
      <h1>{t("nav.work")}</h1>
      <h2>{t("work.jobsTitle")}</h2>
      <p>{t("work.paroleNote")}</p>
      <TranslationCheck keys="work.paroleNote" />
      <ul>{jobs.map((j) => <li key={j.id}>{j.title} — {j.company}, {j.location}</li>)}</ul>
      <div data-testid="resume-section"><h2>{t("phase3.resumeTitle")}</h2><p>{t("phase3.resumeHelp")}</p><ReadAloud text={t("phase3.resumeHelp")} />
        <label>{t("phase3.fullName")} <input value={name} onChange={(e) => setName(e.target.value)} /></label>
        <button type="button" onClick={build}>{t("phase3.buildResume")}</button>
        {resume && <p role="status">{resume.full_name}</p>}</div>
      <div data-testid="interview-section"><h2>{t("phase3.interviewTitle")}</h2><p>{t("phase3.interviewHelp")}</p><ReadAloud text={t("phase3.interviewHelp")} />
        <label>Q <select value={qid} onChange={(e) => setQid(e.target.value)}>{INTERVIEW_QUESTIONS.map((q) => <option key={q.id} value={q.id}>{q.prompt}</option>)}</select></label>
        <label>{t("phase3.answer")} <textarea value={answer} onChange={(e) => setAnswer(e.target.value)} /></label>
        <button type="button" onClick={grade}>{t("phase3.score")}</button>
        {score && <p role="status">{score.score}</p>}</div>
      <div data-testid="gigs-section"><h2>{t("phase3.gigsTitle")}</h2><p>{t("phase3.gigsHelp")}</p><TranslationCheck keys="phase3.gigsHelp" /><ReadAloud text={t("phase3.gigsHelp")} />
        <label>{t("phase3.gigTitle")} <input value={gig} onChange={(e) => setGig(e.target.value)} /></label>
        <button type="button" onClick={postGig}>{t("phase3.postGig")}</button>
        {msg && <p role="status">{msg}</p>}</div>
    </section>
  );
}
