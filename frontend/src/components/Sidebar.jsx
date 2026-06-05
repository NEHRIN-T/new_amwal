import { NavLink } from "react-router-dom";
import { getUser } from "../api/client";
import logo from "../logo.png";
import "./Sidebar.css";

export default function Sidebar({ mode = "client" }) {
  const user = getUser();
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <img className="logo-icon" src={logo} alt="amwal" />
      </div>
      <nav className="sidebar-nav">
        {mode === "client" && (
          <>
            <div className="nav-group-label">INTELLIGENCE</div>
            <NavLink to="/" end className={({ isActive }) => "nav-item" + (isActive ? " active" : "")}>
              Portfolio Overview
            </NavLink>
            <NavLink to="/rental" className={({ isActive }) => "nav-item" + (isActive ? " active" : "")}>
              Rental Intelligence
            </NavLink>
            <NavLink to="/occupancy" className={({ isActive }) => "nav-item" + (isActive ? " active" : "")}>
              Occupancy
            </NavLink>
            <div className="nav-group-label">FINANCE</div>
            <NavLink to="/financial" className={({ isActive }) => "nav-item" + (isActive ? " active" : "")}>
              Financial Dashboard
            </NavLink>
          </>
        )}
        {mode === "backend" && (
          <>
            <NavLink to="/admin/properties" className={({ isActive }) => "nav-item" + (isActive ? " active" : "")}>
              Property Management
            </NavLink>
            <NavLink to="/admin/rent" className={({ isActive }) => "nav-item" + (isActive ? " active" : "")}>
              Rent and Market Data
            </NavLink>
            <NavLink to="/admin/leases" className={({ isActive }) => "nav-item" + (isActive ? " active" : "")}>
              Tenant and Lease
            </NavLink>
            <NavLink to="/admin/occupancy" className={({ isActive }) => "nav-item" + (isActive ? " active" : "")}>
              Occupancy Management
            </NavLink>
            <NavLink to="/admin/financial" className={({ isActive }) => "nav-item" + (isActive ? " active" : "")}>
              Financial Data Entry
            </NavLink>
          </>
        )}
      </nav>
      <div className="sidebar-user">
        <div className="avatar">{user?.first_name?.[0] || "U"}</div>
        <div>
          <div className="user-name">
            {user?.first_name} {user?.last_name}
          </div>
          <div className="user-role">{user?.role}</div>
        </div>
      </div>
      <div className="sidebar-footer">AMWAL v1.0 March 2026</div>
    </aside>
  );
}
