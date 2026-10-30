import { useState } from "react";
import { useTranslation } from "react-i18next";
import { login, register, setToken } from "../api";
import ReadAloud from "../components/ReadAloud";
import MusicPlayer from "../components/MusicPlayer";
export default function SettingsPage() {
  const { t } = useTranslation();
  const [handle, setHandle] = useState("");
  const [pw, setPw] = useState("");
  const [msg, setMsg] = useState("");
  async function doRegister() { try { const r = await register(handle, pw); setToken(r.token); setMsg(t("settings.loggedIn")); } catch (e) { setMsg(e.message); } }
  async function doLogin() { try { const r = await login(handle, pw); setToken(r.token); setMsg(t("settings.loggedIn")); } catch (e) { setMsg(e.message); } }
  return (
    <section>
      <h1>{t("nav.platform")}</h1>
      <h2>{t("settings.accountTitle")}</h2>
      <label>{t("settings.handle")} <input value={handle} onChange={(e) => setHandle(e.target.value)} /></label>
      <label>{t("settings.password")} <input type="password" value={pw} onChange={(e) => setPw(e.target.value)} /></label>
      <button type="button" onClick={doRegister}>{t("settings.register")}</button>
      <button type="button" onClick={doLogin}>{t("settings.login")}</button>
      <h2>{t("readAloud.title")}</h2>
      <p>{t("readAloud.help")}</p>
      <ReadAloud text={t("readAloud.help")} />
      <MusicPlayer />
      {msg && <p role="status">{msg}</p>}
    </section>
  );
}
