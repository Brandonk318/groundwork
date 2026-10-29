import { NavLink, Outlet } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { APP_NAME } from "../brand";
import { AREAS } from "../areas";
import CrisisButton from "./CrisisButton";
import LanguageSwitcher from "./LanguageSwitcher";

export default function Shell() {
  const { t } = useTranslation();
  return (
    <div className="shell">
      <header>
        <strong className="brand">{APP_NAME}</strong>
        <CrisisButton />
      </header>
      <nav aria-label="main">
        <NavLink to="/">{t("nav.home")}</NavLink>
        {AREAS.map((a) => <NavLink key={a.path} to={`/${a.path}`}>{t(`nav.${a.key}`)}</NavLink>)}
      </nav>
      <main><Outlet /></main>
      <footer><LanguageSwitcher /></footer>
    </div>
  );
}
