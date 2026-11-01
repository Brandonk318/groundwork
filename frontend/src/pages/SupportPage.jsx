import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { api } from "../api";
import ReadAloud from "../components/ReadAloud";
import TranslationCheck from "../components/TranslationCheck";
export default function SupportPage() {
  const { t } = useTranslation();
  const [resources, setResources] = useState([]);
  const [meetings, setMeetings] = useState([]);
  const [groups, setGroups] = useState([]);
  const [entries, setEntries] = useState([]);
  const [city, setCity] = useState("");
  const [meetingId, setMeetingId] = useState("m1");
  const [showFallback, setShowFallback] = useState(true);
  const [msg, setMsg] = useState("");
  const [contact, setContact] = useState("");
  const [contacts, setContacts] = useState([]);
  const [joined, setJoined] = useState(false);
  useEffect(() => {
    api("/api/support/resource_directory").then((d) => setResources(d.resources || [])).catch(() => {});
    api("/api/support/twelve_step_locator").then((d) => setMeetings(d.meetings || [])).catch(() => {});
    api("/api/support/community_groups_directory").then((d) => setGroups(d.groups || [])).catch(() => {});
  }, []);
  useEffect(() => {
    api(`/api/support/carpool_board/entries?meeting_id=${meetingId}`).then((d) => setEntries(d.entries || [])).catch(() => {});
    api(`/api/support/needs_a_ride/fallback?meeting_id=${meetingId}`).then((d) => setShowFallback(d.show_fallback)).catch(() => setShowFallback(true));
  }, [meetingId, msg]);
  async function joinCarpool() {
    try { await api("/api/support/carpool_board/entries", { method: "POST", body: { city: city || "Fort Worth", meeting_source: "twelve_step", meeting_id: meetingId } }); setMsg("ok"); }
    catch (e) { setMsg(e.message); }
  }
  async function joinPartners() { try { await api("/api/support/accountability_partners/join", { method: "POST", body: { goals: [] } }); setJoined(true); } catch { setJoined(true); } }
  async function addContact() {
    try { const c = await api("/api/support/needs_a_ride/family/contacts", { method: "POST", body: { label: contact } }); setContacts((x) => [...x, c]); setContact(""); }
    catch (e) { setMsg(e.message); }
  }
  return (
    <section>
      <h1>{t("nav.support")}</h1>
      <h2>{t("support.resourcesTitle")}</h2>
      <p>{t("support.resourcesNote")}</p>
      <TranslationCheck keys="support.resourcesNote" />
      <ul>{resources.map((r) => <li key={r.id}>{r.name} ({r.category}) <ReadAloud text={r.name} /></li>)}</ul>
      <h2>{t("support.meetingsTitle")}</h2>
      <ul>{meetings.map((m) => <li key={m.id}>{m.name} — {m.program}, {m.day} {m.time}, {m.city}</li>)}</ul>
      <div data-testid="mentorship-section"><h2>{t("phase3.mentorshipTitle")}</h2><p>{t("phase3.mentorshipHelp")}</p><ReadAloud text={t("phase3.mentorshipHelp")} /></div>
      <div data-testid="geo-section"><h2>{t("phase3.geoTitle")}</h2><p>{t("phase3.geoHelp")}</p><ReadAloud text={t("phase3.geoHelp")} /></div>
      <div data-testid="carpool-section"><h2>{t("phase3.carpoolTitle")}</h2><p>{t("phase3.carpoolHelp")}</p><ReadAloud text={t("phase3.carpoolHelp")} />
        <label>{t("phase3.carpoolCity")} <input value={city} onChange={(e) => setCity(e.target.value)} placeholder="Fort Worth" /></label>
        <label>{t("phase3.carpoolMeeting")} <input value={meetingId} onChange={(e) => setMeetingId(e.target.value)} /></label>
        <button type="button" onClick={joinCarpool}>{t("phase3.carpoolJoin")}</button>
        <ul>{entries.map((e, i) => <li key={i}>{e.member?.handle} — {e.city} ({e.meeting_id})</li>)}</ul></div>
      <div data-testid="groups-section"><h2>{t("phase3.groupsTitle2")}</h2><p>{t("phase3.groupsHelp")}</p><ReadAloud text={t("phase3.groupsHelp")} />
        <ul>{groups.map((g) => <li key={g.id}>{g.name} — {g.kind}, {g.city}, {g.meeting_time} <span>{t("phase3.sampleBadge")}</span></li>)}</ul></div>
      {showFallback && (<div data-testid="ride-fallback"><h2>{t("phase3.rideFallbackTitle")}</h2><p>{t("phase3.noCarpoolMatch")}</p><p>{t("phase3.rideFallbackHelp")}</p><ReadAloud text={t("phase3.rideFallbackHelp")} /></div>)}
      <div data-testid="family-ride-section"><h2>{t("phase3.familyRideTitle")}</h2><p>{t("phase3.familyRideHelp")}</p><ReadAloud text={t("phase3.familyRideHelp")} />
        <label>{t("phase3.contactLabel")} <input value={contact} onChange={(e) => setContact(e.target.value)} /></label>
        <button type="button" onClick={addContact}>{t("phase3.addContact")}</button>
        <ul>{contacts.map((c) => <li key={c._id}>{c.label} — {c.verified ? t("phase3.verified") : t("phase3.notAvailable")}</li>)}</ul></div>
      <div data-testid="partners-section"><h2>{t("phase3.partnersTitle")}</h2><p>{t("phase3.partnersHelp")}</p><ReadAloud text={t("phase3.partnersHelp")} />
        <button type="button" onClick={joinPartners}>{t("phase3.joinPartners")}</button>{joined && <p role="status">✓</p>}</div>
      {msg && <p role="status">{msg}</p>}
    </section>
  );
}
