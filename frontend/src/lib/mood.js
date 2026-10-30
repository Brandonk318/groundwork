export const ROUGH_MOODS = ["rough", "struggling", "craving"];
export function suggestFilters(mood) { return ROUGH_MOODS.includes(mood) ? ["hide_triggering_content", "quiet_dms"] : []; }
export function isRough(mood) { return ROUGH_MOODS.includes(mood); }
export const MILESTONE_DAYS = [30, 60, 90, 180, 365];
export function reachedMilestones(days) { return MILESTONE_DAYS.filter((m) => days >= m); }
