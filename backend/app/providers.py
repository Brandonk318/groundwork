"""Pluggable local providers. No external APIs or keys. Swap class to use a real provider later."""
from dataclasses import dataclass, field

INTERVIEW_QUESTIONS = [
    {"id": "q1", "prompt": "Tell me about a time you solved a problem at work.", "keywords": ["example", "learned", "result", "helped", "finished"]},
    {"id": "q2", "prompt": "How do you handle a disagreement with a coworker?", "keywords": ["listen", "calm", "talk", "respect", "solution"]},
    {"id": "q3", "prompt": "Why should we hire you for this role?", "keywords": ["reliable", "safety", "team", "show up", "learn"]},
]

class InterviewCoachProvider:
    name = "deterministic-local-v1"
    def score(self, question_id: str, answer: str) -> dict:
        q = next((x for x in INTERVIEW_QUESTIONS if x["id"] == question_id), INTERVIEW_QUESTIONS[0])
        low = (answer or "").lower()
        hits = [k for k in q["keywords"] if k in low]
        length_bonus = 20 if len(answer or "") >= 120 else 10 if len(answer or "") >= 50 else 0
        score = min(100, 30 + len(hits) * 12 + length_bonus)
        tips = []
        if len(hits) < 2: tips.append("Add a concrete example and what you learned.")
        if len(answer or "") < 50: tips.append("Say a little more: situation, action, result.")
        if not tips: tips.append("Strong answer. Keep that example ready.")
        return {"score": score, "matched": hits, "tips": tips, "provider": self.name}

@dataclass
class MatcherAgent:
    """Deterministic fake behind the negotiation interface (ai-matcher skill)."""
    name: str = "deterministic-local-v1"
    def negotiate(self, brief_a: dict, brief_b: dict) -> dict:
        a_int = set(x.lower() for x in brief_a.get("interests", []))
        b_int = set(x.lower() for x in brief_b.get("interests", []))
        shared = sorted(a_int & b_int)
        # Dealbreakers are checked against the OTHER brief's disclosed attributes, from A's side only here.
        b_attrs = {str(v).lower() for v in brief_b.get("attributes", {}).values()}
        a_attrs = {str(v).lower() for v in brief_a.get("attributes", {}).values()}
        a_blocks = [d for d in brief_a.get("dealbreakers", []) if d.lower() in b_attrs]
        b_blocks = [d for d in brief_b.get("dealbreakers", []) if d.lower() in a_attrs]
        score = min(100, 40 + len(shared) * 15)
        if a_blocks or b_blocks:
            return {"fit": "reject", "score": score, "shared": shared, "a_blocks": a_blocks, "b_blocks": b_blocks, "provider": self.name}
        if score < 55:
            return {"fit": "reject", "score": score, "shared": shared, "a_blocks": [], "b_blocks": [], "provider": self.name}
        return {"fit": "accept", "score": score, "shared": shared, "a_blocks": [], "b_blocks": [], "provider": self.name}

COURSES = [
    {"id": "parole_navigation", "title": "Parole navigation (DRAFT — for Brann's review)", "draft": True, "modules": [
        {"id": "pn1", "title": "Know your conditions", "objective": "List three of your supervision conditions.", "content": "General information only. Always check your specific conditions with your officer.", "quiz": [{"prompt": "Who confirms your specific conditions?", "options": ["Your officer", "A coworker", "Social media", "No one"], "answer": 0}]},
        {"id": "pn2", "title": "Check-ins and calendars", "objective": "Put every check-in on a calendar.", "content": "Write down dates the day you get them.", "quiz": [{"prompt": "When should you record a check-in date?", "options": ["Next month", "The day you get it", "Never", "After it passes"], "answer": 1}]}]},
    {"id": "job_interviews", "title": "Job interviews (DRAFT — for Brann's review)", "draft": True, "modules": [
        {"id": "ji1", "title": "Tell your story briefly", "objective": "Practice a 60-second introduction.", "content": "Focus on skills, reliability, and what you can do now.", "quiz": [{"prompt": "A good intro focuses on?", "options": ["Skills you bring now", "Blaming others", "Case details", "Pay first"], "answer": 0}]}]},
    {"id": "relapse_prevention", "title": "Relapse prevention (DRAFT — for Brann's review)", "draft": True, "modules": [
        {"id": "rp1", "title": "Know your triggers", "objective": "Name three personal triggers and one plan for each.", "content": "Draft for peer-specialist review. Not clinical advice. If you're in crisis, call or text 988. Emergency: 911.", "quiz": [{"prompt": "If you're in crisis, what number do you call or text?", "options": ["988", "411", "0", "211"], "answer": 0}]}]},
    {"id": "small_business", "title": "Starting a small business (DRAFT — for Brann's review)", "draft": True, "modules": [
        {"id": "sb1", "title": "Check conditions first", "objective": "Check whether self-employment fits your supervision conditions.", "content": "Some conditions restrict self-employment. Check with your officer first.", "quiz": [{"prompt": "Before starting, check self-employment with?", "options": ["Your officer", "A customer", "No one", "A bank only"], "answer": 0}]}]},
]
