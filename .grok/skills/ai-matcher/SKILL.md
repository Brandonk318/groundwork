---
name: ai-matcher
description: Design and build the AI dating and friend matcher (registry #32, paid, upgraded) where each member's AI agent negotiates with candidates' agents before anyone is introduced, the member can see why a fit was rejected, override it, and rematch. Use when working on matching logic, agent negotiation, rejection reasons, overrides, rematch, or matching safety exclusions.
when-to-use: ai matcher, dating match, friend match, agent negotiation, why was this match rejected, override match, rematch
---

# AI matcher (agent negotiation)

## Flow
1. **Profile -> agent brief.** Member states intent (friend | dating | both), dealbreakers, must-haves, pace. The agent brief is built only from what the member typed into matching — never from posts, check-ins, vault, court dates or criminal history.
2. **Hard safety exclusions (run BEFORE any model call, deterministic code):**
   - mutual blocks, reports under review, no-contact/protective orders the member entered;
   - sponsor/sponsee and accountability-partner pairs; mentor/mentee;
   - minimum days-in-recovery for *dating* (value pending Brann — open-questions Q6; until set, dating mode stays OFF, friend mode only);
   - age 18+ verified for dating; excluded if either member set "friends only".
   Exclusions are never overridable and are shown to the member only as "not available" (never why the *other* person is excluded).
3. **Negotiation.** Agent A and agent B each get their own member's brief and exchange up to N short turns producing `{fit: accept|reject, reasons: [..], score}`. Neither agent sees the other's raw brief; only what that agent chooses to disclose.
4. **Explain.** Store per-candidate decision with plain-language reasons from *the member's own side* ("you said no smokers").
5. **Override.** Member can override a rejection; this sends a soft intro request, never an auto-match. The other member must still accept.
6. **Rematch.** If a match ends, member can rematch; the agent learns from member feedback (stored as preference edits the member can see and edit).

## Engineering rules
- Paid: `tiers.require(tier, "ai_matching")`. Respect locks: a member can lock matching (week/2wk/month/permanent) via app/locks.py.
- Model provider is TBD and costs money: stub behind an interface (`MatcherAgent.negotiate(brief_a, brief_b) -> Decision`) with a deterministic fake for tests. No API keys in code.
- Log decisions without PII; add `matches`, `match_decisions` to wipe.
- Tests: exclusions run before the agent; override cannot bypass exclusions; rejection reasons only reveal the viewer's side; dating disabled until min-days configured.
