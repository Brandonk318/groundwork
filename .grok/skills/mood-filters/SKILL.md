---
name: mood-filters
description: Build mood check-ins, mood-triggered filters, the daily filter reset, time-limited locks (week, two weeks, month), permanent locks, and the single one-month reminder for permanent locks with a don't-remind-again option, while guaranteeing nothing ever blocks the crisis button. Use when working on registry #19 mood_checkins, #33 filters, #34 locks, or anything that hides or limits app content.
when-to-use: mood check-in, mood filters, rough day, daily reset, lock feature, time-limited lock, permanent lock, lock reminder, don't remind again
---

# Mood, filters and locks

Policy already lives in `backend/app/locks.py` with tests in `backend/tests/test_safety.py`. Extend it; never weaken it.

## Rules
- **Mood check-ins** (free): quick pick + optional note. A rough mood (`rough`, `struggling`, `craving`) **suggests** filters; the member accepts or dismisses. Never auto-apply. A rough check-in also shows the crisis button prominently and the relapse protocol link — never a paywall.
- **Filters** (free, upgraded): apply for the member's local calendar day only (`set_on == today` in `America/Chicago` or the member's tz) and reset at local midnight.
- **Locks**: `week`=7, `two_weeks`=14, `month`=30 days, or `permanent`. A lock hides a feature from the member themself (e.g. matching, DMs, feed).
- **Permanent lock reminder**: exactly ONE reminder at +30 days unless `dont_remind`; after it's sent set `reminded=True`. Queue via `app/outbox.py`. The reminder offers keep / unlock / don't remind again.
- **Never lockable or filterable**: anything with `lock_exempt=True` in the registry (crisis_button, relapse_protocol, safe_call_contacts, data_wipe). `make_lock` raises `LockError`; `active_filters` drops them. Keep both checks.
- Early unlock of a time-limited lock: allowed, with a calm confirm (no guilt copy). Brann may later want a cool-off delay — leave a config hook, default off.
- Storage: `mood_checkins`, `filters`, `locks` collections — already in `app/wipe.py`.

## Steps
1. Add API in `app/routers/wellbeing.py`: `POST /api/wellbeing/mood_checkins`, `GET/POST/DELETE /api/wellbeing/filters`, `GET/POST/DELETE /api/wellbeing/locks`, `POST .../locks/{id}/dont_remind`.
2. Add a gate helper used by every feature router: `if feature_locked(user, feature_id): 423` — skipped for lock-exempt ids.
3. Frontend: check-in sheet, suggested-filters card, locks screen. Crisis button stays in Shell regardless.
4. Tests: rough mood suggests, doesn't apply; filter gone next day; each lock duration; one reminder only; dont_remind honored; crisis reachable with every lock/filter on.
