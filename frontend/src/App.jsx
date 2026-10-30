import { Route, Routes } from "react-router-dom";
import Shell from "./components/Shell";
import Home from "./pages/Home";
import AreaPage from "./pages/AreaPage";
import WellbeingPage from "./pages/WellbeingPage";
import CommunityPage from "./pages/CommunityPage";
import SupportPage from "./pages/SupportPage";
import SafetyPage from "./pages/SafetyPage";
import ReentryPage from "./pages/ReentryPage";
import WorkPage from "./pages/WorkPage";
import JourneyPage from "./pages/JourneyPage";
import VenuePage from "./pages/VenuePage";
import SettingsPage from "./pages/SettingsPage";
import FamilyPage from "./pages/FamilyPage";
import LearnPage from "./pages/LearnPage";
import MatchPage from "./pages/MatchPage";
import { AREAS } from "./areas";

const PAGES = { feed: CommunityPage, wellbeing: WellbeingPage, support: SupportPage, safety: SafetyPage, reentry: ReentryPage, work: WorkPage, journey: JourneyPage, venue: VenuePage, settings: SettingsPage, family: FamilyPage, learn: LearnPage, match: MatchPage };

export default function App() {
  return (
    <Routes>
      <Route element={<Shell />}>
        <Route index element={<Home />} />
        {AREAS.map((a) => { const P = PAGES[a.path]; return <Route key={a.path} path={a.path} element={P ? <P /> : <AreaPage area={a} />} />; })}
        <Route path="*" element={<Home />} />
      </Route>
    </Routes>
  );
}
