import { NavLink } from "react-router-dom";

const LINKS = [
  { to: "/overview", label: "Overview" },
  { to: "/forecasts", label: "Forecasts" },
  { to: "/accuracy", label: "Accuracy" },
  { to: "/methodology", label: "Methodology" },
];

export default function Header() {
  return (
    <header className="site-header">
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      <div className="header-inner">
        <NavLink className="wordmark" to="/" aria-label="DevWindmark home">
          DevWindmark
        </NavLink>
        <nav className="primary-nav" aria-label="Primary">
          {LINKS.map((link) => (
            <NavLink key={link.to} to={link.to} className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}>
              {link.label}
            </NavLink>
          ))}
        </nav>
        <nav className="external-nav" aria-label="External profiles">
          <a href="https://devanshportfolio-rho.vercel.app" target="_blank" rel="noopener noreferrer">
            Portfolio
          </a>
          <a href="https://github.com/DevanshSharma-GIT" target="_blank" rel="noopener noreferrer">
            GitHub
          </a>
          <a href="https://www.linkedin.com/in/devansh-sharma-9713a8292/" target="_blank" rel="noopener noreferrer">
            LinkedIn
          </a>
        </nav>
      </div>
    </header>
  );
}
