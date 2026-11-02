# Translation Plan

Target: 21 languages.

Full set (21): en, es, fr, ht, ar, vi, tl, hi, zh (Simplified), ko, pt, so, ur, bn, pa, fa, am, my, ne, sw, ru. RTL: ar, ur, fa.

- Done: en (source) only. Russian (ru) is NOT done: Brann is finishing it himself (in progress).
- Not done (files still hold English text as of 2026-11-01): es (Muse translating now), fr, ht, ar, vi, tl, hi, zh, ko, pt, so, ur, bn, pa, fa, am, my, ne, sw
- Builder: Muse Code (after Phase 5-8 build)

Rules:
- Every locale must have full key parity with en, enforced by an automated missing-text test that fails the build if any key is missing.
- Crisis/safety text (988/911 and similar) stays flagged for human review; machine translation alone is not accepted for it.
- Commits are local only. No push, merge, or deploy without Brann's OK.

Update 2026-10-30: Russian (ru) removed from the target list per Brann (US sanctions; not marketed or prospected). Existing ru files are left in place, not deleted.

Correction 2026-11-01 (Brann): Russian was NOT cut from Groundwork. It stays in the 21-language set. It is NOT finished; Brann is translating it himself. Don't machine-translate it or mark it done. Burmese (my) stays in Groundwork for now.


## Russian vs. Russia (update 2026-11-01, per Brann)
- Russian (ru) stays a **translation target**, because there are many Russian speakers outside Russia. Do not remove Russian from the language list.
- Russia itself is **not a marketing or prospecting target** because of US sanctions.
- Russian is translated by Grok Bot or Muse like the other languages. Never mark it done without counting strings that still match English.
- Iran and Myanmar keep their do-not-target flags, unchanged.
- This replaces the 2026-10-30 note that dropped Russian from the target list.
