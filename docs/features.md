# Features: the 49

Source of truth: `backend/app/registry.py` (tests pin count, sides, tiers, build type). This table is generated from it plus the OSS candidates below; regenerate it when the registry changes.

**Counting notes (faithful to Brann's spec, 2026-10-28)**
- 18 reentry + 10 recovery + 21 own additions = 49 (45 from the original spec + 4 Phase 3 add-ons: `carpool_board`, `community_groups_directory`, `housing_savings`, `music_player`).
- **Courses appears twice** (reentry #14 and own-addition #45). Both entries stay in the registry, and both point at ONE module (`module="courses"`). So 49 registry entries map to 48 modules.
- **Community feed appears only once** in the spec (reentry #13). The brief said it overlapped; the closest overlap is video posts, photo posts, voice notes and anonymous posting, which all post into that one feed. Those keep their own entries.
- Getting the own additions to 17: "mood-triggered filters" + "daily reset of filters" = **one** feature (`filters`, the FREE-tier word), and "time-limited locks" + "permanent locks" + "one reminder after a month" = **one** feature (`locks`). Listed separately they would make 20 own additions and 48 total. See open-questions.md Q4.
- "Video hosting" (PAID) maps to `video_posts`.
- `relapse_protocol` is **free** because of the safety default, even though the spec's FREE list doesn't name it.
- Tier `unassigned` = Brann decides. No prices are set anywhere (`tiers.PLANS["paid"]["price_cents"] is None`).
- Upgraded (custom-built): journey_portfolio, ai_matching, community_feed, filters, virtual_venue. Everything else is stock. OSS candidates are named only; nothing is vendored or installed yet.

| # | id | Feature | Side | Tier | Build | Status | OSS candidate / approach |
|---|---|---|---|---|---|---|---|
| 1 | `reentry_checklist` | 33-step reentry checklist (milestones 30/60/90/180/365 days) | reentry | unassigned | stock | working | Plain Mongo model + step engine; no OSS needed (data from Brann) |
| 2 | `court_calendar` | Court-date calendar with reminders | reentry | unassigned | stock | working | FullCalendar (MIT core), rrule.js / python-dateutil rrule, ics export (ics.py) |
| 3 | `job_board` | Job board filtered to second-chance employers | reentry | unassigned | stock | working | Plain CRUD; seed lists from public fair-chance employer pledges (data, not code) |
| 4 | `resume_builder` | Resume builder | reentry | unassigned | stock | working | JSON Resume schema + themes (MIT); PDF via WeasyPrint or react-pdf |
| 5 | `interview_coach` | AI interview coach (mock sessions + scoring) | reentry | unassigned | stock | working | LLM provider (TBD) + whisper.cpp / faster-whisper for speech; scoring rubric in-house |
| 6 | `application_tracker` | Application tracker | reentry | unassigned | stock | working | Plain CRUD (kanban: dnd-kit, MIT) |
| 7 | `document_vault` | Encrypted document vault (IDs, release papers) | reentry | paid | stock | working | pyca/cryptography AES-GCM envelope (in place); libsodium alt; KMS later |
| 8 | `data_wipe` | One-tap data wipe (lock-exempt) | reentry | unassigned | stock | working | In-house delete + crypto-shred (app/wipe.py) |
| 9 | `resource_directory` | Resource directory (legal aid, treatment, transit; NOT food/housing) | reentry | free | stock | working | Open Referral HSDS schema; FindTreatment.gov (SAMHSA) data; 211 feeds |
| 10 | `mentorship` | Mentorship | reentry | unassigned | stock | working | Plain matching + scheduling (Cal.com self-host, AGPL, optional) |
| 11 | `twelve_step_locator` | Twelve-step meeting locator | reentry | free | stock | working | Meeting Guide spec / TSML (12 Step Meeting List, GPL) JSON feeds; Leaflet map |
| 12 | `counseling_referrals` | Counseling referrals | reentry | unassigned | stock | working | Open Referral HSDS + FindTreatment.gov locator data |
| 13 | `community_feed` | Community feed (one feed for everyone) | reentry | unassigned | upgraded | working | UPGRADED: custom (patterns from Trade Circle community feed) |
| 14 | `courses` | Courses | reentry | paid | stock | working | Contractor Academy engine (video pipeline + quiz) reused; hls.js player |
| 15 | `events` | Events | reentry | unassigned | stock | working | FullCalendar + ics; RSVP in-house |
| 16 | `token_rewards` | Token rewards | reentry | unassigned | stock | working | Plain points ledger (no crypto) |
| 17 | `read_aloud` | Read-aloud | reentry | free | stock | working | Web Speech API speechSynthesis; Piper TTS (MIT) fallback |
| 18 | `multi_language` | Multi-language (en, es, fr, hi, vi, ar, tl, ht) | reentry | free | stock | working | i18next + react-i18next (in place) |
| 19 | `mood_checkins` | Mood check-ins | recovery | free | stock | working | Plain model; charts via Recharts (MIT) |
| 20 | `crisis_button` | Crisis button (988 + 911) (always free, lock-exempt) | recovery | free | stock | working | tel:/sms: links to 988 and 911 (in place) |
| 21 | `geolocation` | Geolocation (opt-in) | recovery | unassigned | stock | working | Browser Geolocation API (opt-in); Leaflet + OpenStreetMap; coarse rounding |
| 22 | `anonymous_posting` | Anonymous posting | recovery | free | stock | working | Flag on feed posts + server-side author stripping (in place: safety.public_post) |
| 23 | `program_groups` | Program-specific groups | recovery | unassigned | stock | working | Plain groups model |
| 24 | `peer_messaging` | Peer messaging (no phone numbers exposed) | recovery | free | stock | working | FastAPI WebSockets or Matrix (Synapse, Apache-2.0) self-host |
| 25 | `milestone_celebrations` | Milestone celebrations | recovery | free | stock | working | Plain; confetti via canvas-confetti (ISC) |
| 26 | `needs_a_ride` | Needs-a-ride | recovery | unassigned | stock | working | Plain request board (no dispatch, no payments) |
| 27 | `safe_call_contacts` | Sponsor / safe-call contacts one tap away (lock-exempt) | recovery | unassigned | stock | working | tel:/sms: deep links; contacts stored encrypted |
| 28 | `virtual_meetings` | Virtual meetings | recovery | unassigned | stock | working | Jitsi Meet (Apache-2.0) or LiveKit (Apache-2.0) |
| 29 | `video_posts` | Video posts | own | paid | stock | working | tus resumable upload (tusd, MIT) + FFmpeg transcode + hls.js |
| 30 | `photo_posts` | Photo posts | own | unassigned | stock | working | Pillow / libvips; EXIF GPS stripping |
| 31 | `journey_portfolio` | Journey portfolio (private by default, shareable when ready) | own | paid | upgraded | working | UPGRADED: custom (reuse Trade Circle portfolio patterns) |
| 32 | `ai_matching` | AI dating + friend matching (agents negotiate first; see why, override, rematch) | own | paid | upgraded | working | UPGRADED: custom agent-negotiation matcher |
| 33 | `filters` | Mood-triggered filters + daily filter reset | own | free | upgraded | working | UPGRADED: custom (policy in app/locks.py) |
| 34 | `locks` | Locks: time-limited (week/2wk/month), permanent, one reminder after a month | own | unassigned | stock | working | In-house policy (app/locks.py) |
| 35 | `merch_rewards` | Merch rewards (discreet, limited drops per milestone; 30 + 90 day anchors) | own | unassigned | stock | working | SVG design templates in-house; fulfillment vendor TBD (needs Brann) |
| 36 | `virtual_venue` | Virtual venue preview (Three.js/WebGL 3D walkthrough) | own | paid | upgraded | working | UPGRADED: Three.js / react-three-fiber + drei; glTF from photogrammetry |
| 37 | `micro_gigs` | Micro-gig board | own | unassigned | stock | working | Plain board; payments later (Stripe Connect needs Brann's OK) |
| 38 | `accountability_partners` | Peer accountability partners (matched 2-to-1) | own | unassigned | stock | working | Plain 2-to-1 matching job |
| 39 | `relapse_protocol` | Relapse protocol (calm first 24 hours after a slip) (always free, lock-exempt) | own | free | stock | working | Static content (needs Brann's wording + review) |
| 40 | `voice_notes` | Voice notes | own | unassigned | stock | working | MediaRecorder API + Opus/WebM |
| 41 | `anonymous_qa` | Anonymous Q&A (further-along members answer newcomers) | own | unassigned | stock | working | Plain Q&A model (answer eligibility by days-in) |
| 42 | `progress_share_card` | Progress share card (one image of journey stats) | own | unassigned | stock | working | Satori/resvg or Pillow server-side render |
| 43 | `day_one_archive` | Day-one archive (sealed note/video, unlocks at a milestone) | own | unassigned | stock | working | Vault crypto + time/milestone unlock |
| 44 | `family_mode` | Family mode (separate login; member controls visibility) | own | unassigned | stock | working | Separate role + scoped tokens (app/security.py ROLES) |
| 45 | `courses_life_skills` | Courses: life skills (parole navigation, interviews, relapse prevention, small business) | own | paid | stock | working | Same as courses (module=courses) |
| 46 | `carpool_board` | Carpool board (opt-in, city-level; in-app messaging only) | own | unassigned | stock | working | Primary ride finder; tied to twelve_step_locator + community_groups_directory |
| 47 | `community_groups_directory` | Community groups directory (recovery, reentry, faith; sample data) | own | unassigned | stock | working | Separate from twelve_step_locator; SAMPLE seed data, no real listings |
| 48 | `housing_savings` | Housing savings (goals + readiness plan; 211 pointers only) | own | unassigned | stock | working | User-entered figures only; never provides housing |
| 49 | `music_player` | Music player (off in academy; sample tracks only) | own | unassigned | stock | working | No streaming accounts; auto-disabled on /learn routes |
