import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import Accuracy from "./pages/Accuracy";
import Forecasts from "./pages/Forecasts";
import Landing from "./pages/Landing";
import Methodology from "./pages/Methodology";
import Overview from "./pages/Overview";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route element={<Layout />}>
        <Route path="/overview" element={<Overview />} />
        <Route path="/forecasts" element={<Forecasts />} />
        <Route path="/accuracy" element={<Accuracy />} />
        <Route path="/methodology" element={<Methodology />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
