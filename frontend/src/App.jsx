import { Route, Routes } from "react-router-dom";
import Shell from "./components/Shell";
import Home from "./pages/Home";
import AreaPage from "./pages/AreaPage";
import { AREAS } from "./areas";

export default function App() {
  return (
    <Routes>
      <Route element={<Shell />}>
        <Route index element={<Home />} />
        {AREAS.map((a) => <Route key={a.path} path={a.path} element={<AreaPage area={a} />} />)}
        <Route path="*" element={<Home />} />
      </Route>
    </Routes>
  );
}
