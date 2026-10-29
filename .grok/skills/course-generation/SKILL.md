---
name: course-generation
description: Generate life-skills course material for the reentry/recovery app (outlines, voice scripts, visual specs, quiz questions) in the Contractor Academy format so it drops into the reused video pipeline and quiz engine. Use when asked to write, outline, script or quiz a course or module (parole navigation, job interviews, relapse prevention, starting a small business, or new topics).
when-to-use: write a course, course outline, module script, quiz questions, life skills course, parole navigation course, job interview course, relapse prevention course, small business course
---

# Course generation (academy format, fresh curriculum)

Courses run on the Contractor Academy engine (video clips + voice quiz). The format comes from the academy; the curriculum here is new. Reference: `/workspace/momo-academy/docs/contractor-academy-spec.md` (format only — don't copy its contractor content).

## Starter tracks (from Brann's spec)
1. Parole navigation  2. Job interviews  3. Relapse prevention  4. Starting a small business
Propose 4–6 modules per track. Mark everything **DRAFT — for Brann's review**.

## Per module, produce exactly
1. **Learning objective**: one sentence, observable ("List three…", "Practice…").
2. **4 script beats**: voice style below. Beat 4 is an out-loud engagement question with a pause.
3. Lead-in: `Are you ready? ... [beat of silence] ... Here we go.`
4. **Action step**: in its own section, `[chime]` before it. One concrete thing to do today.
5. **3 visual specs**: each drawable in 5 seconds (counters, before/after, flow arrows, checklists).
6. **Quiz**: 3 questions — 1 voice question (open answer, with what a good answer contains) + 2 multiple choice (4 options, one correct, a short why for each wrong one).

## Voice style
- Sentences ≤ ~15 words, front-load the verb, `...` for pauses, a strong pause every 4–5 lines.
- 60–90 second clip, one concept. If a sentence can't be drawn in 5 seconds, rewrite it.
- Person-first, no shame: "returning citizen", "person in recovery", "a slip" (not "failure").

## Output shape (JSON for the quiz engine, plus markdown for review)
```json
{"track": "job_interviews", "module": 1, "title": "", "objective": "", "beats": ["", "", "", ""],
 "action_step": "", "visuals": ["", "", ""],
 "quiz": [{"type": "voice", "prompt": "", "good_answer_includes": [""]},
          {"type": "mc", "prompt": "", "options": ["", "", "", ""], "answer": 0, "why_wrong": ["", "", ""]}]}
```

## Guardrails
- Parole/probation content: general info only; always "check your specific conditions with your officer". Conditions vary; some restrict self-employment — say so in the small-business track.
- Relapse prevention: not clinical advice; every module ends with "If you're in crisis, call or text 988. Emergency: 911." Have a peer specialist or clinician review before publishing.
- Texas trades: cosmetology, electrical, ACR need TDLR licenses (criminal-history evaluation available); roofing, GC, painting, landscaping, carpentry, concrete need no state license. Bonding: standard surety bonds often screen out felonies — flag, don't promise.
- No legal/tax advice. Never reference Brann's 33 reentry steps unless they're in `backend/app/data/reentry_steps.json`.
- Save drafts to `content/courses/<track>/module-<n>.{md,json}`; never publish.
