import { useState } from "react";
import { useTranslation } from "react-i18next";
import ReadAloud from "../components/ReadAloud";
import { COURSES } from "../data/phase3";
import { api } from "../api";
import TranslationCheck from "../components/TranslationCheck";
export default function LearnPage() {
  const { t } = useTranslation();
  const [msg, setMsg] = useState("");
  async function quiz(courseId, moduleId) {
    try { const r = await api("/api/learning/courses/quiz", { method: "POST", body: { course_id: courseId, module_id: moduleId, answer: 0 } }); setMsg(r.correct ? "✓" : "Try again"); } catch (e) { setMsg(e.message); }
  }
  return <section><h1>{t("nav.learning")}</h1><h2>{t("phase3.coursesTitle")}</h2><p>{t("phase3.paidNote")}</p><TranslationCheck keys="phase3.paidNote" />
    {COURSES.map((c) => <div key={c.id} data-testid={`course-${c.id}`}><h3>{t(`phase3.${c.key}`)} — {t("phase3.coursesDraft")}</h3><ReadAloud text={t(`phase3.${c.key}`)} /><p>{c.modules} module(s)</p>{c.id === "relapse_prevention" && <p>988 / 911</p>}<button type="button" onClick={() => quiz(c.id, c.id === "parole_navigation" ? "pn1" : c.id === "job_interviews" ? "ji1" : c.id === "relapse_prevention" ? "rp1" : "sb1")}>{t("phase3.checkAnswer")}</button></div>)}
    {msg && <p role="status">{msg}</p>}</section>;
}
