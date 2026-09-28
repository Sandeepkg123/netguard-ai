import { NavLink, Outlet } from "react-router-dom";

function Layout() {
  const links = [
    { path: "/", label: "Dashboard" },
    { path: "/upload", label: "Upload Config" },
    { path: "/frameworks", label: "Frameworks" },
  ];

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="logo">
          <div className="logo-mark">N</div>
          <div>
            <h2>NetGuard AI</h2>
            <span>Security Auditor</span>
          </div>
        </div>

        <nav>
          {links.map((link) => (
            <NavLink
              key={link.path}
              to={link.path}
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <span className="online-dot" />
          Backend connected
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <h1>Network Security Compliance</h1>
            <p>AI-driven multi-vendor configuration auditing</p>
          </div>
        </header>

        <section className="page-content">
          <Outlet />
        </section>
      </main>
    </div>
  );
}

export default Layout;