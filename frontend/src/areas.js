// One placeholder page per feature area. Feature ids match backend/app/registry.py.
export const AREAS = [
  { path: "feed", key: "community", features: ["community_feed", "anonymous_posting", "program_groups", "peer_messaging", "video_posts", "photo_posts", "voice_notes", "anonymous_qa", "events", "virtual_meetings"] },
  { path: "reentry", key: "reentry", features: ["reentry_checklist", "court_calendar"] },
  { path: "work", key: "work", features: ["job_board", "resume_builder", "interview_coach", "application_tracker", "micro_gigs"] },
  { path: "support", key: "support", features: ["resource_directory", "mentorship", "twelve_step_locator", "counseling_referrals", "geolocation", "needs_a_ride", "accountability_partners", "carpool_board", "community_groups_directory"] },
  { path: "journey", key: "journey", features: ["journey_portfolio", "milestone_celebrations", "token_rewards", "merch_rewards", "progress_share_card", "day_one_archive", "housing_savings"] },
  { path: "wellbeing", key: "wellbeing", features: ["mood_checkins", "filters", "locks"] },
  { path: "safety", key: "safety", features: ["relapse_protocol", "safe_call_contacts", "document_vault", "data_wipe"] },
  { path: "learn", key: "learning", features: ["courses", "courses_life_skills"] },
  { path: "match", key: "matching", features: ["ai_matching"] },
  { path: "venue", key: "venue", features: ["virtual_venue"] },
  { path: "family", key: "family", features: ["family_mode"] },
  { path: "settings", key: "platform", features: ["read_aloud", "multi_language", "music_player"] },
];
// crisis_button is not an area: it is on every screen (components/CrisisButton.jsx).
