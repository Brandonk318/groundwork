import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { api } from "../api";
import ReadAloud from "../components/ReadAloud";
import CrisisNotice from "../components/CrisisNotice";
export default function CommunityPage() {
  const { t } = useTranslation();
  const [posts, setPosts] = useState([]);
  const [body, setBody] = useState("");
  const [anon, setAnon] = useState(false);
  const [msg, setMsg] = useState("");
  const [notice, setNotice] = useState(null);
  const [recipient, setRecipient] = useState("");
  const [dm, setDm] = useState("");
  const [eventTitle, setEventTitle] = useState("");
  const [groupName, setGroupName] = useState("");
  const [qa, setQa] = useState("");
  const [questions, setQuestions] = useState([]);
  async function load() { try { setPosts((await api("/api/community/community_feed/posts")).posts || []); } catch {} }
  useEffect(() => { load(); api("/api/community/anonymous_qa/questions").then((d) => setQuestions(d.questions || [])).catch(() => {}); }, []);
  async function post() { try { const r = await api("/api/community/community_feed/posts", { method: "POST", body: { body, anonymous: anon } }); setNotice(r.private_notice || null); setBody(""); load(); } catch (e) { setMsg(e.message); } }
  async function sendDm() { try { const r = await api("/api/community/peer_messaging/messages", { method: "POST", body: { recipient_id: recipient, body: dm } }); setMsg(t("community.dmSent")); if (r.recipient?.phone) setMsg("phone exposed"); } catch (e) { setMsg(e.message); } }
  async function postEvent() { try { await api("/api/community/events", { method: "POST", body: { title: eventTitle } }); setEventTitle(""); setMsg("✓"); } catch (e) { setMsg(e.message); } }
  async function postGroup() { try { await api("/api/community/program_groups", { method: "POST", body: { name: groupName } }); setGroupName(""); setMsg("✓"); } catch (e) { setMsg(e.message); } }
  async function askQa() { try { const r = await api("/api/community/anonymous_qa/questions", { method: "POST", body: { body: qa } }); setNotice(r.private_notice || null); setQa(""); setMsg("✓"); } catch (e) { setMsg(e.message); } }
  async function upload(kind, fid, file) {
    if (!file) return;
    const buf = await file.arrayBuffer();
    let bin = ""; const bytes = new Uint8Array(buf);
    for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
    try { await api(`/api/community/${fid}`, { method: "POST", body: { filename: file.name, content_type: file.type, data_b64: btoa(bin), caption: "" } }); setMsg("✓"); }
    catch (e) { setMsg(e.message); }
  }
  return (
    <section>
      <h1>{t("nav.community")}</h1>
      <h2>{t("community.feedTitle")}</h2>
      <label>{t("community.postBody")} <textarea value={body} onChange={(e) => setBody(e.target.value)} /></label>
      <label><input type="checkbox" checked={anon} onChange={(e) => setAnon(e.target.checked)} /> {t("community.anonymous")}</label>
      <button type="button" onClick={post}>{t("community.post")}</button>
      <CrisisNotice notice={notice} />
      <ul>{posts.map((p, i) => <li key={p._id || i}>{p.body} — {typeof p.author === "object" ? p.author.display : p.author_handle || ""}</li>)}</ul>
      <h2>{t("community.dmTitle")}</h2>
      <p>{t("community.noPhone")}</p>
      <label>{t("community.recipient")} <input value={recipient} onChange={(e) => setRecipient(e.target.value)} /></label>
      <label>{t("community.message")} <input value={dm} onChange={(e) => setDm(e.target.value)} /></label>
      <button type="button" onClick={sendDm}>{t("community.send")}</button>
      <div data-testid="events-section"><h2>{t("phase3.eventsTitle")}</h2><ReadAloud text={t("phase3.eventsTitle")} />
        <label>{t("phase3.eventsTitle")} <input value={eventTitle} onChange={(e) => setEventTitle(e.target.value)} /></label>
        <button type="button" onClick={postEvent}>{t("phase3.postEvent")}</button></div>
      <div data-testid="groups-section"><h2>{t("phase3.groupsTitle")}</h2><ReadAloud text={t("phase3.groupsTitle")} />
        <label>{t("phase3.groupsTitle")} <input value={groupName} onChange={(e) => setGroupName(e.target.value)} /></label>
        <button type="button" onClick={postGroup}>{t("phase3.createGroup")}</button></div>
      <div data-testid="meetings-section"><h2>{t("phase3.meetingsTitle")}</h2><ReadAloud text={t("phase3.meetingsTitle")} /></div>
      <div data-testid="media-section"><h2>{t("phase3.mediaTitle")}</h2><ReadAloud text={t("phase3.mediaTitle")} />
        <label>{t("phase3.photo")} <input type="file" accept="image/*" onChange={(e) => upload("photo", "photo_posts", e.target.files[0])} /></label>
        <label>{t("phase3.video")} <input type="file" accept="video/*" onChange={(e) => upload("video", "video_posts", e.target.files[0])} /></label>
        <label>{t("phase3.voice")} <input type="file" accept="audio/*" onChange={(e) => upload("voice", "voice_notes", e.target.files[0])} /></label></div>
      <div data-testid="qa-section"><h2>{t("phase3.qaTitle")}</h2><p>{t("phase3.qaHelp")}</p><ReadAloud text={t("phase3.qaHelp")} />
        <label>{t("phase3.qaTitle")} <textarea value={qa} onChange={(e) => setQa(e.target.value)} /></label>
        <button type="button" onClick={askQa}>{t("phase3.ask")}</button>
        <ul>{questions.map((q, i) => <li key={q.id || i}>{q.body}</li>)}</ul></div>
      {msg && <p role="status">{msg}</p>}
    </section>
  );
}
