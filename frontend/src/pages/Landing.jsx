import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import DataStatus from "../components/DataStatus";
import Footer from "../components/Footer";
import Header from "../components/Header";

export default function Landing() {
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    document.title = "DevWindmark";
    api.summary().then(setSummary).catch((err) => setError(err.message));
  }, []);

  return (
    <div className="app-shell landing-shell">
      <Header />
      <main id="main-content" className="hero">
        <p className="eyebrow">January 2026 day-ahead window</p>
        <h1>Wind forecast intelligence for electricity procurement.</h1>
        <p className="lede">
          DevWindmark shows the latest national GB wind generation forecast that was available at the
          configured day-ahead decision cutoff, then measures it against Elexon half-hourly wind outturn.
        </p>
        <div className="hero-actions">
          <Link className="primary-button" to="/overview">
            Open dashboard
          </Link>
          <Link className="ghost-button" to="/methodology">
            Read methodology
          </Link>
        </div>
        <p className="period-note">Analysis period: 1 January 2026 to 31 January 2026. Units: MW.</p>
        {error ? <p className="inline-error">{error}</p> : <DataStatus provenance={summary?.provenance} />}
      </main>
      <Footer />
    </div>
  );
}
