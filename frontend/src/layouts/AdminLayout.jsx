import { NavLink, Outlet } from "react-router-dom";
import Icon from "../components/common/Icon";
import { useAuth } from "../context/AuthContext";
import TopbarActions from "../components/common/TopbarActions";
export default function AdminLayout() {
  const { user, logout } = useAuth();

  const navItems = [
    { to: "/admin/dashboard", label: "Dashboard", icon: "dashboard" },
    { to: "/admin/users", label: "Users", icon: "group" },
    { to: "/admin/agents", label: "Agents", icon: "support_agent" },
    { to: "/admin/faqs", label: "FAQs", icon: "help" },
    { to: "/admin/kb", label: "Knowledge Base", icon: "article" },
    { to: "/admin/reports", label: "Reports", icon: "monitoring" },
  ];

  return (
    <div className="sd-page">
      <header className="sd-topbar">
        <div className="sd-topbar-left">
          <span className="sd-brand">SmartDesk</span>

          <nav className="sd-top-nav">
            {navItems.slice(0, 4).map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) => `sd-nav-link ${isActive ? "active" : ""}`}
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>

        <div className="sd-topbar-right">
          <span className="sd-user-name">{user?.full_name}</span>
          <button className="sd-nav-link" onClick={logout}>Logout</button>
          <TopbarActions />
        </div>
      </header>

      <aside className="sd-sidebar">
        <div>
          <div className="sd-sidebar-head">
            <div className="sd-sidebar-title-row">
              <div className="sd-sidebar-logo">
                <Icon name="admin_panel_settings" />
              </div>
              <div>
                <h2 className="sd-heading-sm">Admin Console</h2>
                <p className="sd-label-sm sd-muted">System Control</p>
              </div>
            </div>
          </div>

          <nav className="sd-sidebar-nav">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) => `sd-sidebar-link ${isActive ? "active" : ""}`}
              >
                <Icon name={item.icon} />
                <span>{item.label}</span>
              </NavLink>
            ))}
          </nav>
        </div>

        <div className="sd-sidebar-bottom">
          <button className="sd-sidebar-link" onClick={logout}>
            <Icon name="logout" />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      <main className="sd-console-main">
        <div className="sd-console-content">
          <Outlet />
        </div>
      </main>
    </div>
  );
}