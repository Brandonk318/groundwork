# AGENTS.md: rules for Grok Build and any coding agent in this repo

**Project:** a reentry and recovery social app (working name in `backend/app/config.py` DEFAULT_APP_NAME and `frontend/src/brand.js`; never hard-code it anywhere else). It's a separate project from Trade Circle, Momoempire and Mind At Ease. Patterns are borrowed from Trade Circle; no code is shared at runtime.

## Stack
- Backend: FastAPI + MongoDB (motor), Python 3.13. `cd backend && .venv/bin/python -m pytest -q`
- Frontend: React 19 + Vite + react-router + i18next. `cd frontend && npx vitest run`
- Tests use mongomock-motor. Node 20 on the box, so jsdom is pinned at 26.

## Conventions
- `backend/app/registry.py` is the single source of truth for the 45 features. When a module goes from stub to working, flip its `status` and update docs/features.md.
- `backend/app/tiers.py` is the only place plans live. Never invent prices; `None` means Brann hasn't decided. Unassigned tiers stay unassigned until Brann assigns them.
- One router file per feature group (`app/routers/<group>.py`). Unbuilt features answer 501 through `_stub.py`.
- Every UI string goes in `frontend/src/locales/en/*.json`. Other locales fall back to English until a human translates them. Arabic is RTL, so use CSS logical properties (`inline-start`/`inline-end`) and never `left`/`right`.
- Every collection holding member data must be added to `app/wipe.py` USER_COLLECTIONS. The wipe test enforces this.
- Use person-first language: "returning citizen", "person in recovery".

## Never
- **Never invent Brann's 33 reentry steps.** They live in `backend/app/data/reentry_steps.json`, which is empty until he supplies them. If they're needed and missing, stop and ask.
- Never write clinical or relapse-protocol content as final. Leave it as a draft for review.
- No pushes, remotes, GitHub repo creation, deploys, signups, paid APIs or spending without Brann's explicit OK. Local commits only.
- Never commit secrets. Config comes from `GW_*` env vars.

## Safety defaults (tests pin these; do not weaken them)
1. The crisis button and relapse protocol are always free, never behind a paywall, and never hidden by locks or filters (`always_free`, `lock_exempt`).
2. The crisis surfaces show **988** (call or text) and **911**. The crisis button renders on every screen (Shell).
3. Peer messaging never exposes phone numbers. Use `safety.public_member()` for any other-member payload.
4. Anonymous posts are anonymous to other members. Use `safety.public_post()`, which strips author id, handle, avatar and location.
5. The document vault is encrypted at rest with a per-user DEK wrapped by the server KEK (`vault_crypto.py`). No plaintext on disk.
6. One-tap wipe really deletes, and crypto-shreds the vault key. It's not a soft delete.
7. Family mode visibility is controlled by the member, and every share defaults to off.
8. The journey portfolio is private by default.
9. Locks and filters can never block lock-exempt features (crisis, relapse, safe-call contacts, wipe).

## Project skills
`.grok/skills/` holds the project skills: reentry-checklist, recovery-moderation, milestone-merch, sober-venue-web, course-generation, journey-portfolio, ai-matcher, mood-filters and venue-threejs.
