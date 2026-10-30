import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../api";

export default function MusicPlayer() {
  const { t } = useTranslation();
  const { pathname } = useLocation();
  const [tracks, setTracks] = useState([]);
  const [playing, setPlaying] = useState(null);
  useEffect(() => { api("/api/platform/music_player/tracks").then((d) => setTracks(d.tracks || [])).catch(() => setTracks([{ id: "t1", title: "Sample Track One", sample: true }])); }, []);
  if (pathname.startsWith("/learn")) {
    return <p data-testid="music-off">{t("phase3.musicOffAcademy")}</p>;
  }
  return (
    <div data-testid="music-player">
      <h2>{t("phase3.musicTitle")}</h2>
      <p>{t("phase3.musicHelp")}</p>
      <ul>{tracks.map((x) => <li key={x.id}>{x.title} ({t("phase3.sampleBadge")}) <button type="button" onClick={() => setPlaying(playing === x.id ? null : x.id)}>{playing === x.id ? t("phase3.pause") : t("phase3.play")}</button></li>)}</ul>
    </div>
  );
}
