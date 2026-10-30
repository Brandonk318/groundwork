export const COURSES = [
  { id: "parole_navigation", key: "parole", modules: 2 },
  { id: "job_interviews", key: "interviews", modules: 1 },
  { id: "relapse_prevention", key: "relapse", modules: 1 },
  { id: "small_business", key: "business", modules: 1 },
];
export const INTERVIEW_QUESTIONS = [
  { id: "q1", prompt: "Tell me about a time you solved a problem at work.", keywords: ["example", "learned", "result", "helped", "finished"] },
  { id: "q2", prompt: "How do you handle a disagreement with a coworker?", keywords: ["listen", "calm", "talk", "respect", "solution"] },
  { id: "q3", prompt: "Why should we hire you for this role?", keywords: ["reliable", "safety", "team", "show up", "learn"] },
];
export function scoreInterview(questionId, answer) {
  const q = INTERVIEW_QUESTIONS.find((x) => x.id === questionId) || INTERVIEW_QUESTIONS[0];
  const low = (answer || "").toLowerCase();
  const hits = q.keywords.filter((k) => low.includes(k));
  const bonus = (answer || "").length >= 120 ? 20 : (answer || "").length >= 50 ? 10 : 0;
  return { score: Math.min(100, 30 + hits.length * 12 + bonus), matched: hits };
}
export const MERCH = [
  { id: "mark-tee-30", milestone_day: 30, code: "one stripe at the hem", visible_text: "GROUNDWORK" },
  { id: "mark-hoodie-90", milestone_day: 90, code: "three stripes at the hem", visible_text: "GROUNDWORK" },
  { id: "mark-cap-180", milestone_day: 180, code: "small circle at the hem", visible_text: "GROUNDWORK" },
];
export const BANNED_VISIBLE = ["sober", "sobriety", "recovery", "addict", "jail", "prison", "clean time"];
export function merchIsDiscreet(item) { const blob = `${item.visible_text} ${item.code}`.toLowerCase(); return !BANNED_VISIBLE.some((b) => blob.includes(b)); }
export function coarseCity(city) { return { city: (city || "").trim(), precision: "city" }; }
export function tokenBalance(ledger) { return ledger.reduce((s, e) => s + e.points, 0); }
export function negotiate(a, b) {
  const shared = (a.interests || []).filter((x) => (b.interests || []).map((y) => y.toLowerCase()).includes(x.toLowerCase()));
  const aBlocks = (a.dealbreakers || []).filter((d) => Object.values(b.attributes || {}).map(String).map((s) => s.toLowerCase()).includes(d.toLowerCase()));
  const score = Math.min(100, 40 + shared.length * 15);
  if (aBlocks.length) return { fit: "reject", score, reasons: aBlocks.map((x) => `You listed ${x} as a dealbreaker.`) };
  return score >= 55 ? { fit: "accept", score, reasons: [`You share: ${shared.join(", ")}`] } : { fit: "reject", score, reasons: ["Not enough shared interests yet."] };
}
