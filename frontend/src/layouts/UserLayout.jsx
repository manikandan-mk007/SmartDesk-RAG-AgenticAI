import { Link, NavLink, Outlet } from "react-router-dom";
import Button from "../components/common/Button";
import Icon from "../components/common/Icon";
import { useAuth } from "../context/AuthContext";
import TopbarActions from "../components/common/TopbarActions";

export default function UserLayout() {
  const { user, logout } = useAuth();

  return (
    <div className="sd-page">
      <header className="sd-topbar">
        <div className="sd-topbar-left">
          <Link to="/" className="sd-brand">SmartDesk</Link>

          <nav className="sd-top-nav">
            <NavLink to="/" className={({ isActive }) => `sd-nav-link ${isActive ? "active" : ""}`}>
              Home
            </NavLink>
            <NavLink to="/tickets" className={({ isActive }) => `sd-nav-link ${isActive ? "active" : ""}`}>
              My Tickets
            </NavLink>
          </nav>
        </div>

        <div className="sd-topbar-right">
          {user ? (
            <>
              <span className="sd-user-name">{user.full_name}</span>
              <button className="sd-nav-link" onClick={logout}>Logout</button>
            </>
          ) : (
            <>
              <Link to="/login" className="sd-nav-link">Login</Link>
              <Link to="/register"><Button>Register</Button></Link>
            </>
          )}

          <TopbarActions />
          
        </div>
      </header>

      <main className="sd-main">
        <Outlet />
      </main>
    </div>
  );
}