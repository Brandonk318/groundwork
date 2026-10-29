# Open questions (for Brann)

1. **Brann's 33 reentry steps.** They weren't provided. `backend/app/data/reentry_steps.json` and `.grok/skills/reentry-checklist/references/33-steps.md` are placeholders, and nobody invents them. Which steps land on the 30/60/90/180/365-day milestones?
2. **The 25 "unassigned" tiers.** Notable ones:
   - `locks`: filters are FREE but locks aren't on either list. Should locks be free too, since they're a safety tool?
   - `safe_call_contacts`: this is crisis-adjacent, so free is recommended.
   - `data_wipe`: free is recommended. A privacy escape hatch shouldn't be paywalled.
   - `community_feed`, `photo_posts`, `voice_notes`, `events`, `virtual_meetings`, `mentorship`, the work tools, `family_mode`, `merch_rewards`.
   - The paid price, and whether there's more than one paid plan. Nothing is priced in code.
3. **Anonymity vs. safety.** Anonymous posts hide the author from members. Can moderators or staff see who wrote an anonymous post when it signals a crisis or a threat? Is there a policy for law-enforcement requests? This decides whether author ids are stored at all and who can read them.
4. **Feature count.** The spec's own-additions list reads as 20 items if filters (2) and locks (3) are split out. The scaffold groups them so the total stays 45. Confirm, or the registry becomes 48.
5. **"Video hosting" = video posts?** Can short clips stay free, with paid covering storage or length? Do the day-one archive videos and portfolio videos count as video hosting?
6. **AI dating safety.** What are the minimum days in recovery before dating is unlocked (the "13th-stepping" risk)? What age verification? What are the hard exclusions (no-contact or protective orders, registry status, sponsor/sponsee pairs)? Does matching ever use criminal-history data? (Recommended: no.)
7. **One-tap wipe vs. retention.** Is there a legal hold or required audit retention? Backups need a purge window (for example 30 days), and that has to be stated on the wipe screen.
8. **Family mode.** Which appointments can be shared, and can court dates ever be visible? What happens when a member revokes a family member's access mid-session? Is family mode free?
9. **Crisis copy translations.** Who reviews non-English crisis text? Machine translation alone isn't acceptable for safety copy. 988 offers Spanish; what's the plan for the other languages?
10. **Final name.** Groundwork or Commissary Club. Rename means changing `backend/app/config.py` DEFAULT_APP_NAME and `frontend/src/brand.js`.
11. **Merch.** Fulfillment vendor, and whether drops are earned only or can also be bought.
12. **Micro-gigs and payments.** Who pays whom, platform fees, 1099s, and how parole self-employment limits are handled.
13. **Relapse protocol wording.** Brann's words plus a review by a peer specialist or clinician before launch.
