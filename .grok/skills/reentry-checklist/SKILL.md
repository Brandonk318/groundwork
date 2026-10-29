---
name: reentry-checklist
description: Walk a returning citizen (someone coming home from jail or prison) through Brann's 33-step reentry process, track which steps are done, and turn the next steps into a plain action plan. Use when the user mentions reentry, coming home, release planning, the 33 steps, or building reentry features into the recovery/reentry social app.
when-to-use: reentry checklist, 33-step reentry, release plan, returning citizen, what do I do after release, reentry tracker feature
---

# Reentry checklist

Help a person (or a feature of the reentry app) move through the 33-step reentry process one step at a time.

## Source of truth
1. Read `references/33-steps.md` first. It holds Brann's own 33-step list.
2. If that file still says `PASTE THE 33 STEPS HERE`, stop and ask the user for the list. Never invent the 33 steps or fill gaps with guesses.

## How to run it
1. Ask where the person is: days until or since release, state or county, and which steps are already done.
2. Show the full list with each step marked done, in progress, or not started.
3. Pick the next 3 steps that unlock the most (an ID usually unlocks a bank account, a job and housing applications).
4. For each of those 3 steps, give: what it is, what documents or info it needs, where to go (look up the real local office or website and link it; say so if you can't confirm it), and a realistic time estimate.
5. End with one sentence on the single thing to do today.

## Rules
- Plain, respectful, non-judgmental words. Say "returning citizen" or "person coming home", never "ex-con" or "inmate".
- Parole or probation conditions come first. If a step could conflict with supervision terms, tell them to check with their officer.
- Don't give legal advice. For record sealing, expungement or court matters, point to legal aid and say it's general info.
- Keep personal details (case numbers, addresses, SSN) out of shared or public output.

## In the app
When building this as an app feature, model each step as {id, title, category, depends_on, documents_needed, status, due_date} so progress can be tracked and nudged.
