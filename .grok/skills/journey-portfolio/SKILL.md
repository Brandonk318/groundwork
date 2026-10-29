---
name: journey-portfolio
description: Scaffold and build the journey portfolio module (registry #31, paid, upgraded): a curated timeline of milestones with photos and videos for any journey (sobriety, release, business, custody, credit, trade learning), private by default and shareable only when the member chooses. Use when building, extending or reviewing the portfolio feature, its API, models, UI, or share links.
when-to-use: journey portfolio, milestone timeline, portfolio module, share my journey, private timeline, portfolio share link
---

# Journey portfolio

## Rules that never bend
- **Private by default.** Every item and the portfolio itself start `visibility="private"`. Sharing is an explicit member action, per item or per portfolio.
- Visibility levels: `private` -> `family` (only family accounts the member approved, see family_mode) -> `members` -> `link` (unguessable token, revocable) . No public indexing; share pages send `noindex`.
- Paid feature: gate with `tiers.require(user_tier, "journey_portfolio")`. Milestone celebrations themselves stay free.
- Strip EXIF/GPS from photos and video metadata on upload. Never show dates of release/sobriety on shared views unless the member ticks "show dates".
- Add `portfolio_items` (and any new collection) to `app/wipe.py` USER_COLLECTIONS; media deletes with the wipe.

## Build steps
1. Model (`app/models.py` PortfolioItem exists): `{user_id, journey, title, story, happened_on, media: [{kind, key}], milestone_day, visibility, position, created_at}`. Journeys: sobriety, release, business, custody, credit, trade, other.
2. Router: replace the stub in `app/routers/journey.py` with `GET/POST/PATCH/DELETE /api/journey/journey_portfolio/items`, `POST .../share` (mint/revoke link token), `GET /p/{token}` (read-only shared view honoring visibility).
3. Reuse Trade Circle's portfolio ordering pattern (`position` + reorder endpoint) by reading `/tmp/tc/backend/app/routers/portfolio.py`; adapt, don't import.
4. Auto-suggest an item when a milestone hits (30/60/90/180/365) but never auto-publish it.
5. Frontend: `pages/AreaPage` -> real `Journey` page; timeline grouped by journey; share dialog states plainly who will see it.
6. Tests: default private; other members get 404 for private items; revoked link 404s; family sees only `family`+ items after member grants; wipe removes everything.
