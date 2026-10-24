import { Outlet } from "react-router-dom";
import Footer from "./Footer";
import Header from "./Header";

export default function Layout() {
  return (
    <div className="app-shell">
      <Header />
      <main id="main-content" className="page-main">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
